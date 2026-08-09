import os, re, json, time, sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from ddgs import DDGS

DB_PATH = "customer.db"
MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-3.5-flash")
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

app = FastAPI(title="NewsFindr Backend", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

TRUSTED = ("reuters.com, apnews.com, bbc.com, nytimes.com, theguardian.com, wsj.com, "
           "bloomberg.com, cnbc.com, techcrunch.com, ndtv.com, economictimes.indiatimes.com, "
           "thehindu.com, indianexpress.com, livemint.com, espn.com, forbes.com")


def chat(system: str, user: str, temperature: float = 0.0) -> str:
    """One Gemini call with combined system+user context; one retry on transient errors."""
    payload = system + "\n\n" + user
    last_err = None
    for attempt in range(2):
        try:
            r = client.models.generate_content(
                model=MODEL_NAME, contents=payload,
                config={"temperature": temperature})
            try:
                return (r.text or "").strip()
            except ValueError:            # response had no text parts (e.g. safety block)
                return ""
        except Exception as e:            # e.g. transient rate limit
            last_err = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Gemini call failed after 2 attempts: {last_err}")


def get_customer(email: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, interests FROM customers WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row


def expand_queries(interests, user_query):
    system = ("You are a news search-query expansion assistant. Given ONE user interest "
              "(and an optional specific user query), generate EXACTLY ONE precise, time-sensitive "
              "DuckDuckGo search query that retrieves the LATEST breaking news and recent "
              "developments about that interest. Rules: focus ONLY on current events; include "
              "freshness words such as latest, today, this week or breaking; NEVER include "
              "specific years or dates; output ONLY the search query text.")
    queries = []
    for interest in interests:
        q = chat(system, f"Generate one search query related to: '{interest}' "
                         f"considering the user query: '{user_query}'").strip('"')
        if q:
            queries.append(q)
    return queries


def ddg_search(query: str, max_results: int = 5):
    results, last_err = [], None
    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({"title": r.get("title", ""), "url": r.get("href", ""),
                                    "body": r.get("body", "")})
            if results:
                return results
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    if last_err:
        raise RuntimeError(f"DuckDuckGo search failed after 3 attempts: {last_err}")
    return results


def _extract_json_list(text: str):
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if not m:
        return []
    try:
        parsed = json.loads(m.group(0))
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def filter_results(results, interests):
    system = ("You are a news credibility and relevance filter for a personalised news agent. "
              "Evaluate every search result on TWO axes: 1. CREDIBILITY - prefer established, "
              "trustworthy news organisations (e.g. " + TRUSTED + "). Reject blogs, forums, "
              "social-media posts, content farms, SEO spam and unknown/low-quality sites. "
              "2. RELEVANCE - keep only items whose topic matches the user's interests. "
              "Return ONLY a JSON list of the approved results, each as "
              "{\"title\": ..., \"url\": ..., \"body\": ...}. No markdown fences, JSON only.")
    prompt = ("User interests: " + json.dumps(interests) +
              "\nEvaluate the credibility and relevance of these search results and keep only "
              "trustworthy, interest-relevant ones:\n" + json.dumps(results, indent=2))
    filtered = _extract_json_list(chat(system, prompt))
    return filtered or results


def summarize(results):
    system = ("You are a news summarizer for a personalised news agent. You receive credible "
              "news results (title, URL, snippet). For EACH result, in order: 1. Write a one-line "
              "HEADLINE in bold using the result's title (or infer it from the URL/domain). "
              "2. Write a concise 2-3 sentence summary of the latest development it reports, "
              "based on the snippet and the source context. If only a bare URL is available, "
              "summarize from the domain/path context and say so honestly. Number the articles "
              "1., 2., 3. ... and keep the tone neutral and factual.")
    return chat(system, "Summarize the following credible news results for the user:\n" +
                json.dumps(results, indent=2))


class NewsRequest(BaseModel):
    email: str
    user_query: str


@app.get("/")
def health():
    return {"status": "ok", "service": "NewsFindr backend", "model": MODEL_NAME}


@app.post("/news")
def news(req: NewsRequest):
    row = get_customer(req.email)
    if not row:
        return {"found": False, "message": "email not found", "urls": [], "summary": ""}
    name, interests_str = row
    try:
        interests = json.loads(interests_str)
    except (json.JSONDecodeError, TypeError):
        interests = [str(interests_str)]
    queries = expand_queries(interests, req.user_query)
    results = []
    for q in queries:
        results.extend(ddg_search(q))
    filtered = filter_results(results, interests)
    top = filtered[:3]                                    # top-3 latest news
    return {"found": True, "customer": name, "interests": interests,
            "queries": queries, "urls": [r.get("url", "") for r in top],
            "summary": summarize(top)}

# NewsFindr — Agentic AI-Powered News Retrieval

An agentic AI system that delivers **real-time, personalized, credible news** to registered customers.

## Architecture
1. **SQL agent** verifies the customer's email against `customer.db` (SQLite) and retrieves their interests ("email not found" for unknown users).
2. **Query expansion (LLM, Google Gemini `gemini-3.5-flash`)** turns each interest into a precise, time-sensitive search query (latest/today/this week, no years).
3. **DuckDuckGo search (`ddgs`)** fetches the top-5 fresh results per query.
4. **Credibility filter (LLM)** keeps only trustworthy, interest-relevant URLs.
5. **Summarizer (LLM)** produces numbered per-article summaries of the top-3 latest articles.

## Repository contents
- `NewsFindr_Agentic_AI_News_Retrieval.ipynb` — the full learner notebook (run in Google Colab)
- `backend/` — FastAPI backend (Hugging Face Space, Docker SDK): `POST /news {email, user_query}` (Gemini-powered; needs a `GOOGLE_API_KEY` Space secret)
- `frontend/` — Gradio frontend (Hugging Face Space) calling the backend
- `customer.db` + `create_db.py` — the customer dataset

## Links
- Frontend Space: see the notebook's Project Links section
- Backend Space: see the notebook's Project Links section

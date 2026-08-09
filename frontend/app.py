import os
import requests
import gradio as gr

BACKEND_URL = os.environ.get("BACKEND_URL", "").rstrip("/")

def fetch_news(email, user_query):
    if not BACKEND_URL:
        return ("BACKEND_URL is not configured. Add it as a Space secret.", "", "")
    try:
        r = requests.post(f"{BACKEND_URL}/news",
                          json={"email": email, "user_query": user_query}, timeout=180)
        data = r.json()
    except Exception as e:
        return (f"Backend error: {e}", "", "")
    if not data.get("found"):
        return (data.get("message", "email not found"), "", "")
    header = (f"### Verified customer: {data.get('customer', '')}\n"
              f"**Interests:** {', '.join(data.get('interests', []))}\n\n"
              f"**Expanded queries:** {' | '.join(data.get('queries', []))}")
    urls = "\n".join(f"{i+1}. {u}" for i, u in enumerate(data.get("urls", [])))
    return header, urls, data.get("summary", "")

demo = gr.Interface(
    fn=fetch_news,
    inputs=[
        gr.Textbox(label="Customer email", value="kevin.f8641860-7@gmail.com"),
        gr.Textbox(label="What news are you looking for?", value="latest startup funding news"),
    ],
    outputs=[
        gr.Markdown(label="Verified customer"),
        gr.Textbox(label="Top credible URLs", lines=5),
        gr.Markdown(label="Summaries"),
    ],
    title="NewsFindr - Personalized News Agent",
    description=("Enter a registered customer email and a topic. The agent verifies the customer, "
                 "expands their interests into fresh search queries, fetches DuckDuckGo news, "
                 "credibility-filters the sources, and summarizes the top-3 latest articles."),
    examples=[
        ["kevin.f8641860-7@gmail.com", "latest startup funding news"],
        ["alice.6eb33c45-5@gmail.com", "latest technology and business news"],
        ["oscar.edd38e10-6@gmail.com", "latest sports news in India"],
    ],
)

if __name__ == "__main__":
    demo.launch()

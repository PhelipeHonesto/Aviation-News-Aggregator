import httpx
from openai import OpenAI

def rewrite_article(title: str, body: str, api_key: str) -> str:
    """
    Rewrite a news article using OpenAI GPT. Returns the rewritten body as a string.
    """
    http_client = httpx.Client(timeout=httpx.Timeout(30.0), follow_redirects=True)
    client = OpenAI(api_key=api_key, http_client=http_client)
    prompt = f"Rewrite the following news article for a general audience. Keep it concise, informative, and engaging. \n\nTitle: {title}\n\nArticle: {body}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        edited_body = response.choices[0].message.content
        if not edited_body:
            raise RuntimeError("AI failed to generate content.")
        return edited_body
    except Exception as e:
        raise RuntimeError(f"OpenAI error: {e}") 
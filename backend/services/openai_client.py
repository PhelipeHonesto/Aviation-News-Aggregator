import httpx
from openai import OpenAI
import logging

def rewrite_article(title: str, body: str, api_key: str) -> str:
    """
    Rewrite a news article using OpenAI GPT with aviation-specific context.
    Returns the rewritten body as a string.
    """
    if not api_key:
        raise ValueError("OpenAI API key is required")
    
    if not title or not body:
        raise ValueError("Title and body are required for rewriting")
    
    http_client = httpx.Client(timeout=httpx.Timeout(60.0), follow_redirects=True)
    client = OpenAI(api_key=api_key, http_client=http_client)
    
    # Aviation-specific prompt for better context
    prompt = f"""Rewrite the following aviation news article for Orange Sunshine Aviation's audience. 
    
    Guidelines:
    - Write in a professional but engaging tone suitable for aviation professionals
    - Keep it concise (2-3 paragraphs max)
    - Focus on key facts and implications for the aviation industry
    - Use clear, accessible language
    - Maintain accuracy while making it more readable
    - Include relevant context about how this affects aviation operations
    
    Title: {title}
    
    Original Article: {body}
    
    Rewritten Article:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        edited_body = response.choices[0].message.content
        if not edited_body:
            raise RuntimeError("AI failed to generate content.")
        
        # Clean up the response
        edited_body = edited_body.strip()
        
        # Ensure it's not too short or too long
        if len(edited_body) < 50:
            raise RuntimeError("AI generated content is too short.")
        if len(edited_body) > 2000:
            edited_body = edited_body[:2000] + "..."
        
        logging.info(f"Successfully rewrote article: {title[:50]}...")
        return edited_body
        
    except Exception as e:
        logging.error(f"OpenAI error while rewriting article '{title}': {e}")
        raise RuntimeError(f"Failed to rewrite article: {str(e)}") 
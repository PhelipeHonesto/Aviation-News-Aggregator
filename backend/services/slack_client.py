import requests

def format_slack_message(article) -> dict:
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":newspaper: {article.title or 'No Title'}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": article.body or "No content available.",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Source: *{article.source or 'N/A'}* | <{article.link or '#'}|Read Original>",
                    }
                ],
            },
        ]
    }

def post_article_to_slack(article, webhook_url: str) -> None:
    payload = format_slack_message(article)
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status() 
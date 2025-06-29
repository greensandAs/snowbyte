import requests
import logging
import html
from config.settings import FALLBACK_IMAGE_URL
from utils.helpers import normalize_text

def send_blog_card_to_google_chat(title, summary, url, image_url, webhook_url):
    """
    Sends a rich Google Chat message card with blog details.
    """
    try:
        # --- Normalize and sanitize content ---
        safe_title = normalize_text(title.strip())[:200]

        if not summary or not isinstance(summary, str):
            safe_summary = "Summary not available."
        else:
            normalized_summary = normalize_text(summary.strip())
            escaped_summary = html.escape(normalized_summary)
            final_summary = escaped_summary.replace('\n', '<br>')
            safe_summary = final_summary[:4000]

        final_image_url = image_url or FALLBACK_IMAGE_URL

        # --- Google Chat card structure ---
        card = {
            "cardsV2": [{
                "cardId": "new_blog_card",
                "card": {
                    "header": {
                        "title": "SnowBytes",
                        "subtitle": "Latest Snowflake Blog From Medium",
                        "imageUrl": "https://media.licdn.com/dms/image/v2/D5612AQGXKCeRh4xFdw/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1727556320033?e=2147483647&v=beta&t=dPcJdj3s7xMhjUKHjE8fF8cavBCNe7sbTAT1GGpbzq4",
                        "imageType": "CIRCLE"
                    },
                    "sections": [{
                        "collapsible": False,
                        "uncollapsibleWidgetsCount": 1,
                        "widgets": [
                            {"textParagraph": {"text": f"<b>{safe_title}</b>"}},
                            {"divider": {}},
                            {"decoratedText": {"icon": {"knownIcon": "DESCRIPTION"}, "text": "Summary"}},
                            {"textParagraph": {"text": f"{safe_summary}<br><br><b>🔗<a href=\"{url}\">Read Full Article</a></b>"}},
                            {
                                "image": {
                                    "imageUrl": final_image_url,
                                    "onClick": {"openLink": {"url": url}}
                                }
                            },
                            {"divider": {}},
                            {"textParagraph": {
                                "text": "<i>Summary generated using <a href=\"https://docs.snowflake.com/en/guides-overview-ai-features\">Snowflake Cortex AI</a> ❄️</i>"
                            }}
                        ]
                    }]
                }
            }]
        }

        # --- Send card to webhook ---
        response = requests.post(webhook_url, json=card)
        response.raise_for_status()

        print(f"✅ Sent: {title}")
        logging.info(f"[Notifier] Successfully posted blog: {title}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send: {title}\nError: {e}\nPayload: {card}")
        logging.error(f"[Notifier] Failed to send to Google Chat. Title: {title}. Error: {e}. Payload: {card}")
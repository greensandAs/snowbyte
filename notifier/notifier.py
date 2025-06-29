import requests
import logging
import html
import time
import random
from config.settings import FALLBACK_IMAGE_URL
from utils.helpers import normalize_text

def send_blog_card_to_google_chat(title, summary, url, image_url, webhook_url, max_retries=5):
    safe_title = normalize_text(title.strip())[:200]

    if not summary or not isinstance(summary, str):
        safe_summary = "Summary not available."
    else:
        normalized_summary = normalize_text(summary.strip())
        escaped_summary = html.escape(normalized_summary)
        final_summary = escaped_summary.replace('\n', '<br>')
        safe_summary = final_summary[:4000]

    final_image_url = image_url if image_url else FALLBACK_IMAGE_URL

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
                        {"textParagraph": {
                            "text": f"{safe_summary}<br><br><b>🔗<a href=\"{url}\">Read Full Article</a></b>"
                        }},
                        {"image": {"imageUrl": final_image_url, "onClick": {"openLink": {"url": url}}}},
                        {"divider": {}},
                        {"textParagraph": {
                            "text": "<i>Summary generated using <a href=\"https://docs.snowflake.com/en/guides-overview-ai-features\">Snowflake Cortex AI</a> ❄️</i>"
                        }}
                    ]
                }]
            }
        }]
    }

    # Retry logic
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(webhook_url, json=card)
            if response.status_code == 200:
                print(f"✅ Sent: {title}")
                logging.info(f"[Notifier] Sent blog card: {title}")
                return
            elif response.status_code == 429 or 500 <= response.status_code < 600:
                raise requests.exceptions.RequestException(f"Retryable status {response.status_code}: {response.text}")
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            wait = min(2 ** attempt + random.uniform(0, 1), 30)
            logging.warning(f"[Notifier] Attempt {attempt} failed for {title}: {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)

    print(f"❌ Failed to send: {title} after {max_retries} attempts.")
    logging.error(f"[Notifier] Gave up on: {title}. Payload: {card}")

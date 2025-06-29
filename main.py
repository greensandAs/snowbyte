import time
import logging
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from snowflake.snowpark import Session

from scraper.medium_scraper import fetch_urls, fetch_title_content
from storage.snowflake_handler import (
    create_table,
    fetch_existing_titles,
    load_dataframe_to_snowflake,
    enrich_data_with_cortex,
    get_last_day_blogs
)
from notifier.notifier import send_blog_card_to_google_chat
from config.settings import SNOWFLAKE_CONFIG, GOOGLE_CHAT_WEBHOOK

# 🔧 Setup logging
logging.basicConfig(
    filename="snowflake_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    logging.info("🚀 ETL pipeline started.")
    print("🚀 ETL pipeline started.")

    base_url = "https://medium.com/snowflake"
    scraper_session = requests.Session()
    blog_urls = fetch_urls(base_url)

    if not blog_urls:
        logging.warning("No blog URLs found. Exiting.")
        print("❌ No blog URLs found. Exiting.")
        return

    data = []
    for url in blog_urls:
        time.sleep(1)  # Avoid hammering the site
        title, content, full_url, image_url = fetch_title_content(url, scraper_session)
        data.append({
            "TITLE": title,
            "CONTENT": content,
            "URL": full_url,
            "IMAGE_URL": image_url,
            "LOAD_TIME": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            "SUMMARY": None,
            "COMPLETE_SUMMARY": None,
            "SUMMARY_TOKENS": None,
            "SUMMARY_CREDITS": None,
            "COMPLETE_TOKENS": None,
            "COMPLETE_CREDITS": None
        })

    df_all = pd.DataFrame(data)

    # 🧊 Connect to Snowflake
    session = Session.builder.configs(SNOWFLAKE_CONFIG).create()
    create_table(session)

    existing_titles = fetch_existing_titles(session)
    new_rows = df_all[~df_all["TITLE"].isin(existing_titles)]

    if new_rows.empty:
        logging.info("No new blog posts to process.")
        print("🔄 No new blog posts to process.")
    else:
        print(f"🆕 Found {len(new_rows)} new articles to ingest.")
        load_dataframe_to_snowflake(new_rows, session)
        enrich_data_with_cortex(session)

    # 📢 Notify Google Chat with fresh blogs
    recent_blogs = get_last_day_blogs(session)
    print(f"📬 Sending {len(recent_blogs)} blog summaries to Google Chat...")

    for _, row in recent_blogs.iterrows():
        send_blog_card_to_google_chat(
            title=row["TITLE"],
            summary=row["SUMMARY"],
            url=row["URL"],
            image_url=row["IMAGE_URL"],
            webhook_url=GOOGLE_CHAT_WEBHOOK
        )
        time.sleep(5)

    session.close()
    print("✅ ETL pipeline complete.")
    logging.info("✅ ETL pipeline complete.")

if __name__ == "__main__":
    main()

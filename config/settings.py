import os

# 🔐 Webhook for Google Chat Notification (Set via GitHub Secrets)
GOOGLE_CHAT_WEBHOOK = os.getenv("GOOGLE_CHAT_WEBHOOK")

# 🌐 Snowflake Connection Configuration
SNOWFLAKE_CONFIG = {
    "account": "FFDBDRK-HJ42628",
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": "COMPUTE_WH",
    "database": "SNOWBYTE",
    "schema": "DEV"
}

# ❄️ Cortex Parameters for Enrichment
CORTEX_PARAMS = {
    "model": "mistral-large2",
    "prompt": "Summarize the content after ':-', it was blog content. Our motive is to summarize the whole content so that the reader gets quick insight on the blog. Make sure the summarized content should be within 150 words:-",
    "summarize_credit": 0.10 / 1000000,
    #Complete_Credit will differ based on model - Refer "https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf"
    "complete_credit": 1.95 / 1000000
}

# 🖼️ Fallback Image for Blogs Without Thumbnails
FALLBACK_IMAGE_URL = "https://www.artefact.com/wp-content/uploads/2023/12/snowflake-medium-article-visual.png"

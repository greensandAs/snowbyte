# SnowBytes❄️      

![Python Version](https://img.shields.io/badge/python-3.10-blue.svg?style=for-the-badge&logo=python)
![Snowflake Cortex](https://img.shields.io/badge/Snowflake%20Cortex-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white)
![GitHub Actions](https://img.shields.io/github/actions/workflow/status/greensandAs/snowbyte/medium_blog_schedule.yml?style=for-the-badge&logo=githubactions&logoColor=white)

This project is a fully automated ELT pipeline that scrapes Snowflake articles from the official Medium Website, enriches them with AI-generated summaries using **Snowflake Cortex**, stores the results in a Snowflake database, and sends notifications to both Google Chat and an operator via email.

---

### ✨ Core Features

*   **Automated Daily ETL:** Runs on a daily schedule using GitHub Actions to fetch the latest content.
*   **Dual AI Summarization:** Leverages two different Snowflake Cortex functions:
    *   `SNOWFLAKE.CORTEX.SUMMARIZE()` for a quick, concise summary.
    *   `SNOWFLAKE.CORTEX.COMPLETE()` with a custom prompt on the `mistral-large` model for a more detailed completion.
*   **AI Cost Tracking:** Automatically calculates and stores the estimated Snowflake credit cost for each AI operation, enabling usage monitoring.
*   **Rich Google Chat Notifications:** Delivers beautifully formatted cards to a Google Chat space for each new article, complete with title, summary, and thumbnail.
*   **Automated Pipeline Monitoring:** Sends detailed HTML email notifications on the success or failure of each pipeline run.
*   **Robust & Resilient:** Built with production in mind, featuring:
    *   Idempotent design to prevent duplicate data.
    *   Exponential backoff and retry logic for network requests.
    *   Polite scraping with rate limiting.
*   **Secure & Configurable:** Manages all credentials and webhooks securely using GitHub Secrets and environment variables.

### 📊 Workflow

The pipeline follows a clear, automated workflow orchestrated by GitHub Actions.

```mermaid
graph TD
    A[Schedule Trigger] --> B(Scrape Medium Blog);
    B --> C{New Articles?};
    C -- Yes --> D(Load Raw Data to Snowflake);
    D --> E(Enrich with Cortex AI Summaries);
    E --> F(Query Recent Articles);
    F --> G(Send Google Chat Cards);
    G --> H(Pipeline Success);
    C -- No --> I(Pipeline Success);
    subgraph "GitHub Actions Monitoring"
        H --> J[Send Success Email];
        E -- on failure --> K[Send Failure Email];
    end
   ``` 

### 🚀 Getting Started

Follow these instructions to set up the project for both local development and automated deployment.

#### Prerequisites

*   Python 3.10+
*   A Snowflake account with a user, role, and warehouse. Cortex AI functions must be enabled for your account.
*   A Google Chat space with an incoming webhook URL.
*   A Gmail account for sending email notifications via SMTP (if using the GitHub Action as-is).

#### 1. Local Setup

For running the script on your own machine:

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/[YOUR_USERNAME]/[YOUR_REPO_NAME].git
    cd [YOUR_REPO_NAME]
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Create an environment file:**
    Create a file named `.env` in the root directory and populate it with your credentials.

    **.env example:**
    ```
    # Snowflake Credentials
    SNOWFLAKE_USER="your_snowflake_username"
    SNOWFLAKE_PASSWORD="your_snowflake_password"

    # Google Chat Webhook URL
    GOOGLE_CHAT_WEBHOOK="https://chat.googleapis.com/..."
    ```
    *Note: The `.gitignore` file should include `.env` to prevent committing secrets.*

5.  **Run the pipeline manually:**
    ```sh
    python main.py
    ```

#### 2. GitHub Actions Setup (for Automation)

To enable the automated daily runs, you must add the following secrets to your GitHub repository:

1.  Go to your repository on GitHub.
2.  Navigate to **Settings** > **Secrets and variables** > **Actions**.
3.  Click **New repository secret** for each of the following:

    *   `SNOWFLAKE_USER`: Your Snowflake username.
    *   `SNOWFLAKE_PASSWORD`: Your Snowflake password.
    *   `GOOGLE_CHAT_WEBHOOK`: Your Google Chat incoming webhook URL.
    *   `SMTP_USERNAME`: Your Gmail address for sending email alerts.
    *   `SMTP_PASSWORD`: An [App Password](https://support.google.com/accounts/answer/185833) for your Gmail account. **Do not use your main password.**

Once these secrets are set, the workflow in `.github/workflows/medium_blog_schedule.yml` will run automatically.

### 📂 Project Structure

```
.
├── .github/workflows/
│ └── medium_blog_schedule.yml # GitHub Actions workflow for daily execution and monitoring
├── config/
│ └── settings.py # Static configuration for Snowflake, Cortex, and fallbacks
├── notifier/
│ └── notifier.py # Sends rich cards to Google Chat with retry logic
├── scraper/
│ └── medium_scraper.py # Extracts article content and metadata from Medium
├── storage/
│ └── snowflake_handler.py # Manages Snowflake table, data loading, and Cortex AI enrichment
├── utils/
│ └── helpers.py # Utility functions for text normalization and retry logic
├── main.py # Main script, the entry point of the ETL application
├── requirements.txt # Project dependencies
└── README.md # You are here!
```

## Contributors

- Aslam M - aslam.kader@tigeranalytics.com
- Ranjith S - ranjith.subbaiya@tigeranalytics.com

## Maintainers

- Aslam M - aslam.kader@tigeranalytics.com
- Ranjith S - ranjith.subbaiya@tigeranalytics.com

## Release

| # | Release Version | Description | Key Features | Released on | Team Details |
|---|---|---|---|---|---|
| 1 | RL_V1 | Initial release. | - Scrapes Medium Blog Website.<br>- Load the data in snowflake.<br>- Apply Cortex AI Function.<br>-Send as notification to Google Space | 2025-06-30 | Aslam & Ranjith |

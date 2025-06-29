import pandas as pd
import logging
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, to_timestamp_tz, dateadd
from config.settings import CORTEX_PARAMS

def create_table(session: Session):
    """Create table if it doesn't exist."""
    session.sql("""
        CREATE TABLE IF NOT EXISTS MEDIUM_BLOG_DATA (
            TITLE STRING,
            CONTENT STRING,
            URL STRING,
            IMAGE_URL STRING,
            LOAD_TIME STRING,
            SUMMARY STRING,
            COMPLETE_SUMMARY STRING,
            SUMMARY_TOKENS NUMBER,
            SUMMARY_CREDITS NUMBER(38,13),
            COMPLETE_TOKENS NUMBER,
            COMPLETE_CREDITS NUMBER(38,13)
        );
    """).collect()
    logging.info("[create_table] Table check/creation complete.")

def fetch_existing_titles(session: Session) -> set:
    """Returns titles already stored in Snowflake to avoid duplicates."""
    try:
        df = session.sql("SELECT TITLE FROM MEDIUM_BLOG_DATA").to_pandas()
        return set(df["TITLE"])
    except Exception as e:
        logging.warning(f"[fetch_existing_titles] Warning: {e}")
        return set()

def load_dataframe_to_snowflake(df: pd.DataFrame, session: Session):
    """Loads new blog data into Snowflake."""
    session.write_pandas(df, "MEDIUM_BLOG_DATA")
    logging.info(f"[load_dataframe_to_snowflake] Inserted {len(df)} new rows.")

def enrich_data_with_cortex(session: Session):
    """Use Snowflake Cortex to enrich blog content with summaries."""
    try:
        prompt = CORTEX_PARAMS["prompt"].replace("'", "''")
        model = CORTEX_PARAMS["model"]
        sc = CORTEX_PARAMS["summarize_credit"]
        cc = CORTEX_PARAMS["complete_credit"]

        session.sql(f"""
            UPDATE MEDIUM_BLOG_DATA SET
                COMPLETE_SUMMARY = TRIM(SNOWFLAKE.CORTEX.COMPLETE('{model}', '{prompt}' || CONTENT)),
                SUMMARY = SNOWFLAKE.CORTEX.SUMMARIZE(CONTENT),
                SUMMARY_TOKENS = SNOWFLAKE.CORTEX.COUNT_TOKENS('summarize', CONTENT),
                SUMMARY_CREDITS = {sc:.10f} * SNOWFLAKE.CORTEX.COUNT_TOKENS('summarize', CONTENT),
                COMPLETE_TOKENS = SNOWFLAKE.CORTEX.COUNT_TOKENS('{model}', '{prompt}' || CONTENT),
                COMPLETE_CREDITS = {cc:.10f} * SNOWFLAKE.CORTEX.COUNT_TOKENS('{model}', '{prompt}' || CONTENT)
            WHERE SUMMARY IS NULL AND CONTENT != 'Error';
        """).collect()
        logging.info("[enrich_data_with_cortex] Enrichment completed.")

    except Exception as e:
        logging.error(f"[enrich_data_with_cortex] Cortex enrichment failed: {e}")

def get_last_day_blogs(session: Session) -> pd.DataFrame:
    """Retrieves blogs added in the last 24 hours that have summaries."""
    try:
        start_time = session.sql("SELECT dateadd('hour', -24, current_timestamp())").collect()[0][0]
        df = (
            session.table("MEDIUM_BLOG_DATA")
            .filter(to_timestamp_tz(col("LOAD_TIME")) >= start_time)
            .filter(col("SUMMARY").is_not_null())
            .sort(col("LOAD_TIME").desc())
            .to_pandas()
        )
        logging.info(f"[get_last_day_blogs] Fetched {len(df)} recent blogs.")
        return df
    except Exception as e:
        logging.error(f"[get_last_day_blogs] Failed to fetch recent blogs: {e}")
        return pd.DataFrame()
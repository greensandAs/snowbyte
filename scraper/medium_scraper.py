import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.settings import FALLBACK_IMAGE_URL
from utils.helpers import normalize_text

def fetch_urls(base_url: str, limit: int = 20) -> list:
    """
    Fetches a list of Medium blog URLs under a specific base path.
    
    Args:
        base_url (str): Medium collection homepage (e.g., https://medium.com/snowflake)
        limit (int): Maximum number of blog links to return

    Returns:
        List[str]: Full blog URLs
    """
    try:
        session = requests.Session()
        response = session.get(base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = {
            urljoin(base_url, a['href'])
            for a in soup.find_all('a', href=True)
            if a['href'].startswith('/snowflake') and '/followers' not in a['href']
        }

        return list(links)[:limit]

    except Exception as e:
        logging.error(f"[fetch_urls] Failed to extract blog URLs: {e}")
        return []

def fetch_title_content(url: str, session: requests.Session) -> tuple:
    """
    Scrapes title, content and image URL from a Medium blog article.
    
    Args:
        url (str): Full URL to a Medium blog post
        session (requests.Session): Pre-existing requests session

    Returns:
        Tuple[str, str, str, str]: (TITLE, CONTENT, URL, IMAGE_URL)
    """
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find('h1')
        article_tag = soup.find('article')

        # Try to fetch OG image or fallback to constant
        og_image_tag = soup.find('meta', property='og:image')
        image_url = og_image_tag['content'] if og_image_tag and og_image_tag.get('content') else FALLBACK_IMAGE_URL

        title = normalize_text(title_tag.text.strip().upper()) if title_tag else "N/A"
        content = normalize_text(article_tag.get_text(strip=True)) if article_tag else "N/A"

        return title, content, url, image_url

    except Exception as e:
        logging.error(f"[fetch_title_content] Failed to scrape article from {url}: {e}")
        return "N/A", "Error", url, FALLBACK_IMAGE_URL
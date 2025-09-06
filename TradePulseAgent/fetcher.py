import requests
import logging
from bs4 import BeautifulSoup
from config import AV_API_KEY

def fetch_financial_news_urls():
    """
    Fetches a list of financial news articles (including URLs) from the Alpha Vantage API.
    """
    logging.info("Fetching financial news URLs from Alpha Vantage...")
    if AV_API_KEY == "YOUR_API_KEY":
        logging.error("Alpha Vantage API key is not set. Please configure it in config.py or as an environment variable.")
        return []

    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={AV_API_KEY}&sort=LATEST'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "feed" in data:
            logging.info(f"Successfully fetched {len(data['feed'])} news items.")
            return data['feed']
        else:
            logging.warning(f"Could not fetch news URLs. Response: {data}")
            return []

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news URLs from Alpha Vantage: {e}")
        return []

def get_article_text(url):
    """
    Fetches and extracts the main text content from a given URL.
    """
    logging.info(f"Fetching article content from: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all paragraph tags and join their text.
        # This is a simple approach and might need refinement for specific sites.
        paragraphs = soup.find_all('p')
        article_text = ' '.join([p.get_text() for p in paragraphs])
        
        if not article_text:
            logging.warning("Could not extract any paragraph text from the article.")
            return None
            
        logging.info(f"Successfully extracted text from article.")
        return article_text

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching article content from {url}: {e}")
        return None
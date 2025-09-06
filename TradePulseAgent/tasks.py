import logging
import time
from fetcher import fetch_financial_news_urls, get_article_text
from summarizer import summarize_text
from processor import format_post
from publisher import publish_post

# Limit the number of articles to process in each run
MAX_ARTICLES_PER_RUN = 3

def run_agent_task():
    """
    The main LLM-powered task for the agent.
    """
    logging.info("--- Running LLM Agent Task ---")
    
    news_items = fetch_financial_news_urls()
    
    if not news_items:
        logging.info("No news items fetched. Ending task.")
        return

    articles_processed = 0
    for item in news_items:
        if articles_processed >= MAX_ARTICLES_PER_RUN:
            logging.info(f"Reached max articles for this run ({MAX_ARTICLES_PER_RUN}).")
            break

        url = item.get('url')
        if not url:
            logging.warning("News item has no URL. Skipping.")
            continue

        article_text = get_article_text(url)
        if not article_text:
            continue

        summary = summarize_text(article_text)
        if not summary:
            continue

        post = format_post(summary)
        if not post:
            continue

        publish_post(post)
        articles_processed += 1

        # Add a delay between posts to avoid rate limiting
        if articles_processed < MAX_ARTICLES_PER_RUN:
            time.sleep(10)
            
    logging.info("--- Agent Task Finished ---")
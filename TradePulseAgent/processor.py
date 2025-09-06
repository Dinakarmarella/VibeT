import logging

def format_post(summary):
    """
    Formats a summarized text into a social media post with hashtags.
    """
    if not summary:
        return None
    
    post = f"{summary} #TradingNews #FinancialNews"
    logging.info("Formatted summary into a post.")
    return post
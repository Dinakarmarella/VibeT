import cohere
import logging
from config import COHERE_API_KEY

co = None

def initialize_cohere():
    """Initializes the Cohere client.
    Returns:
        bool: True if initialization is successful, False otherwise.
    """
    global co
    if COHERE_API_KEY.startswith("YOUR_COHERE"):
        logging.error("Cohere API key not set. Please configure it in config.py or as an environment variable.")
        return False
    try:
        co = cohere.Client(COHERE_API_KEY)
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Cohere client: {e}")
        return False

def summarize_text(text):
    """Summarizes the given text using the Cohere API.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summarized text, or None if an error occurs.
    """
    if co is None:
        if not initialize_cohere():
            return None

    try:
        response = co.summarize(
            text=text,
            length='short',
            format='paragraph',
            model='command',
            additional_command='to be suitable for a tweet',
        )
        summary = response.summary
        logging.info(f"Successfully summarized text.")
        return summary
    except Exception as e:
        logging.error(f"Error during Cohere summarization: {e}")
        return None

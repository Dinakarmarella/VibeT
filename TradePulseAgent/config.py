import os

# --- API and Credentials Configuration ---

# Alpha Vantage API Key
# Get a free API key from: https://www.alphavantage.co/support/#api-key
AV_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "YOUR_API_KEY")

# Cohere API Key
# Get a free API key from: https://cohere.com/
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "YOUR_COHERE_API_KEY")

# Twitter API Credentials
# Get these from your Twitter Developer App: https://developer.twitter.com/
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "YOUR_TWITTER_API_KEY")
TWITTER_API_SECRET_KEY = os.environ.get("TWITTER_API_SECRET_KEY", "YOUR_TWITTER_API_SECRET_KEY")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "YOUR_TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "YOUR_TWITTER_ACCESS_TOKEN_SECRET")

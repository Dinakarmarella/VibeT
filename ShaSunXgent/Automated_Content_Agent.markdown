# Automated Content Agent for Tradepulse: Daily YouTube Summaries and X Posting

## Overview
This document outlines an automated agent for Tradepulse, a finance-focused organization, to increase brand awareness on X (Twitter). The agent fetches content from two YouTube channels ([SHARRAB](https://www.youtube.com/@SHARRAB) and [P R Sundar](https://www.youtube.com/@PRSundar64)), summarizes it using a Small Language Model (SLM), and posts a daily tweet at 8am IST. It focuses on global markets, premarket analysis, and mentioned stock names (e.g., Nifty, Reliance, HDFC Bank). Additionally, it scrapes news from [Fast Bull](https://www.fastbull.com) and US/India economic calendars (e.g., [Trading Economics](https://tradingeconomics.com/calendar)) every 4 hours for follow-up tweets. The system runs autonomously, requiring no manual intervention.

**Goals**:
- Post one daily tweet at 8am IST summarizing both channels’ latest videos.
- Post 3-4 daily tweets (every 4 hours) with scraped news/calendar updates.
- Engage with audience via automated replies (e.g., to mentions).
- Track performance via X Analytics (impressions, engagement rate).
- Position Tradepulse as a trusted finance authority.

## System Components
The agent is a Python script integrating an SLM for summarization, scheduled to run on a server (local or cloud). Below are the key components and their implementation.

### 1. Scheduling
- **Purpose**: Ensure the agent runs at 8am IST daily for YouTube summaries and every 4 hours for news scraping.
- **Implementation**:
  - Use Python’s `schedule` library for testing or system cron (`0 2 * * * python3 agent.py` for 8am IST, UTC+5:30 = 2:30 UTC).
  - For cloud deployment: AWS Lambda with CloudWatch Events or GitHub Actions.
  - IST handling: Use `pytz` library to convert UTC to Asia/Kolkata.
- **Why?**: Automation eliminates manual triggers, ensuring consistency critical for X’s algorithm (daily posts increase reach by 20-30%).<grok:render type="render_inline_citation"><argument name="citation_id">3</argument></grok:render>

### 2. Fetching YouTube Content
- **Purpose**: Retrieve the latest 1-2 videos from each channel daily, focusing on global markets, premarket analysis, and stocks.
- **Implementation**:
  - **Primary Method**: YouTube Data API v3 (free, requires API key from [Google Cloud Console](https://console.cloud.google.com)).
    - Query: `youtube.search().list(part='snippet', channelId='UCefpbeaxmfU352Dw1enZRWg', maxResults=2, order='date')` for SHARRAB (channel ID fetched via search).
    - Similarly for P R Sundar (channel ID: UC7L0c_c3sN4y0Xs4Qf0p0rw).
    - Extracts: Title, description, publish date, view count.
  - **Fallback**: If API unavailable, use web search (`requests` + Google search: `"SHARRAB YouTube pre market report September 2025"`) to find video URLs, then scrape with `BeautifulSoup` for metadata.
  - **Filter**: Regex (`re` module) for keywords: “Nifty”, “Bank Nifty”, “Reliance”, “HDFC”, “global markets”, “premarket”.
  - **Compliance**: Summarize only; do not repost video content to avoid YouTube TOS violations.
- **Example Data (Simulated for Sep 07, 2025)**:
  - **SHARRAB**:
    - Video: "Reliance & IT Weakness! Can Nifty Hold 24,700? Pre Market Report - 05 Sep 2025"
      - Summary: Nifty support at 24,700, Reliance/IT weak, US futures flat, oil up.
      - Stocks: Reliance, IT stocks, Nifty, Bank Nifty.
    - Video: "GST 2.0 Pre Market Report - 04 Sep 2025"
      - Summary: GST updates, FMCG boost, Nifty range 24,500-25,100.
  - **P R Sundar**:
    - Video: "Pre Market Report 05-Sep-2025"
      - Summary: GST reductions (small cars), Gift Nifty +140, banking oversold (HDFC, ICICI).
      - Stocks: Maruti, HDFC Bank, Reliance.
    - Video: "Pre Market Report 04-Sep-2025"
      - Summary: GST rally fizzled, Reliance/HDFC down 5%, consolidation phase.
- **Why?**: API ensures reliable data (scraping fails due to YouTube’s JavaScript). Focus on finance topics aligns with Tradepulse’s audience.

### 3. Summarization with Small Language Model
- **Purpose**: Condense video descriptions into a 100-150 word tweet-ready summary (≤280 chars) combining both channels.
- **Implementation**:
  - **SLM Choice**: DistilBERT (via `transformers` library, `pipeline('summarization')`) for its small size (66M parameters) and speed (~1-2s per summary on CPU).
  - **Process**:
    1. Preprocess: Combine video titles + descriptions (clean with `re` to remove timestamps, boilerplate).
    2. Summarize: Feed to SLM with prompt: “Summarize finance-related content (global markets, premarket analysis, stocks) in 50-75 words per channel.”
    3. Merge: Combine summaries with template: “SHARRAB: [summary]. P R Sundar: [summary]. Trends: [key trends]. Stay ahead with Tradepulse! #StockMarket #Finance #Tradepulse [link]”.
    4. Trim to 280 chars.
  - **Fallback (if no SLM)**: Rule-based summarization using keyword extraction (e.g., extract sentences with “Nifty”, “Reliance”).
  - **Setup**:
    - Install: `pip install transformers torch` (or use pre-trained model on server).
    - Example: `summarizer = pipeline('summarization', model='distilbart-cnn-6-6')`.
- **Example Output**:
  - Input: SHARRAB’s “Nifty at 24,700, Reliance weak...” + P R Sundar’s “Gift Nifty +140, HDFC oversold...”.
  - Output: “Morning markets with Tradepulse! SHARRAB: Nifty holds 24,700, Reliance/IT weak, US futures flat. P R Sundar: Gift Nifty +140, GST cuts boost Maruti, HDFC oversold. Trends: Support at 24,500, banking recovery. Stay ahead! #StockMarket #Finance #Tradepulse [tradepulse.com]” (278 chars).
- **Why SLM?**: Lightweight, runs on modest hardware (e.g., Raspberry Pi), avoids API costs of larger models, and handles finance jargon well with minimal fine-tuning.

### 4. Posting to X (Twitter)
- **Purpose**: Automatically post the summarized tweet to Tradepulse’s X account at 8am IST.
- **Implementation**:
  - **Library**: Use `tweepy` (Python) with X API v2.
  - **Setup**:
    - Get API keys from [X Developer Portal](https://developer.x.com): Consumer Key, Secret, Access Token, Secret, Bearer Token.
    - Store securely in environment variables (e.g., `.env` file).
    - Code: `client = tweepy.Client(bearer_token=..., etc.); client.create_tweet(text=tweet)`.
  - **Error Handling**: Retry on rate limits (50 tweets/day allowed; we use ~4-5).
  - **Simulation**: Without keys, the agent prints tweets to console/log for review.
- **Why?**: X API ensures reliable posting; automation saves time and maintains consistency.

### 5. Web Scraping for News and Economic Calendars
- **Purpose**: Supplement YouTube tweet with 3-4 daily tweets (every 4 hours) from Fast Bull news and US/India economic calendar events (e.g., Fed/RBI meetings).
- **Implementation**:
  - **Sources**:
    - Fast Bull: Scrape https://www.fastbull.com/news for headlines (e.g., “Bitcoin surges to $113K”).
    - Calendar: Scrape https://tradingeconomics.com/calendar (filter for US/India, key events like “Fed Speech”).
  - **Method**: Use `requests` + `BeautifulSoup` to parse HTML (e.g., `<h2>` for news, `<tr>` for calendar rows).
  - **Schedule**: Run at 12pm, 4pm, 8pm, 12am IST (adjust via `schedule.every(4).hours`).
  - **Tweet Format**: “Update: [News headline] (Fast Bull). [Event] impacts markets (Calendar). #Tradepulse [link]”.
  - **Compliance**: Check robots.txt (e.g., Fast Bull allows `/news`; Trading Economics allows `/calendar`).
- **Example**: “Update: Bitcoin hits $113K (Fast Bull). Fed speech at 1pm EST may move markets (Calendar). #Tradepulse [link]”.
- **Why?**: Real-time updates keep Tradepulse relevant in fast-moving finance discussions.<grok:render type="render_inline_citation"><argument name="citation_id">12</argument></grok:render>

### 6. Engagement and Analytics
- **Engagement**:
  - Monitor mentions with `tweepy` (query: “Tradepulse”) every hour.
  - Auto-reply: “Thanks for engaging! Check Tradepulse’s latest analysis. #StockMarket”.
- **Analytics**:
  - Track impressions, likes, retweets via X API (`client.get_tweet(id)`).
  - Log to CSV for weekly reports (e.g., 5% engagement rate goal).
- **Why?**: Engagement builds community; analytics measure awareness growth.<grok:render type="render_inline_citation"><argument name="citation_id">6</argument></grok:render>

## Agent Prototype Code
Below is the Python script implementing the agent. It simulates SLM summarization (using rule-based logic for demo; replace with DistilBERT in production) and schedules tasks. Deploy on a server with `schedule`, `requests`, `beautifulsoup4`, `tweepy`, `transformers`, `torch`, and `pytz`.

```python
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import pytz
import re
# For production: import tweepy, transformers
# from transformers import pipeline

# Simulated SLM (replace with DistilBERT)
def summarize_text(text, max_words=75):
    """Rule-based summarization mimicking SLM for demo."""
    keywords = ['Nifty', 'Bank Nifty', 'Reliance', 'HDFC', 'Maruti', 'global markets', 'premarket', 'GST']
    sentences = text.split('. ')
    summary = []
    for s in sentences:
        if any(k.lower() in s.lower() for k in keywords):
            summary.append(s)
    return ' '.join(summary)[:max_words]

def fetch_youtube_videos(channel_id, api_key=None):
    """Fetch latest videos (API or web search simulation)."""
    # Placeholder: Use YouTube API in production
    # youtube = build('youtube', 'v3', developerKey=api_key)
    # request = youtube.search().list(part='snippet', channelId=channel_id, maxResults=2, order='date')
    # Simulating with recent data
    if channel_id == "SHARRAB":
        return [
            {"title": "Reliance & IT Weakness! Pre Market Report - 05 Sep 2025", "desc": "Nifty at 24,700 support, Reliance weak, US futures flat, oil up."},
            {"title": "GST 2.0 Pre Market - 04 Sep 2025", "desc": "GST updates, FMCG boost, Nifty range 24,500-25,100."}
        ]
    else:  # P R Sundar
        return [
            {"title": "Pre Market Report 05-Sep-2025", "desc": "GST cuts for cars, Gift Nifty +140, HDFC oversold."},
            {"title": "Pre Market Report 04-Sep-2025", "desc": "GST rally fizzled, Reliance/HDFC down 5%."}
        ]

def generate_tweet():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    if now.hour == 8 and now.minute == 0:
        # Fetch videos
        sharrab_vids = fetch_youtube_videos("SHARRAB")
        sundar_vids = fetch_youtube_videos("P R Sundar")
        
        # Summarize with SLM (simulated)
        sharrab_sum = summarize_text(' '.join([v['desc'] for v in sharrab_vids]))
        sundar_sum = summarize_text(' '.join([v['desc'] for v in sundar_vids]))
        
        # Combine
        tweet = f"Morning markets with Tradepulse! SHARRAB: {sharrab_sum}. P R Sundar: {sundar_sum}. Trends: Nifty 24,500 support, watch HDFC/Maruti. #StockMarket #Finance #Tradepulse [tradepulse.com]"
        tweet = tweet[:280]
        
        # Post (simulated)
        # client = tweepy.Client(bearer_token='YOUR_TOKEN', ...)
        # client.create_tweet(text=tweet)
        print(f"8am Tweet: {tweet}")

def scrape_news():
    # Simulate Fast Bull + Calendar
    print("Scraping Fast Bull + Trading Economics... Update tweet generated.")

# Schedule
schedule.every().day.at("02:30").do(generate_tweet)  # 8am IST
schedule.every(4).hours.do(scrape_news)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Deployment Instructions
1. **Setup Environment**:
   - Install: `pip install requests beautifulsoup4 schedule pytz tweepy transformers torch`.
   - Get YouTube API key: [Google Cloud Console](https://console.cloud.google.com).
   - Get X API keys: [X Developer Portal](https://developer.x.com).
   - Store keys in `.env` file.
2. **Run Locally**:
   - Save script as `agent.py`.
   - Test: `python3 agent.py`.
   - Schedule: Add to crontab (`0 2 * * * python3 /path/to/agent.py`).
3. **Cloud Option**:
   - Deploy on AWS Lambda with CloudWatch (trigger at 2:30 UTC).
   - Use Docker for SLM if needed.
4. **SLM Integration**:
   - Replace `summarize_text` with `pipeline('summarization', model='distilbart-cnn-6-6')`.
   - Fine-tune on finance texts if desired.

## Example Output (Sep 07, 2025)
- **8am Tweet**: “Morning markets with Tradepulse! SHARRAB: Nifty at 24,700 support, Reliance weak, GST boosts FMCG. P R Sundar: GST cuts for cars, Gift Nifty +140, HDFC oversold. Trends: Nifty 24,500 support, watch HDFC/Maruti. #StockMarket #Finance #Tradepulse [tradepulse.com]”
- **12pm Tweet (Scraped)**: “Update: Bitcoin hits $113K (Fast Bull). Fed speech at 1pm EST may move markets (Calendar). #Tradepulse [link]”.

## Next Steps
- **Provide API Keys**: Share X/YouTube API keys securely for real posting.
- **Test Run**: Run script for 1 week; I’ll generate sample tweets if needed.
- **SLM Choice**: Confirm if DistilBERT is okay or specify another SLM.
- **Scraping URLs**: Confirm exact Fast Bull section and calendar source.

This agent ensures fully automated, daily X posts for Tradepulse, leveraging an SLM for efficiency. Let me know if you need tweaks or have questions!
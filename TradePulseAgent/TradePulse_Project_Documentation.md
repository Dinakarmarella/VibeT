# TradePulse Agent: Project Documentation

## 1. Project Overview

`TradePulseAgent` is an automated social media bot that uses a Small Language Model (SLM) to create intelligent, summarized news posts for Twitter. The agent fetches full news articles from various financial news sources, summarizes them into concise and engaging tweets, and publishes them automatically. It runs continuously, providing timely and unique news updates every three hours.

## 2. How It Works (LLM-Powered Workflow)

The agent follows an intelligent, multi-step workflow:

1.  **Scheduling**: The main `agent.py` script uses a scheduler to trigger the main task every 3 hours.
2.  **URL Fetching**: The `fetcher` module calls the **Alpha Vantage API** to get a list of the latest financial news articles, including their URLs.
3.  **Content Extraction**: For each URL, the `fetcher` uses the **BeautifulSoup** library to parse the article's HTML and extract the clean, full text of the article.
4.  **Summarization**: The extracted text is sent to the **Cohere API**, where a powerful language model summarizes the article into a short, tweet-length paragraph.
5.  **Processing & Publishing**: The `processor` module adds relevant hashtags to the summary, and the `publisher` module connects to the **Twitter API** to post the final content to your configured account.
6.  **Logging**: Throughout this process, the agent logs its actions, successes, and any potential errors to the `agent.log` file for easy monitoring and debugging.

## 3. Project Structure

The project is organized into several modules, each with a distinct responsibility:

*   `agent.py`: The main entry point of the application. It initializes the logger and schedules the main task.
*   `config.py`: Centralizes all API keys and credentials. **This is the primary file you will need to edit to add your credentials**.
*   `fetcher.py`: Contains the logic for fetching news URLs from Alpha Vantage and extracting the full article text with BeautifulSoup.
*   `summarizer.py`: A new module responsible for interacting with the Cohere API to summarize the article text.
*   `processor.py`: Handles the final formatting of the summarized text into a tweet.
*   `publisher.py`: Manages the publishing of posts to Twitter.
*   `tasks.py`: Contains the `run_agent_task` function, which orchestrates the entire fetch -> extract -> summarize -> publish workflow.
*   `requirements.txt`: A list of all the Python libraries required to run the agent.
*   `agent.log`: The log file where the agent records its activity.

## 4. Setup and Configuration

To get the agent running, follow these steps:

### Step 1: Install Dependencies

Make sure you have Python installed. Then, open a terminal in the project directory and install the required libraries using pip:

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Credentials

The agent requires API credentials for three services: Alpha Vantage (for news URLs), Cohere (for summarization), and Twitter (for posting). For security, it is **strongly recommended** to set these as environment variables.

**Required Environment Variables:**

```
# For Alpha Vantage (get from alphavantage.co)
ALPHAVANTAGE_API_KEY="YOUR_API_KEY"

# For Cohere (get from cohere.com)
COHERE_API_KEY="YOUR_COHERE_API_KEY"

# For Twitter (get from developer.twitter.com)
TWITTER_API_KEY="YOUR_TWITTER_API_KEY"
TWITTER_API_SECRET_KEY="YOUR_TWITTER_API_SECRET_KEY"
TWITTER_ACCESS_TOKEN="YOUR_TWITTER_ACCESS_TOKEN"
TWITTER_ACCESS_TOKEN_SECRET="YOUR_TWITTER_ACCESS_TOKEN_SECRET"
```

**Alternative (Less Secure):**

If you prefer not to use environment variables, you can directly edit the `config.py` file and replace the placeholder values with your actual credentials.

## 5. Running the Agent

Once you have configured your credentials, you can start the agent by running the following command in your terminal:

```bash
python agent.py
```

The agent will start, run the task once immediately, and then continue to run in the background, posting news updates every 3 hours.

## 6. Monitoring the Agent

You can monitor the agent's activity by checking the `agent.log` file. This file will show you when the agent runs, what news it has fetched, whether the posts were successful, and any errors that may have occurred.

## 7. Implementation History

This project has evolved through several key stages:

*   **Initial State**: The project began with a detailed specification but a non-functional script that was blocked from its data source due to a web scraping error (`403 Forbidden`).
*   **API Integration**: The first major step was to replace the unreliable web scraper with a stable API call to **Alpha Vantage** to fetch news headlines.
*   **Publisher Implementation**: The agent was then enhanced to publish content to **Twitter** and **LinkedIn**.
*   **Modular Refactoring**: To improve maintainability, the code was refactored from a single script into a modular structure with clear separation of concerns (fetching, processing, publishing, etc.).
*   **LinkedIn Removal**: As per user request, the LinkedIn functionality was removed to focus the agent solely on Twitter.
*   **LLM Integration**: The most significant upgrade was the integration of a Small Language Model (SLM). The agent now fetches full article content, uses the **Cohere API** to generate intelligent summaries, and posts these unique summaries to Twitter. This represents the current, most advanced version of the agent.

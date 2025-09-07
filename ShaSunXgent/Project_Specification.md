# Project Specification: Automated Content Agent

## 1. Overview

This document provides a complete technical specification for the Automated Content Agent, a modular and configurable system designed to automate the content lifecycle: fetching from various sources, processing it using AI, and publishing it to social media platforms.

### 1.1. Goals

- **Automate Content Pipeline:** Eliminate manual effort in content creation and publication.
- **Increase Brand Awareness:** Maintain a consistent and relevant social media presence.
- **Provide Timely Information:** Deliver summaries of financial news and analysis promptly.
- **Establish Authority:** Position the brand as a reliable source of financial information.

### 1.2. Core Functionality

The agent performs a complete, end-to-end workflow:
1.  **Fetches** new video content from specified YouTube channels.
2.  **Processes** the video descriptions using a Small Language Model (SLM) to generate summaries.
3.  **Publishes** the formatted summaries to a configured X (Twitter) account.
4.  **Maintains State** by recording all actions in a local database to prevent duplicate content publication.

---

## 2. System Architecture

The architecture is designed to be modular, decoupled, and configurable, ensuring the system is maintainable and extensible.

### 2.1. Architectural Principles

- **Modular (Separation of Concerns):** The system is divided into distinct components, each with a single responsibility.
- **Decoupled:** Modules are independent and communicate through well-defined interfaces.
- **Stateful:** The system uses a local database to track its progress and prevent duplicate work.
- **Configurable:** Logic is separated from configuration, allowing for easy adaptation.

### 2.2. Architecture Diagram

```
+-----------+      +--------------+      +-----------+      +-----------+      +-----------+
| Scheduler | ---> | Orchestrator | ---> |  Fetcher  | ---> | Processor | ---> | Publisher |
+-----------+      +--------------+      +-----------+      +-----------+      +-----------+
     |                    |                     |                  |                  |
     |                    +---------------------+------------------+------------------+
     |                                          |
     |                                          v
     |                                  +----------------+
     +--------------------------------> |  State Manager |
                                        +----------------+
                                             (Database)
```

### 2.3. Component Breakdown

- **Orchestrator (`orchestrator.py`):** The central "Manager." It directs the overall workflow, calling other modules in sequence and managing high-level error handling.
- **Fetcher (`fetcher.py`):** The "Researcher." It retrieves raw data from external sources (currently YouTube) using the appropriate APIs.
- **Processor (`processor.py`):** The "Writer." It uses a Hugging Face `transformers` model to clean and summarize raw text.
- **Publisher (`publisher.py`):** The "Publicist." It formats the final content and posts it to social media platforms (currently X) using the `tweepy` library.
- **State Manager (`state_manager.py`):** The system's "Memory." It uses an SQLite database to log all processed items and their status, preventing redundant work.

---

## 3. Workflow

The primary task (`daily_youtube_summary`) follows this sequence:

1.  **Trigger:** A system scheduler (e.g., `cron`) executes `main.py`.
2.  **Initialization:** The `Orchestrator` is initialized, loading all configurations and modules.
3.  **Fetch:** The `Orchestrator` calls the `Fetcher`. The `Fetcher` queries the YouTube API for recent videos and consults the `State Manager` to filter out any videos that have already been processed.
4.  **Process:** For each new video, the `Orchestrator` passes its description to the `Processor`, which returns a generated summary.
5.  **Publish:** The `Orchestrator` passes the summary to the `Publisher`. The `Publisher` formats the text into a tweet and posts it to X.
6.  **Update State:** Upon successful publication, the `Orchestrator` instructs the `State Manager` to mark the video ID as `published` in the database.

---

## 4. Configuration (`config.yaml`)

All agent behavior is controlled via the `config.yaml` file. A template (`config.yaml.template`) is provided.

- **`api_keys`**: Holds all necessary credentials for YouTube and X APIs.
- **`sources`**: Defines the data sources, such as YouTube channel IDs and news website URLs.
- **`processor`**: Configures the SLM, including the Hugging Face model name and summarization parameters.
- **`publisher`**: Contains settings for publication, such as the tweet format template.
- **`system`**: Specifies system-level settings, like the path to the state database.

---

## 5. Implementation Details

- **Language:** Python 3
- **Key Libraries:**
    - **Fetcher:** `google-api-python-client` for YouTube API access.
    - **Processor:** `transformers` and `torch` for loading and running the SLM.
    - **Publisher:** `tweepy` for interacting with the X API.
    - **State Manager:** `sqlite3` for database interaction.
    - **Configuration:** `PyYAML` for loading the `config.yaml` file.

---

## 6. Setup and Usage

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure:** Copy `config.yaml.template` to `config.yaml` and populate it with your API keys and desired settings.
3.  **Run:**
    ```bash
    python main.py
    ```
4.  **Schedule:** For autonomous operation, set up a system scheduler (like `cron` on Linux or Task Scheduler on Windows) to run the `python main.py` command at your desired interval.

---

## 7. Future Enhancements

The modular architecture allows for straightforward expansion:

- **Web Scraping:** Implement the news scraping logic in the `Fetcher`.
- **Advanced Processing:** Enhance the `Processor` to perform more sophisticated trend analysis.
- **Multi-Platform Publishing:** Extend the `Publisher` to support additional social media platforms.
- **Engagement Module:** Create a new module to automatically reply to mentions and engage with users.

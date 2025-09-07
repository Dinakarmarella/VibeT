# Automated Content Agent - Architecture

This document outlines the system architecture for the Automated Content Agent, designed to fetch, process, and publish content to social media platforms.

## 1. Guiding Principles

The architecture is based on the following principles:

- **Modular (Separation of Concerns):** The system is divided into distinct components (modules), each with a single, well-defined responsibility. This makes the system easier to develop, test, and maintain.
- **Decoupled:** Modules are designed to be as independent as possible. They communicate through well-defined interfaces, reducing the impact of changes within one module on others.
- **Stateful:** The system maintains a persistent state to track its progress, prevent duplicate work, and allow for graceful recovery from failures.
- **Configurable:** Core logic is separated from configuration. Behavior (like data sources or scheduling) can be changed without modifying the code.

## 2. System Components (Modules)

The system is composed of a "team" of specialized modules that work together under the direction of an Orchestrator.

![Architecture Diagram](https://i.imgur.com/5gAqB4x.png)

### 2.1. Orchestrator (`orchestrator.py`)

- **Role:** The "Manager" or the brain of the operation.
- **Responsibilities:**
    - Initiates tasks based on a schedule (e.g., "start daily YouTube summary").
    - Coordinates the flow of data between the other modules (Fetcher -> Processor -> Publisher).
    - Manages error handling and retry logic at a high level.
    - Logs the overall status of tasks.

### 2.2. Fetcher (`fetcher.py`)

- **Role:** The "Researcher."
- **Responsibilities:**
    - Retrieves raw data from various external sources defined in the configuration file.
    - Handles the specific logic for each source (e.g., calling the YouTube API, scraping a news website).
    - Does not modify or process the data; its only job is to collect it.

### 2.3. Processor (`processor.py`)

- **Role:** The "Writer."
- **Responsibilities:**
    - Takes raw data from the Fetcher.
    - Cleans and preprocesses the text.
    - Utilizes a Small Language Model (SLM) to generate summaries or other content.
    - Formats the output into a polished, ready-to-publish piece of content.

### 2.4. Publisher (`publisher.py`)

- **Role:** The "Publicist."
- **Responsibilities:**
    - Takes the final content from the Processor.
    - Connects to external social media platforms (e.g., X, LinkedIn).
    - Handles the API-specific logic for posting content.
    - Reports the status of the publication (success or failure).

### 2.5. State Manager (`state_manager.py`)

- **Role:** The system's "Memory."
- **Responsibilities:**
    - Provides a simple interface for reading and writing to a persistent database (e.g., SQLite).
    - Tracks the status of each piece of content (e.g., `fetched`, `processed`, `published`, `failed`).
    - Allows other modules to check if an item has already been processed.

## 3. Data and Workflow

### 3.1. Workflow

1.  **Trigger:** An external scheduler (like a system `cron` job) runs `main.py` at a configured time.
2.  **Orchestration:** `main.py` invokes the **Orchestrator**.
3.  **Task Execution:** The Orchestrator begins a defined task (e.g., `daily_youtube_summary`).
4.  **Fetch:** The Orchestrator instructs the **Fetcher** to get new data. The Fetcher first consults the **State Manager** to identify new items.
5.  **Process:** For each new item, the Orchestrator passes it to the **Processor** to be summarized.
6.  **Publish:** The resulting summary is then sent to the **Publisher** to be posted.
7.  **State Update:** The Orchestrator instructs the **State Manager** to update the status of the item at each successful step (e.g., from `fetched` to `processed`, then to `published`).

### 3.2. Configuration (`config.yaml`)

All environment-specific details will be stored in a configuration file, including:
- API keys and secrets.
- YouTube channel IDs.
- News website URLs and scraping selectors.
- SLM model names and parameters.
- Tweet templates and hashtags.

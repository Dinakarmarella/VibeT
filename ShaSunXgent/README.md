# Automated Content Agent

This project is a modular and configurable agent designed to automate the entire content lifecycle: fetching from various sources, processing it using AI, and publishing it to social media platforms.

## Overview

The agent is built with a modular architecture, separating the core responsibilities of fetching, processing, and publishing into distinct components. This design allows for easy maintenance, testing, and extension.

For a detailed explanation of the system's design, please see [architecture.md](architecture.md).

## Features

- **Multi-Source Fetching:** Can retrieve content from YouTube channels, news websites, and more.
- **AI-Powered Summarization:** Uses a Small Language Model (SLM) to generate concise and relevant summaries.
- **Multi-Platform Publishing:** Can post content to various social media platforms (initially X).
- **Stateful Operation:** Remembers what content it has already processed to prevent duplicates and allow for failure recovery.
- **Highly Configurable:** All major settings, from API keys to data sources, are managed in an external configuration file, not in the code.

## Getting Started

### Prerequisites

- Python 3.8+
- Pip (Python package installer)

### Installation

1.  **Clone the repository (or download the source code).**

2.  **Create a configuration file:**
    ```bash
    cp config.yaml.template config.yaml
    ```

3.  **Fill in your credentials** and settings in `config.yaml`. This includes your API keys for YouTube and X, as well as the specific channels or sites you want to monitor.

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Agent

To run the agent manually for a single task, you can execute the main script:

```bash
python main.py
```

For automated, scheduled execution, you can set up a system `cron` job or use a cloud-based scheduler (like AWS Lambda) to run the `main.py` script at your desired intervals.

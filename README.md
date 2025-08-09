
# SLM Defect Automation

This project automates the triage of Sev1 defects from Jira using a small language model (SLM).

## Setup

1.  **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

2.  **Configure credentials:**

    Create a `.env` file in the `DJ_SLM` directory and add the following:

    ```
    JIRA_API_URL=https://your-jira-instance.atlassian.net/rest/api/3
    JIRA_USER_EMAIL=your-email@example.com
    JIRA_API_TOKEN=your-jira-api-token
    DYNATRACE_API_URL=https://your-dynatrace-environment.live.dynatrace.com/api/v2
    DYNATRACE_API_TOKEN=your-dynatrace-api-token
    ```

## Usage

To run the automation for a specific Jira issue, use the `orchestrator.py` script:

```
python orchestrator.py <JIRA_ISSUE_ID>
```

For example:

```
python orchestrator.py DEF-123
```

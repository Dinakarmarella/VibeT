

import os
import sys
import pandas as pd

# Add the src directory to the Python path to allow for module imports
sys.path.append(os.path.dirname(__file__))

from jira_api import fetch_closed_defects, post_comment
from predict import predict

def format_comment(prediction_results, historical_examples):
    """Formats the prediction and examples into a Jira comment."""
    top_prediction = prediction_results[0]
    predicted_label, predicted_score = top_prediction

    comment = f"""
h2. AI Root Cause Analysis

*Prediction:* The model predicts the root cause is *{predicted_label}* with a confidence of {predicted_score:.2%}.

h2. Context from Similar Historical Defects
"""
    if not historical_examples.empty:
        comment += "Here are some past defects with the same predicted root cause:\n"
        for index, row in historical_examples.iterrows():
            comment += f"* *{row['Defect_ID']}*: {row['Summary']}\n"
    else:
        comment += f"No historical examples found for the root cause: '{predicted_label}'\n"

    return comment

def run_and_update_jira():
    """
    Fetches issues from Jira, predicts their root cause, and posts the analysis as a comment.
    """
    print("Loading historical data for context...")
    project_root = os.path.dirname(os.path.dirname(__file__))
    raw_data_path = os.path.join(project_root, 'data', 'raw_data.csv')
    try:
        context_df = pd.read_csv(raw_data_path)
        print("Historical data loaded successfully.")
    except FileNotFoundError:
        print("Error: raw_data.csv not found. Cannot provide historical context.")
        return

    # JQL to fetch issues. Modify this to target the desired issues.
    # WARNING: This will post comments to the issues found. Start with a narrow JQL.
    # For example: 'project = \"YOUR_PROJECT\" AND status = \"New\" AND resolution = Unresolved'
    jql = "status=Closed" # Using "Closed" as a safe default for demonstration
    print(f"Fetching Jira issues with JQL: '{jql}'...")

    try:
        issues = fetch_closed_defects(jql=jql).get('issues', [])
        if not issues:
            print("No issues found for the given JQL query.")
            return
        
        print(f"Found {len(issues)} issues. Processing...")

        for issue in issues:
            issue_key = issue['key']
            print(f"\n--- Processing Issue: {issue_key} ---")

            # The predict function expects a dict with 'Summary' and 'Comments'
            # We need to map the Jira issue fields to this format.
            # We'll use the 'summary' and 'description' fields.
            issue_details = {
                "Summary": issue.get('fields', {}).get('summary', ''),
                "Comments": str(issue.get('fields', {}).get('description', '')) # Using description as a stand-in for comments
            }

            # 1. Get prediction
            predictions = predict(issue_details)
            top_label = predictions[0][0]
            
            # 2. Get context
            examples = context_df[context_df['Root_Cause'] == top_label].head(3)

            # 3. Format comment
            comment_body = format_comment(predictions, examples)
            print(f"Prediction for {issue_key}: '{top_label}'.")

            # 4. Post comment to Jira
            # UNCOMMENT THE LINE BELOW TO ACTUALLY POST TO JIRA
            # post_comment(issue_key, comment_body)
            print(f"Generated comment for {issue_key}. (Posting is currently disabled).")
            # For demonstration, we just print the comment
            print("--- Comment Body ---")
            print(comment_body)
            print("--------------------")


    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your Jira domain, email, and API token in 'config.yaml' are correct.")


if __name__ == "__main__":
    run_and_update_jira()

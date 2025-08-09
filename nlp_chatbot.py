import re
import os
import sys

# Add the directory containing slm_automation.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from slm_automation import extract_transaction_id, query_dynatrace_logs, assign_team_by_keyword, load_data

# Load data once at the beginning
historical_kb, keyword_team_map = load_data()

def nlp_chatbot_query(user_query):
    print(f"Chatbot received query: {user_query}")
    extracted_id = extract_transaction_id(user_query)

    if extracted_id:
        print(f"  Extracted ID: {extracted_id}")
        # Simulate Dynatrace query
        dynatrace_query = f"fetch logs | filter (matchesPhrase(content, \"{extracted_id}\"))"
        logs_response = query_dynatrace_logs(dynatrace_query)
        
        # Load keyword_team_map for team assignment
        _, keyword_team_map = load_data()
        assigned_team = assign_team_by_keyword(user_query, keyword_team_map)

        response_message = f"Bot:\n- ID: {extracted_id}\n"
        if "logs" in logs_response:
            response_message += f"- Log Snippet: {logs_response['logs']}\n"
        elif "error" in logs_response:
            response_message += f"- Log Query Error: {logs_response['error']}\n"
        response_message += f"- Suggested Team: {assigned_team}\n"
        response_message += "- Suggested Action: Review full logs and investigate further."
    else:
        # Load keyword_team_map for team assignment even if no ID is found
        _, keyword_team_map = load_data()
        assigned_team = assign_team_by_keyword(user_query, keyword_team_map)
        response_message = f"Bot: I couldn't find a specific ID in your query. " \
                           f"However, based on keywords, the suggested team is: {assigned_team}. " \
                           f"Please provide an order_id or transaction_id for a more detailed analysis."

    return response_message

if __name__ == "__main__":
    print("\n--- NLP Chatbot Test ---")
    test_queries = [
        "investigate order_id ABC123",
        "check transaction TXN-98765",
        "what happened with ORD-54321",
        "show me logs for 1234567890AB",
        "general query about system performance",
        "database connection issues",
        "payment gateway failure",
        "authentication problems"
    ]

    for query in test_queries:
        print(f"\nUser: {query}")
        response = nlp_chatbot_query(query)
        print(response)

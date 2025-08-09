import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import re
import requests
import base64
from dotenv import load_dotenv

load_dotenv() # Load environment variables

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORICAL_KB_PATH = os.path.join(BASE_DIR, 'mock_historical_kb.csv')
KEYWORD_TEAM_MAP_PATH = os.path.join(BASE_DIR, 'mock_keyword_team_map.csv')

# Load data
def load_data():
    historical_kb = pd.read_csv(HISTORICAL_KB_PATH)
    keyword_team_map = pd.read_csv(KEYWORD_TEAM_MAP_PATH)
    return historical_kb, keyword_team_map

# Initialize embedding model
def initialize_embedding_model():
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return model

# Create and save FAISS index
def create_faiss_index(historical_kb, model):
    # Combine relevant text fields for embedding
    historical_kb['combined_text'] = historical_kb['Summary'] + " " + historical_kb['Issue_Description']
    embeddings = model.encode(historical_kb['combined_text'].tolist())
    
    # FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    faiss.write_index(index, os.path.join(BASE_DIR, 'faiss_index.bin'))
    return index

def load_faiss_index():
    return faiss.read_index(os.path.join(BASE_DIR, 'faiss_index.bin'))

def search_historical_kb(new_defect_description, model, faiss_index, historical_kb, top_k=1):
    new_defect_embedding = model.encode([new_defect_description])
    distances, indices = faiss_index.search(np.array(new_defect_embedding).astype('float32'), top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        similarity_score = 1 - (distances[0][i] / 2) # Convert L2 distance to similarity score (0 to 1)
        results.append({
            'historical_defect': historical_kb.iloc[idx].to_dict(),
            'similarity_score': similarity_score
        })
    return results

def extract_transaction_id(text):
    # Pattern 1: Prefixed IDs (e.g., order_id ABC123, TXN-987)
    match = re.search(r'(?:order_id|transaction_id|order id|transaction id|ORD-|TXN_)\s*([A-Za-z0-9-]+)\b', text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Pattern 2: Specific format like ABC-12345
    match = re.search(r'\b([A-Z]{3}-\d{3,})\b', text, re.IGNORECASE)
    if match:
        return match.group(1)

    return None

def assign_team_by_keyword(text, keyword_team_map):
    text_lower = text.lower()
    for index, row in keyword_team_map.iterrows():
        keyword = row['Keyword'].lower()
        if keyword in text_lower:
            return row['Assignment_Team']
    return "Unassigned"

from jira_agent import fetch_jira_issue, update_jira_ticket

DYNATRACE_API_URL = os.getenv("DYNATRACE_API_URL")
DYNATRACE_API_TOKEN = os.getenv("DYNATRACE_API_TOKEN")

def query_dynatrace_logs(query, time_frame="-1h"):
    if not all([DYNATRACE_API_URL, DYNATRACE_API_TOKEN]):
        print("Dynatrace API credentials not fully configured in .env. Skipping Dynatrace query.")
        return {"logs": "Mock Dynatrace logs for query: " + query}

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"
    }
    # Dynatrace Logs API endpoint for DQL queries
    url = f"{DYNATRACE_API_URL}/log/query"
    payload = {
        "query": query,
        "timeFrame": time_frame
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Dynatrace logs: {e}")
        return {"error": str(e)}

def process_defect(defect_description, model, faiss_index, historical_kb, keyword_team_map):
    # 2. Semantic Similarity Check
    similar_defects = search_historical_kb(defect_description, model, faiss_index, historical_kb)
    if similar_defects and similar_defects[0]['similarity_score'] > 0.7: # Threshold for duplicate
        print(f"  Found similar historical defect (score: {similar_defects[0]['similarity_score']:.2f}):")
        print(f"    Summary: {similar_defects[0]['historical_defect']['Summary']}")
        print(f"    Resolution: {similar_defects[0]['historical_defect']['Resolution_Steps']}")
        assigned_team = similar_defects[0]['historical_defect']['Solving_Team']
        resolution_steps = similar_defects[0]['historical_defect']['Resolution_Steps']
    else:
        print("  No highly similar historical defect found. Proceeding with keyword assignment.")
        # 3. Extract Transaction ID (if any)
        extracted_id = extract_transaction_id(defect_description)
        if extracted_id:
            print(f"  Extracted Transaction ID: {extracted_id}")
            # Query Dynatrace with DQL
            dynatrace_query = f"fetch logs | filter (matchesPhrase(content, \"{extracted_id}\"))"
            print(f"  Querying Dynatrace with: {dynatrace_query}")
            dynatrace_logs = query_dynatrace_logs(dynatrace_query)
            print(f"  Dynatrace Logs: {dynatrace_logs}")
            # In a real scenario, you would analyze these logs
        else:
            print("  No Transaction ID found.")

        # 4. Keyword-Based Team Assignment
        assigned_team = assign_team_by_keyword(defect_description, keyword_team_map)
        resolution_steps = "Investigate logs and provide detailed analysis." # Default for new issues

    print(f"  Assigned Team: {assigned_team}")
    print(f"  Suggested Resolution: {resolution_steps}")
    return assigned_team, resolution_steps

if __name__ == "__main__":
    historical_kb, keyword_team_map = load_data()
    model = initialize_embedding_model()
    
    # Check if FAISS index already exists, otherwise create it
    if not os.path.exists(os.path.join(BASE_DIR, 'faiss_index.bin')):
        faiss_index = create_faiss_index(historical_kb, model)
        print("FAISS index created and saved.")
    else:
        faiss_index = load_faiss_index()
        print("FAISS index loaded from file.")

    print("Historical KB:")
    print(historical_kb.head())
    print("\nKeyword Team Map:")
    print(keyword_team_map.head())

    # Example usage of search_historical_kb
    test_defect = "User cannot log in to the application."
    print(f"\nSearching for similar defects to: '{test_defect}'")
    similar_defects = search_historical_kb(test_defect, model, faiss_index, historical_kb)
    for defect in similar_defects:
        print(f"  Similarity Score: {defect['similarity_score']:.2f}")
        print(f"  Historical Defect Summary: {defect['historical_defect']['Summary']}")
        print(f"  Historical Defect Resolution: {defect['historical_defect']['Resolution_Steps']}")

    # Example usage of extract_transaction_id
    print("\nTesting Transaction ID Extraction:")
    test_texts = [
        "User reported issue with order_id ABC12345.",
        "Transaction ID: TXN-98765",
        "Failed to process payment for ORD-54321.",
        "No specific ID mentioned here.",
        "The error code is XYZ789012.",
        "Please check the log for ID: 1234567890AB"
    ]
    for text in test_texts:
        extracted_id = extract_transaction_id(text)
        print(f"  Text: \"{text}\" -> Extracted ID: {extracted_id}")

    # Example usage of assign_team_by_keyword
    print("\nTesting Team Assignment by Keyword:")
    defect_descriptions = [
        "Database connection issues are preventing users from logging in.",
        "Payment gateway is timing out for all transactions.",
        "Authentication service is down, users cannot log in.",
        "General system error, no specific keywords."
    ]
    for desc in defect_descriptions:
        assigned_team = assign_team_by_keyword(desc, keyword_team_map)
        print(f"  Description: \"{desc}\" -> Assigned Team: {assigned_team}")

    # --- MVP Flow Execution Example ---
    print("\n--- MVP Flow Execution Example ---")
    # 1. Simulate fetching a new Sev1 Jira issue
    new_jira_issue_id = "DEF-789"
    new_jira_issue = fetch_jira_issue(new_jira_issue_id)
    if new_jira_issue and "fields" in new_jira_issue and "description" in new_jira_issue["fields"]:
        print(f"Fetched new Jira issue: {new_jira_issue['fields']['summary']} - {new_jira_issue['fields']['description']}")
        defect_description = new_jira_issue['fields']['description']
    else:
        print("Failed to fetch Jira issue or description not found. Using a default description.")
        defect_description = "Simulated defect: User cannot log in to the application due to an authentication error."

    # 2. Semantic Similarity Check
    similar_defects = search_historical_kb(defect_description, model, faiss_index, historical_kb)
    if similar_defects and similar_defects[0]['similarity_score'] > 0.7: # Threshold for duplicate
        print(f"  Found similar historical defect (score: {similar_defects[0]['similarity_score']:.2f}):")
        print(f"    Summary: {similar_defects[0]['historical_defect']['Summary']}")
        print(f"    Resolution: {similar_defects[0]['historical_defect']['Resolution_Steps']}")
        assigned_team = similar_defects[0]['historical_defect']['Solving_Team']
        resolution_steps = similar_defects[0]['historical_defect']['Resolution_Steps']
    else:
        print("  No highly similar historical defect found. Proceeding with keyword assignment.")
        # 3. Extract Transaction ID (if any)
        extracted_id = extract_transaction_id(defect_description)
        if extracted_id:
            print(f"  Extracted Transaction ID: {extracted_id}")
            # Query Dynatrace with DQL
            dynatrace_query = f"fetch logs | filter (matchesPhrase(content, \"{extracted_id}\"))"
            print(f"  Querying Dynatrace with: {dynatrace_query}")
            dynatrace_logs = query_dynatrace_logs(dynatrace_query)
            print(f"  Dynatrace Logs: {dynatrace_logs}")
            # In a real scenario, you would analyze these logs
        else:
            print("  No Transaction ID found.")

        # 4. Keyword-Based Team Assignment
        assigned_team = assign_team_by_keyword(defect_description, keyword_team_map)
        resolution_steps = "Investigate logs and provide detailed analysis." # Default for new issues

    print(f"  Assigned Team: {assigned_team}")
    print(f"  Suggested Resolution: {resolution_steps}")

    # 5. Simulate updating Jira ticket
    update_payload = {
        "fields": {
            "assignee": {"name": assigned_team}, # Jira API expects a dictionary for assignee
            "comment": [{
                "add": {
                    "body": f"Automated triage: Assigned to {assigned_team}. Suggested action: {resolution_steps}"
                }
            }]
        }
    }
    update_result = update_jira_ticket(new_jira_issue_id, update_payload)
    print(f"Jira Update Result: {update_result}")

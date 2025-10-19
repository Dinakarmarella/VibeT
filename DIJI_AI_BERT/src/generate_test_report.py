import os
import yaml
import joblib
import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification

def generate_report(test_text: str, test_app: str, search_rc: str):
    """
    Generates a detailed report for a given test case.

    Args:
        test_text (str): The input text from the test case.
        test_app (str): The application associated with the test case.
        search_rc (str): The specific Root Cause to search for in historical data.
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    paths = config["paths"]
    params = config["bert_model"]

    model_path = os.path.join(project_root, paths["bert_model"])
    label_encoder_path = os.path.join(project_root, paths["label_encoder"])
    raw_data_path = os.path.join(project_root, paths["raw_data"])
    report_file_path = os.path.join(project_root, "test_report.txt")

    # --- 1. Prediction Details ---
    print("Loading model and making prediction...")
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    label_encoder = joblib.load(label_encoder_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    encoding = tokenizer.encode_plus(
        test_text, return_tensors='pt', max_length=params["max_length"], padding='max_length', truncation=True
    )
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        confidence, predicted_idx = torch.max(probabilities, dim=1)

    predicted_confidence = confidence.cpu().numpy()[0]
    predicted_label = label_encoder.inverse_transform([predicted_idx.cpu().numpy()[0]])[0]

    # --- 2. Similar Defects from Historical Data ---
    print("Searching for similar historical defects...")
    try:
        df_raw = pd.read_csv(raw_data_path)
        similar_defects = df_raw[df_raw['Root_Cause'] == search_rc].head(5)
    except FileNotFoundError:
        similar_defects = pd.DataFrame() # Handle case where raw data is missing

    # --- 3. Format the Report ---
    print("Formatting report...")
    report = []
    report.append("="*50)
    report.append("DIJI_AI TEST CASE REPORT")
    report.append("="*50)
    
    report.append("\n1. Issue Context:")
    report.append(f"   - Application: {test_app}")
    report.append(f"   - Summary: {test_text[:200]}...") # Truncate for brevity
    
    report.append("\n2. Prediction Details:")
    report.append(f"   - Predicted Root Cause: {predicted_label}")
    report.append(f"   - Overall Confidence: {predicted_confidence:.2%}")
    
    report.append(f"\n3. Similar Defects from Historical Data (Top 5 with RC '{search_rc}'):")
    if not similar_defects.empty:
        for index, row in similar_defects.iterrows():
            report.append(f"   - Defect ID {row.get('Defect_ID', 'N/A')}: {row.get('Summary', 'N/A')[:100]}...")
    else:
        report.append(f"   - No historical defects found with Root Cause: '{search_rc}'")
        
    report.append("\n" + "="*50 + "\n")
    
    final_report = "\n".join(report)

    # --- 4. Save the Report ---
    print(f"Saving report to {report_file_path}...")
    with open(report_file_path, 'a') as f:
        f.write(final_report)
        
    print("Report generated successfully.")
    print(final_report)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python generate_test_report.py <path_to_issue_file> <test_case_app> <search_for_rc>")
        sys.exit(1)

    issue_file_path = sys.argv[1]
    test_case_app = sys.argv[2]
    search_for_rc = sys.argv[3]
    
    try:
        with open(issue_file_path, 'r') as f:
            test_case_text = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{issue_file_path}' was not found.")
        sys.exit(1)

    print(f"Received new test case for app '{test_case_app}' from file.")
    generate_report(
        test_text=test_case_text,
        test_app=test_case_app,
        search_rc=search_for_rc
    )

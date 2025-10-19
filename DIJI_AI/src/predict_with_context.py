import pandas as pd
from predict import predict
import yaml
import os

# Load config
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
config = yaml.safe_load(open(config_path))
raw_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config["paths"]["raw_data"])

# Mock issue for testing
mock_issue = {
    "Summary": "Application crashes on startup",
    "Comments": "User reports that the application closes immediately after opening. Log file shows a null pointer exception.",
    "Error_Code": "NPE-001",
    "Severity": "High",
    "Application": "MobileApp"
}

def predict_with_context(issue: dict):
    # Get predictions
    predictions = predict(issue)
    top_prediction_label = predictions[0][0]
    top_prediction_prob = predictions[0][1]

    print(f"Prediction for new issue: {top_prediction_label} (Confidence: {top_prediction_prob:.2%})")
    print("-" * 20)

    # Find similar issues
    df = pd.read_csv(raw_data_path)
    similar_issues = df[df["Root_Cause"] == top_prediction_label]

    if not similar_issues.empty:
        print("Found similar historical issues:")
        for _, row in similar_issues.head(3).iterrows():
            print(f"  - Defect ID: {row['Defect_ID']}, Summary: {row['Summary']}")
    else:
        print("No similar historical issues found.")

if __name__ == "__main__":
    predict_with_context(mock_issue)

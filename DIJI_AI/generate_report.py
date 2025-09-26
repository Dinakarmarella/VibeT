import os
import sys
import pandas as pd

# Add the DIJI_AI directory to the Python path to allow for module imports
sys.path.append(os.path.dirname(__file__))

from src.predict import predict

def generate_prediction_report(issue_details, output_file=None):
    report_lines = []

    def print_to_report(text):
        report_lines.append(text)
        if output_file is None:
            print(text)

    print_to_report("\n--- Prediction Report ---")
    
    # 4. A brief context of the issue.
    print_to_report("\n1. Issue Context (Brief Context of the Issue):")
    print_to_report(f"   Summary: {issue_details.get('Summary', 'N/A')}")
    print_to_report(f"   Comments: {issue_details.get('Comments', 'N/A')}")
    print_to_report(f"   Severity: {issue_details.get('Severity', 'N/A')}")
    print_to_report(f"   Application: {issue_details.get('Application', 'N/A')}")

    try:
        predictions = predict(issue_details)
        if not predictions:
            print_to_report("   No predictions could be made for this issue.")
            return

        top_predicted_root_cause = predictions[0][0]
        confidence_score = predictions[0][1]

        print_to_report("\n2. Prediction Details:")
        # 2. The nearest Root Cause (RC).
        print_to_report(f"   Nearest Root Cause (RC): {top_predicted_root_cause}")
        # 3. The RC for the application.
        print_to_report(f"   RC for the Application: {top_predicted_root_cause}") # Assuming this is the same as Nearest RC
        # 1. Confidence score of the prediction.
        print_to_report(f"   Confidence Score of Prediction: {confidence_score:.4f}")
        print_to_report("   Top 3 Predictions:")
        for label, score in predictions:
            print_to_report(f"     - {label}: {score:.4f}")

        # 5. Similar defects from historical data.
        predictions_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "predictions_processed_data.csv"))
        similar_defects = predictions_df[predictions_df['predicted_root_cause'] == top_predicted_root_cause]
        
        print_to_report(f"\n3. Similar Defects from Historical Data (Top 5 with RC '{top_predicted_root_cause}'):")
        if not similar_defects.empty:
            print_to_report("   Note: No explicit 'defect id' column found in historical data. Displaying all available columns.")
            for index, row in similar_defects.head(5).iterrows():
                print_to_report(f"   --- Defect {index + 1} (Original Index: {row.name}) ---") # Added original index as a pseudo-ID
                for col in similar_defects.columns:
                    print_to_report(f"     {col}: {row[col]}")
        else:
            print_to_report("   No similar defects found in historical data.")

    except RuntimeError as e:
        print_to_report(f"Error during prediction: {e}")
        print_to_report("Please ensure the model has been trained and artifacts are present.")
    except Exception as e:
        print_to_report(f"An unexpected error occurred: {e}")

    if output_file:
        with open(output_file, 'w') as f:
            f.write("\n".join(report_lines))
        print(f"\nReport saved to {output_file}")

if __name__ == "__main__":
    # User-provided issue for testing
    test_issue = {
        "Summary": "Order Management FAILED with error 401 -- root cause hint: cache synchronization issue $$%%.",
        "Comments": "StackTrace>> NullRef @ line 72 in module_XYZ227. TemporaryFix>> restart service(Order Management) && clear-cache >> still failing. AdditionalNote: !! config mismatch in env%$#path: /opt/app/bin/start.sh !!! WARN !!! Users=affected >> count=68 sessions dropped.",
        "Severity": "high",
        "Application": "order management"
    }
    report_path = os.path.join(os.path.dirname(__file__), "prediction_report.txt")
    generate_prediction_report(test_issue, output_file=report_path)
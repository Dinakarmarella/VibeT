import joblib
import yaml
import os
import numpy as np
from predict import predict, combine_fields

# Load config and model
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
config = yaml.safe_load(open(config_path))
model = joblib.load(config["paths"]["model"])

# Mock issue for testing
mock_issue = {
    "Summary": "Application crashes on startup",
    "Comments": "User reports that the application closes immediately after opening. Log file shows a null pointer exception.",
    "Error_Code": "NPE-001",
    "Severity": "High",
    "Application": "MobileApp"
}

def explain_prediction(issue: dict):
    # Get the top prediction
    predictions = predict(issue)
    top_prediction_label = predictions[0][0]

    print(f"Prediction: {top_prediction_label}")
    print("-" * 20)

    # Extract vectorizer and classifier from pipeline
    vectorizer = model.named_steps['tfidf']
    classifier = model.named_steps['clf']

    # Find the index of the predicted class
    class_index = np.where(classifier.classes_ == top_prediction_label)[0][0]

    # Get the coefficients for that class
    class_coefficients = classifier.coef_[class_index]

    # Get feature names from the vectorizer
    feature_names = vectorizer.get_feature_names_out()

    # Transform the issue text to see which features are present
    text = combine_fields(issue)
    transformed_text = vectorizer.transform([text])
    present_features_indices = transformed_text.toarray()[0].nonzero()[0]

    # Get the coefficients for the features present in the text
    present_coefficients = class_coefficients[present_features_indices]
    present_feature_names = feature_names[present_features_indices]

    # Sort features by their coefficient value
    sorted_indices = np.argsort(present_coefficients)[::-1]

    print("Top words/phrases contributing to this prediction:")
    for i in sorted_indices[:10]: # Print top 10
        feature = present_feature_names[i]
        coeff = present_coefficients[i]
        if coeff > 0:
            print(f"  - '{feature}' (Contribution: {coeff:.2f})")

if __name__ == "__main__":
    explain_prediction(mock_issue)

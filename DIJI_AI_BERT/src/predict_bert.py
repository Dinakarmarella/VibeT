import os
import yaml
import joblib
import torch
from transformers import BertTokenizer, BertForSequenceClassification

def predict_root_cause(text: str) -> str:
    """
    Predicts the root cause for a given text using the fine-tuned BERT model.

    Args:
        text: The input text (e.g., from a Jira ticket).

    Returns:
        The predicted root cause as a string.
    """
    # --- 1. Load Config and Set Paths ---
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    paths = config["paths"]
    params = config["bert_model"]

    model_path = os.path.join(project_root, paths["bert_model"])
    label_encoder_path = os.path.join(project_root, paths["label_encoder"])
    
    # --- 2. Load Model, Tokenizer, and Label Encoder ---
    print("Loading model, tokenizer, and label encoder...")
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    label_encoder = joblib.load(label_encoder_path)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval() # Set model to evaluation mode

    # --- 3. Tokenize Input Text ---
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=params["max_length"],
        return_token_type_ids=False,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )

    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    # --- 4. Make Prediction ---
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).cpu().numpy()[0]

    # --- 5. Decode Prediction ---
    predicted_label = label_encoder.inverse_transform([prediction])[0]

    return predicted_label

if __name__ == "__main__":
    # Example Usage
    sample_text = "The login service is failing with a 500 internal server error. Users are unable to access their accounts. The logs show a null pointer exception in the authentication module."
    
    predicted_cause = predict_root_cause(sample_text)
    
    print("\n--- Prediction ---")
    print(f"Sample Text: \n\"{sample_text}\"")
    print(f"\nPredicted Root Cause: {predicted_cause}")
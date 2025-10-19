import os
import yaml
import joblib
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Add the src directory to the Python path to allow for module imports
import sys
sys.path.append(os.path.dirname(__file__))
from preprocess import combine_fields

# --- 1. Load Config and Set Paths ---
project_root = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(project_root, "config.yaml")
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Get paths and parameters from config
model_path = os.path.join(project_root, config["paths"]["cnn_model"])
tokenizer_path = os.path.join(project_root, config["paths"]["tokenizer"])
label_encoder_path = os.path.join(project_root, config["paths"]["label_encoder"])
max_length = config["cnn_model"]["max_length"]

# --- 2. Load Saved Artifacts ---
try:
    model = load_model(model_path)
    tokenizer = joblib.load(tokenizer_path)
    label_encoder = joblib.load(label_encoder_path)
except Exception as e:
    print(f"Error loading model or artifacts: {e}")
    print("Please ensure the model has been trained and artifacts are present.")
    model, tokenizer, label_encoder = None, None, None

def predict(issue: dict):
    """
    Predicts the root cause for a given issue using the trained CNN model.
    """
    if not all([model, tokenizer, label_encoder]):
        raise RuntimeError("Model and artifacts are not loaded. Cannot make predictions.")

    # 1. Preprocess the input text
    text = combine_fields(issue)
    sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(sequence, maxlen=max_length, padding='post', truncating='post')

    # 2. Make prediction
    probabilities = model.predict(padded_sequence)[0]

    # 3. Decode predictions
    top_indices = probabilities.argsort()[::-1][:3] # Get top 3 predictions
    
    preds = []
    for i in top_indices:
        label = label_encoder.classes_[i]
        score = float(probabilities[i])
        preds.append((label, score))
        
    return preds
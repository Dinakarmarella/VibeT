import os
import yaml
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


def train_cnn():
    """
    Trains a CNN model for text classification.
    """
    # --- 1. Load Config and Set Paths ---
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Get paths and parameters from config
    processed_data_path = os.path.join(project_root, config["paths"]["processed_data"])
    model_path = os.path.join(project_root, config["paths"]["cnn_model"])
    tokenizer_path = os.path.join(project_root, config["paths"]["tokenizer"])
    label_encoder_path = os.path.join(project_root, config["paths"]["label_encoder"])
    
    params = config["cnn_model"]
    vocab_size = params["vocab_size"]
    embedding_dim = params["embedding_dim"]
    max_length = params["max_length"]
    num_epochs = params["num_epochs"]
    batch_size = params["batch_size"]
    target_column = params["target_column"]

    # --- 2. Load and Preprocess Data ---
    print("Loading preprocessed data...")
    df = pd.read_csv(processed_data_path)
    df.dropna(subset=['text', target_column], inplace=True)

    X = df['text']
    y_text = df[target_column]

    # --- 3. Tokenize Text ---
    print("Tokenizing text data...")
    tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(X)
    X_sequences = tokenizer.texts_to_sequences(X)
    X_padded = pad_sequences(X_sequences, maxlen=max_length, padding='post', truncating='post')

    # --- 4. Encode Labels ---
    print("Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_text)
    num_classes = len(label_encoder.classes_)

    # --- 5. Build CNN Model ---
    print("Building the CNN model...")
    model = Sequential([
        Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length),
        Conv1D(128, 5, activation='relu'),
        GlobalMaxPooling1D(),
        Dense(64, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    model.summary()

    # --- 6. Train Model ---
    print("Training the model...")
    model.fit(X_padded, y_encoded, epochs=num_epochs, batch_size=batch_size, validation_split=0.2)

    # --- 7. Save Artifacts ---
    print("Saving model and supporting artifacts...")
    model.save(model_path)
    joblib.dump(tokenizer, tokenizer_path)
    joblib.dump(label_encoder, label_encoder_path)

    print(f"Model saved to {model_path}")
    print(f"Tokenizer saved to {tokenizer_path}")
    print(f"Label Encoder saved to {label_encoder_path}")

if __name__ == "__main__":
    train_cnn()
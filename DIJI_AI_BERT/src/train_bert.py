import os
import yaml
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup

class JiraTicketDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )

        return {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def train_bert():
    """
    Fine-tunes a BERT model for text classification.
    """
    # --- 1. Load Config and Set Paths ---
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    paths = config["paths"]
    params = config["bert_model"]
    
    processed_data_path = os.path.join(project_root, paths["processed_data"])
    model_path = os.path.join(project_root, paths["bert_model"])
    label_encoder_path = os.path.join(project_root, paths["label_encoder"])

    MODEL_NAME = params["model_name"]
    MAX_LEN = params["max_length"]
    BATCH_SIZE = params["batch_size"]
    EPOCHS = params["num_epochs"]
    LEARNING_RATE = float(params["learning_rate"])
    target_column = params["target_column"]

    # --- 2. Load and Preprocess Data ---
    print("Loading preprocessed data...")
    df = pd.read_csv(processed_data_path)
    df.dropna(subset=['text', target_column], inplace=True)

    # --- 3. Encode Labels ---
    print("Encoding labels...")
    label_encoder = LabelEncoder()
    df['label_encoded'] = label_encoder.fit_transform(df[target_column])
    num_classes = len(label_encoder.classes_)

    # --- 4. Split Data ---
    df_train, df_val = train_test_split(df, test_size=0.1, random_state=42, stratify=df[target_column])

    # --- 5. Set up Tokenizer and Datasets ---
    print(f"Loading tokenizer: {MODEL_NAME}")
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = JiraTicketDataset(
        texts=df_train.text.to_numpy(),
        labels=df_train.label_encoded.to_numpy(),
        tokenizer=tokenizer,
        max_len=MAX_LEN
    )

    val_dataset = JiraTicketDataset(
        texts=df_val.text.to_numpy(),
        labels=df_val.label_encoded.to_numpy(),
        tokenizer=tokenizer,
        max_len=MAX_LEN
    )

    train_data_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_data_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    # --- 6. Build BERT Model ---
    print(f"Loading pre-trained model: {MODEL_NAME}")
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=num_classes)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    # --- 7. Set up Optimizer and Scheduler ---
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    total_steps = len(train_data_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
    )

    # --- 8. Train Model ---
    print("Starting training...")
    for epoch in range(EPOCHS):
        print(f'Epoch {epoch + 1}/{EPOCHS}')
        print('-' * 10)

        # --- Training Phase ---
        model.train()
        total_loss = 0
        for batch in train_data_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

        avg_train_loss = total_loss / len(train_data_loader)
        print(f"Train loss: {avg_train_loss}")

        # --- Validation Phase ---
        model.eval()
        correct_predictions = 0
        total_predictions = 0
        with torch.no_grad():
            for batch in val_data_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)

                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                logits = outputs.logits
                predictions = torch.argmax(logits, dim=1)
                correct_predictions += torch.sum(predictions == labels)
                total_predictions += labels.size(0)

        val_accuracy = correct_predictions.double() / total_predictions
        print(f"Validation Accuracy: {val_accuracy:.4f}")

    # --- 9. Save Artifacts ---
    print("Saving model and supporting artifacts...")
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)
    joblib.dump(label_encoder, label_encoder_path)

    print(f"Model saved to {model_path}")
    print(f"Label Encoder saved to {label_encoder_path}")

if __name__ == "__main__":
    train_bert()
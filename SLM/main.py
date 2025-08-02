import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model

# --- Constants ---
MODEL_NAME = "microsoft/phi-3-mini-4k-instruct"
DATASET_PATH = "C:\Users\DINAKARMARELLA\Documents\Dins\VibeT\SLM\training_data.csv"
OUTPUT_DIR = "C:\Users\DINAKARMARELLA\Documents\Dins\VibeT\SLM\results"

def format_prompt(row):
    """Formats a single row of the DataFrame into a prompt string."""
    instruction = row['instruction']
    input_text = row['input']
    output = row['output']
    
    if pd.notna(input_text) and input_text.strip():
        return f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
    else:
        return f"### Instruction:\n{instruction}\n\n### Response:\n{output}"

class SimpleDataset:
    def __init__(self, tokenized_data):
        self.tokenized_data = tokenized_data

    def __len__(self):
        return len(self.tokenized_data["input_ids"])

    def __getitem__(self, idx):
        return {key: val[idx] for key, val in self.tokenized_data.items()}

def load_and_prepare_dataset(tokenizer):
    """Loads the dataset from CSV, formats it, and tokenizes it."""
    df = pd.read_csv(DATASET_PATH)
    prompts = df.apply(format_prompt, axis=1).tolist()
    
    tokenizer.pad_token = tokenizer.eos_token
    tokenized_data = tokenizer(
        prompts,
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    )
    # The labels are the input_ids themselves for language modeling.
    tokenized_data["labels"] = tokenized_data["input_ids"].clone()
    return SimpleDataset(tokenized_data)

def main():
    """
    Main function to orchestrate the SLM workflow.
    """
    print("--- Starting SLM Fine-Tuning Workflow ---")

    # 1. Load Tokenizer
    print(f"1. Loading tokenizer for '{MODEL_NAME}'...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    print("   Tokenizer loaded successfully.")

    # 2. Load and Prepare Dataset
    print(f"2. Loading and preparing dataset from '{DATASET_PATH}'...")
    train_dataset = load_and_prepare_dataset(tokenizer)
    print(f"   Dataset loaded and tokenized. Found {len(train_dataset)} records.")

    # 3. Load Model
    print(f"3. Loading base model '{MODEL_NAME}'...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=torch.float16, # Use float16 for memory efficiency
        device_map="auto" # Automatically use GPU if available
    )
    print("   Base model loaded successfully.")

    # 4. Configure PEFT/LoRA
    print("4. Configuring LoRA for efficient fine-tuning...")
    lora_config = LoraConfig(
        r=16, # Rank of the update matrices. Higher rank means more parameters to train.
        lora_alpha=32, # Alpha parameter for scaling.
        target_modules="all-linear", # Apply LoRA to all linear layers.
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    print("   LoRA configured successfully.")
    model.print_trainable_parameters()

    # 5. Configure and Run Trainer
    print("5. Configuring and starting the training process...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=3, # Train for 3 epochs
        logging_steps=10,
        save_steps=10,
        fp16=True, # Use mixed precision training
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )

    trainer.train()
    print("   Training completed.")

    # 6. Save the fine-tuned model
    print(f"6. Saving fine-tuned model adapters to '{OUTPUT_DIR}'...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("   Model saved successfully.")

    print("\n--- SLM Fine-Tuning Workflow Finished ---")

if __name__ == "__main__":
    main()

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import logging

# --- Constants ---
BASE_MODEL_NAME = "EleutherAI/pythia-14m"
ADAPTER_PATH = "C:\Users\DINAKARMARELLA\Documents\Dins\VibeT\SLM\results"
LOG_FILE = "C:\Users\DINAKARMARELLA\Documents\Dins\VibeT\SLM\inference.log"

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def format_prompt(instruction, input_text=None):
    """Formats the instruction and optional input into a prompt string."""
    if input_text and input_text.strip():
        return f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
    else:
        return f"### Instruction:\n{instruction}\n\n### Response:\n"

def main():
    """
    Main function to load the model and start the interactive inference loop.
    """
    logging.info("--- Starting Inference Script ---")

    # 1. Load Base Model and Tokenizer
    logging.info(f"1. Loading base model '{BASE_MODEL_NAME}'...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
        logging.info("   Base model and tokenizer loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading base model or tokenizer: {e}")
        return

    # 2. Load the LoRA Adapters
    logging.info(f"2. Loading fine-tuned adapters from '{ADAPTER_PATH}'...")
    try:
        model = PeftModel.from_pretrained(model, ADAPTER_PATH)
        logging.info("   Adapters loaded and applied successfully.")
    except Exception as e:
        logging.error(f"Error loading LoRA adapters: {e}. Make sure the path is correct and training was completed.")
        return

    # Set model to evaluation mode
    model.eval()
    logging.info("Model set to evaluation mode.")

    # 3. Interactive Inference Loop
    logging.info("\n--- Ready for Inference ---")
    print("\nEnter your instruction below. Type 'exit' or 'quit' to end.")
    
    while True:
        instruction = input(">> Instruction: ")
        if instruction.lower() in ["exit", "quit"]:
            break

        # Format and tokenize the prompt
        prompt = format_prompt(instruction)
        inputs = tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to("cuda")

        # Generate the response
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=150, pad_token_id=tokenizer.eos_token_id)
        
        # Decode and print the response
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up the output to only show the response part
        cleaned_response = response_text.split("### Response:")[-1].strip()
        
        print(f"\nModel Response:\n{cleaned_response}\n")

    logging.info("--- Inference Script Finished ---")

if __name__ == "__main__":
    main()

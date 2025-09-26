import pandas as pd
import re
import sys
import yaml
import os




def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def combine_fields(row):
    parts = [
        clean_text(row.get("Summary", "")),
        clean_text(row.get("Comments", ""))[:800],
        f"error_code_{row.get('Error_Code','')}",
        f"severity_{row.get('Severity','')}",
        f"app_{row.get('Application','')}"
    ]
    return " ".join([p for p in parts if p])


def preprocess_csv(input_path, output_path):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check for the new CNN model config first, with a fallback to the old one
    if 'cnn_model' in config:
        target_column = config["cnn_model"]["target_column"]
    else:
        target_column = config["model"]["target_column"]

    df = pd.read_csv(input_path)
    df["text"] = df.apply(combine_fields, axis=1)
    df_processed = df[["text", target_column]]
    df_processed.to_csv(output_path, index=False)
    print(f"Preprocessed data saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python preprocess.py <input_csv_path> <output_csv_path>")
        sys.exit(1)
    input_csv_path = sys.argv[1]
    output_csv_path = sys.argv[2]
    preprocess_csv(input_csv_path, output_csv_path)

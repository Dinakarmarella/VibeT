import pandas as pd
import re
import yaml
import os

def clean_text(text):
    """
    Cleans the input text by removing various noisy patterns.
    """
    if not isinstance(text, str):
        return ""
    
    # Remove stack traces, additional notes, etc.
    text = re.sub(r'StackTrace>>.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'AdditionalNote:.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'MonitorLogs==.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'DEBUG>>>.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'@@ Investigating.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'TemporaryFix>>.*', '', text, flags=re.IGNORECASE)
    
    # Remove special markers and warnings
    text = re.sub(r'(\$\$%%|!! ALERT !!|!!! WARN !!!|CRITICAL::|###)', '', text)
    
    # Remove file paths
    text = re.sub(r'\S*\/[\S\.]*', '', text)
    
    # Remove non-alphanumeric characters (but keep spaces) and collapse whitespace
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def main():
    """
    Main function to load, clean, and save the data.
    """
    # Load config to get paths
    # Assumes the script is run from the root of the DIJI_AI_BERT project
    config_path = 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    raw_data_path = config['paths']['raw_data']
    processed_data_path = config['paths']['processed_data']

    print(f"Loading raw data from {raw_data_path}...")
    df = pd.read_csv(raw_data_path)

    # Combine summary and comments into a single text column
    df['text'] = df['Summary'].fillna('') + ' ' + df['Comments'].fillna('')
    
    print("Cleaning text data...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # Select columns for the processed file
    # Keep original text for comparison if needed, but model will use cleaned_text
    processed_df = df[['cleaned_text', 'Root_Cause']]
    processed_df = processed_df.rename(columns={'cleaned_text': 'text'}) # rename for the model
    
    print(f"Saving processed data to {processed_data_path}...")
    processed_df.to_csv(processed_data_path, index=False)
    
    print(f"Data cleaning complete. Cleaned file saved to {processed_data_path}")

if __name__ == '__main__':
    main()

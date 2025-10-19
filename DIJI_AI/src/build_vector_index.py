
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
os.environ['CURL_CA_BUNDLE'] = ''

def create_and_save_index(data_path, index_save_path, data_mapping_save_path, model_name='all-MiniLM-L6-v2'):
    """
    Loads issue data, creates sentence embeddings, builds a FAISS index,
    and saves the index and data mapping to disk.
    """
    print("Loading data...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: The file {data_path} was not found.")
        return

    # Combine Summary and Comments for a richer embedding
    df['text'] = df['Summary'].fillna('') + " " + df['Comments'].fillna('')
    
    # Ensure there are no empty strings, which can cause issues
    df = df[df['text'].str.strip().astype(bool)]
    
    if df.empty:
        print("No text data found to index after cleaning. Aborting.")
        return

    print(f"Loading sentence transformer model: {model_name}...")
    model = SentenceTransformer(model_name)

    print("Generating embeddings for the issue text...")
    # The model will output a 384-dimensional vector for 'all-MiniLM-L6-v2'
    embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)

    # FAISS requires the embeddings to be in a specific float32 format.
    embeddings = np.array(embeddings).astype('float32')
    
    d = embeddings.shape[1]  # Dimensionality of the vectors
    
    print(f"Building FAISS index with {d} dimensions...")
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)

    print(f"Saving FAISS index to {index_save_path}...")
    faiss.write_index(index, index_save_path)

    # Save the original data (or at least the IDs) to map index results back to defects
    # We'll save the entire dataframe for now for easy lookup
    df_to_save = df[['Defect_ID', 'Summary', 'Root_Cause']].reset_index(drop=True)
    
    print(f"Saving data mapping to {data_mapping_save_path}...")
    with open(data_mapping_save_path, 'wb') as f:
        pickle.dump(df_to_save, f)

    print("Vector index and data mapping have been successfully created.")

if __name__ == '__main__':
    # Assuming the script is in DIJI_AI/src and data is in DIJI_AI/data
    # Adjust paths as necessary
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, '..'))
    
    data_file = os.path.join(base_dir, 'data', 'raw_data.csv')
    
    # Create a directory for the index if it doesn't exist
    index_dir = os.path.join(base_dir, 'vector_index')
    os.makedirs(index_dir, exist_ok=True)
    
    index_file = os.path.join(index_dir, 'diji_ai.index')
    mapping_file = os.path.join(index_dir, 'data_mapping.pkl')

    create_and_save_index(data_file, index_file, mapping_file)

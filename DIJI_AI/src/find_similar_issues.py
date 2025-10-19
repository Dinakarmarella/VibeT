

import os
os.environ['CURL_CA_BUNDLE'] = ''

import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

class IssueFinder:
    def __init__(self, index_path, data_mapping_path, model):
        print("Loading FAISS index...")
        self.index = faiss.read_index(index_path)
        
        print("Loading data mapping...")
        with open(data_mapping_path, 'rb') as f:
            self.df_map = pickle.load(f)
            
        self.model = model
        print("IssueFinder initialized.")

    def find_similar(self, query, k=5):
        """
        Finds k most similar issues to a given query.
        """
        print(f"\nSearching for top {k} similar issues for query: '{query}'")
        
        # Encode the query to get its embedding
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        # Perform the search
        distances, indices = self.index.search(query_embedding, k)
        
        print("\n--- Search Results ---")
        # indices is a 2D array, so we take the first row
        for i, idx in enumerate(indices[0]):
            # Retrieve the original data using the index
            similar_issue = self.df_map.iloc[idx]
            distance = distances[0][i]
            
            print(f"Result {i+1}: (Distance: {distance:.4f})")
            print(f"  Defect_ID: {similar_issue['Defect_ID']}")
            print(f"  Summary: {similar_issue['Summary']}")
            print(f"  Root_Cause: {similar_issue['Root_Cause']}")
            print("---")
        
        return self.df_map.iloc[indices[0]]

if __name__ == '__main__':
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, '..'))
    
    index_file = os.path.join(base_dir, 'vector_index', 'diji_ai.index')
    mapping_file = os.path.join(base_dir, 'vector_index', 'data_mapping.pkl')

    # Check if the index files exist
    if not os.path.exists(index_file) or not os.path.exists(mapping_file):
        print("Error: Index files not found.")
        print("Please run `build_vector_index.py` first to create the index.")
    else:
        # Load the model first
        print("Loading model for standalone run...")
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize the finder
        finder = IssueFinder(index_file, mapping_file, model)

        # --- Example Usage ---
        # This query is a hypothetical new issue
        example_query = "Application is crashing on startup on Windows servers after the new security patch was applied."
        
        # Find similar issues
        similar_issues_df = finder.find_similar(example_query, k=3)


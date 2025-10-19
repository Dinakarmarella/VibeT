

import pandas as pd
import networkx as nx
import os

def build_and_save_graph():
    """
    Reads raw defect data, builds a knowledge graph, and saves it to a file.
    The graph connects defects to their attributes like root cause, application, etc.
    """
    # Construct paths relative to the script location
    script_dir = os.path.dirname(__file__)
    data_path = os.path.abspath(os.path.join(script_dir, '''..''', '''data''', '''raw_data.csv'''))
    graph_output_path = os.path.abspath(os.path.join(script_dir, '''..''', '''data''', '''diji_knowledge_graph.gml'''))

    print(f"Reading data from {data_path}...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return

    G = nx.Graph()

    print("Building graph...")
    for _, row in df.iterrows():
        defect_id = row['Defect_ID']
        root_cause = row['Root_Cause']
        application = row['Application']
        error_code = str(row['Error_Code'])

        # Add nodes with attributes to distinguish their types
        G.add_node(defect_id, type='defect')
        G.add_node(root_cause, type='root_cause')
        G.add_node(application, type='application')
        G.add_node(error_code, type='error_code')

        # Add edges to represent relationships
        G.add_edge(defect_id, root_cause)
        G.add_edge(defect_id, application)
        G.add_edge(defect_id, error_code)

    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    # Save the graph
    nx.write_gml(G, graph_output_path)
    print(f"Graph saved to {graph_output_path}")

if __name__ == '__main__':
    build_and_save_graph()


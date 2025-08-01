# Main agent file for the Log and RCA Agent

import os
import ssl

# This is a global workaround to disable SSL certificate verification.
# It's often necessary in corporate environments with SSL inspection.
# Use with caution.
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# This line disables SSL verification for Hugging Face Hub downloads.
# It is a workaround for networks with self-signed certificates.
os.environ['HF_HUB_DISABLE_SSL'] = '1'

from neo4j import GraphDatabase
from transformers import pipeline
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from MCP.mcp_core import Message, Context

class LogRCAAgent:
    def __init__(self, neo4j_uri="bolt://localhost:7687", neo44j_user="neo4j", neo4j_password="password", embedding_model_name='all-MiniLM-L6-v2'):
        """
        Initializes the Log and RCA Agent.

        :param neo4j_uri: Neo4j URI.
        :param neo4j_user: Neo4j username.
        :param neo4j_password: Neo4j password.
        :param embedding_model_name: Name of the SentenceTransformer model to use for embeddings.
        """
        try:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            print("Successfully connected to Neo4j.")
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            self.neo4j_driver = None

        # Initialize the NLP pipeline for triplet extraction
        self.triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large')

        # Initialize SentenceTransformer model for embeddings
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Initialize FAISS index for embeddings
        self.faiss_index = faiss.IndexFlatL2(self.embedding_dim) # L2 distance for similarity
        self.log_id_map = [] # To map FAISS index to original log messages


    def _parse_triplets(self, extracted_text):
        """
        Parses the triplets from the model output.
        The expected format is: '<triplet> subject | relation | object <triplet> ...'
        """
        # The pipeline returns a list with a single dictionary.
        text = extracted_text[0]['generated_text']
        triplets = []
        # Find all occurrences of the triplet pattern.
        for triplet_str in text.split('<triplet>'):
            triplet_str = triplet_str.strip()
            if not triplet_str:
                continue
            
            parts = [p.strip() for p in triplet_str.split('|')]
            if len(parts) == 3:
                subject, relation, obj = parts
                triplets.append((subject, relation, obj))
        return triplets

    def _create_embedding(self, text):
        """
        Creates an embedding for the given text using the SentenceTransformer model.
        """
        return self.embedding_model.encode(text).astype('float32')

    def process_logs(self, log_dir="logs"):
        """
        Processes logs from the specified directory, extracts triplets, and updates the knowledge graph.

        :param log_dir: The directory containing the log files.
        """
        if not self.neo4j_driver:
            print("Cannot process logs, Neo4j is not connected.")
            return

        try:
            log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
            for log_file in log_files:
                with open(os.path.join(log_dir, log_file), "r") as f:
                    for log_message in f:
                        log_message = log_message.strip()
                        if log_message:
                            # Create embedding for the log message
                            log_embedding = self._create_embedding(log_message)
                            self.faiss_index.add(np.array([log_embedding]))
                            self.log_id_map.append(log_message) # Store the original log message

                            extracted_text = self.triplet_extractor(log_message, return_tensors=True, return_text=True)
                            triplets = self._parse_triplets(extracted_text)

                            with self.neo4j_driver.session() as session:
                                for sub, rel, obj in triplets:
                                    session.run("MERGE (s:Entity {name: $sub}) "
                                                "MERGE (o:Entity {name: $obj}) "
                                                "MERGE (s)-[:RELATION {type: $rel}]->(o)",
                                                sub=sub, rel=rel, obj=obj)
                                print(f"Successfully added triplets to Neo4j for log: {log_message}")

        except Exception as e:
            print(f"Error processing logs: {e}")

    def _query_vector_db(self, query_embedding, k=5):
        """
        Queries the FAISS index for the k most similar log messages.
        """
        D, I = self.faiss_index.search(np.array([query_embedding]), k)
        return [self.log_id_map[i] for i in I[0]]

    def _get_git_diff(self, commit_hash=None):
        """
        Retrieves Git diffs. Placeholder for actual implementation.
        """
        return "Git functionality is currently disabled."

    def _hypothesize_root_cause(self, query, relevant_logs, git_diffs, historical_defects):
        """
        Uses the LLM to hypothesize the root cause based on provided context.
        """
        context = f"User Query: {query}\n\nRelevant Log Messages:\n" + "\n".join(relevant_logs) + \
                  f"\n\nRecent Git Diffs:\n{git_diffs}" + \
                  f"\n\nHistorical Defects:\n{historical_defects}"

        prompt = f"Analyze the following context and provide a concise root cause hypothesis. " \
                 f"Also, suggest potential solutions or next steps.\n\nContext:\n{context}\n\nRoot Cause Hypothesis and Solutions:"

        # Using the triplet_extractor pipeline as a general text generation LLM
        # In a real scenario, you might use a dedicated LLM for this task.
        response = self.triplet_extractor(prompt, max_new_tokens=200, num_return_sequences=1)
        return response[0]['generated_text']

    def _score_confidence(self, hypothesis):
        """
        Scores the confidence of the root cause hypothesis using the LLM.
        """
        prompt = f"Given the following root cause hypothesis: '{hypothesis}'. " \
                 f"On a scale of 0 to 1, how confident are you in this hypothesis? " \
                 f"Provide only the numerical score.\nConfidence Score:"
        
        # Using the triplet_extractor pipeline as a general text generation LLM
        response = self.triplet_extractor(prompt, max_new_tokens=10, num_return_sequences=1)
        try:
            score = float(response[0]['generated_text'].strip())
            return max(0.0, min(1.0, score)) # Ensure score is between 0 and 1
        except ValueError:
            return 0.5 # Default to 0.5 if parsing fails

    def query_agent(self, input_message: Message, context: Context) -> Message:
        """
        This method will take a user query from an MCP Message and use the LLM
        to get an answer from the knowledge graph, returning the result as an MCP Message.
        """
        query = input_message.content.get("query", "")
        if not query:
            return Message(sender="LogRCAAgent", receiver=input_message.sender, content={"error": "No query provided in message content."}, message_type="error")

        if not self.neo4j_driver:
            return Message(sender="LogRCAAgent", receiver=input_message.sender, content={"error": "Cannot query agent, Neo4j is not connected."}, message_type="error")

        # Generate embedding for the query
        query_embedding = self._create_embedding(query)

        # Find similar logs from the vector database
        relevant_logs = self._query_vector_db(query_embedding)
        print(f"Relevant logs found: {relevant_logs}")

        # Get Git diffs (placeholder)
        git_diffs = self._get_git_diff()
        print(f"Git diffs: {git_diffs}")

        # Historical defects (placeholder - would come from a DB)
        historical_defects = "No historical defects found."

        # Hypothesize root cause
        root_cause_hypothesis = self._hypothesize_root_cause(query, relevant_logs, git_diffs, historical_defects)
        print(f"Root Cause Hypothesis: {root_cause_hypothesis}")

        # Score confidence
        confidence_score = self._score_confidence(root_cause_hypothesis)
        print(f"Confidence Score: {confidence_score}")

        # Update context with analysis results
        if context.shared_analysis_results is None:
            context.shared_analysis_results = {}
        context.shared_analysis_results["root_cause_hypothesis"] = root_cause_hypothesis
        context.shared_analysis_results["confidence_score"] = confidence_score

        # Placeholder for Cypher query generation and execution - needs _generate_cypher_query implementation
        # cypher_query = self._generate_cypher_query(query, relevant_logs)
        # print(f"Generated Cypher: {cypher_query}")
        # with self.neo4j_driver.session() as session:
        #     result = session.run(cypher_query)
        #     response_data = result.data()
        # response = f"The result of your query is: {response_data}"

        return Message(
            sender="LogRCAAgent",
            receiver=input_message.sender, # Send back to the sender of the query
            content={
                "root_cause_hypothesis": root_cause_hypothesis,
                "confidence_score": confidence_score,
                "relevant_logs": relevant_logs
            },
            message_type="root_cause_analysis"
        )

    def run(self):
        """
        Main loop for the agent.
        """
        print("Log and RCA Agent is running...")
        # In a real scenario, this would be a continuous loop
        # or triggered by an event.


if __name__ == "__main__":
    agent = LogRCAAgent()
    with open("debug_output.txt", "w") as f:
        f.write("--- Processing Logs and Building Knowledge Graph ---\n")
        agent.process_logs()
        f.write("---------------------------------------------------\n")

        f.write("--- Querying Agent for Root Cause ---\n")
        query = "What is the root cause of the payment service failure?"
        f.write(f"User Query: {query}\n")
        response = agent.query_agent(query, []) # Pass an empty list for parsed_triplets for now
        f.write(f"Agent Response: {response}\n")
        f.write("-----------------------------------\n")

    # The rest of the execution is commented out for now.
    # agent.run()
    # Example usage:
    # agent.ingest_logs({"message": "Example log entry"})
    # agent.process_logs()
    # response = agent.query_agent("What is the root cause of the latest incident?")
    # print(response)

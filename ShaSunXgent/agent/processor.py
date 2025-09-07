"""
The Processor module for the Automated Content Agent.

This module is responsible for taking raw text data and using an SLM
to transform it into summarized, publishable content.
"""

from transformers import pipeline, Pipeline

class Processor:
    """Processes text using an SLM to generate summaries."""

    def __init__(self, processor_config: dict):
        """
        Initializes the Processor with a specified SLM.

        Args:
            processor_config: A dictionary containing configuration for the SLM.
        """
        self.config = processor_config
        self.summarizer = self._load_model()
        print("Processor: Initialized.")

    def _load_model(self) -> Pipeline | None:
        """Loads the summarization pipeline from Hugging Face."""
        model_name = self.config.get('model')
        if not model_name:
            print("Processor: Error - No model specified in config.")
            return None
        
        try:
            print(f"Processor: Loading summarization model '{model_name}'. This may take a moment...")
            # Using device=-1 forces CPU, which is more compatible for general use.
            # For GPU, set device=0 (or another GPU index).
            summarizer_pipeline = pipeline(
                "summarization", 
                model=model_name,
                device=-1
            )
            print("Processor: Model loaded successfully.")
            return summarizer_pipeline
        except Exception as e:
            print(f"Processor: Error loading model '{model_name}'. Please ensure it's a valid Hugging Face model name and that you have an internet connection. Error: {e}")
            return None

    def summarize(self, text: str) -> str | None:
        """
        Generates a summary of the given text.

        Args:
            text: The input text to summarize.

        Returns:
            The summarized text, or None if summarization fails.
        """
        if not self.summarizer:
            print("Processor: Summarizer model not loaded. Cannot summarize.")
            return None

        print(f"Processor: Summarizing text starting with: '{text[:80]}...'")
        try:
            summary_list = self.summarizer(
                text,
                max_length=self.config.get('max_length', 150),
                min_length=self.config.get('min_length', 30),
                do_sample=False
            )
            summary = summary_list[0]['summary_text']
            print(f"Processor: Summary generated successfully.")
            return summary
        except Exception as e:
            print(f"Processor: An error occurred during summarization: {e}")
            return None

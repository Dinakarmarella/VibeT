"""
The Processor module for the Automated Content Agent.

This module uses a Hugging Face SLM to summarize text. It is capable of
handling long-form text (like video transcripts) by using a Map-Reduce strategy.
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
        # A rough estimation of max tokens for the model, used for chunking.
        # (e.g., distilbart is 1024 tokens). We use a smaller number for safety.
        self.chunk_max_length = 512 
        print("Processor: Initialized.")

    def _load_model(self) -> Pipeline | None:
        """Loads the summarization pipeline from Hugging Face."""
        model_name = self.config.get('model')
        if not model_name:
            print("Processor: Error - No model specified in config.")
            return None
        
        try:
            print(f"Processor: Loading summarization model '{model_name}'. This may take a moment...")
            summarizer_pipeline = pipeline(
                "summarization", 
                model=model_name,
                device=-1 # Force CPU
            )
            print("Processor: Model loaded successfully.")
            return summarizer_pipeline
        except Exception as e:
            print(f"Processor: Error loading model '{model_name}'. Error: {e}")
            return None

    def _summarize_chunk(self, text: str) -> str:
        """Helper function to summarize a single chunk of text."""
        if not self.summarizer:
            return ""
        
        # Use a higher max_length for intermediate summaries
        summary_list = self.summarizer(
            text,
            max_length=150, # Max length for a chunk summary
            min_length=40,
            do_sample=False
        )
        return summary_list[0]['summary_text']

    def summarize(self, text: str) -> str | None:
        """
        Generates a summary of the given text. If the text is too long,
        it automatically uses a Map-Reduce strategy.

        Args:
            text: The input text to summarize.

        Returns:
            The summarized text, or None if summarization fails.
        """
        if not self.summarizer:
            print("Processor: Summarizer model not loaded. Cannot summarize.")
            return None

        print(f"Processor: Summarizing text of length {len(text.split())} words...")
        try:
            # Heuristic: If text is longer than our chunk size, use Map-Reduce
            if len(text.split()) > self.chunk_max_length:
                print("Processor: Text is long. Applying Map-Reduce summarization strategy.")
                
                # MAP STEP: Summarize each chunk
                # Simple chunking by splitting text. A more advanced method would use a proper text splitter.
                chunks = [" ".join(text.split()[i:i+self.chunk_max_length]) for i in range(0, len(text.split()), self.chunk_max_length)]
                print(f"Processor: MAP: Split text into {len(chunks)} chunks.")
                chunk_summaries = [self._summarize_chunk(chunk) for chunk in chunks]
                combined_summary_text = " ".join(chunk_summaries)
                
                print("Processor: REDUCE: Summarizing the combined chunk summaries.")
                # REDUCE STEP: Summarize the combined summaries
                final_summary = self._summarize_chunk(combined_summary_text)

            else:
                print("Processor: Text is short. Applying standard summarization.")
                final_summary = self._summarize_chunk(text)

            print("Processor: Final summary generated successfully.")
            return final_summary

        except Exception as e:
            print(f"Processor: An error occurred during summarization: {e}")
            return None

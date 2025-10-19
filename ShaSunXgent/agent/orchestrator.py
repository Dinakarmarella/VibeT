"""
The Orchestrator module for the Automated Content Agent.

This module is the central coordinator, responsible for managing the workflow
by calling the appropriate Fetcher, Transcriber, Processor, and Publisher modules.
"""

import yaml
import os
from datetime import datetime

# Local imports
from .state_manager import StateManager
from .fetcher import Fetcher
from .transcriber import Transcriber
from .processor import Processor
from .publisher import Publisher

class Orchestrator:
    """The main coordinator of the agent."""

    def __init__(self, config_path: str):
        """
        Initializes the Orchestrator with settings from a config file.

        Args:
            config_path: Path to the YAML configuration file.
        """
        print("Orchestrator: Initializing...")
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Orchestrator: Error - Configuration file not found at '{config_path}'.")
            exit()
        
        self._load_api_keys()

        # Initialize all modules
        self.state_manager = StateManager(self.config.get('system', {}).get('database_path', 'agent_state.db'))
        self.fetcher = Fetcher(self.config, self.state_manager, self.api_keys)
        self.transcriber = Transcriber()
        self.processor = Processor(self.config.get('processor', {}))
        self.publisher = Publisher(self.config.get('publisher', {}), self.api_keys)
        print("Orchestrator: Configuration and all modules loaded.")

    def _load_api_keys(self):
        """Loads API keys, giving priority to environment variables."""
        print("Orchestrator: Loading API keys...")
        cfg_keys = self.config.get('api_keys', {})
        self.api_keys = {
            'youtube': os.environ.get('YOUTUBE_API_KEY') or cfg_keys.get('youtube'),
            'x_api_key': os.environ.get('X_API_KEY') or cfg_keys.get('x_api_key'),
            'x_api_secret': os.environ.get('X_API_SECRET') or cfg_keys.get('x_api_secret'),
            'x_access_token': os.environ.get('X_ACCESS_TOKEN') or cfg_keys.get('x_access_token'),
            'x_access_token_secret': os.environ.get('X_ACCESS_TOKEN_SECRET') or cfg_keys.get('x_access_token_secret'),
        }

    def execute_task(self, task_name: str):
        """
        Executes a specific task defined in the configuration.

        Args:
            task_name: The name of the task to execute.
        """
        print(f"Orchestrator: Starting task '{task_name}'...")
        if task_name == 'daily_youtube_summary':
            self.run_youtube_summary_flow()
        else:
            print(f"Orchestrator: Error - Task '{task_name}' not recognized.")
        print(f"Orchestrator: Task '{task_name}' finished.")

    def save_summary_to_log(self, video, summary):
        """Appends a summary to the youtube_summarizer_log.md file."""
        log_file = "youtube_summarizer_log.md"
        with open(log_file, "a") as f:
            f.write(f"## Daily Summary - {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(f"### Video: {video['title']}\n")
            f.write(f"*   **ID:** `{video['id']}`\n")
            f.write(f"*   **Summary:** {summary}\n\n")

    def run_youtube_summary_flow(self):
        """
        Runs the full workflow for fetching, transcribing, processing, and publishing.
        """
        print("Orchestrator: Running YouTube Transcript Summary workflow...")
        
        # 1. Fetch new video metadata
        new_videos = self.fetcher.get_new_youtube_videos()
        if not new_videos:
            print("Orchestrator: No new videos found. Workflow finished.")
            return

        print(f"Orchestrator: Found {len(new_videos)} new videos to process.")
        for video in new_videos:
            print(f"--- Starting workflow for video: {video['title']} ---")
            
            # 2. Get the full transcript
            transcript = self.transcriber.get_transcript(video['id'])
            if not transcript:
                # If transcript fails, mark as failed and skip to the next video
                self.state_manager.mark_as_processed(video['id'], video['source'], 'failed_transcription')
                print(f"--- Finished workflow for video: {video['title']} (Transcription Failed) ---")
                continue

            # 3. Process the transcript to get a summary
            summary = self.processor.summarize(transcript)
            if not summary:
                self.state_manager.mark_as_processed(video['id'], video['source'], 'failed_processing')
                print(f"--- Finished workflow for video: {video['title']} (Processing Failed) ---")
                continue
            
            # Save the summary to the log file
            self.save_summary_to_log(video, summary)

            # 4. Publish the summary
            success = self.publisher.post(summary=summary, trends="AI Summary")
            if success:
                print(f"Orchestrator: Successfully published summary for '{video['title']}'.")
                self.state_manager.mark_as_processed(video['id'], video['source'], 'published')
            else:
                print(f"Orchestrator: Failed to publish summary for '{video['title']}'. Will retry on next run.")
            
            print(f"--- Finished workflow for video: {video['title']} ---")
        
        print("Orchestrator: YouTube Transcript Summary workflow complete.")
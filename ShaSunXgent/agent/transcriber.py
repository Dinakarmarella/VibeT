"""
The Transcriber module for the Automated Content Agent.

This module is responsible for fetching the full text transcript of a YouTube video.
"""

import youtube_transcript_api as yt_api
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class Transcriber:
    """Fetches video transcripts from YouTube."""

    def __init__(self):
        """Initializes the Transcriber."""
        print("Transcriber: Initialized.")

    def get_transcript(self, video_id: str) -> str | None:
        """
        Retrieves the full transcript for a given YouTube video ID.

        Args:
            video_id: The unique identifier of the YouTube video.

        Returns:
            The full transcript as a single string, or None if a transcript
            cannot be retrieved.
        """
        print(f"Transcriber: Getting transcript for video ID: {video_id}")
        try:
            # First, list all available transcripts for the video
            transcript_list = yt_api.YouTubeTranscriptApi.list_transcripts(video_id)

            # Find the English transcript from the list
            # You can also iterate here to find manually created transcripts or specific languages
            transcript = transcript_list.find_transcript(['en'])

            # Fetch the actual transcript data
            transcript_data = transcript.fetch()

            # Combine the transcript segments into a single block of text
            full_transcript = " ".join([item['text'] for item in transcript_data])
            print(f"Transcriber: Successfully retrieved transcript for video ID: {video_id}")
            return full_transcript
        
        except TranscriptsDisabled:
            print(f"Transcriber: Warning - Transcripts are disabled for video ID: {video_id}")
            return None
        except NoTranscriptFound as e:
            print(f"Transcriber: Warning - Could not find a transcript for video ID: {video_id}. Error: {e}")
            return None
        except Exception as e:
            print(f"Transcriber: An unexpected error occurred while fetching transcript for video ID {video_id}: {e}")
            return None

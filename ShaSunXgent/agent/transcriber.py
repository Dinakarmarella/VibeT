"""
The Transcriber module for the Automated Content Agent.

This module is responsible for fetching the full text transcript of a YouTube video
using yt-dlp.
"""

import yt_dlp
import os
import re

class Transcriber:
    """Fetches video transcripts from YouTube using yt-dlp."""

    def __init__(self):
        """Initializes the Transcriber."""
        print("Transcriber: Initialized (using yt-dlp).")

    def get_transcript(self, video_id: str) -> str | None:
        """
        Retrieves the full transcript for a given YouTube video ID using yt-dlp.

        Args:
            video_id: The unique identifier of the YouTube video.

        Returns:
            The full transcript as a single string, or None if a transcript
            cannot be retrieved.
        """
        print(f"Transcriber: Attempting to get transcript for video ID: {video_id} using yt-dlp.")
        
        subtitle_path = f"{video_id}.en.vtt"
        
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'quiet': True,
            'outtmpl': f'{video_id}',
            'subtitlesformat': 'vtt',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

            # The subtitle file will be named based on the video ID and language.
            # For example: 'kMPt5FTY_io.en.vtt'
            # We need to find the correct file name.
            
            actual_subtitle_path = None
            for file in os.listdir('.'):
                if file.startswith(video_id) and file.endswith('.en.vtt'):
                    actual_subtitle_path = file
                    break

            if actual_subtitle_path and os.path.exists(actual_subtitle_path):
                print(f"Transcriber: Found and downloaded subtitle file: {actual_subtitle_path}")
                with open(actual_subtitle_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Basic VTT parsing: ignore metadata and join text lines
                transcript_lines = []
                for line in lines:
                    line = line.strip()
                    if '-->' in line or line.isdigit() or 'WEBVTT' in line or not line:
                        continue
                    # Remove VTT tags like <c> and </c>
                    line = re.sub(r'<[^>]+>', '', line)
                    transcript_lines.append(line)
                
                transcript = " ".join(transcript_lines)
                
                # Clean up the downloaded file
                os.remove(actual_subtitle_path)
                
                if transcript:
                    print(f"Transcriber: Successfully extracted transcript for {video_id}.")
                    return transcript
                else:
                    print(f"Transcriber: Subtitle file for {video_id} was empty or invalid.")
                    return None
            else:
                print(f"Transcriber: No English transcript found or downloaded for video ID: {video_id}.")
                return None

        except yt_dlp.utils.DownloadError as e:
            print(f"Transcriber: yt-dlp DownloadError for {video_id}: {e}")
            return None
        except Exception as e:
            print(f"Transcriber: An unexpected error occurred with yt-dlp for {video_id}: {e}")
            # Clean up partial file if it exists
            if actual_subtitle_path and os.path.exists(actual_subtitle_path):
                os.remove(actual_subtitle_path)
            return None

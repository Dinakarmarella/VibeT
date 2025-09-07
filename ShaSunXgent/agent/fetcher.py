"""
The Fetcher module for the Automated Content Agent.

This module is responsible for retrieving raw data from various sources
like YouTube, news websites, etc.
"""
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Local imports
from .state_manager import StateManager


class Fetcher:
    """Collects data from external sources."""

    def __init__(self, config: dict, state_manager: StateManager):
        """
        Initializes the Fetcher with data source configurations.

        Args:
            config: The application's configuration dictionary.
            state_manager: An instance of the StateManager.
        """
        self.config = config
        self.state_manager = state_manager
        self.youtube_api_key = self.config.get('api_keys', {}).get('youtube')
        print("Fetcher: Initialized.")

    def get_new_youtube_videos(self, max_results=2) -> list:
        """
        Fetches the latest videos from configured YouTube channels that have not
        yet been processed.

        Args:
            max_results: The maximum number of recent videos to check per channel.

        Returns:
            A list of dictionaries, where each dictionary represents a new video
            with its id, title, and description.
        """
        if not self.youtube_api_key or self.youtube_api_key == "YOUR_YOUTUBE_API_KEY":
            print("Fetcher: Error - YouTube API key is missing or not set in config.yaml.")
            return []

        print("Fetcher: Getting new YouTube videos...")
        new_videos = []
        try:
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            for channel in self.config.get('sources', {}).get('youtube_channels', []):
                channel_id = channel.get('channel_id')
                channel_name = channel.get('name')
                print(f"Fetcher: Checking channel: {channel_name}")

                request = youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    maxResults=max_results,
                    order='date',
                    type='video'
                )
                response = request.execute()

                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    
                    if not self.state_manager.is_processed(video_id):
                        print(f"Fetcher: Found new video: {item['snippet']['title']}")
                        video_details = {
                            'id': video_id,
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'source': channel_name
                        }
                        new_videos.append(video_details)
                        # Mark as fetched immediately to avoid reprocessing in concurrent runs
                        self.state_manager.mark_as_processed(
                            item_id=video_id, 
                            source=channel_name, 
                            status='fetched'
                        )
                    else:
                        print(f"Fetcher: Skipping already processed video: {item['snippet']['title']}")

        except HttpError as e:
            print(f"Fetcher: An HTTP error {e.resp.status} occurred: {e.content}")
        except Exception as e:
            print(f"Fetcher: An unexpected error occurred: {e}")
            
        return new_videos

    def scrape_news_website(self, site_name: str):
        """
        Scrapes the latest news from a configured website.

        This is a placeholder. In a real implementation, this would use
        libraries like requests and BeautifulSoup.
        """
        print(f"Fetcher: Scraping news from {site_name}... (Not yet implemented)")
        # TODO: Implement web scraping logic
        return []

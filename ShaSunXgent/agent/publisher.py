"""
The Publisher module for the Automated Content Agent.

This module is responsible for posting the final, processed content
to social media platforms like X.
"""

import tweepy

class Publisher:
    """Publishes content to social media platforms."""

    def __init__(self, publisher_config: dict, api_keys: dict):
        """
        Initializes the Publisher with platform and API key configurations.

        Args:
            publisher_config: Config for the publishing platform (e.g., tweet templates).
            api_keys: A dictionary of API keys.
        """
        self.config = publisher_config
        self.api_keys = api_keys
        self.client = self._initialize_client()
        print("Publisher: Initialized.")

    def _initialize_client(self):
        """Initializes and authenticates the Tweepy client."""
        required_keys = ['x_api_key', 'x_api_secret', 'x_access_token', 'x_access_token_secret']
        if not all(self.api_keys.get(key) and "YOUR_" not in self.api_keys.get(key) for key in required_keys):
            print("Publisher: Error - Missing or placeholder X API keys in config.yaml. Publishing will be disabled.")
            return None
        
        try:
            client = tweepy.Client(
                consumer_key=self.api_keys['x_api_key'],
                consumer_secret=self.api_keys['x_api_secret'],
                access_token=self.api_keys['x_access_token'],
                access_token_secret=self.api_keys['x_access_token_secret']
            )
            # Verify credentials
            client.get_me()
            print("Publisher: X (Twitter) client authenticated successfully.")
            return client
        except Exception as e:
            print(f"Publisher: Error authenticating with X API. Please check your keys. Error: {e}")
            return None

    def post(self, summary: str, trends: str = "N/A") -> bool:
        """
        Formats and posts the given content to the configured platform.

        Args:
            summary: The main summary text.
            trends: A string describing key trends (optional).

        Returns:
            True if posting was successful, False otherwise.
        """
        if not self.client:
            print("Publisher: Client not initialized. Cannot post.")
            return False

        platform = self.config.get("platform", "x")
        print(f"Publisher: Preparing to post content to {platform}...")
        
        try:
            template = self.config.get('tweet_template', '{summary}')
            content_to_post = template.format(summary=summary, trends=trends)
            content_to_post = content_to_post[:280] # Ensure it fits within Twitter's limit

            print("---- TWEET START ----")
            print(content_to_post)
            print("---- TWEET END ----")

            self.client.create_tweet(text=content_to_post)
            print("Publisher: Successfully posted to X.")
            return True
        except Exception as e:
            print(f"Publisher: Error posting to X: {e}")
            return False

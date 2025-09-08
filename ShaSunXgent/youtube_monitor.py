import os
import datetime
from googleapiclient.discovery import build
import sys

# Add the parent directory of ShaSunXgent to sys.path to import transcript_summarizer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from transcript_summarizer import get_youtube_transcript, summarize_text

# --- Configuration --- #
API_KEY = "YOUR_API_KEY"  # Replace with your YouTube Data API Key

# Replace with the actual channel IDs you want to monitor
# Example: 'UC_x5XG1OV2P6wMqXZhv5atQ' (Google Developers)
CHANNEL_IDS = [
    "@SHARRAB",
    "@PRSundar64"
]

HASHTAGS = [
    "#Premarket", 
    "#premarketanalysis", 
    "#Indianstockmarket", 
    "#nifty", 
    "#niftybank"
]

# --- YouTube API Functions --- #
def get_youtube_service():
    """Builds and returns the YouTube API service."""
    return build("youtube", "v3", developerKey=API_KEY)

def get_channel_id_from_handle(youtube, handle_or_name):
    """
    Resolves a YouTube channel handle or name to its Channel ID.
    """
    try:
        # Try by handle first (more precise for @handles)
        if handle_or_name.startswith('@'):
            response = youtube.channels().list(
                forHandle=handle_or_name[1:], # Remove the @ symbol
                part='id'
            ).execute()
            if response['items']:
                return response['items'][0]['id']
        
        # If not a handle or handle not found, try searching by name
        response = youtube.search().list(
            q=handle_or_name,
            type='channel',
            part='id',
            maxResults=1
        ).execute()
        if response['items']:
            return response['items'][0]['id']
        
        print(f"Warning: Could not find Channel ID for '{handle_or_name}'.")
        return None
    except Exception as e:
        print(f"Error resolving channel '{handle_or_name}': {e}")
        return None

def search_videos_by_channel_and_tags(youtube, channel_id, published_after, hashtags):
    """
    Searches for videos in a given channel published after a specific time
    and containing any of the specified hashtags in their title or description.
    """
    query = " OR ".join(hashtags)
    
    search_response = youtube.search().list(
        channelId=channel_id,
        part="id,snippet",
        type="video",
        publishedAfter=published_after.isoformat() + "Z", # ISO 8601 format
        q=query, # Search query for hashtags
        maxResults=10 # Adjust as needed
    ).execute()

    videos = []
    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        
        # Basic check for hashtags in title or description (case-insensitive)
        found_hashtags = False
        for tag in hashtags:
            if tag.lower() in title.lower() or tag.lower() in description.lower():
                found_hashtags = True
                break
        
        if found_hashtags:
            videos.append({
                "id": video_id,
                "title": title,
                "description": description
            })
    return videos

# --- Main Logic --- #
if __name__ == "__main__":
    youtube = get_youtube_service()
    combined_summaries = []

    # Calculate time 24 hours ago for 'publishedAfter'
    # This will search for videos published in the last 24 hours
    published_after = datetime.datetime.utcnow() - datetime.timedelta(days=1)

    print(f"Searching for videos published after: {published_after.isoformat()} UTC")

    resolved_channel_ids = {}
    for handle_or_name in CHANNEL_IDS:
        print(f"Resolving Channel ID for: {handle_or_name}")
        channel_id = get_channel_id_from_handle(youtube, handle_or_name)
        if channel_id:
            resolved_channel_ids[handle_or_name] = channel_id
        else:
            print(f"Skipping channel {handle_or_name} due to inability to resolve ID.")

    for handle_or_name, channel_id in resolved_channel_ids.items():
        print(f"\n--- Processing Channel: {handle_or_name} (ID: {channel_id}) ---")
        videos = search_videos_by_channel_and_tags(youtube, channel_id, published_after, HASHTAGS)

        if not videos:
            print(f"No new relevant videos found for channel {handle_or_name}.")
            continue

        for video in videos:
            print(f"Found video: {video['title']} (ID: {video['id']})")
            
            transcript = get_youtube_transcript(video['id'])
            if transcript:
                summary = summarize_text(transcript)
                if summary:
                    combined_summaries.append(
                        f"Channel: {handle_or_name}\n"
                        f"Video Title: {video['title']}\n"
                        f"Video URL: https://www.youtube.com/watch?v={video['id']}\n"
                        f"Summary: {summary}\n"
                        "---"
                    )
                else:
                    print(f"Could not summarize video {video['id']}.")
            else:
                print(f"Could not retrieve transcript for video {video['id']}.")

    if combined_summaries:
        final_output = "\n".join(combined_summaries)
        print("\n--- Combined Summaries for Twitter Posting ---")
        print(final_output)
        
        # You can save this to a file if needed
        # with open("combined_summaries.txt", "w", encoding="utf-8") as f:
        #     f.write(final_output)
    else:
        print("No summaries generated for any channel.")
import yt_dlp
from transformers import pipeline

import os
import tempfile
import re

def get_youtube_transcript(video_id: str) -> str | None:
    """
    Retrieves the full transcript for a given YouTube video ID using yt-dlp.
    Downloads the subtitle file to a temporary location and parses it.
    """
    print(f"Attempting to get transcript for video ID: {video_id} using yt-dlp.")
    
    # Create a temporary directory to store the subtitle file
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, '%(id)s.%(ext)s')
        
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'quiet': True,
            'outtmpl': filepath,
            'format': 'bestaudio/best', # This is needed to trigger download process for subtitles
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)
                
                # Find the downloaded subtitle file
                subtitle_filepath = None
                for f in os.listdir(tmpdir):
                    if f.endswith('.vtt') or f.endswith('.srt'):
                        subtitle_filepath = os.path.join(tmpdir, f)
                        break
                
                if subtitle_filepath:
                    print(f"Found subtitle file: {subtitle_filepath}")
                    with open(subtitle_filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic parsing for VTT/SRT to extract text
                    # Remove timestamps, speaker names (if any), and other metadata
                    # This is a simplified parser, a dedicated library would be more robust
                    lines = content.splitlines()
                    transcript_lines = []
                    for line in lines:
                        if '-->' in line or line.strip().isdigit() or line.strip() == '' or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                            continue
                        # Remove HTML tags and extra spaces
                        clean_line = re.sub(r'<[^>]+>', '', line).strip()
                        if clean_line:
                            transcript_lines.append(clean_line)
                    
                    transcript = " ".join(transcript_lines)
                    print(f"Successfully extracted transcript for video ID: {video_id}")
                    return transcript
                else:
                    print(f"No English subtitle file found for video ID: {video_id} after download.")
                    return None

        except yt_dlp.utils.DownloadError as e:
            print(f"yt-dlp DownloadError for {video_id}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with yt-dlp for {video_id}: {e}")
            return None

def summarize_text(text: str) -> str | None:
    """
    Summarizes the given text using a Hugging Face summarization pipeline.
    """
    if not text:
        return None

    try:
        # You can choose a different model if needed, e.g., "facebook/bart-large-cnn"
        # Be aware that larger models require more memory.
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        
        # Summarize in chunks if the text is too long for the model's context window
        # distilbart-cnn-12-6 has a max input length of 1024 tokens.
        # We'll split by sentences and process chunks.
        
        # A more robust chunking strategy would involve tokenization and overlap.
        # For simplicity, we'll do a basic split and join.
        
        max_chunk_length = 500 # Approximate words per chunk
        words = text.split()
        
        if len(words) > max_chunk_length:
            print("Text is long, summarizing in chunks...")
            chunks = [" ".join(words[i:i + max_chunk_length]) for i in range(0, len(words), max_chunk_length)]
            
            summaries = []
            for i, chunk in enumerate(chunks):
                print(f"Summarizing chunk {i+1}/{len(chunks)}...")
                # Adjust max_length and min_length for chunk summaries
                chunk_summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]["summary_text"]
                summaries.append(chunk_summary)
            
            # Summarize the summaries
            final_summary = summarizer(" ".join(summaries), max_length=250, min_length=50, do_sample=False)[0]["summary_text"]
        else:
            print("Text is short, summarizing directly...")
            final_summary = summarizer(text, max_length=250, min_length=50, do_sample=False)[0]["summary_text"]
            
        print("Successfully summarized text.")
        return final_summary
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None

if __name__ == "__main__":
    # Replace with the actual YouTube video ID
    # Example: "dQw4w9WgXcQ" for Rick Astley - Never Gonna Give You Up
    import sys
    if len(sys.argv) < 2:
        print("Usage: python transcript_summarizer.py <youtube_video_id>")
        sys.exit(1)
    video_id = sys.argv[1] 

    transcript = get_youtube_transcript(video_id)

    if transcript:
        summary = summarize_text(transcript)
        if summary:
            print("\n--- Summary ---")
            print(summary)
        else:
            print("Could not generate summary.")
    else:
        print("Could not retrieve transcript.")
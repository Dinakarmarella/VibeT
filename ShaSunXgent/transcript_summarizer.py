import sys
import io
import yt_dlp
from transformers import pipeline
import os
import re

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_youtube_transcript(video_id: str) -> str | None:
    """
    Retrieves the full transcript for a given YouTube video ID using yt-dlp.
    This function saves the subtitle file to disk and then reads it.
    """
    print(f"Attempting to get transcript for video ID: {video_id} using file-based yt-dlp.")
    
    subtitle_filename = f"{video_id}.en.vtt"
    
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'vtt',
        'skip_download': True,
        'outtmpl': f"{video_id}", # yt-dlp will add the lang and extension
        'overwrites': True,
    }
    
    try:
        # Ensure the file doesn't exist before we start
        if os.path.exists(subtitle_filename):
            os.remove(subtitle_filename)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Use download=True to force the subtitle write, skip_download=True prevents video download
            ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)

        # Check if the subtitle file was created
        if os.path.exists(subtitle_filename):
            print(f"Found subtitle file: {subtitle_filename}")
            with open(subtitle_filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean up the file immediately
            os.remove(subtitle_filename)
            
            # Parse the content
            lines = content.splitlines()
            transcript_lines = []
            for line in lines:
                if '-->' in line or line.strip().isdigit() or line.strip() == '' or line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
                    continue
                clean_line = re.sub(r'<[^>]+>', '', line).strip()
                if clean_line:
                    transcript_lines.append(clean_line)
            
            transcript = " ".join(transcript_lines)
            print(f"Successfully extracted transcript for video ID: {video_id}")
            return transcript
        else:
            print(f"Subtitle file '{subtitle_filename}' not found after download attempt.")
            return None

    except Exception as e:
        print(f"An unexpected error occurred with yt-dlp for {video_id}: {e}")
        # Clean up the file if it exists on error
        if os.path.exists(subtitle_filename):
            os.remove(subtitle_filename)
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
            
            # Join the summaries of the chunks
            final_summary = " ".join(summaries)
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
    # Example: "dQw4w9WgXcQ" for Rick Astley - Never Gonna Give Up
    import sys
    if len(sys.argv) < 2:
        print("Usage: python transcript_summarizer.py <youtube_video_id>")
        sys.exit(1)
    video_id = sys.argv[1] 

    transcript = get_youtube_transcript(video_id)

    if transcript:
        print("\n--- Transcript ---")
        print(transcript)
        summary = summarize_text(transcript)
        if summary:
            print("\n--- Summary ---")
            print(summary)
        else:
            print("Could not generate summary.")
    else:
        print("Could not retrieve transcript.")
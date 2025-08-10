
import whisper
import os

# Set the path to the ffmpeg executable
ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "ffmpeg-master-latest-win64-gpl", "bin", "ffmpeg.exe")
print(f"ffmpeg path: {ffmpeg_path}")
print(f"ffmpeg path exists: {os.path.exists(ffmpeg_path)}")
whisper.audio.FFMPEG_PATH = ffmpeg_path

def transcribe_audio(audio_path):
    """
    Transcribes the given audio file using the Whisper model.
    """
    if not os.path.exists(audio_path):
        return f"Error: Audio file not found at {audio_path}"

    print(f"Loading Whisper model...")
    model = whisper.load_model("tiny")
    
    print(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path)
    
    transcription = result["text"]
    print("Transcription complete.")
    
    return transcription

if __name__ == "__main__":
    # Assuming the audio file is in the same directory as the script
    audio_file = "Mastering Network Traffic_Cisco.mp3" # Assuming mp3, please change if not
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, audio_file)
    
    transcribed_text = transcribe_audio(audio_path)
    
    if "Error" not in transcribed_text:
        with open("transcription.txt", "w") as f:
            f.write(transcribed_text)
        print("Transcription saved to transcription.txt")
    else:
        print(transcribed_text)

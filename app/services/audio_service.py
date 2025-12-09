import os
import tempfile
import asyncio
import whisper

# Global variable to hold the loaded model
MODEL = None

def get_model():
    global MODEL
    if MODEL is None:
        print("⏳ Loading Whisper model (small)...")
        MODEL = whisper.load_model("small")
        print("✅ Whisper model loaded.")
    return MODEL

def transcribe_sync(contents: bytes, ext: str, language: str = None) -> str:
    """
    Synchronous function to handle file I/O and blocking model inference.
    """
    model = get_model()
    
    # Create a temporary file to store the audio bytes
    # suffix is important for ffmpeg to detect format
    suffix = f".{ext}" if ext else ".mp3"
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(contents)
        tmp_path = tmp_file.name
    
    try:
        # Run inference with translation task
        # task="translate" will translate input audio (any language) to English text
        # If language is provided, force it. Otherwise, auto-detect.
        options = {"task": "translate"}
        if language:
            options["language"] = language

        result = model.transcribe(tmp_path, **options)
        return result["text"].strip()
    except Exception as e:
        raise Exception(f"Whisper transcription failed: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

async def transcribe_audio_content(contents: bytes, ext: str, language: str = None) -> str:
    """
    Transcribes audio content and translates it to English using local OpenAI Whisper model.
    Runs the blocking transcription in a separate thread.
    """
    return await asyncio.to_thread(transcribe_sync, contents, ext, language)


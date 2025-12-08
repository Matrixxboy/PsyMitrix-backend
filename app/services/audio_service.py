import io
import speech_recognition as sr
from pydub import AudioSegment

async def transcribe_audio_content(contents: bytes, ext: str) -> str:
    """
    Transcribes audio content to text using Google Speech Recognition.
    """
    # --- Load and convert to WAV in memory ---
    audio_segment = AudioSegment.from_file(io.BytesIO(contents), format=ext)
    wav_buffer = io.BytesIO()
    audio_segment.export(wav_buffer, format="wav")
    wav_buffer.seek(0)

    # --- Speech recognition in chunks ---
    recognizer = sr.Recognizer()
    full_text = ""

    with sr.AudioFile(wav_buffer) as source:
        while True:
            try:
                audio_data = recognizer.record(source, duration=30)
                if not audio_data.frame_data:
                    break
                text = recognizer.recognize_google(audio_data)
                full_text += " " + text
            except sr.UnknownValueError:
                # Speech was unintelligible
                continue
            except sr.RequestError as e:
                raise Exception(f"Could not request results; {e}")
            except Exception as e:
                 # If loop breaks or other error, we might want to capture partial text or raise
                 # For now, simplistic handling as per original code structure intent
                 if full_text: 
                     break # Partial success?
                 raise e

    return full_text.strip()

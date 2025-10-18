from pydub import AudioSegment
import speech_recognition as sr
import io
import os

def audio_to_text_online(file_path: str):
    # Detect file format automatically
    file_ext = os.path.splitext(file_path)[1][1:].lower()

    # Load and convert any audio type (mp3, m4a, wav, flac, etc.)
    try:
        audio = AudioSegment.from_file(file_path, format=file_ext)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # Export to WAV in memory
    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)

    recognizer = sr.Recognizer()
    full_text = ""

    with sr.AudioFile(wav_buffer) as source:
        while True:
            try:
                # Read 30 seconds at a time (you can increase this)
                audio_data = recognizer.record(source, duration=30)
                if not audio_data.frame_data:
                    break
                text = recognizer.recognize_google(audio_data)
                full_text += " " + text
            except sr.UnknownValueError:
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"⚠️ Error during transcription: {e}")
                break

    print("\n🎧 Full Transcribed Text:\n")
    print(full_text.strip())

# Example usage
audio_to_text_online("test.m4a")   # Works for mp3, m4a, wav, flac, etc.

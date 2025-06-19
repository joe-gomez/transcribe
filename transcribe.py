import whisper
import tempfile
import os

# Load the model only once at import
try:
    model = whisper.load_model("small")  # Change to "base" or other sizes if needed
except Exception as e:
    model = None
    print(f"Failed to load Whisper model: {e}")

def transcribe(file_bytes, language, original_name="audio.mp3"):
    """
    Transcribe an audio/video file using OpenAI Whisper.
    
    Args:
        file_bytes (bytes): The contents of the uploaded file.
        language (str or None): ISO language code (e.g., 'en'), or None for auto-detect.
        original_name (str): Original filename (for correct extension).

    Returns:
        str: The transcribed text, or error message if transcription fails.
    """
    if model is None:
        return "Model not loaded. Please restart the server."

    ext = os.path.splitext(original_name)[1].lower() if "." in original_name else ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        temp_audio.write(file_bytes)
        temp_audio_path = temp_audio.name

    options = {}
    if language:
        options["language"] = language  # Should be ISO code, e.g. "en"

    try:
        result = model.transcribe(temp_audio_path, **options)
        text = result.get("text", "")
    except Exception as e:
        text = f"Transcription failed: {e}"
    finally:
        try:
            os.remove(temp_audio_path)
        except Exception:
            pass

    return text

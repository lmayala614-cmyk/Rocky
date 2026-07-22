import whisper
import sounddevice as sd
import numpy as np
import threading

model = None
_is_listening = False
_transcribed_text = None


def load_model():
    """Load Whisper model - call once at startup."""
    global model
    print("Loading Whisper model...")
    model = whisper.load_model("tiny")
    print("Whisper ready!")


def is_listening():
    return _is_listening


def get_transcription():
    """Returns transcribed text if ready, None if still processing."""
    global _transcribed_text
    if _transcribed_text is not None:
        text = _transcribed_text
        _transcribed_text = None
        return text
    return None


def _record_and_transcribe(duration=5):
    global _is_listening, _transcribed_text
    try:
        recording = sd.rec(
            int(duration * 16000),
            samplerate=16000,
            channels=1,
            dtype="float32"
        )
        sd.wait()
        result = model.transcribe(recording.flatten())
        _transcribed_text = result["text"].strip()
        print(f"Transcribed: {_transcribed_text}")
    except Exception as e:
        print(f"Voice error: {e}")
        _transcribed_text = ""
    _is_listening = False


def listen(duration=5):
    """Start listening in background thread."""
    global _is_listening
    if _is_listening or model is None:
        return
    _is_listening = True
    thread = threading.Thread(
        target=_record_and_transcribe,
        args=(duration,),
        daemon=True
    )
    thread.start()
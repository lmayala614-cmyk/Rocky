import numpy as np
import threading
import sounddevice as sd

# Current audio levels
bass = 0.0
mid = 0.0
treble = 0.0
overall = 0.0

_lock = threading.Lock()
_stream = None
_running = False

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024


def _audio_callback(indata, frames, time_info, status):
    global bass, mid, treble, overall
    if status:
        return

    # Get mono signal
    signal = indata[:, 0] if indata.ndim > 1 else indata.flatten()

    # FFT to get frequency content
    fft = np.abs(np.fft.rfft(signal))
    freqs = np.fft.rfftfreq(len(signal), 1/SAMPLE_RATE)

    # Split into frequency bands
    bass_mask   = freqs < 250
    mid_mask    = (freqs >= 250) & (freqs < 4000)
    treble_mask = freqs >= 4000

    b = float(np.mean(fft[bass_mask]))   if bass_mask.any()   else 0
    m = float(np.mean(fft[mid_mask]))    if mid_mask.any()    else 0
    tr = float(np.mean(fft[treble_mask])) if treble_mask.any() else 0

    # Normalize roughly
    scale = 0.0001
    with _lock:
        bass   = min(1.0, b  * scale * 3)
        mid    = min(1.0, m  * scale * 2)
        treble = min(1.0, tr * scale)
        overall = min(1.0, (b + m * 0.5) * scale * 2)


def start():
    global _stream, _running
    if _running:
        return
    try:
        # Try to find a loopback or output device
        devices = sd.query_devices()
        input_device = None
        
        # On Mac look for BlackHole or similar loopback
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0 and 'blackhole' in d['name'].lower():
                input_device = i
                break
        
        _stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            callback=_audio_callback,
            device=input_device  # None = default input
        )
        _stream.start()
        _running = True
        print(f"Audio analyzer started on device: {input_device}")
    except Exception as e:
        print(f"Audio analyzer failed: {e} — using fallback")


def stop():
    global _stream, _running
    if _stream:
        _stream.stop()
        _stream.close()
        _running = False


def get_levels():
    with _lock:
        return bass, mid, treble, overall
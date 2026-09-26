import base64
import numpy as np
from scipy.signal import resample_poly

def resample(b64_audio_16k: str) -> str:
    # Decode base64 → raw bytes
    pcm_bytes = base64.b64decode(b64_audio_16k)

    # Bytes → int16 numpy array
    audio_16k = np.frombuffer(pcm_bytes, dtype=np.int16)

    # Resample 16k → 8k (downsample by factor of 2)
    audio_8k = resample_poly(audio_16k, up=1, down=2)

    # Convert back to int16 (resample_poly outputs float)
    audio_8k = np.asarray(audio_8k, dtype=np.int16)

    # Encode back to base64
    pcm_8k_bytes = audio_8k.tobytes()
    return base64.b64encode(pcm_8k_bytes).decode("ascii")

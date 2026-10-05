import logging

import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)


class AudioResampler:
    """
    High-quality audio resampling for real-time communication between Cartesia and Teler.
    """
    cartesia_output_sample_rate: int
    teler_input_sample_rate: int

    def __init__(self):
        self.cartesia_output_sample_rate = 16000  # Cartesia streams to us at 16kHz
        self.teler_input_sample_rate = 8000  # Teler requires 8kHz audio from us

    def downsample(self, audio_data: bytes) -> bytes:
        """
        Downsample audio to Teler's required 8kHz.

        Args:
            audio_data: Raw PCM audio data as bytes
            source_rate: Source sample rate

        Returns:
            Downsampled audio data as bytes (pcm 16kHz format at pcm 8kHz)
        """
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            factor = self.cartesia_output_sample_rate // self.teler_input_sample_rate

            downsampled_array = signal.decimate(
                audio_array, 
                q=factor,
                n=8,
                ftype='iir'
            )

            downsampled_int16 = downsampled_array.astype(np.int16)

            return downsampled_int16.tobytes()

        except Exception as e:
            logger.error(f"Error downsampling audio: {e}")
            return audio_data
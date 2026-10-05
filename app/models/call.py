from typing import Optional
from app.utils.audio_processor import AudioResampler


class Call:
    id: str
    start_message_sent: bool = False
    server_acknowledged: bool = False
    cartesia_stream_id: Optional[str] = None
    audio_processor: AudioResampler

    def __init__(self):
        self.start_message_sent = False
        self.server_acknowledged = False
        self.audio_processor = AudioResampler()
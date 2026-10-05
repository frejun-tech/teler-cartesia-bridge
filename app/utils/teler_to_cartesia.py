from app.core.config import settings
from app.core import config
import json
import logging
from fastapi import WebSocket
from app.models.call import Call

logger = logging.getLogger(__name__)

async def teler_to_cartesia(cartesia_ws, teler_ws: WebSocket, call: Call):
    """
    Receive audio chunks from Teler and forward to Cartesia
    """
    try:
        while True:
            try:
                message = await teler_ws.receive_text()
                data = json.loads(message)

                if data.get("type") == "start":
                    call.id = data.get("call_id")
                
                elif data.get("type") == "audio" and call.server_acknowledged:
                    audio_b64 = data["data"]["audio_b64"]

                    # audio payload
                    payload = {
                        "event": "media_input",
                        "stream_id": data["stream_id"],
                        "media": {
                            "payload": audio_b64
                        }
                    }
                    await cartesia_ws.send(json.dumps(payload))

                elif data.get("type") == "audio" and not call.start_message_sent:
                    call.start_message_sent = True
                    stream_id = data.get("stream_id")
                    # agent config payload
                    payload = {
                        "event": "start",
                        "stream_id": stream_id,
                        "config": {
                            "input_format": "pcm_16000"
                        },
                        "agent": {
                            "system_prompt": "You are a helpful and friendly voice assistant. Keep your responses concise, natural, and conversational. Speak clearly and at a moderate pace.",
                        }
                    }
                    await cartesia_ws.send(json.dumps(payload))
            
            except Exception as e:
                logger.error(f"[media-stream][teler] Audio processing error: {type(e).__name__}: {e}")
                raise  

    except Exception as e:
        logger.info(f"[media-stream][teler] Fatal error: {type(e).__name__}: {e}")
        raise
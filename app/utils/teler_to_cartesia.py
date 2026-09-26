import json
import base64
import logging
from fastapi import WebSocket
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

async def teler_to_cartesia(cartesia_ws, teler_ws: WebSocket):
    """
    Receive audio chunks from Teler and forward to Cartesia
    """
    try:
        # audio_buffer = b""
        while True:
            try:
                message = await teler_ws.receive_text()
                data = json.loads(message)
                
                if data.get("type") != "audio":
                    continue

                audio_b64 = data["data"]["audio_b64"]
                
                # payload = json.dumps()
                await cartesia_ws.send(json.dumps({
                    "event": "media_input",
                    "stream_id": data["stream_id"],
                    "media": {
                        "payload": audio_b64
                    }
                }))
                logger.info(f"[media-stream][teler] Audio sent to Cartesia")
            
            except Exception as e:
                logger.error(f"[media-stream][teler] Audio processing error: {type(e).__name__}: {e}")
                raise  

    except Exception as e:
        logger.info(f"[media-stream][teler] Fatal error: {type(e).__name__}: {e}")
        raise
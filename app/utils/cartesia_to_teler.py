import json
import base64
import logging
from fastapi import WebSocket
from app.core.config import settings
from websockets.exceptions import ConnectionClosed
from app.utils.resample import resample

logger = logging.getLogger(__name__)


# FRAME_BYTES = 120

async def cartesia_to_teler(cartesia_ws, teler_ws):
    """
    Receive from Cartesia and forward to Teler.
    """
    # audio_buffer = b""
    chunk_id = 0
    # audio_buffer = b""
    # # CHUNK_BUFFER_SIZE = settings.CHUNK_BUFFER_SIZE
    # FRAME_BYTES = 160

    try:
        async for message in cartesia_ws:
            data = json.loads(message)

            if data.get('event') == "ack":
                logger.info(data)
                logger.info(f"[cartesia] Server {data.get('event')}")

            elif data.get('event') == "media_output":
                media = data.get('media')
                payload = media.get('payload')

                # audio_b64 = resample(payload)
                logger.info(f"Payload: ${payload}")

                # chunk_bytes = base64.b64decode(audio_b64)
                # audio_buffer += chunk_bytes

                # while len(audio_buffer) >= FRAME_BYTES:
                #     frame = audio_buffer[:FRAME_BYTES]
                #     audio_buffer = audio_buffer[FRAME_BYTES:]

                await teler_ws.send_json({
                    "type": "audio",
                    "audio_b64": payload,
                    "chunk_id": chunk_id,
                })
                logger.info("Audio sent to Teler.")
                chunk_id += 1


            elif data.get('event') == "clear":
                # audio_buffer = b""
                await teler_ws.send_json({"type": "clear"})
    except Exception as e:
        logger.error(f"Error in remote stream handler: {e}")


    except ConnectionClosed:
        logger.info("Cartesia WebSocket disconnected")

        if teler_ws.client_state != WebSocketState.DISCONNECTED:
            await teler_ws.close()
        try:
            await cartesia_ws.close()
        except Exception as e:
            logger.error(f"Error closing Cartesia WebSocket: {type(e).__name__}: {e}")
        logger.debug("cartesia_to_teler task ended")

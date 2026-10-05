from fastapi.websockets import WebSocketState
from app.core.config import settings
import base64
from app.models.call import Call
import json
import logging
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)


async def cartesia_to_teler(cartesia_ws, teler_ws, call: Call):
    """
    Receive from Cartesia and forward to Teler.
    """
    audio_buffer = []
    chunk_id = 0

    async def _flush():
        nonlocal chunk_id, audio_buffer
        if not audio_buffer:
            return
        try:
            combined_audio = b"".join(audio_buffer)

            downsampled_data = call.audio_processor.downsample(combined_audio)
            downsampled_b64 = base64.b64encode(downsampled_data).decode('utf-8')

            await teler_ws.send_json({
                "type": "audio",
                "audio_b64": downsampled_b64,
                "chunk_id": chunk_id
            })
            logger.debug(f"Sent audio to Teler (chunk {chunk_id})")
            chunk_id += 1
            audio_buffer = []
        except Exception as e:
            logger.error(f"Error processing buffered audio: {e}")
            audio_buffer = []

    try:
        async for message in cartesia_ws:
            data = json.loads(message)

            if data.get('event') == "ack":
                call.server_acknowledged = True
                logger.info(f"[cartesia] Server acknowledged the request.")

            elif data.get('event') == "media_output":
                media = data.get('media')
                media_payload = media.get('payload')
                audio_buffer.append(base64.b64decode(media_payload))

                # flush once the buffer is filled
                if len(audio_buffer) >= settings.CHUNK_BUFFER_SIZE:
                    logger.debug("Buffer filled.")
                    await _flush()
                else:
                    logger.debug("Bufferring the chunks")


            elif data.get('event') == "clear":
                logger.debug("Clear the buffer")
                audio_buffer = []
                await teler_ws.send_json({"type": "clear"})
    except Exception as e:
        logger.error(f"Error in remote stream handler: {e}")


    except ConnectionClosed:
        logger.info(f"Cartesia WebSocket disconnected, Error: {e}")

        if teler_ws.client_state != WebSocketState.DISCONNECTED:
            await teler_ws.close()
        try:
            await cartesia_ws.close()
        except Exception as e:
            logger.error(f"Error closing Cartesia WebSocket: {type(e).__name__}: {e}")
        logger.debug("cartesia_to_teler task ended")

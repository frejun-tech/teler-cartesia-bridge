import json
import asyncio
import logging
import time

import websockets
from fastapi import (APIRouter, HTTPException, WebSocket, status)
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketDisconnect, WebSocketState
from pydantic import BaseModel
from app.utils.get_access_token import get_access_token

from app.core.config import settings
from app.utils.teler_to_cartesia import teler_to_cartesia
from app.utils.cartesia_to_teler import cartesia_to_teler
from app.utils.teler_client import TelerClient

logger = logging.getLogger(__name__)
router = APIRouter()

class CallFlowRequest(BaseModel):
    call_id: str
    account_id: str
    from_number: str
    to_number: str

class CallRequest(BaseModel):
    from_number: str
    to_number: str

@router.get("/")
async def root():
    return {"message": "Welcome to the Teler-cartesia bridge"}

@router.post("/flow", status_code=status.HTTP_200_OK, include_in_schema=False)
async def stream_flow(payload: CallFlowRequest):
    """
    Return stream flow as JSON Response containing websocket url to connect
    """
    ws_url = f"wss://{settings.SERVER_DOMAIN}/api/v1/calls/media-stream"
    stream_flow = {
        "action": "stream",
        "ws_url": ws_url,
        "chunk_size": 400,
        "sample_rate": "8k",  
        "record": True
    }
    return JSONResponse(stream_flow)

@router.post("/initiate-call", status_code=status.HTTP_200_OK)
async def initiate_call(call_request: CallRequest):
    """
    Initiate a call using Teler SDK.
    """
    try:
        if not settings.CARTESIA_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cartesia_API_KEY not configured"
            )
        teler_client = TelerClient(api_key=settings.TELER_API_KEY)
        call = await teler_client.voice.calls.create(
            from_number=call_request.from_number,
            to_number=call_request.to_number,
            flow_url=f"https://{settings.SERVER_DOMAIN}/api/v1/calls/flow",
            status_callback_url=f"https://{settings.SERVER_DOMAIN}/api/v1/webhooks/receiver",
            record=False,
        )
        logger.info(f"Call created: {call}")
        return JSONResponse(content={"success": True, "call_id": call.id})
    except Exception as e:
        logger.error(f"Failed to create call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Call creation failed."
        )

@router.websocket("/media-stream")
async def media_stream(teler_ws: WebSocket):
    """
    Handle received and sent audio chunks, Teler -> Cartesia, Cartesia -> Teler
    """
    await teler_ws.accept()
    logger.info("Teler connected...")

    try:
        if not settings.CARTESIA_API_KEY:
            await teler_ws.close(code=1008, reason="CARTESIA API KEY not configured")
            return
            
        CARTESIA_ACCESS_TOKEN = await get_access_token()

        if not CARTESIA_ACCESS_TOKEN:
            await teler_ws.close(code=1008, reason="CARTESIA Access Token not configured")
            return

        headers = {
            "Authorization": f"Bearer {CARTESIA_ACCESS_TOKEN}",
            "Cartesia-Version": "2025-04-16",
        }
        
        async with websockets.connect(
            settings.CARTESIA_WS_URL,
            additional_headers=headers
        ) as cartesia_ws:
            logger.info("[media-stream] Successfully connected to Cartesia WebSocket")
            
            payload = json.dumps({
                "event": "start",
                "config": { "input_format": "mulaw_8000" },
                "agent": {
                    "introduction": "Hello, I'm an AI assistant",
                    "system_prompt": "### Your Role \n You are a helpful assistant"
                }
            })
            await cartesia_ws.send(payload)

            recv_task = asyncio.create_task(
                teler_to_cartesia(cartesia_ws, teler_ws), 
                name="teler_to_cartesia"
            )
            send_task = asyncio.create_task(
                cartesia_to_teler(cartesia_ws, teler_ws),
                name="cartesia_to_teler"
            )

            try:
                done, pending = await asyncio.wait(
                    [recv_task, send_task],
                    return_when=asyncio.FIRST_COMPLETED  
                )

                for task in done:
                    if task.exception():
                        logger.error(f"Task {task.get_name()} failed: {task.exception()}")
                    else:
                        logger.debug(f"Task {task.get_name()} completed successfully")

                for task in pending:
                    logger.error(f"Canceling task {task.get_name()}")
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            except Exception as e:
                logger.error(f"Error in task handling: {type(e).__name__}: {e}")


    except WebSocketDisconnect:
        logger.error("[media-stream] Teler WebSocket disconnected — closing Cartesia connection...")
        if cartesia_ws and not cartesia_ws.closed:
            await cartesia_ws.close()
            logger.info("[media-stream] Cartesia connection closed after Teler disconnect")

    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"[media-stream] WebSocket connection failed with status {e.status_code}: {e}")
        if e.status_code == 403:
            logger.error("[media-stream] Invalid API key or permission issue.")
    except Exception as e:
        logger.error(f"[media-stream] Top-level error: {type(e).__name__}: {e}")
    finally:
        if teler_ws.client_state != WebSocketState.DISCONNECTED:
            await teler_ws.close()
        logger.info("[media-stream] Connection closed.")

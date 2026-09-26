import httpx
import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

async def get_access_token():
    retries = 0
    max_retries = 5
    
    CARTESIA_ACCESS_TOKEN_API=f"https://api.cartesia.ai/access-token"

    payload = { "grants": {"agent": True}, "expires_in": 300 }

    headers = {
        "Cartesia-Version": "2025-04-16",
        "Authorization": f"Bearer {settings.CARTESIA_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        while retries < max_retries:
            try:
                response = await client.post(
                    url=CARTESIA_ACCESS_TOKEN_API,
                    json=payload,
                    headers=headers
                )
                data = response.json()

                CARTESIA_ACCESS_TOKEN = data.get("token")
                if CARTESIA_ACCESS_TOKEN:
                    logger.info(f"Got Access Token: {CARTESIA_ACCESS_TOKEN}")
                    return CARTESIA_ACCESS_TOKEN

            except Exception as e:
                logger.error(f"Error contacting Cartesia: {e}")

            retries += 1
            logger.warning(f"Retrying... attempt {retries}/{max_retries}")
            await asyncio.sleep(2)

    logger.error("Failed to get access token from Cartesia after max retries.")
    return None

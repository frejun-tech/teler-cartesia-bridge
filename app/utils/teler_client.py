from teler import AsyncClient
from app.core.config import settings

teler_client = AsyncClient(api_key=settings.TELER_API_KEY)
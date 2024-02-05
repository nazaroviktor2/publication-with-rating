from fastapi import APIRouter

from app.api.v1 import api_v1
from conf.config import settings

api_router = APIRouter(prefix=settings.API_PREFIX)

api_router.include_router(api_v1)

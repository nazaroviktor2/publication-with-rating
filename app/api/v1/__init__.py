from fastapi import APIRouter

from app.api.v1.auth.router import login_router
from app.api.v1.publication.router import publication_router
from app.api.v1.vote.router import vote_router
from conf.config import settings

api_v1 = APIRouter(prefix=settings.API_V1_PREFIX)

api_v1.include_router(login_router, tags=['auth'])
api_v1.include_router(publication_router, tags=['publication'])
api_v1.include_router(vote_router, tags=['vote'])

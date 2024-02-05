from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import api_router
from app.metrics import metrics, prometheus_metrics
from app.on_startup.redis import start_redis


def setup_middleware(app: FastAPI) -> None:
    # CORS Middleware should be the last.
    # See https://github.com/tiangolo/fastapi/issues/1663 .
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.middleware('http')(prometheus_metrics)


def setup_routers(app: FastAPI) -> None:
    app.add_route('/metrics', metrics)

    app.include_router(api_router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('START APP')
    await start_redis()
    yield
    logger.info('END APP')


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    setup_middleware(app)
    setup_routers(app)

    return app

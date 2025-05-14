from fastapi import APIRouter

router = APIRouter()

from .google.routes import router as google_router

router.include_router(google_router)
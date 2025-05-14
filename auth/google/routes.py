from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import get_current_user, create_or_get_user, exchange_code_for_tokens, GOOGLE_CLIENT_ID, REDIRECT_URI
from .schemas import UserResponse, AuthResponse
from core.models import db_helper
from google.oauth2 import id_token
from google.auth.transport import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/google", tags=["auth"])

@router.get("/login")
async def google_login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
    )
    return RedirectResponse(google_auth_url)

@router.get("/callback", response_model=AuthResponse)
async def google_callback(code: str, db: AsyncSession = Depends(db_helper.session_dependency)):
    token_data = await exchange_code_for_tokens(code)

    
    id_token_str = token_data.get("id_token")
    if not id_token_str:
        logger.error("No id_token received")
        raise HTTPException(status_code=400, detail="No id_token received")
    
    idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), GOOGLE_CLIENT_ID)
    
    user = await create_or_get_user(idinfo, db)
    return {"user": user, "token": id_token_str}

@router.get("/me", response_model=UserResponse)
async def get_user(user: UserResponse = Depends(get_current_user)):
    logger.info(f"Current user: {user}")
    return user

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from google.oauth2 import id_token
from google.auth.transport import requests
from core.models import User
from core.models import db_helper
from .schemas import UserCreate, UserResponse
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes={"openid": "openid", "email": "email", "profile": "profile"}
)

async def exchange_code_for_tokens(code: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise HTTPException(status_code=400, detail="Invalid or already used authorization code")
            raise HTTPException(status_code=502, detail=f"Failed to exchange code: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def create_or_get_user(idinfo: dict, db: AsyncSession) -> User:
    google_id = idinfo["sub"]
    email = idinfo.get("email")
    username = idinfo.get("name")
    avatar = idinfo.get("picture")

    result = await db.execute(select(User).filter(User.google_id == google_id))
    user = result.scalars().first()

    if not user:
        user_data = UserCreate(
            username=username,
            email=email,
            avatar=avatar,
            google_id=google_id
        )
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(db_helper.session_dependency)) -> UserResponse:
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        user = await create_or_get_user(idinfo, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import db_helper
from .dependencies import get_all, edit_user_role
from .schemas import UserResponseSchema, RoleUpdateSchema

router = APIRouter(tags=["Users"], prefix="/users")

@router.get("/", response_model=list[UserResponseSchema])
async def get_users(db: AsyncSession = Depends(db_helper.session_dependency)):
    data = await get_all(db)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return data

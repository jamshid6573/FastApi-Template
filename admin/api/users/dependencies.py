from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User
from .schemas import RoleUpdateSchema

async def get_all(db: AsyncSession):
        result = await db.execute(select(User))
        return result.scalars().all()

    

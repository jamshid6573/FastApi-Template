import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import TypeVar, Generic, Type
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import os

M = TypeVar("M")  
C = TypeVar("C")  # Create Schema
U = TypeVar("U")  # Update Schema

class BaseCRUD(Generic[M, C, U]):
    def __init__(self, model: Type[M]):
        self.model = model

    async def get_all(self, db: AsyncSession):
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, obj_id: int):
        obj = await db.get(self.model, obj_id)
        if not obj:
            return HTTPException(status_code=404, detail=f"{self.model.__name__} with id {obj_id} not found")
        return obj

    async def create(self, db: AsyncSession, obj_data: C):
        new_obj = self.model(**obj_data.model_dump())
        db.add(new_obj)
        try:
            await db.commit()
            await db.refresh(new_obj)
            return new_obj
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Item with name '{obj_data.name}' already exists!")

    async def update(self, db: AsyncSession, obj_id: int, obj_data: U):
        obj = await db.get(self.model, obj_id)
        if not obj:
            return HTTPException(status_code=404, detail=f"{self.model.__name__} with id {obj_id} not found")
        obj_dict = obj_data.model_dump(exclude_unset=True)
        for key, value in obj_dict.items():
            setattr(obj, key, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, obj_id: int):
        obj = await db.get(self.model, obj_id)
        if not obj:
            return HTTPException(status_code=404, detail=f"{self.model.__name__} with id {obj_id} not found")
        await db.delete(obj)
        try:
            await db.commit()
            return f"{obj.name} with id {obj.id} deleted successfully"
        except IntegrityError as e:
            return HTTPException(status_code=400, detail=f"Error: {e.orig}")
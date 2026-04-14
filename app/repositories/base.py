from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete


class BaseRepository:
    model = None

    def __init__(self, db: AsyncSession):
        self.db = db    

    async def find_all(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one()

    async def update_one(self, row_id: int, data: dict):
        stmt = update(self.model).where(self.model.id == row_id).values(**data).returning(self.model)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one()

    async def delete_one(self, row_id: int):
        stmt = delete(self.model).where(self.model.id == row_id)
        await self.db.execute(stmt)
        await self.db.commit()
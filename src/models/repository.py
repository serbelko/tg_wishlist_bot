# async_repository.py
from typing import Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from models import PlanORM, Base

class PlanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_plan(self, user_id: str, text: str, label=str) -> dict:
        plan_id = uuid4()
        new_plan = PlanORM(id=plan_id, user_id=user_id, text=text, label=label)

        self.db.add(new_plan)
        await self.db.commit()
        await self.db.refresh(new_plan)

        return new_plan.to_dict()

    async def get_plan_by_user_id(self, user_id: str) -> Optional[list]:
        result = await self.db.execute(
            PlanORM.__table__.select().where(PlanORM.user_id == user_id)
        )
        plans = result.scalars().all()
        return [plan.label for plan in plans]
    
    
    async def get_plan_by_plan_id(self, plan_id: str):
        result = await self.db.execute(
            PlanORM.__table__.select().where(PlanORM.id == plan_id)
        )
        plan = result.scalars().first()
        return plan.to_dict()
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict

from sqlalchemy import Column, Integer, String, Text, UUID, null
from sqlalchemy.orm import DeclarativeBase


Base = declarative_base()

class PlanORM(Base):
    __tablename__ = "plans"

    id = Column("plan_id", String, primary_key=True)
    user_id = Column("user_id", String, nullable=False, index=True)
    label = Column('label', String)
    text = Column('text', Text)

    def to_dict(self) -> Dict:
        model_dict = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "label": str(self.label),
            "text": self.text
        }
        return model_dict
    

class UserORM(Base):
    __tablename__ = "user_table"

    user_id = Column("user_id", String, nullable=False, primary_key=True)
    language = Column("language", String, nullable=False)

    def to_dict(self) -> Dict:
        model_dict = {
            "user_id": str(self.user_id),
            "language": str(self.language),
        }
        return model_dict
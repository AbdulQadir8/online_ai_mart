from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_name: str = Field(unique=True, nullable=False)
    full_name: str
    email: str = Field(unique=True, nullable=True)
    password: str 

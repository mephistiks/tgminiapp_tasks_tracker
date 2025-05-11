from pydantic import BaseModel, Field
from typing import Literal
from datetime import date, datetime

class UserCreate(BaseModel):
    telegram_id: str = Field(..., min_length=1)
    fio: str = Field(..., min_length=1)


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    time_spent: float | None = Field(None, ge=0)
    task_date: date | None = None
    init_data: str
    group_id: int | None = None


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    init_data: str


class GroupAddMember(BaseModel):
    group_name: str
    telegram_id: str


class GroupAddAdmin(BaseModel):
    group_name: str
    telegram_id: str


class InitData(BaseModel):
    init_data: str


class TaskReportFilter(BaseModel):
    init_data: str
    filter_mode: Literal['my', 'admin_all', 'group']
    group_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    time_spent: float
    task_date: date | None = None
    creator_name: str | None = None
    group_id: int | None = None
    created_at: datetime


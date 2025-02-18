from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class UserCreate(BaseModel):
    telegram_id: str = Field(..., min_length=1)
    fio: str = Field(..., min_length=1)


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    time_spent: Optional[float] = Field(None, ge=0)
    task_date: Optional[date] = None
    init_data: str
    group_id: Optional[int] = None


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


# Фильтр для отчётов:
class TaskReportFilter(BaseModel):
    init_data: str
    filter_mode: str  # "my" | "admin_all" | "group"
    group_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    time_spent: float
    task_date: Optional[date]
    creator_name: Optional[str]
    group_id: Optional[int]
    created_at: datetime


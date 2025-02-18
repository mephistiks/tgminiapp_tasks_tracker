# app/api.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..dependencies import get_db, get_user_id_from_init_data
from .. import crud
from ..schemas import (
    UserCreate,
    GroupAddMember,
    GroupAddAdmin,
    GroupCreate,
    TaskCreate,
    InitData,
    TaskReportFilter
)

router = APIRouter()


@router.post("/user")
def create_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
    user = crud.create_or_update_user(db, user_data)
    return {"status": "ok", "message": f"User {user.telegram_id} saved/updated"}


@router.get("/users")
def get_all_users_route(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return [{"id": user.telegram_id, "fio": user.fio} for user in users]



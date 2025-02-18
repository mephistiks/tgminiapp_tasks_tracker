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


@router.get("/")
def get_all_groups_route(db: Session = Depends(get_db)):
    return crud.get_all_groups(db)


@router.post("/")
def create_group_route(group_data: GroupCreate, db: Session = Depends(get_db)):
    group = crud.create_group(db, group_data.name)
    return {"status": "ok", "group_id": group.id}


@router.put("/members")
def put_user_to_group_route(member_data: GroupAddMember, db: Session = Depends(get_db)):
    status_msg = crud.add_user_to_group(
        db, member_data.group_name, member_data.telegram_id)
    return {"status": status_msg}


@router.put("/admins")
def put_admin_to_group_route(member_data: GroupAddAdmin, db: Session = Depends(get_db)):
    status_msg = crud.add_admin_to_group(
        db, member_data.group_name, member_data.telegram_id)
    return {"status": status_msg}


@router.post("/my")
def get_my_groups_route(init_data: InitData, role: str = Query("member", pattern="^(member|admin)$"), db: Session = Depends(get_db)):
    user_id = get_user_id_from_init_data(init_data.init_data)
    groups = crud.get_my_groups(db, user_id, role)
    return [{"id": g.id, "name": g.name} for g in groups]



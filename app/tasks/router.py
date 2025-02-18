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

@router.post("/")
def create_task_route(task_data: TaskCreate, db: Session = Depends(get_db)):
    creator_id = get_user_id_from_init_data(task_data.init_data)
    new_task = crud.create_task(db, task_data, creator_id)
    return {"task_id": new_task.id}


@router.post("/report/filter")
def get_tasks_report_filter_route(req: TaskReportFilter, db: Session = Depends(get_db)):
    user_id = get_user_id_from_init_data(req.init_data)
    return crud.get_tasks_for_report_filtered(db, user_id, req.filter_mode, req.group_id)



@router.get("/")
def get_all_tasks_route(db: Session = Depends(get_db)):
    return crud.get_all_tasks(db)

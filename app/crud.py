# app/crud.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .models import User, Task, Group, GroupMember, GroupAdmin
from .schemas import UserCreate, TaskCreate


def create_or_update_user(db: Session, user_data: UserCreate) -> User:
    user = db.query(User).filter(User.telegram_id ==
                                 user_data.telegram_id).first()
    if user:
        user.fio = user_data.fio
    else:
        user = User(
            telegram_id=user_data.telegram_id,
            fio=user_data.fio,
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session) -> List[User]:
    return db.query(User).all()


def create_group(db: Session, name: str) -> Group:
    existing_group = db.query(Group).filter(Group.name == name).first()
    if existing_group:
        raise HTTPException(status_code=400)
    group = Group(name=name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def add_user_to_group(db: Session, group_name: str, telegram_id: str) -> str:
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=404)
    user_to_add = db.query(User).filter(
        User.telegram_id == telegram_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404)
    existing_member = db.query(GroupMember).filter(
        GroupMember.group_id == group.id,
        GroupMember.user_id == user_to_add.id
    ).first()
    if existing_member:
        raise HTTPException(status_code=400)
    new_member = GroupMember(group_id=group.id, user_id=user_to_add.id)
    db.add(new_member)
    db.commit()
    return f"User {telegram_id} added to group {group.name}"


def add_admin_to_group(db: Session, group_name: str, telegram_id: str) -> str:
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=404)
    user_to_add = db.query(User).filter(
        User.telegram_id == telegram_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404)
    existing_admin = db.query(GroupAdmin).filter(
        GroupAdmin.group_id == group.id,
        GroupAdmin.user_id == user_to_add.id
    ).first()
    if existing_admin:
        raise HTTPException(
            status_code=400)
    new_admin = GroupAdmin(group_id=group.id, user_id=user_to_add.id)
    db.add(new_admin)
    db.commit()
    return f"Юзер {telegram_id} теперь админ в {group.name}"



def get_my_groups(db: Session, user_id: str, role: str) -> List[Group]:
    if role == "member":
        groups = (
            db.query(Group)
            .join(GroupMember, Group.id == GroupMember.group_id)
            .join(User, User.id == GroupMember.user_id)
            .filter(User.telegram_id == user_id)
            .all()
        )
    else:
        groups = (
            db.query(Group)
            .join(GroupAdmin, Group.id == GroupAdmin.group_id)
            .join(User, User.id == GroupAdmin.user_id)
            .filter(User.telegram_id == user_id)
            .all()
        )
    return groups


def get_all_groups(db: Session) -> List[Group]:
    return db.query(Group).all()


def create_task(db: Session, task_data: TaskCreate, creator_id: str) -> Task:
    if task_data.group_id is not None:
        group = db.query(Group).filter(Group.id == task_data.group_id).first()
        if not group:
            raise HTTPException(status_code=404)
        is_member = (
            db.query(GroupMember)
            .join(User, User.id == GroupMember.user_id)
            .filter(GroupMember.group_id == group.id, User.telegram_id == creator_id)
            .first()
        )
        is_admin = (
            db.query(GroupAdmin)
            .join(User, User.id == GroupAdmin.user_id)
            .filter(GroupAdmin.group_id == group.id, User.telegram_id == creator_id)
            .first()
        )
        if not is_member and not is_admin:
            raise HTTPException(
                status_code=403,
            )
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        time_spent=task_data.time_spent,
        task_date=task_data.task_date,
        creator_id=creator_id,
        group_id=task_data.group_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_all_tasks(db: Session):
    rows = (
        db.query(Task, User)
        .outerjoin(User, Task.creator_id == User.telegram_id)
        .all()
    )
    result = []
    for task, user in rows:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "time_spent": task.time_spent or 0,
            "task_date": task.task_date.isoformat() if task.task_date else "",
            "creator_name": user.fio if user else "",
            "group_id": task.group_id,
            "created_at": task.created_at.isoformat() if task.created_at else "",
        })
    return result


def get_tasks_for_report_filtered(
    db: Session,
    user_id: str,
    filter_mode: str,
    group_id: Optional[int]
):
    admin_group_ids = [
        gid for (gid,) in db.query(GroupAdmin.group_id)
                            .join(User, User.id == GroupAdmin.user_id)
                            .filter(User.telegram_id == user_id)
                            .all()
    ]
    if filter_mode == "my":
        condition = (Task.creator_id == user_id)
    elif filter_mode == "admin_all":
        if admin_group_ids:
            condition = or_(
                Task.creator_id == user_id,
                Task.group_id.in_(admin_group_ids)
            )
        else:
            condition = (Task.creator_id == user_id)
    elif filter_mode == "group":
        if not group_id:
            raise HTTPException(
                status_code=400)
        if group_id not in admin_group_ids:
            raise HTTPException(
                status_code=403,
            )
        condition = (Task.group_id == group_id)
    else:
        raise HTTPException(status_code=400)
    rows = (
        db.query(Task, User)
        .outerjoin(User, Task.creator_id == User.telegram_id)
        .filter(condition)
        .all()
    )
    result = []
    for task, user in rows:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "time_spent": task.time_spent or 0,
            "task_date": task.task_date.isoformat() if task.task_date else "",
            "creator_name": user.fio if user else "",
            "group_id": task.group_id,
            "created_at": task.created_at.isoformat() if task.created_at else "",
        })
    return result

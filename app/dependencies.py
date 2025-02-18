import json
from urllib.parse import parse_qs

from fastapi import HTTPException
from .db import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_id_from_init_data(init_data: str) -> str:
    parsed = parse_qs(init_data)
    user_id = None
    if "user" in parsed:
        try:
            user_obj = json.loads(parsed["user"][0])
            user_id = str(user_obj.get("id"))
        except Exception as ex:
            print("Error parsing initData:", ex)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid init data")
    return user_id

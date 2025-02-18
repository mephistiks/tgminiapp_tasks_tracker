from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import Base, engine
from .users.router import router as users_router
from .groups.router import router as groups_router
from .tasks.router import router as tasks_router

Base.metadata.create_all(bind=engine)


app = FastAPI()


app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")


@app.get("/")
def serve_index():
    return FileResponse("dist/index.html")


app.include_router(users_router, prefix="/api")
app.include_router(groups_router, prefix="/api/groups")
app.include_router(tasks_router, prefix="/api/tasks")

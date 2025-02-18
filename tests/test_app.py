import pytest
from httpx import ASGITransport, AsyncClient

from ..app.app import app
from ..app.db import Base


@pytest.fixture
def db_prepare():
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///db.sqlite', echo=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.usefixtures('db_prepare')
@pytest.mark.anyio
async def test_index():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200


@pytest.mark.usefixtures('db_prepare')
@pytest.mark.anyio
async def test_create_and_update_user():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        payload = {"telegram_id": "user1", "fio": "User One"}
        response = await client.post("/api/user", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "User user1 saved/updated" in data["message"]

        payload_update = {"telegram_id": "user1", "fio": "User One Updated"}
        response = await client.post("/api/user", json=payload_update)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

        response = await client.get("/api/users")
        assert response.status_code == 200
        users = response.json()
        user = next((u for u in users if u["id"] == "user1"), None)
        assert user is not None
        assert user["fio"] == "User One Updated"


@pytest.mark.usefixtures('db_prepare')
@pytest.mark.anyio
async def test_get_all_tasks():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        response = await client.get("/api/tasks/")
        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)


@pytest.mark.usefixtures('db_prepare')
@pytest.mark.anyio
async def test_create_group():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        payload = {"name": "Test Group", "init_data": 'user={"id":"user1"}'}
        response = await client.post("/api/groups/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        group_id = data["group_id"]

        # integrity error
        response = await client.post("/api/groups/", json=payload)
        assert response.status_code == 400

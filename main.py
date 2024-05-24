import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from encryption import tasagare_hash
from database import Database

app = FastAPI()

client = AsyncIOMotorClient(os.getenv("MONGO_URI", 'mongodb://localhost:27017'))
db = client.team_management


@app.middleware("*")
async def auth_middleware(request: Request, call_next):
    if request.url.path not in ["/login", "/openapi.json", "/docs", "/autocomplete"]:
        session_id = request.cookies.get("session_id")
        if not session_id:
            return Response(status_code=403)

        session = await db.sessions.find_one({"session_id": session_id})
        if not session:
            return Response(status_code=403)

        user = await db.users.find_one({"_id": session.get("user_id")})
        if not user:
            return Response(status_code=403)

        request.state.user = user

    response = await call_next(request)
    return response


database = Database(db)


class TaskAssignRequest(BaseModel):
    task_id: int
    acceptor_username: str


class TaskResponse(BaseModel):
    task_id: int
    title: str
    description: str
    ctime: int
    mtime: int
    due_date: str
    completed: bool
    created_by: str
    assigned_by: List[str]
    assigned_to: List[Dict]


class TaskCreateRequest(BaseModel):
    title: str
    description: str
    due_date: str


# FastAPI Endpoints
@app.post("/login")
async def login(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        print(e)
        return JSONResponse({"detail": "Login failed"}, 400)
    print(tasagare_hash(body['password']))
    session_id = await database.login(body['username'], tasagare_hash(body['password']))
    response = JSONResponse({"detail": "Login successful"})
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.get("/your_tasks", response_model=List[TaskResponse])
async def your_tasks(request: Request):
    username = request.state.user['username']
    tasks = await database.tasks_for(username)
    return tasks


@app.get("/assigned_by_you", response_model=List[TaskResponse])
async def assigned_by_you(request: Request):
    username = request.state.user['username']
    tasks = await database.tasks_by(username)
    return tasks


@app.get("/all_tasks")
async def all_tasks():
    return await database.tasks()


@app.post("/complete_task")
async def complete_task(task_id: int):
    await database.complete_task(task_id)
    return {"detail": "Task completed"}


@app.post("/accept_task")
async def accept_task(task_id: int, request: Request):
    username = request.state.user['username']
    await database.accept_task(task_id, username)
    return {"detail": "Task accepted"}


@app.post("/decline_task")
async def decline_task(task_id: int, reason: str, request: Request):
    username = request.state.user['username']
    await database.decline_task(task_id, username, reason)
    return {"detail": "Task declined"}


@app.post("/assign_task")
async def assign_task(request: Request, body: TaskAssignRequest):
    await database.assign_task(body.task_id, request.state.user['username'], body.acceptor_username)
    return {"detail": "Task assigned"}


@app.get("/autocomplete")
@app.post("/autocomplete")
async def autocomplete(text: str):
    usernames = await database.get_username_containing(text)
    return usernames


@app.post("/create_task")
async def create_task(request: TaskCreateRequest, request_obj: Request):
    created_by = request_obj.state.user['username']
    task_id = await database.create_task(request.title, request.description, request.due_date, created_by)
    return {"detail": "Task created", "task_id": task_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5300)

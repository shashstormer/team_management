from typing import List, Dict
import time
import uuid
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase


class Database:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def login(self, username: str, password: str) -> str:
        user = await self.db.users.find_one({"username": username, "password": password})
        if user:
            session_id = str(uuid.uuid4())
            await self.db.sessions.insert_one({
                "session_id": session_id,
                "user_id": user["_id"],
                "ctime": int(time.time()),
                "mtime": int(time.time())
            })
            return session_id
        raise HTTPException(status_code=401, detail="Invalid username or password")

    async def tasks(self):
        return await self.db.tasks.find().to_list(None)

    async def tasks_for(self, username: str) -> List[Dict]:
        tasks = await self.db.tasks.find({"assigned_to.member_username": username}).to_list(None)
        return tasks

    async def tasks_by(self, username: str) -> List[Dict]:
        tasks = await self.db.tasks.find({"assigned_by": username}).to_list(None)
        return tasks

    async def complete_task(self, task_id: int) -> None:
        result = await self.db.tasks.update_one({"task_id": task_id}, {"$set": {"completed": True}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")

    async def accept_task(self, task_id: int, username: str) -> None:
        result = await self.db.tasks.update_one(
            {"task_id": task_id, "assigned_to.member_username": username},
            {"$set": {"assigned_to.$.accepted": True}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task or user not found")

    async def decline_task(self, task_id: int, username: str, reason: str) -> None:
        result = await self.db.tasks.update_one(
            {"task_id": task_id, "assigned_to.member_username": username},
            {"$set": {"assigned_to.$.accepted": False, "assigned_to.$.reason": reason}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task or user not found")

    async def assign_task(self, task_id: int, assigner_username: str, acceptor_username: str) -> None:
        task = await self.db.tasks.find_one({"task_id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        assigner = await self.db.users.find_one({"username": assigner_username})
        acceptor = await self.db.users.find_one({"username": acceptor_username})
        if not assigner or not acceptor:
            raise HTTPException(status_code=404, detail="Assigner or acceptor not found")

        assigned_to_entry = {
            "member_username": acceptor_username,
            "assigned_time": int(time.time()),
            "accepted": None,
            "reason": "",
            "assigned_by": assigner_username
        }

        await self.db.tasks.update_one(
            {"task_id": task_id},
            {"$push": {"assigned_by": assigner_username, "assigned_to": assigned_to_entry}}
        )

    async def get_username_containing(self, text: str) -> List[str]:
        users = await self.db.users.find(
            {"$or": [
                {"username": {"$regex": text, "$options": "i"}},
                {"display_name": {"$regex": text, "$options": "i"}}
            ]}
        ).to_list(None)
        return [user['username'] for user in users]

    async def create_task(self, title: str, description: str, due_date: str, created_by: str) -> int:
        task_id = await self.db.tasks.count_documents({}) + 1
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "ctime": int(time.time()),
            "mtime": int(time.time()),
            "due_date": due_date,
            "completed": False,
            "created_by": created_by,
            "assigned_by": [],
            "assigned_to": []
        }
        await self.db.tasks.insert_one(task)
        return task_id

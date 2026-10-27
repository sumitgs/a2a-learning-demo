from pydantic import BaseModel
from typing import List, Optional

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    severity: str = "low"

class TaskListResponse(BaseModel):
    tasks: List[Task]
    total: int

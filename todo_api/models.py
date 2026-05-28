from pydantic import BaseModel
from typing import Optional

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None


class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    completed: bool = False
from fastapi import APIRouter, HTTPException
from models import TodoCreate, Todo
from database import todos, todo_id_counter

router = APIRouter()

@router.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    global todo_id_counter

    todo_id_counter += 1

    new_todo = {
        "id": todo_id_counter,
        "title": todo.title,
        "description": todo.description,
        "due_date": todo.due_date,
        "completed": False
    }

    todos[todo_id_counter] = new_todo
    return new_todo

    @router.get("/todos")
def get_todos(status: str = None):
    result = list(todos.values())

    if status == "completed":
        result = [t for t in result if t["completed"]]
    elif status == "pending":
        result = [t for t in result if not t["completed"]]

    return result


    @router.put("/todos/{todo_id}/complete")
def complete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")

    todos[todo_id]["completed"] = True
    return todos[todo_id]

    @router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")

    del todos[todo_id]
    return {"message": "Todo deleted successfully"}
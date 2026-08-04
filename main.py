from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()
connection =sqlite3.connect("tasks.db")
cursor=connection.cursor()
tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build Task API",
        "done": False
    },
    {
        "id": 3,
        "title": "Push to GitHub",
        "done": True
    }
]
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY,
    title TEXT,
    done BOOLEAN
)
""")
connection.commit()
cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:

    for task in tasks:

        cursor.execute(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            (task["id"], task["title"], task["done"])
        )

    connection.commit()



class TaskCreate(BaseModel):
    title: str
class TaskUpdate(BaseModel):
    title: str
    done: bool

@app.get("/tasks")
def task_list():

    cursor.execute("SELECT * FROM tasks")

    rows = cursor.fetchall()

    tasks = []

    for row in rows:

        tasks.append({
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        })

    return tasks

@app.get("/health")
def health():
    return {
        "status": "ok"
    }



@app.get("/tasks/{id}")
def get_task(id: int):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }



@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    new_id = len(tasks) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task
@app.put("/tasks/{id}")
def update_task(id: int, updated_task: TaskUpdate):

    for task in tasks:

        if task["id"] == id:

            if updated_task.title.strip() == "":
                raise HTTPException(
                    status_code=400,
                    detail="Title cannot be empty"
                )

            task["title"] = updated_task.title
            task["done"] = updated_task.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )
@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):

    for index, task in enumerate(tasks):

        if task["id"] == id:

            tasks.pop(index)

            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )
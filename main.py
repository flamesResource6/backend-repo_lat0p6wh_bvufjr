import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from database import db, create_document, get_documents

app = FastAPI(title="ClickUp Pro Replica API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health
@app.get("/")
def read_root():
    return {"message": "Backend running"}


# Expose schemas to the database viewer
@app.get("/schema")
def get_schema():
    from schemas import User, Workspace, Space, Folder, ListModel, Task, Comment
    return {
        "user": User.model_json_schema(),
        "workspace": Workspace.model_json_schema(),
        "space": Space.model_json_schema(),
        "folder": Folder.model_json_schema(),
        "list": ListModel.model_json_schema(),
        "task": Task.model_json_schema(),
        "comment": Comment.model_json_schema(),
    }


# Minimal endpoints for the frontend to consume
class CreateWorkspace(BaseModel):
    name: str
    description: Optional[str] = None


@app.post("/workspaces")
def create_workspace(payload: CreateWorkspace):
    from schemas import Workspace
    try:
        ws = Workspace(name=payload.name, description=payload.description)
        new_id = create_document("workspace", ws)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/workspaces")
def list_workspaces():
    try:
        items = get_documents("workspace", {}, limit=50)
        # Convert ObjectId to string
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class CreateList(BaseModel):
    name: str
    workspace_id: Optional[str] = None


@app.post("/lists")
def create_list(payload: CreateList):
    from schemas import ListModel
    try:
        lst = ListModel(name=payload.name, workspace_id=payload.workspace_id)
        new_id = create_document("listmodel", lst)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/lists")
def list_lists(workspace_id: Optional[str] = None):
    try:
        filter_q = {"workspace_id": workspace_id} if workspace_id else {}
        items = get_documents("listmodel", filter_q, limit=200)
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class CreateTask(BaseModel):
    title: str
    description: Optional[str] = None
    list_id: str


@app.post("/tasks")
def create_task(payload: CreateTask):
    from schemas import Task
    try:
        task = Task(title=payload.title, description=payload.description, list_id=payload.list_id)
        new_id = create_document("task", task)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks")
def list_tasks(list_id: Optional[str] = None):
    try:
        filter_q = {"list_id": list_id} if list_id else {}
        items = get_documents("task", filter_q, limit=500)
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Diagnostic endpoint
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

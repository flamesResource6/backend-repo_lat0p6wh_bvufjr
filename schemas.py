"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Workspace -> "workspace" collection
- List -> "list" collection
- Task -> "task" collection
- Comment -> "comment" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class User(BaseModel):
    """
    Users collection schema
    Collection name: "user"
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    is_active: bool = Field(True, description="Whether user is active")


class Workspace(BaseModel):
    """
    Workspaces collection schema
    Collection name: "workspace"
    """
    name: str = Field(..., description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    owner_id: Optional[str] = Field(None, description="Owner user id (string)")
    members: List[str] = Field(default_factory=list, description="User ids that are members")


class Space(BaseModel):
    """
    Spaces collection schema
    Collection name: "space"
    """
    name: str
    workspace_id: str = Field(..., description="Workspace id (string)")
    color: Optional[str] = None


class Folder(BaseModel):
    """
    Folders collection schema
    Collection name: "folder"
    """
    name: str
    space_id: str = Field(..., description="Space id (string)")


class ListModel(BaseModel):
    """
    Lists collection schema
    Collection name: "listmodel" (use alias "list" via routes)
    """
    name: str
    workspace_id: Optional[str] = Field(None, description="Workspace id (string)")
    space_id: Optional[str] = Field(None, description="Space id (string)")
    folder_id: Optional[str] = Field(None, description="Folder id (string)")
    color: Optional[str] = None


class Task(BaseModel):
    """
    Tasks collection schema
    Collection name: "task"
    """
    title: str
    description: Optional[str] = None
    list_id: str = Field(..., description="List id (string)")
    status: Literal["todo", "in_progress", "review", "done"] = Field("todo")
    priority: Literal["none", "low", "medium", "high", "urgent"] = Field("none")
    assignees: List[str] = Field(default_factory=list, description="User ids")
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)


class Comment(BaseModel):
    """
    Comments collection schema
    Collection name: "comment"
    """
    task_id: str = Field(..., description="Related task id (string)")
    author_id: Optional[str] = None
    body: str


# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!

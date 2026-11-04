from datetime import date
from enum import Enum
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(str, Enum):
    planning = "planning"
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    client_name: str = Field(min_length=1, max_length=120)
    site_address: str = Field(min_length=1, max_length=300)
    project_type: str = Field(min_length=1, max_length=80)
    status: ProjectStatus = ProjectStatus.planning
    budget: float = Field(ge=0)
    start_date: date | None = None
    target_completion_date: date | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    client_name: str | None = Field(default=None, min_length=1, max_length=120)
    site_address: str | None = Field(default=None, min_length=1, max_length=300)
    project_type: str | None = Field(default=None, min_length=1, max_length=80)
    status: ProjectStatus | None = None
    budget: float | None = Field(default=None, ge=0)
    start_date: date | None = None
    target_completion_date: date | None = None


class Project(ProjectInput):
    model_config = ConfigDict(from_attributes=True)

    id: str


app = FastAPI(title="RECC Constructions API", version="1.0.0")
projects: dict[str, Project] = {}
projects_lock = Lock()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project_input: ProjectInput) -> Project:
    project = Project(id=str(uuid4()), **project_input.model_dump())
    with projects_lock:
        projects[project.id] = project
    return project


@app.get("/api/v1/projects", response_model=list[Project])
def list_projects() -> list[Project]:
    with projects_lock:
        return list(projects.values())


@app.get("/api/v1/projects/{project_id}", response_model=Project)
def get_project(project_id: str) -> Project:
    with projects_lock:
        project = projects.get(project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@app.patch("/api/v1/projects/{project_id}", response_model=Project)
def update_project(project_id: str, project_update: ProjectUpdate) -> Project:
    changes = project_update.model_dump(exclude_unset=True)
    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Project fields cannot be set to null",
        )

    with projects_lock:
        project = projects.get(project_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        updated_project = project.model_copy(update=changes)
        projects[project_id] = updated_project
    return updated_project


@app.delete("/api/v1/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str) -> Response:
    with projects_lock:
        if projects.pop(project_id, None) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
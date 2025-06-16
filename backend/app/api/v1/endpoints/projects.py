from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.project import Project as ProjectModel
from ....models.task import Task as TaskModel
from ....schemas.project import Project, ProjectCreate, ProjectUpdate
from ....schemas.user import UserInDB

router = APIRouter()

def get_project(db: Session, project_id: int, user_id: int):
    return db.query(ProjectModel).filter(
        ProjectModel.id == project_id,
        ProjectModel.owner_id == user_id
    ).first()

@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    projects = db.query(ProjectModel).filter(
        ProjectModel.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return projects

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        db_project = ProjectModel(
            **project.model_dump(),
            owner_id=current_user.id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

@router.get("/{project_id}", response_model=Project)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    db_project = get_project(db, project_id, current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    db_project = get_project(db, project_id, current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        update_data = project.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    db_project = get_project(db, project_id, current_user.id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        db.query(TaskModel).filter(TaskModel.project_id == project_id).delete()
        
        db.delete(db_project)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

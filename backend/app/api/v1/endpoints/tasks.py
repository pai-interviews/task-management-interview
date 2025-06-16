from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ....core.database import get_db
from ....core.security import get_current_user
from ....models.task import Task as TaskModel, TaskStatus
from ....models.project import Project as ProjectModel
from ....models.comment import Comment as CommentModel
from ....models.user import User as UserModel
from ....schemas.task import Task, TaskCreate, TaskUpdate
from ....schemas.comment import Comment, CommentCreate
from ....schemas.user import UserInDB

router = APIRouter()

def get_task(db: Session, task_id: int, user_id: int):
    return db.query(TaskModel).join(
        ProjectModel,
        TaskModel.project_id == ProjectModel.id
    ).filter(
        TaskModel.id == task_id,
        ProjectModel.owner_id == user_id
    ).first()

@router.get("/", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    project_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    limit = min(limit, 1000)
    
    query = db.query(TaskModel).join(
        ProjectModel,
        TaskModel.project_id == ProjectModel.id
    ).filter(ProjectModel.owner_id == current_user.id)
    
    if status:
        status_lower = status.lower()
        if status_lower not in [s.value for s in TaskStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in TaskStatus])}"
            )
        query = query.filter(TaskModel.status == status_lower)
    if project_id is not None:
        project = db.query(ProjectModel).filter(
            ProjectModel.id == project_id,
            ProjectModel.owner_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        query = query.filter(TaskModel.project_id == project_id)
    if assignee_id is not None:
        assignee = db.query(UserModel).filter(UserModel.id == assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee not found"
            )
        query = query.filter(TaskModel.assignee_id == assignee_id)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    try:
        if not task.title or not task.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title and project_id are required"
            )
        
        project = db.query(ProjectModel).filter(
            ProjectModel.id == task.project_id,
            ProjectModel.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        
        # Validate assignee exists if provided
        if task.assignee_id is not None:
            assignee = db.query(UserModel).filter(UserModel.id == task.assignee_id).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee not found"
                )

        # Create the task
        task_data = task.model_dump()
        # Add owner_id which is the actual field in the model
        task_data['owner_id'] = current_user.id
        
        db_task = TaskModel(**task_data)
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return db_task
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )

@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    task = get_task(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    db_task = get_task(db, task_id, current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.model_dump(exclude_unset=True)
    
    # Verify project exists and is owned by user if project_id is being updated
    if 'project_id' in update_data:
        project = db.query(ProjectModel).filter(
            ProjectModel.id == update_data['project_id'],
            ProjectModel.owner_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Verify assignee exists if assignee_id is being updated
    if 'assignee_id' in update_data and update_data['assignee_id'] is not None:
        assignee = db.query(UserModel).filter(UserModel.id == update_data['assignee_id']).first()
        if not assignee:
            raise HTTPException(status_code=400, detail="Assignee not found")
    
    try:
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    db_task = get_task(db, task_id, current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        db.delete(db_task)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )

@router.post("/{task_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    task = get_task(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        db_comment = CommentModel(
            **comment.model_dump(),
            task_id=task_id,
            user_id=current_user.id
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comment"
        )

@router.get("/{task_id}/comments", response_model=List[Comment])
def read_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    task = get_task(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return db.query(CommentModel).filter(
        CommentModel.task_id == task_id
    ).all()

from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Union
from datetime import datetime
from ..models.task import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Union[TaskPriority, int] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    project_id: int
    assignee_id: Optional[int] = None
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if isinstance(v, int):
            priority_map = {1: TaskPriority.LOW, 2: TaskPriority.MEDIUM, 3: TaskPriority.HIGH}
            return priority_map.get(v, TaskPriority.MEDIUM)
        return v

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Union[TaskPriority, int]] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v is None:
            return v
        if isinstance(v, int):
            # Convert integer to TaskPriority enum
            priority_map = {1: TaskPriority.LOW, 2: TaskPriority.MEDIUM, 3: TaskPriority.HIGH}
            return priority_map.get(v, TaskPriority.MEDIUM)
        return v

class TaskInDBBase(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Task(TaskInDBBase):
    """Task model for API responses"""

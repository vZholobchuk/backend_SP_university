from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    todo = "До виконання"
    in_progress = "В процесі"
    done = "Виконано"

class TaskPriority(str, Enum):
    low = "Низький"
    medium = "Середній"
    high = "Високий"

class TaskBase(BaseModel):
    title: str = Field(..., example="Лабораторна робота 1")
    description: Optional[str] = Field(None, example="Описати предметну область")
    status: TaskStatus = Field(default=TaskStatus.todo)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    deadline: Optional[datetime] = None
    subject: str = Field(..., example="Проєктування програмних продуктів")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None
    subject: Optional[str] = None

class TaskResponse(TaskBase):
    id: str = Field(..., alias="_id")
    user_id: str = Field(..., description="ID користувача, якому належить завдання")

    class Config:
        populate_by_name = True

class ScheduleType(str, Enum):
    lecture = "Лекція"
    practice = "Практика"
    consultation = "Консультація"

class ScheduleBase(BaseModel):
    subject: str = Field(..., example="Проєктування програмних продуктів")
    type: str = Field(default="Лекція")
    start_time: datetime
    end_time: datetime
    room: Optional[str] = Field(None, example="Аудиторія 401")
    teacher: Optional[str] = Field(None, example="Іванов І.І.")
    subgroup: Optional[str] = Field(None, example="1 підгрупа")
    lesson_number: Optional[str] = Field(None, example="1")
    link: Optional[str] = Field(None, example="https://meet.google.com/...")

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleResponse(ScheduleBase):
    id: str = Field(..., alias="_id")
    user_id: str = Field(..., description="ID користувача, якому належить розклад")

    class Config:
        populate_by_name = True

class UserBase(BaseModel):
    email: str = Field(..., example="student@example.com")
    name: str = Field(..., example="Іван Іванов")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="password123")

class UserInDB(UserBase):
    hashed_password: str

class UserResponse(UserBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class EmployeeRole(str, Enum):
    SELLER = "SELLER"
    ADMIN = "ADMIN"


class LoginDto(BaseModel):
    email: EmailStr = Field(..., description="Email сотрудника")
    password: str = Field(..., min_length=1, description="Пароль")


class CreateEmployeeDto(BaseModel):
    role: EmployeeRole = Field(..., description="Роль сотрудника")
    name: str = Field(..., min_length=1, description="Имя")
    lastname: str = Field(..., min_length=1, description="Фамилия")
    patronymic: Optional[str] = Field(None, description="Отчество")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=1, description="Пароль")


class UpdateEmployeeDto(BaseModel):
    role: Optional[EmployeeRole] = None
    name: Optional[str] = None
    lastname: Optional[str] = None
    patronymic: Optional[str] = None
    email: Optional[EmailStr] = None


class EmployeeResponse(BaseModel):
    id: str
    role: str
    name: str
    lastname: str
    patronymic: Optional[str]
    email: str

    class Config:
        from_attributes = True


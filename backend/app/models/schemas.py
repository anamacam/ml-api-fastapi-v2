"""
Esquemas Pydantic para la API de usuarios.

Define los modelos para la creación, actualización y
visualización de datos de usuario a través de la API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from .user import UserRole, UserStatus

# --- Esquemas Base ---

class UserBase(BaseModel):
    """Esquema base para un usuario con campos comunes."""
    email: EmailStr = Field(..., description="Correo electrónico del usuario.")
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único.")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del usuario.")
    
    class Config:
        orm_mode = True

# --- Esquemas para Creación y Actualización ---

class UserCreate(UserBase):
    """Esquema para la creación de un nuevo usuario."""
    password: str = Field(..., min_length=8, description="Contraseña del usuario.")

class UserUpdate(BaseModel):
    """Esquema para actualizar un usuario existente."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# --- Esquemas para Respuestas de la API ---

class UserInDB(UserBase):
    """Esquema que representa un usuario tal como está en la BD (con ID)."""
    id: int = Field(..., description="ID único del usuario.")
    hashed_password: str = Field(..., description="Contraseña hasheada del usuario.")
    is_active: bool = Field(..., description="Si el usuario está activo.")
    is_superuser: bool = Field(..., description="Si el usuario es superusuario.")
    status: UserStatus = Field(..., description="Estado actual del usuario.")
    created_at: datetime = Field(..., description="Fecha de creación del usuario.")
    
class UserPublic(BaseModel):
    """Esquema para la información pública de un usuario."""
    id: int
    username: str
    full_name: Optional[str]
    
    class Config:
        orm_mode = True



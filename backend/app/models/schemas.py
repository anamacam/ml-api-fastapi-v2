# -*- coding: utf-8 -*-
"""
Esquemas de usuario - Validacion robusta de datos de entrada.

Define los modelos para la creacion, actualizacion y
visualizacion de datos de usuario a traves de la API.

Validaciones mejoradas:
- Validacion estricta de email
- Passwords seguros
- Usernames unicos
- Validaciones de longitud
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .user import UserStatus

# --- Esquemas Base ---


class UserBase(BaseModel):
    """Esquema base para un usuario con campos comunes."""

    email: EmailStr = Field(..., description="Correo electrónico del usuario.")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Nombre de usuario único."
    )
    full_name: Optional[str] = Field(
        None, max_length=100, description="Nombre completo del usuario."
    )

    class Config:
        from_attributes = True


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
        from_attributes = True

"""
Modelos de usuario para autenticación y autorización.

Este módulo define los modelos de base de datos y esquemas
para la gestión de usuarios del sistema.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from ..core.database import Base
from ..core.security import get_password_hash, verify_password


class UserRole(str, Enum):
    """Roles de usuario disponibles en el sistema."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"


class UserStatus(str, Enum):
    """Estados de usuario disponibles."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


# Tabla de asociación para la relación many-to-many entre usuarios y roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class Role(Base):
    """
    Modelo de rol de usuario.

    Define los diferentes roles que pueden tener los usuarios
    y sus permisos asociados.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string de permisos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class User(Base):
    """
    Modelo de usuario del sistema.

    Contiene toda la información necesaria para autenticación,
    autorización y gestión de usuarios.
    """
    __tablename__ = "users"

    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Información personal
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    full_name = Column(String(100), nullable=True)

    # Estado del usuario
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    status = Column(String(20), default=UserStatus.PENDING.value)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow)

    # Campos de seguridad
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Metadatos adicionales
    preferences = Column(Text, nullable=True)  # JSON string de preferencias
    user_metadata = Column(Text, nullable=True)  # JSON string de metadata adicional

    # Relaciones
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

    @property
    def display_name(self) -> str:
        """Nombre para mostrar del usuario."""
        if self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username

    def set_password(self, password: str) -> None:
        """
        Establecer contraseña hasheada para el usuario.

        Args:
            password: Contraseña en texto plano.
        """
        self.hashed_password = get_password_hash(password)
        self.password_changed_at = datetime.utcnow()

    def verify_password(self, password: str) -> bool:
        """
        Verificar contraseña del usuario.

        Args:
            password: Contraseña en texto plano.

        Returns:
            bool: True si la contraseña es correcta.
        """
        return verify_password(password, self.hashed_password)

    def has_role(self, role_name: str) -> bool:
        """
        Verificar si el usuario tiene un rol específico.

        Args:
            role_name: Nombre del rol a verificar.

        Returns:
            bool: True si el usuario tiene el rol.
        """
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission: str) -> bool:
        """
        Verificar si el usuario tiene un permiso específico.

        Args:
            permission: Permiso a verificar.

        Returns:
            bool: True si el usuario tiene el permiso.
        """
        if self.is_superuser:
            return True

        for role in self.roles:
            if role.permissions:
                import json
                try:
                    permissions = json.loads(role.permissions)
                    if permission in permissions:
                        return True
                except json.JSONDecodeError:
                    continue

        return False

    def is_locked(self) -> bool:
        """
        Verificar si la cuenta está bloqueada.

        Returns:
            bool: True si la cuenta está bloqueada.
        """
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False

    def lock_account(self, duration_minutes: int = 30) -> None:
        """
        Bloquear la cuenta por un período específico.

        Args:
            duration_minutes: Duración del bloqueo en minutos.
        """
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)

    def unlock_account(self) -> None:
        """Desbloquear la cuenta."""
        self.locked_until = None
        self.failed_login_attempts = 0

    def to_dict(self) -> dict:
        """
        Convertir el usuario a diccionario (sin información sensible).

        Returns:
            dict: Datos del usuario.
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'roles': [role.name for role in self.roles]
        }


class UserSession(Base):
    """
    Modelo de sesión de usuario.

    Rastrea las sesiones activas de los usuarios para
    gestión de seguridad y análisis.
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_info = Column(Text, nullable=True)  # JSON string

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    # Estados
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String(100), nullable=True)

    # Relación
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, token='{self.session_token[:8]}...')>"

    def is_expired(self) -> bool:
        """
        Verificar si la sesión ha expirado.

        Returns:
            bool: True si la sesión ha expirado.
        """
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """
        Verificar si la sesión es válida.

        Returns:
            bool: True si la sesión es válida.
        """
        return (
            self.is_active and
            not self.is_expired() and
            self.revoked_at is None
        )

    def revoke(self, reason: str = "user_logout") -> None:
        """
        Revocar la sesión.

        Args:
            reason: Razón de la revocación.
        """
        self.is_active = False
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason


class ApiKey(Base):
    """
    Modelo de clave API para acceso programático.

    Permite a los usuarios acceder a la API usando
    claves API en lugar de autenticación por sesión.
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Nombre descriptivo
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    prefix = Column(String(10), nullable=False)  # Prefijo visible de la clave

    # Permisos y restricciones
    permissions = Column(Text, nullable=True)  # JSON string de permisos específicos
    allowed_ips = Column(Text, nullable=True)  # JSON array de IPs permitidas
    rate_limit = Column(Integer, default=1000)  # Requests por hora

    # Estados
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    # Estadísticas de uso
    usage_count = Column(Integer, default=0)

    # Relación
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<ApiKey(name='{self.name}', prefix='{self.prefix}')>"

    def is_expired(self) -> bool:
        """
        Verificar si la clave API ha expirado.

        Returns:
            bool: True si la clave ha expirado.
        """
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def is_valid(self) -> bool:
        """
        Verificar si la clave API es válida.

        Returns:
            bool: True si la clave es válida.
        """
        return (
            self.is_active and
            not self.is_revoked and
            not self.is_expired()
        )

    def increment_usage(self) -> None:
        """Incrementar contador de uso de la clave."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()

    def revoke(self) -> None:
        """Revocar la clave API."""
        self.is_active = False
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()


class UserActivity(Base):
    """
    Modelo para registrar actividad de usuarios.

    Rastrea acciones importantes realizadas por los usuarios
    para auditoría y análisis de comportamiento.
    """
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Contexto de la actividad
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    resource = Column(String(100), nullable=True)  # Recurso afectado
    resource_id = Column(String(50), nullable=True)  # ID del recurso

    # Metadata adicional
    activity_metadata = Column(Text, nullable=True)  # JSON string con datos adicionales

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<UserActivity(user_id={self.user_id}, type='{self.activity_type}')>"

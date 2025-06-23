"""
Repository pattern - Extraído de database.py

REFACTORED: Separando repository pattern en módulo independiente
- BaseRepository genérico
- Operaciones CRUD type-safe
- Validaciones de datos
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Base para modelos SQLAlchemy
class Base(DeclarativeBase):
    """Base class para todos los modelos SQLAlchemy"""
    id: Union[int, str]  # Type hint para el atributo id común


# Type hints para Generic Repository
ModelType = TypeVar("ModelType", bound=Base)

# Configurar logger específico para el módulo de base de datos
logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType]):
    """
    🗂️ Repository pattern genérico type-safe

    Repository base con operaciones CRUD genéricas:
    - Create, Read, Update, Delete
    - Validaciones automáticas
    - Manejo de errores consistente
    - Type safety con generics
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Inicializar repository

        Args:
            model: Clase del modelo SQLAlchemy
            session: Sesión de base de datos
        """
        self.model = model
        self.session = session

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Crear nueva entidad

        Args:
            data: Datos para crear la entidad

        Returns:
            ModelType: Entidad creada

        Raises:
            ValueError: Si los datos son inválidos
        """
        self._validate_create_data(data)
        
        try:
            entity = self.model(**data)
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            logger.debug("Entidad creada: %s", entity)
            return entity
        except Exception as e:
            logger.error("Error creando entidad: %s", e)
            raise

    async def get_by_id(self, entity_id: Union[int, str]) -> Optional[ModelType]:
        """
        Obtener entidad por ID

        Args:
            entity_id: ID de la entidad

        Returns:
            Optional[ModelType]: Entidad encontrada o None
        """
        try:
            # Usar getattr para acceder al atributo id de forma segura
            id_column = getattr(self.model, 'id', None)
            if id_column is None:
                logger.error("Modelo %s no tiene atributo 'id'", self.model.__name__)
                return None
                
            result = await self.session.execute(
                select(self.model).where(id_column == entity_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error obteniendo entidad por ID %s: %s", entity_id, e)
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtener todas las entidades con paginación

        Args:
            skip: Número de entidades a saltar
            limit: Número máximo de entidades a retornar

        Returns:
            List[ModelType]: Lista de entidades
        """
        try:
            result = await self.session.execute(
                select(self.model).offset(skip).limit(limit)
            )
            # Convertir Sequence a List para cumplir con el type hint
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error obteniendo entidades: %s", e)
            return []

    async def update(
        self, entity_id: Union[int, str], data: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Actualizar entidad

        Args:
            entity_id: ID de la entidad
            data: Datos a actualizar

        Returns:
            Optional[ModelType]: Entidad actualizada o None
        """
        self._validate_update_data(data)
        
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None

            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            await self.session.flush()
            await self.session.refresh(entity)
            logger.debug("Entidad actualizada: %s", entity)
            return entity
        except Exception as e:
            logger.error("Error actualizando entidad %s: %s", entity_id, e)
            return None

    async def delete(self, entity_id: Union[int, str]) -> bool:
        """
        Eliminar entidad

        Args:
            entity_id: ID de la entidad

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            entity = await self.get_by_id(entity_id)
            if not entity:
                return False

            await self.session.delete(entity)
            await self.session.flush()
            logger.debug("Entidad eliminada: %s", entity_id)
            return True
        except Exception as e:
            logger.error("Error eliminando entidad %s: %s", entity_id, e)
            return False

    async def count(self) -> int:
        """
        Contar total de entidades

        Returns:
            int: Número total de entidades
        """
        try:
            result = await self.session.execute(select(self.model))
            return len(result.scalars().all())
        except Exception as e:
            logger.error("Error contando entidades: %s", e)
            return 0

    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validar datos para crear entidad"""
        if not data:
            raise ValueError("Los datos no pueden estar vacíos")

    def _validate_update_data(self, data: Dict[str, Any]) -> None:
        """Validar datos para actualizar entidad"""
        if not data:
            raise ValueError("Los datos de actualización no pueden estar vacíos") 
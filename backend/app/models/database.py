from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import Generator

from app.core.config import settings

# Crear engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para obtener DB session
def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos de base de datos
class MLModel(Base):
    """Modelo para almacenar información de modelos ML"""
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # sklearn, tensorflow, pytorch, etc.
    version = Column(String(20), nullable=False, default="1.0.0")
    description = Column(Text)
    file_path = Column(String(500), nullable=False)
    input_schema = Column(Text)  # JSON schema
    output_schema = Column(Text)  # JSON schema
    status = Column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE, TRAINING
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Métricas del modelo
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)

class Prediction(Base):
    """Modelo para almacenar predicciones"""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    input_data = Column(Text, nullable=False)  # JSON
    output_data = Column(Text)  # JSON
    status = Column(String(20), default="PROCESSING")  # PROCESSING, COMPLETED, FAILED
    error_message = Column(Text)
    processing_time = Column(Float)  # segundos
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class UploadedFile(Base):
    """Modelo para archivos subidos"""
    __tablename__ = "uploaded_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(20), nullable=False)  # model, dataset, other
    mime_type = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# Crear todas las tablas
def create_tables():
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine) 
import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

def setup_logging():
    """Configurar sistema de logging"""
    
    # Remover handlers por defecto de loguru
    logger.remove()
    
    # Configurar formato
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_file),
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=True
    )
    
    # Interceptar logs de otros loggers
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where record originated
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # Configurar loggers de terceros
    loggers_to_intercept = [
        "uvicorn",
        "uvicorn.access", 
        "fastapi",
        "sqlalchemy.engine",
        "alembic",
    ]
    
    for logger_name in loggers_to_intercept:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]
        logging.getLogger(logger_name).setLevel(logging.INFO)
    
    logger.info("🚀 Sistema de logging configurado correctamente") 
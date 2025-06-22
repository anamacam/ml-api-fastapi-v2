import asyncio
import logging
import sys
from pathlib import Path

import asyncpg
from app.core.database import Base, DatabaseConfig, DatabaseManager

# Añadir el directorio raíz del proyecto al sys.path
# para que los imports de la app funcionen correctamente
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_test_database():
    """Configura la base de datos de prueba en la VPS"""
    try:
        # Conectar a postgres para crear la base de datos de prueba
        conn = await asyncpg.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port=5432,
            database="postgres",
        )

        # Crear base de datos de prueba si no existe
        await conn.execute(
            """
            DROP DATABASE IF EXISTS ml_api_test;
            CREATE DATABASE ml_api_test;
        """
        )

        logger.info("Base de datos de prueba creada exitosamente")

        # Cerrar conexión a postgres
        await conn.close()

        # Configurar la nueva base de datos de prueba
        test_config = DatabaseConfig(
            database_url=(
                "postgresql+asyncpg://postgres:postgres@localhost:5432/" "ml_api_test"
            ),
            echo=True,
        )

        # Inicializar el manager con la nueva base de datos
        manager = DatabaseManager(test_config)
        await manager.initialize()

        # Asegurarnos de que el engine se ha inicializado
        if manager.engine is None:
            raise RuntimeError(
                "El engine de la base de datos no se inicializó correctamente."
            )

        # Crear las tablas necesarias
        async with manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Tablas creadas exitosamente en la base de datos de prueba")

        # Cerrar la conexión
        await manager.cleanup()

    except Exception as e:
        logger.error(f"Error al configurar la base de datos de prueba: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(setup_test_database())

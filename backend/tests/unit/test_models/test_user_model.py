"""
Tests unitarios para el modelo de usuario.

Este módulo contiene tests que verifican el funcionamiento correcto
del modelo de usuario, incluyendo validación, autenticación y
métodos de utilidad.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserStatus
from app.models.schemas import UserCreate, UserUpdate, UserInDB


class TestUserModel:
    """Tests para el modelo de usuario."""

    @pytest.fixture
    def user_data(self, sample_user_data):
        """
        Fixture que proporciona datos de usuario válidos.

        Args:
            sample_user_data: Datos de usuario de ejemplo

        Returns:
            dict: Datos de usuario para tests
        """
        return sample_user_data

    @pytest.fixture
    def user_instance(self, user_data):
        """
        Fixture que proporciona una instancia del modelo User.

        Args:
            user_data: Datos de usuario

        Returns:
            User: Instancia del modelo User
        """
        return User(**user_data)

    @pytest.mark.unit
    def test_user_creation_success(self, user_data):
        """
        Test que verifica la creación exitosa de un usuario.

        Args:
            user_data: Datos de usuario válidos
        """
        # Arrange & Act
        user = User(**user_data)

        # Assert
        assert user.id == user_data["id"]
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.full_name == user_data["full_name"]
        assert user.is_active == user_data["is_active"]
        assert user.is_superuser == user_data["is_superuser"]

    @pytest.mark.unit
    def test_user_email_validation(self):
        """
        Test que verifica la validación del email del usuario.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                id=1,
                email="invalid-email",  # Email inválido
                username="testuser",
                full_name="Test User",
                is_active=True,
                is_superuser=False,
            )

    @pytest.mark.unit
    def test_user_username_validation(self):
        """
        Test que verifica la validación del username del usuario.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            User(
                id=1,
                email="test@example.com",
                username="ab",  # Username muy corto
                full_name="Test User",
                is_active=True,
                is_superuser=False,
            )

    @pytest.mark.unit
    def test_user_str_representation(self, user_instance):
        """
        Test que verifica la representación string del usuario.

        Args:
            user_instance: Instancia del modelo User
        """
        # Act
        str_repr = str(user_instance)

        # Assert
        assert user_instance.username in str_repr
        assert user_instance.email in str_repr

    @pytest.mark.unit
    def test_user_repr_representation(self, user_instance):
        """
        Test que verifica la representación repr del usuario.

        Args:
            user_instance: Instancia del modelo User
        """
        # Act
        repr_str = repr(user_instance)

        # Assert
        assert "User" in repr_str
        assert str(user_instance.id) in repr_str
        assert user_instance.username in repr_str

    @pytest.mark.unit
    def test_user_is_active_property(self, user_instance):
        """
        Test que verifica la propiedad is_active del usuario.

        Args:
            user_instance: Instancia del modelo User
        """
        # Assert
        assert isinstance(user_instance.is_active, bool)
        assert user_instance.is_active is True

    @pytest.mark.unit
    def test_user_is_superuser_property(self, user_instance):
        """
        Test que verifica la propiedad is_superuser del usuario.

        Args:
            user_instance: Instancia del modelo User
        """
        # Assert
        assert isinstance(user_instance.is_superuser, bool)
        assert user_instance.is_superuser is False

    @pytest.mark.unit
    def test_user_has_permission_superuser(self):
        """
        Test que verifica que un superusuario tiene todos los permisos.
        """
        # Arrange
        superuser = User(
            id=1,
            email="admin@example.com",
            username="admin",
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
        )

        # Act & Assert
        assert superuser.has_permission("any_permission") is True
        assert superuser.has_permission("admin_only") is True

    @pytest.mark.unit
    def test_user_has_permission_regular_user(self, user_instance):
        """
        Test que verifica los permisos de un usuario regular.

        Args:
            user_instance: Instancia del modelo User
        """
        # Act & Assert
        assert user_instance.has_permission("read") is True
        assert user_instance.has_permission("admin_only") is False

    @pytest.mark.unit
    def test_user_can_make_prediction_active_user(self, user_instance):
        """
        Test que verifica que un usuario activo puede hacer predicciones.

        Args:
            user_instance: Instancia del modelo User
        """
        # Act & Assert
        assert user_instance.can_make_prediction() is True

    @pytest.mark.unit
    def test_user_can_make_prediction_inactive_user(self):
        """
        Test que verifica que un usuario inactivo no puede hacer predicciones.
        """
        # Arrange
        inactive_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=False,
            is_superuser=False,
        )

        # Act & Assert
        assert inactive_user.can_make_prediction() is False

    @pytest.mark.unit
    def test_user_get_display_name_with_full_name(self, user_instance):
        """
        Test que verifica get_display_name cuando hay full_name.

        Args:
            user_instance: Instancia del modelo User
        """
        # Act
        display_name = user_instance.get_display_name()

        # Assert
        assert display_name == user_instance.full_name

    @pytest.mark.unit
    def test_user_get_display_name_without_full_name(self):
        """
        Test que verifica get_display_name cuando no hay full_name.
        """
        # Arrange
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            full_name=None,
            is_active=True,
            is_superuser=False,
        )

        # Act
        display_name = user.get_display_name()

        # Assert
        assert display_name == user.username


@pytest.mark.unit
class TestUserCreate:
    """Tests para el modelo UserCreate."""

    def test_user_create_success(self):
        """
        Test que verifica la creación exitosa de UserCreate.
        """
        # Arrange & Act
        user_create = UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="secure_password123",
        )

        # Assert
        assert user_create.email == "test@example.com"
        assert user_create.username == "testuser"
        assert user_create.full_name == "Test User"
        assert user_create.password == "secure_password123"

    def test_user_create_password_validation(self):
        """
        Test que verifica la validación de contraseña en UserCreate.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Password must be at least 8 characters"):
            UserCreate(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                password="short",  # Contraseña muy corta
            )


@pytest.mark.unit
class TestUserUpdate:
    """Tests para el modelo UserUpdate."""

    def test_user_update_partial_update(self):
        """
        Test que verifica la actualización parcial con UserUpdate.
        """
        # Arrange & Act
        user_update = UserUpdate(
            email="newemail@example.com",
            full_name="New Full Name"
            # username y password opcionales
        )

        # Assert
        assert user_update.email == "newemail@example.com"
        assert user_update.full_name == "New Full Name"
        assert user_update.username is None
        assert user_update.password is None

    def test_user_update_all_fields(self):
        """
        Test que verifica la actualización de todos los campos con UserUpdate.
        """
        # Arrange & Act
        user_update = UserUpdate(
            email="updated@example.com",
            username="updateduser",
            full_name="Updated User",
            password="new_secure_password123",
        )

        # Assert
        assert user_update.email == "updated@example.com"
        assert user_update.username == "updateduser"
        assert user_update.full_name == "Updated User"
        assert user_update.password == "new_secure_password123"

    def test_user_update_empty_update(self):
        """
        Test que verifica una actualización vacía con UserUpdate.
        """
        # Arrange & Act
        user_update = UserUpdate()

        # Assert
        assert user_update.email is None
        assert user_update.username is None
        assert user_update.full_name is None
        assert user_update.password is None


@pytest.mark.unit
class TestUserInDB:
    """Tests para el modelo UserInDB."""

    def test_user_in_db_with_hashed_password(self, sample_user_data):
        """
        Test que verifica UserInDB con contraseña hasheada.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        hashed_password = "$2b$12$hashedpassword"
        sample_user_data["hashed_password"] = hashed_password

        # Act
        user_in_db = UserInDB(**sample_user_data)

        # Assert
        assert user_in_db.hashed_password == hashed_password
        assert hasattr(user_in_db, "id")
        assert hasattr(user_in_db, "email")
        assert hasattr(user_in_db, "username")

    def test_user_in_db_verify_password_success(self, sample_user_data):
        """
        Test que verifica la verificación exitosa de contraseña.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        sample_user_data["hashed_password"] = "$2b$12$hashedpassword"
        user_in_db = UserInDB(**sample_user_data)

        # Act
        result = user_in_db.verify_password("correct_password")

        # Assert
        assert result is True

    def test_user_in_db_verify_password_failure(self, sample_user_data):
        """
        Test que verifica la verificación fallida de contraseña.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        sample_user_data["hashed_password"] = "$2b$12$hashedpassword"
        user_in_db = UserInDB(**sample_user_data)

        # Act
        result = user_in_db.verify_password("wrong_password")

        # Assert
        assert result is False

    def test_user_in_db_inheritance(self, sample_user_data):
        """
        Test que verifica que UserInDB hereda de User correctamente.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        sample_user_data["hashed_password"] = "$2b$12$hashedpassword"

        # Act
        user_in_db = UserInDB(**sample_user_data)

        # Assert
        assert isinstance(user_in_db, User)
        assert hasattr(user_in_db, "has_permission")
        assert hasattr(user_in_db, "can_make_prediction")
        assert hasattr(user_in_db, "get_display_name")

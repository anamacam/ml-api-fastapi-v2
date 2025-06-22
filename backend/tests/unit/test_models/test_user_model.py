"""
Tests unitarios para el modelo de usuario.

Este módulo contiene tests que verifican el funcionamiento correcto
del modelo de usuario, incluyendo validación, autenticación y
métodos de utilidad.
"""

import pytest
from app.core.security import get_password_hash, verify_password
from app.models.schemas import UserCreate, UserInDB, UserUpdate
from app.models.user import User


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
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str

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
        # Un usuario regular sin roles específicos no debería tener permisos
        assert user_instance.has_permission("read") is False

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
        display_name = user_instance.display_name

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
        display_name = user.display_name

        # Assert
        assert display_name == user.username


@pytest.mark.unit
class TestUserCreate:
    """Tests para el esquema UserCreate."""

    def test_user_create_success(self):
        """
        Test que verifica la creación exitosa con UserCreate.
        """
        # Arrange
        user_data = {
            "email": "create@example.com",
            "username": "createuser",
            "full_name": "Create User",
            "password": "strong_password_123",
        }

        # Act
        user_create = UserCreate(**user_data)

        # Assert
        assert user_create.email == user_data["email"]
        assert user_create.username == user_data["username"]
        assert user_create.full_name == user_data["full_name"]
        assert user_create.password == user_data["password"]

    def test_user_create_password_validation(self):
        """
        Test que verifica la validación de contraseña en UserCreate.
        """
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="String should have at least 8 characters"
        ):
            UserCreate(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                password="short",  # Contraseña muy corta
            )


@pytest.mark.unit
class TestUserUpdate:
    """Tests para el esquema UserUpdate."""

    def test_user_update_partial_update(self):
        """
        Test que verifica una actualización parcial con UserUpdate.
        """
        # Arrange
        update_data = {"full_name": "Updated Name"}

        # Act
        user_update = UserUpdate(**update_data)

        # Assert
        assert user_update.full_name == "Updated Name"
        assert user_update.email is None  # Los otros campos deben ser None

    def test_user_update_all_fields(self):
        """
        Test que verifica una actualización de todos los campos con UserUpdate.
        """
        # Arrange
        update_data = {
            "email": "update@example.com",
            "full_name": "Full Updated Name",
            "password": "new_strong_password",
        }

        # Act
        user_update = UserUpdate(**update_data)

        # Assert
        assert user_update.email == update_data["email"]
        assert user_update.full_name == update_data["full_name"]
        assert user_update.password == update_data["password"]

    def test_user_update_empty_update(self):
        """
        Test que verifica que una actualización vacía es válida.
        """
        # Arrange
        update_data = {}

        # Act
        user_update = UserUpdate(**update_data)

        # Assert
        assert user_update.dict(exclude_unset=True) == {}


@pytest.mark.unit
class TestUserInDB:
    """Tests para el esquema UserInDB."""

    def test_user_in_db_with_hashed_password(self, sample_user_data):
        """
        Test que verifica UserInDB con contraseña hasheada.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        hashed_password = get_password_hash("strong_password")
        sample_user_data["hashed_password"] = hashed_password

        # Act
        user_in_db = UserInDB(**sample_user_data)

        # Assert
        assert user_in_db.hashed_password == hashed_password

    def test_user_in_db_verify_password_success(self, sample_user_data):
        """
        Test que verifica la verificación exitosa de contraseña.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        plain_password = "verifyme"
        hashed_password = get_password_hash(plain_password)
        sample_user_data["hashed_password"] = hashed_password
        user_in_db = UserInDB(**sample_user_data)

        # Act & Assert
        assert verify_password(plain_password, user_in_db.hashed_password)

    def test_user_in_db_verify_password_failure(self, sample_user_data):
        """
        Test que verifica la verificación fallida de contraseña.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        plain_password = "verifyme"
        wrong_password = "wrong"
        hashed_password = get_password_hash(plain_password)
        sample_user_data["hashed_password"] = hashed_password
        user_in_db = UserInDB(**sample_user_data)

        # Act & Assert
        assert not verify_password(wrong_password, user_in_db.hashed_password)

    def test_user_in_db_inheritance(self, sample_user_data):
        """
        Test que verifica que UserInDB hereda de User correctamente.

        Args:
            sample_user_data: Datos de usuario
        """
        # Arrange
        sample_user_data["hashed_password"] = "a_hash"

        # Act
        user_in_db = UserInDB(**sample_user_data)

        # Assert
        assert user_in_db.username == sample_user_data["username"]
        assert "password" not in user_in_db.dict()

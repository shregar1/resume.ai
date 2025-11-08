from pydantic import ValidationError
import pytest

from dtos.configurations.db import DBConfigurationDTO

from tests.dtos.configurations.test_configuration_abstractions import (
    TestIConfigurationDTO,
)


@pytest.mark.asyncio
class TestDBConfigurationDTO(TestIConfigurationDTO):

    @pytest.fixture
    def user_name(self):
        return "test_user"

    @pytest.fixture
    def password(self):
        return "test_password"

    @pytest.fixture
    def database(self):
        return "test_database"

    @pytest.fixture
    def host(self):
        return "test_host"

    @pytest.fixture
    def port(self):
        return 5432

    @pytest.fixture
    def connection_string(self):
        return "test_connection_string"

    async def test_db_configurations_dto_all_field_valid(
        self,
        user_name: str,
        password: str,
        database: str,
        host: str,
        port: int,
        connection_string: str
    ):
        configuration_dto = DBConfigurationDTO(
            user_name=user_name,
            password=password,
            database=database,
            host=host,
            port=port,
            connection_string=connection_string,
        )

        assert configuration_dto.user_name == user_name
        assert configuration_dto.password == password
        assert configuration_dto.database == database
        assert configuration_dto.host == host
        assert configuration_dto.port == port
        assert configuration_dto.connection_string == connection_string

    async def test_db_configurations_dto_all_none_error(self):

        with pytest.raises(ValidationError) as exc_info:
            DBConfigurationDTO(
                user_name=None,
                password=None,
                database=None,
                host=None,
                port=None,
                connection_string=None,
            )

        assert isinstance(exc_info.value.errors(), list)
        assert len(exc_info.value.errors()) == 6
        assert exc_info.value.errors()[0]["input"] is None

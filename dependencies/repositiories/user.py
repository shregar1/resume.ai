from typing import Callable

from repositories.user import UserRepository
from start_utils import logger


class UserRepositoryDependency:
    """
    Dependency provider for UserRepository.
    Provides a factory for creating UserRepository instances with DI.
    """

    @staticmethod
    def derive() -> Callable:
        """
        Returns a factory function that creates a UserRepository with the
        given parameters.
        Logs when the factory is created and when a repository is instantiated.
        """
        logger.debug("UserRepositoryDependency factory created")

        def factory(
            urn,
            user_urn,
            api_name,
            session,
            user_id,
        ):
            logger.info(
                "Instantiating UserRepository"
            )
            return UserRepository(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                session=session,
                user_id=user_id,
            )
        return factory

from typing import Callable

from abstractions.dependency import IDependency

from services.user.login import UserLoginService

from start_utils import logger


class UserLoginServiceDependency(IDependency):
    """
    Dependency provider for UserLoginService.
    Provides a factory for creating UserLoginService instances with DI.
    """
    @staticmethod
    def derive() -> Callable:
        """
        Returns a factory function that creates a UserLoginService with the
        given parameters.
        Logs when the factory is created and when a service is instantiated.
        """
        logger.debug("UserLoginServiceDependency factory created")

        def factory(
            urn,
            user_urn,
            api_name,
            user_id,
            jwt_utility,
            user_repository,
        ):
            logger.info(
                "Instantiating UserLoginService"
            )
            return UserLoginService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                user_repository=user_repository,
                jwt_utility=jwt_utility,
            )
        return factory

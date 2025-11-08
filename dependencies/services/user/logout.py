from typing import Callable

from abstractions.dependency import IDependency

from services.user.logout import UserLogoutService

from start_utils import logger


class UserLogoutServiceDependency(IDependency):
    """
    Dependency provider for UserLogoutService.
    Provides a factory for creating UserLogoutService instances with DI.
    """
    @staticmethod
    def derive() -> Callable:
        """
        Returns a factory function that creates a UserLogoutService with the
        given parameters.
        Logs when the factory is created and when a service is instantiated.
        """
        logger.debug("UserLogoutServiceDependency factory created")

        def factory(
            urn,
            user_urn,
            api_name,
            user_id,
            jwt_utility,
            user_repository,
        ):
            logger.info(
                "Instantiating UserLogoutService"
            )
            return UserLogoutService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                user_repository=user_repository,
                jwt_utility=jwt_utility,
            )
        return factory

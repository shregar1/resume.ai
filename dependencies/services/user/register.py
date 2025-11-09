from typing import Callable

from abstractions.dependency import IDependency

from services.user.registration import UserRegistrationService

from start_utils import logger


class UserRegistrationServiceDependency(IDependency):
    """
    Dependency provider for UserRegistrationService.
    Provides a factory for creating UserRegistrationService instances with DI.
    """
    @staticmethod
    def derive() -> Callable:
        """
        Returns a factory function that creates a UserRegistrationService with
        the given parameters.
        Logs when the factory is created and when a service is instantiated.
        """
        logger.debug("UserRegistrationServiceDependency factory created")

        def factory(
            urn,
            user_urn,
            api_name,
            user_id,
            user_repository,
        ):
            logger.info(
                "Instantiating UserRegistrationService"
            )
            return UserRegistrationService(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
                user_repository=user_repository,
            )
        return factory

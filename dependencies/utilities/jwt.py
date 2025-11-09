from typing import Callable

from utilities.jwt import JWTUtility
from start_utils import logger


class JWTUtilityDependency:
    """
    Dependency provider for JWTUtility.
    Provides a factory for creating JWTUtility instances with DI.
    """
    @staticmethod
    def derive() -> Callable:
        """
        Returns a factory function that creates a JWTUtility with the
        given parameters.
        Logs when the factory is created and when a utility is instantiated.
        """
        logger.debug("JWTUtilityDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            user_id: str,
        ):
            logger.info(
                "Instantiating JWTUtility"
            )
            return JWTUtility(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
            )
        return factory

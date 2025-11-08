from typing import Callable

from start_utils import logger

from utilities.dictionary import DictionaryUtility


class DictionaryUtilityDependency:
    """
    Dependency provider for DictionaryUtility.
    Provides a factory for creating DictionaryUtility instances with DI.
    """
    @staticmethod
    def derive() -> Callable:
        """
        Returns a factory function that creates a DictionaryUtility with
        the given parameters.
        Logs when the factory is created and when a utility is instantiated.
        """
        logger.debug("DictionaryUtilityDependency factory created")

        def factory(
            urn: str,
            user_urn: str,
            api_name: str,
            user_id: str,
        ):
            logger.info(
                "Instantiating DictionaryUtility"
            )
            return DictionaryUtility(
                urn=urn,
                user_urn=user_urn,
                api_name=api_name,
                user_id=user_id,
            )
        return factory

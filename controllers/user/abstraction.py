from abstractions.controller import IController

from start_utils import logger


class IUserController(IController):
    """
    Base user controller abstraction for all user controllers.
    Inherits from IController and provides common initialization and logging.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
    ) -> None:
        logger.debug(
            "Initializing IUserController"
        )
        super().__init__(urn, user_urn, api_name, user_id)

from controllers.apis.abstraction import IAPIController

from start_utils import logger


class IV1APIController(IAPIController):
    """
    API v1 controller abstraction for all v1 API controllers.
    Inherits from IAPIController and provides common initialization
    and logging.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
    ) -> None:
        logger.debug(
            "Initializing IV1APIController"
        )
        super().__init__(urn, user_urn, api_name, user_id)

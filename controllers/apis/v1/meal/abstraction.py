from controllers.apis.v1.abstraction import IV1APIController
from start_utils import logger


class IV1MealAPIController(IV1APIController):
    """
    Abstraction for v1 meal API controllers.
    Inherits from IV1APIController and provides common initialization and
    logging.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
    ) -> None:
        logger.debug(
            "Initializing IV1MealAPIController"
        )
        super().__init__(urn, user_urn, api_name, user_id)

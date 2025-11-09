"""
Custom error for handling not found scenarios in the application.
"""
from abstractions.error import IError


class NotFoundError(IError):
    """
    Exception for not found errors.
    Args:
        responseMessage (str): Description of the error.
        responseKey (str): Key for programmatic error handling.
        httpStatusCode (int): HTTP status code to return.
    """

    def __init__(
        self, responseMessage: str, responseKey: str, httpStatusCode: int
    ) -> None:

        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode

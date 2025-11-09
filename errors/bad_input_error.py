"""
Custom error for handling bad input scenarios in the application.
"""
from abstractions.error import IError


class BadInputError(IError):
    """
    Exception for bad input errors.
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

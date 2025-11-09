from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from http import HTTPStatus
from sqlalchemy.orm import Session
from typing import Callable

from controllers.user.abstraction import IUserController

from constants.api_lk import APILK
from constants.api_status import APIStatus

from dependencies.db import DBDependency
from dependencies.repositiories.user import UserRepositoryDependency
from dependencies.services.user.logout import UserLogoutServiceDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency
from dependencies.utilities.jwt import JWTUtilityDependency

from dtos.requests.user.logout import UserLogoutRequestDTO
from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError
from repositories.user import UserRepository
from utilities.dictionary import DictionaryUtility
from utilities.jwt import JWTUtility


class UserLogoutController(IUserController):
    """
    Controller for user logout.
    Handles POST requests for user logout endpoints.
    """
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ) -> None:
        super().__init__(urn)
        self._urn: str = urn
        self._user_urn: str = user_urn
        self._api_name: str = APILK.LOGOUT
        self._user_id: str = user_id
        self._logger = self.logger
        self._dictionary_utility: DictionaryUtility = None

    @property
    def urn(self):
        return self._urn

    @urn.setter
    def urn(self, value):
        self._urn = value

    @property
    def user_urn(self):
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value):
        self._user_urn = value

    @property
    def api_name(self):
        return self._api_name

    @api_name.setter
    def api_name(self, value):
        self._api_name = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def dictionary_utility(self):
        return self._dictionary_utility

    @dictionary_utility.setter
    def dictionary_utility(self, value):
        self._dictionary_utility = value

    async def post(
        self,
        request: Request,
        request_payload: UserLogoutRequestDTO,
        session: Session = Depends(DBDependency.derive),
        user_repository: UserRepository = Depends(
            UserRepositoryDependency.derive
        ),
        user_logout_service_factory: Callable = Depends(
            UserLogoutServiceDependency.derive
        ),
        dictionary_utility: DictionaryUtility = Depends(
            DictionaryUtilityDependency.derive
        ),
        jwt_utility: JWTUtility = Depends(
            JWTUtilityDependency.derive
        )
    ) -> JSONResponse:
        try:

            self.logger.debug("Fetching request URN")
            self.urn: str = request.state.urn
            self.user_id: str = getattr(request.state, "user_id", None)
            self.user_urn: str = getattr(request.state, "user_urn", None)
            self.logger = self.logger.bind(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
            )
            self.dictionary_utility: DictionaryUtility = (
                dictionary_utility(
                    urn=self.urn,
                    user_urn=self.user_urn,
                    api_name=self.api_name,
                    user_id=self.user_id,
                )
            )
            self.jwt_utility: JWTUtility = jwt_utility(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
            )
            self.user_repository = user_repository(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                session=session,
            )

            self.logger.debug("Validating request")
            self.request_payload = request_payload.model_dump()
            self.request_payload.update({"user_id": request.state.user_id})

            await self.validate_request(
                urn=self.urn,
                user_urn=self.user_urn,
                request_payload=self.request_payload,
                request_headers=dict(request.headers.mutablecopy()),
                api_name=self.api_name,
                user_id=self.user_id,
            )
            self.logger.debug("Verified request")

            self.logger.debug("Running online user service")
            response_dto: BaseResponseDTO = await user_logout_service_factory(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                jwt_utility=self.jwt_utility,
                user_repository=self.user_repository,
            ).run()

            self.logger.debug("Preparing response metadata")
            httpStatusCode = HTTPStatus.OK
            self.logger.debug("Prepared response metadata")

        except (BadInputError, UnexpectedResponseError, NotFoundError) as err:

            self.logger.error(
                f"{err.__class__} error occured while logging out user: {err}"
            )
            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage=err.responseMessage,
                responseKey=err.responseKey,
                data={},
            )
            httpStatusCode = err.httpStatusCode
            self.logger.debug("Prepared response metadata")

        except Exception as err:

            self.logger.error(
                f"{err.__class__} error occured while logging out user: {err}"
            )

            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage="Failed to logout users.",
                responseKey="error_internal_server_error",
                data={},
            )
            httpStatusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self.logger.debug("Prepared response metadata")

        return JSONResponse(
            content=self.dictionary_utility.convert_dict_keys_to_camel_case(
                response_dto.model_dump()
            ),
            status_code=httpStatusCode,
        )

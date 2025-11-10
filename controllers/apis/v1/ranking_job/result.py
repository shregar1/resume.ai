from fastapi import Request, Path, Depends
from fastapi.responses import JSONResponse
from http import HTTPStatus
from redis import Redis

from constants.api_lk import APILK
from constants.api_status import APIStatus

from controllers.apis.v1.ranking_job.abstraction import IV1RankingJobController

from dependencies.cache import CacheDependency
from dependencies.utilities.dictionary import DictionaryUtilityDependency

from dtos.requests.ranking_job.result import FetchRankingJobResultRequestDTO
from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError

from services.apis.v1.ranking_job.result import FetchRankingJobResultService


from utilities.dictionary import DictionaryUtility


class FetchRankingJobResultController(IV1RankingJobController):
    """
    Controller for fetching the result of a ranking job.
    Handles GET requests for fetching the result of a ranking job.
    """
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self._urn = urn
        self._user_urn = None
        self._api_name = APILK.FETCH_RANKING_JOB_RESULT
        self._user_id = None
        self._logger = self.logger
        self._dictionary_utility = None

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

    async def get(
        self,
        request: Request,
        job_id: str = Path(...),
        dictionary_utility: DictionaryUtility = Depends(
            DictionaryUtilityDependency.derive
        ),
        redis_session: Redis = Depends(
            CacheDependency.derive
        )
    ) -> JSONResponse:
        try:

            self.logger.debug("Fetching request URN")
            self.urn = request.state.urn
            self.user_id = getattr(request.state, "user_id", None)
            self.user_urn = getattr(request.state, "user_urn", None)
            self.logger = self.logger.bind(
                urn=self.urn, user_urn=self.user_urn, api_name=self.api_name
            )
            self.dictionary_utility: DictionaryUtility = (
                dictionary_utility(
                    urn=self.urn,
                    user_urn=self.user_urn,
                    api_name=self.api_name,
                    user_id=self.user_id,
                )
            )

            if not job_id:
                raise BadInputError(
                    status_code=400,
                    responseMessage="Job ID is required",
                    responseKey="error_job_id_required"
                )
            
            service: FetchRankingJobResultService = FetchRankingJobResultService(
                urn=self.urn,
                user_urn=self.user_urn,
                api_name=self.api_name,
                user_id=self.user_id,
                redis_session=redis_session
            )
            response_dto = await service.run(
                request_dto=FetchRankingJobResultRequestDTO(
                    job_id=job_id
                )
            )
            self.logger.debug("Preparing response metadata")
            httpStatusCode = HTTPStatus.OK
            self.logger.debug("Prepared response metadata")

        except (BadInputError, UnexpectedResponseError, NotFoundError) as err:

            self.logger.error(
                f"{err.__class__} error occured while logging in user: {err}"
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
                f"{err.__class__} error occured while logging in user: {err}"
            )

            self.logger.debug("Preparing response metadata")
            response_dto: BaseResponseDTO = BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.FAILED,
                responseMessage="Failed to login users.",
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

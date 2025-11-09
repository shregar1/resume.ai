import uuid
import os
from datetime import datetime

from fastapi import Request, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
from http import HTTPStatus
from typing import List

from constants.api_lk import APILK
from constants.api_status import APIStatus
from constants.file_type import FileTypeConstant

from controllers.apis.v1.ranking_job.abstraction import IV1RankingJobController

from dependencies.utilities.dictionary import DictionaryUtilityDependency

from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError

from utilities.dictionary import DictionaryUtility

class CreateRankingJobController(IV1RankingJobController):
    """
    Controller for creating a ranking job.
    Handles POST requests for creating a ranking job endpoints.
    """
    def __init__(self, urn: str = None) -> None:
        super().__init__(urn)
        self._urn = urn
        self._user_urn = None
        self._api_name = APILK.CREATE_RANKING_JOB
        self._user_id = None
        self._logger = self.logger
        self._dictionary_utility = None
        self._jwt_utility = None

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
        background_tasks: BackgroundTasks,
        job_description: str = Form(...),
        job_title: str = Form(""),
        company: str = Form(""),
        cv_files: List[UploadFile] = File(...),
        dictionary_utility: DictionaryUtility = Depends(
            DictionaryUtilityDependency.derive
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

            if not cv_files:
                raise BadInputError(
                    status_code=400,
                    responseMessage="No CV files provided",
                    responseKey="no_cv_files_provided"
                )
            
            if len(cv_files) > 100:
                raise BadInputError(
                    status_code=400,
                    responseMessage="Maximum 100 CVs allowed per job",
                    responseKey="maximum_100_cvs_allowed_per_job"
                )
            
            # Create job ID
            job_id = str(uuid.uuid4())
            
            # Ensure data directory exists
            os.makedirs(settings.cv_dir, exist_ok=True)
            
            # Save uploaded files
            saved_files = []
            for i, cv_file in enumerate(cv_files):
                # Validate file extension
                file_ext = os.path.splitext(cv_file.filename)[1].lower()
                if file_ext.strip(".") not in FileTypeConstant.ALLOWED_EXTENSIONS:
                    raise BadInputError(
                        status_code=400,
                        responseMessage=f"Unsupported file type: {file_ext}. Allowed: {', '.join(FileTypeConstant.ALLOWED_EXTENSIONS)}",
                        responseKey="unsupported_file_type"
                    )
                
                # Save file
                file_path = os.path.join(settings.cv_dir, f"{job_id}_{i}_{cv_file.filename}")
                
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await cv_file.read()
                    
                    # Check file size
                    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
                        raise HTTPException(
                            status_code=400,
                            detail=f"File {cv_file.filename} exceeds maximum size of {settings.max_upload_size_mb}MB"
                        )
                    
                    await f.write(content)
                
                saved_files.append({
                    "file_path": file_path,
                    "file_type": file_ext.replace(".", ""),
                    "original_name": cv_file.filename
                })
            
            # Store initial job status
            job_store[job_id] = {
                "job_id": job_id,
                "status": "processing",
                "created_at": datetime.now().isoformat(),
                "cv_count": len(saved_files),
                "job_title": job_title,
                "company": company
            }


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


@app.post("/api/v1/rankings", response_model=RankingResponse)
async def create_ranking_job(

):
    """Create a new CV ranking job.
    
    Args:
        job_description: Job description text
        job_title: Job title
        company: Company name
        cv_files: List of CV files (PDF, DOCX, TXT)
        
    Returns:
        Job information
    """
    try:
        # Validate files

        
        # Process in background
        background_tasks.add_task(
            process_ranking_job,
            job_id,
            job_description,
            job_title,
            company,
            saved_files
        )
        
        return RankingResponse(
            job_id=job_id,
            status="processing",
            message=f"Ranking job created with {len(saved_files)} CVs. Processing in background."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ranking job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

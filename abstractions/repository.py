from abc import ABC
from datetime import datetime
from operator import attrgetter
from cachetools import cachedmethod, LRUCache
from loguru import logger
from sqlalchemy.ext.declarative import DeclarativeMeta


class IRepository(ABC):

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
        model: DeclarativeMeta = None,
        cache: LRUCache = None,
    ) -> None:
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
        )
        self._model = model
        self._cache = cache

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
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def cache(self):
        return self._cache

    @cache.setter
    def cache(self, value):
        self._cache = value

    def create_record(
        self,
        record: DeclarativeMeta,
    ) -> DeclarativeMeta:

        start_time = datetime.now()
        self.session.add(record)
        self.session.commit()

        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record

    @cachedmethod(attrgetter('_cache'))
    def retrieve_record_by_id(
        self,
        id: str,
        is_deleted: bool = False
    ) -> DeclarativeMeta:
        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(self.model.id == id, self.model.is_deleted == is_deleted)
            .first()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    @cachedmethod(attrgetter('_cache'))
    def retrieve_record_by_urn(
        self,
        urn: str,
        is_deleted: bool = False,
    ) -> DeclarativeMeta:

        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(self.model.urn == urn, self.model.is_deleted == is_deleted)
            .first()
        )
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    def update_record(
        self,
        id: str,
        new_data: dict,
    ) -> DeclarativeMeta:

        start_time = datetime.now()
        record = (
            self.session.query(self.model)
            .filter(self.model.id == id)
            .first()
        )

        if not record:
            raise ValueError(f"{self.model.__name__} with id {id} not found")

        for attr, value in new_data.items():
            setattr(record, attr, value)

        self.session.commit()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record

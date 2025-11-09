from sqlalchemy.orm import Session

from start_utils import db_session, logger


class DBDependency:
    """
    Dependency provider for SQLAlchemy DB session.
    Provides the shared DB session for DI.
    """
    @staticmethod
    def derive() -> Session:
        """
        Returns the shared SQLAlchemy DB session instance.
        Logs when the DB dependency is derived.
        """
        logger.debug("DBDependency: returning db_session instance")
        return db_session

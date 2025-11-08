"""
SQLAlchemy model for the user table, representing application users and their
authentication details.
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    Boolean,
    Index,
)

from constants.db.table import Table

from models import Base


class User(Base):
    """
    SQLAlchemy model for a user.
    Fields:
        id (BigInteger): Primary key.
        urn (str): Unique resource name for the user.
        email (str): User's email address.
        password (str): User's hashed password.
        is_deleted (bool): Soft delete flag.
        last_login (datetime): Last login timestamp.
        is_logged_in (bool): Login status.
        created_on (datetime): Creation timestamp.
        created_by (BigInteger): Creator's user ID.
        updated_on (datetime): Last update timestamp.
        updated_by (BigInteger): Last updater's user ID.
    """
    __tablename__ = Table.USER

    id = Column(BigInteger, primary_key=True)
    urn = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    last_login = Column(DateTime(timezone=True))
    is_logged_in = Column(Boolean, nullable=False, default=False)
    created_on = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=datetime.utcnow
    )
    created_by = Column(BigInteger, nullable=False)
    updated_on = Column(DateTime(timezone=True))
    updated_by = Column(BigInteger)


Index('ix_user_urn', User.urn)
Index('ix_user_email', User.email, unique=True)
Index('ix_user_created_on', User.created_on)

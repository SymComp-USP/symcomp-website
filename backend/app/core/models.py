import uuid
from datetime import datetime

from sqlalchemy import MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

POSTGRES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """ This __tablename__ may be overriden in children classes, avoiding cases like "Activity" -> "activitys" """
        return cls.__name__.lower() + "s"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        sort_order=-1
    )
    
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        sort_order=9997
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now(),
        sort_order=9998
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        default=None,
        index=True,
        sort_order=9999
    )
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

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
        """This __tablename__ may be overriden in children classes, avoiding cases like "Activity" -> "activitys" """
        return cls.__name__.lower() + "s"

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.mixins import TimestampsMixin, UUIDPKMixin
from app.core.models import Base


class DummyModel(Base, UUIDPKMixin):
    foo: Mapped[str] = mapped_column(String(50))
    bar: Mapped[str] = mapped_column(String(50))


class DummyModelWithMixins(Base, UUIDPKMixin, TimestampsMixin):
    foo: Mapped[str] = mapped_column(String(50))
    bar: Mapped[str] = mapped_column(String(50))


def test_automatic_tablename():
    assert DummyModel.__tablename__ == "dummymodels"


def test_inherited_fields():
    columns = DummyModelWithMixins.__table__.columns.keys()

    assert "id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns
    assert "deleted_at" in columns


def test_metadata_naming_convention():
    convention = DummyModel.metadata.naming_convention

    assert convention["ix"] == "%(column_0_label)s_idx"
    assert convention["uq"] == "%(table_name)s_%(column_0_name)s_key"
    assert convention["ck"] == "%(table_name)s_%(constraint_name)s_check"
    assert convention["fk"] == "%(table_name)s_%(column_0_name)s_fkey"
    assert convention["pk"] == "%(table_name)s_pkey"

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.users import services
from app.users.schemas import UserCreate, UserUpdate
from app.users.services import UserAlreadyDeletedError, UserAlreadyExistsError


@pytest.mark.asyncio
async def test_create_user_service(db_session: AsyncSession):
    user_in = UserCreate(
        email="service_test@example.com", name="Service User", password="password123"
    )
    user = await services.create_user(db_session, user_in)

    assert user.id is not None
    assert user.email == "service_test@example.com"
    assert user.name == "Service User"


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession):
    user_in = UserCreate(
        email="get_id@example.com", name="Get By ID", password="password123"
    )
    created_user = await services.create_user(db_session, user_in)

    fetched_user = await services.get_user_by_id(db_session, created_user.id)
    assert fetched_user is not None
    assert fetched_user.id == created_user.id


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    user_in = UserCreate(
        email="get_email@example.com", name="Get By Email", password="password123"
    )
    created_user = await services.create_user(db_session, user_in)

    fetched_user = await services.get_user_by_email(db_session, "get_email@example.com")
    assert fetched_user is not None
    assert fetched_user.id == created_user.id


@pytest.mark.asyncio
async def test_update_user_service(db_session: AsyncSession):
    user_in = UserCreate(
        email="update@example.com", name="Old Name", password="password123"
    )
    created_user = await services.create_user(db_session, user_in)

    update_dto = UserUpdate(name="New Name")
    updated_user = await services.update_user(db_session, created_user, update_dto)

    assert updated_user.name == "New Name"


@pytest.mark.asyncio
async def test_soft_delete_user_service(db_session: AsyncSession):
    user_in = UserCreate(
        email="delete@example.com", name="Delete Me", password="password123"
    )
    created_user = await services.create_user(db_session, user_in)

    await services.delete_user(db_session, created_user)

    deleted_user = await services.get_user_by_id(db_session, created_user.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_create_user_with_existing_active_email_raises(db_session: AsyncSession):
    user_in = UserCreate(
        email="duplicate@example.com", name="First", password="password123"
    )
    await services.create_user(db_session, user_in)

    duplicate_in = UserCreate(
        email="duplicate@example.com", name="Second", password="password456"
    )
    with pytest.raises(UserAlreadyExistsError):
        await services.create_user(db_session, duplicate_in)


@pytest.mark.asyncio
async def test_delete_already_deleted_user_raises(db_session: AsyncSession):
    user_in = UserCreate(
        email="double_delete@example.com", name="Delete Twice", password="password123"
    )
    created_user = await services.create_user(db_session, user_in)

    await services.delete_user(db_session, created_user)

    with pytest.raises(UserAlreadyDeletedError):
        await services.delete_user(db_session, created_user)


@pytest.mark.asyncio
async def test_create_user_reactivates_soft_deleted_account(db_session: AsyncSession):
    # Cria, soft-deleta e depois recria com o mesmo e-mail: deve reativar a
    # conta antiga (mesmo id) em vez de criar um registro novo.
    user_in = UserCreate(
        email="reactivate@example.com", name="Original Name", password="oldpassword"
    )
    original_user = await services.create_user(db_session, user_in)
    original_id = original_user.id

    # Simula privilégios que precisam ser resetados na reativação
    original_user.is_admin = True
    original_user.is_verified = True
    await db_session.flush()

    await services.delete_user(db_session, original_user)

    reactivate_in = UserCreate(
        email="reactivate@example.com", name="New Name", password="newpassword"
    )
    reactivated_user = await services.create_user(db_session, reactivate_in)

    assert reactivated_user.id == original_id
    assert reactivated_user.name == "New Name"
    assert reactivated_user.deleted_at is None
    assert reactivated_user.is_admin is False
    assert reactivated_user.is_verified is False
    # assert services.verify_password("newpassword", reactivated_user.password_hash)

    # Não deve haver mais nenhum registro deletado pendente para esse e-mail
    still_deleted = await services.get_deleted_user_by_email(
        db_session, "reactivate@example.com"
    )
    assert still_deleted is None

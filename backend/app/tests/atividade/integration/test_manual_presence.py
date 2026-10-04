from datetime import UTC, datetime, timedelta

from app.atividade.models import Atividade, TipoAtividade
from app.auth.dependencies import get_current_admin_user
from app.main import app
from app.semana.models import SemanaEvent, SemanaParticipant


async def test_admin_registers_subscribed_user_without_name(
    db_client, db_session, user_factory
):
    admin = await user_factory(email="attendance-admin@example.com")
    admin.is_admin = True
    admin.is_verified = True

    attendee = await user_factory(email="attendance-user@example.com", name="Attendee")
    week = SemanaEvent(nome="Attendance test", ano=2040)
    db_session.add(week)
    await db_session.flush()

    db_session.add(
        SemanaParticipant(
            semana_id=week.id,
            user_id=attendee.id,
            nickname="attendee2040",
        )
    )
    starts_at = datetime.now(UTC) + timedelta(days=1)
    activity = Atividade(
        semana_id=week.id,
        tipo=TipoAtividade.PALESTRA,
        titulo="Attendance test activity",
        comeca_as=starts_at,
        termina_as=starts_at + timedelta(hours=1),
        codigo="T040",
        pontos=0,
        horas=1,
    )
    db_session.add(activity)
    await db_session.flush()

    app.dependency_overrides[get_current_admin_user] = lambda: admin
    response = await db_client.post(
        f"/api/v1/admin/semanas/{week.id}/atividades/{activity.id}/presencas",
        json={"nome": "", "email": attendee.email},
    )

    assert response.status_code == 201, response.text
    assert response.json()["nome"] == attendee.name
    assert response.json()["email"] == attendee.email
    assert response.json()["user_id"] == str(attendee.id)

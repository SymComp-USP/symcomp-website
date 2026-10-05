import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.challenge import Challenge, ChallengeScoringType
from app.semana.models import PointEvent, Semana, SemanaParticipant
from app.semana.services import list_ranking


async def test_list_ranking_excludes_points_from_deleted_challenge(
    db_session: AsyncSession, user_factory
):
    semana = Semana(nome="Semana Teste", ano=2026)
    db_session.add(semana)
    await db_session.flush()

    user = await user_factory()
    zero_score_user = await user_factory(email="zero-score@example.com")
    participant = SemanaParticipant(
        semana_id=semana.id,
        user_id=user.id,
        nickname="RankingTest123",
    )
    zero_score_participant = SemanaParticipant(
        semana_id=semana.id,
        user_id=zero_score_user.id,
        nickname="RankingZero123",
    )
    challenge = Challenge(
        title="Deleted challenge",
        scoring_type=ChallengeScoringType.QUIZ,
        semana_id=semana.id,
        deleted_at=datetime.now(UTC),
    )
    active_challenge = Challenge(
        title="Active challenge",
        scoring_type=ChallengeScoringType.QUIZ,
        semana_id=semana.id,
    )
    db_session.add_all(
        [participant, zero_score_participant, challenge, active_challenge]
    )
    await db_session.flush()

    db_session.add_all(
        [
            PointEvent(
                semana_participant_id=participant.id,
                amount=100,
                source_type="challenge",
                source_id=challenge.id,
            ),
            PointEvent(
                semana_participant_id=participant.id,
                amount=20,
                source_type="challenge",
                source_id=active_challenge.id,
            ),
            PointEvent(
                semana_participant_id=participant.id,
                amount=15,
                source_type="atividade",
                source_id=uuid.uuid4(),
            ),
            PointEvent(
                semana_participant_id=zero_score_participant.id,
                amount=75,
                source_type="challenge",
                source_id=challenge.id,
            ),
        ]
    )
    await db_session.flush()

    ranking = await list_ranking(db_session, semana.id)

    points_by_participant = {row.id: row.points for row in ranking}
    assert points_by_participant == {
        participant.id: 35,
        zero_score_participant.id: 0,
    }

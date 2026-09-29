from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.challenges.models.challenge import ChallengeScoringType
from app.challenges.services.image import build_challenge_image_url


class AnswerBody(BaseModel):
    question_id: UUID
    answer: str


class SubmissionResponse(BaseModel):
    submitted_at: datetime
    score: int


class InputSubmission(BaseModel):
    answer: str


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prompt: str
    points_value: int
    current_answer: str | None = None


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    nickname: str
    user_id: UUID
    challenge_id: UUID
    score: int
    submitted_at: datetime | None


class ParticipantScoreAdjustment(BaseModel):
    amount: int


class ParticipantScoreResponse(BaseModel):
    id: UUID
    challenge_id: UUID
    score: int


class QuestionCreate(BaseModel):
    prompt: str
    answer: str
    points_value: int = 0


class QuestionUpdate(BaseModel):
    prompt: str | None = None
    answer: str | None = None
    points_value: int | None = None


class ChallengeCreate(BaseModel):
    title: str
    prompt: str = ""
    scoring_type: ChallengeScoringType = ChallengeScoringType.QUIZ
    finishes_at: datetime | None = None
    semana_id: int | None = None
    points_value: int = 0
    input_answer: str | None = None
    resource_urls: list[str] = Field(default_factory=list)

    questions: list[QuestionCreate] = Field(default_factory=list)

    @field_validator("finishes_at")
    @classmethod
    def validate_finishes_at_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("finishes_at must include a timezone.")
        return value


class ChallengeUpdate(BaseModel):
    title: str | None = None
    prompt: str | None = None
    questions: list[QuestionCreate] | None = None
    finishes_at: datetime | None = None
    points_value: int | None = None
    input_answer: str | None = None
    resource_urls: list[str] | None = None

    @field_validator("finishes_at")
    @classmethod
    def validate_finishes_at_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("finishes_at must include a timezone.")
        return value


class RankingEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    score: int
    name: str
    nickname: str


class AdminQuestionResponse(BaseModel):
    """Question com o gabarito visível (admin)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prompt: str
    answer: str
    points_value: int


class ChallengeImageMixin(BaseModel):
    """Adiciona `image_url` a qualquer schema de challenge.

    Espera que o ORM (ou dict de entrada) traga `image_path`. Esse campo
    é carregado, usado para montar `image_url`, e **excluído** da resposta.
    """

    image_path: str | None = Field(default=None, exclude=True)
    image_url: str | None = None

    @model_validator(mode="after")
    def _fill_image_url(self):
        if self.image_url is None:
            self.image_url = build_challenge_image_url(self.image_path)
        return self


class ChallengeResponse(ChallengeImageMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    prompt: str
    scoring_type: ChallengeScoringType
    finishes_at: datetime
    resource_urls: list[str] = Field(default_factory=list)
    questions: list[QuestionResponse] = Field(default_factory=list)
    is_participant: bool = False
    submitted_at: datetime | None = None


class ChallengePublicResponse(ChallengeImageMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    prompt: str
    scoring_type: ChallengeScoringType
    finishes_at: datetime
    resource_urls: list[str] = Field(default_factory=list)


class AdminChallengeResponse(ChallengeImageMixin):
    """Challenge com questões completas (admin)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    prompt: str
    scoring_type: ChallengeScoringType
    finishes_at: datetime
    semana_id: int | None = None
    points_value: int = 0
    input_answer: str | None = None
    resource_urls: list[str] = Field(default_factory=list)
    questions: list[AdminQuestionResponse] = Field(default_factory=list)

from sqlalchemy import String, DateTime, UUIDType, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, SQLEnum, relationship
from enum import Enum
from core.models import Base
from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.core.config import settings
import jwt
from presenca import Presenca


class StatusAtividade(str, Enum):
    PROVISORIA = "provisoria"
    CONFIRMADA = "confirmada"


class TipoAtividade(str, Enum):
    PALESTRA = "palestra"
    ENCERRAMENTO = "encerramento"
    CONVERSA = "conversa"
    COFFEE_BREAK = "coffee_break"


class SemanaEvent(Base):
    __tablename__ = "semana_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255))
    ano: Mapped[int] = mapped_column()
    atividades: Mapped[list["Atividade"]] = relationship(back_populates="semana")


class Atividade(Base):
    __tablename__ = "atividade"

    id: Mapped[int] = mapped_column(primary_key=True)
    semana_event_id: Mapped[int] = mapped_column(ForeignKey("semana_event.id"))

    tipo: Mapped[TipoAtividade] = mapped_column(SQLEnum(TipoAtividade))
    titulo: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[StatusAtividade] = mapped_column(
        SQLEnum(StatusAtividade), default=StatusAtividade.PROVISORIA
    )
    comeca_as: Mapped[datetime] = mapped_column(DateTime, unique=True)
    termina_as: Mapped[datetime] = mapped_column(DateTime, unique=True)
    qr_code: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    uid: Mapped[UUID] = mapped_column(UUIDType, default=uuid4, unique=True)
    token: Mapped[str | None] = mapped_column(String(512), default="", nullable=True)

    semana_id: Mapped[int] = mapped_column(ForeignKey("semana_event.id"))
    semana: Mapped["SemanaEvent"] = mapped_column(ForeignKey("semana_event"))

    registro_presenca: Mapped[list["Presenca"]] = relationship(
        back_populates="atividade", cascade="all, delete-orphan"
    )

    def _generate_signed_token(self) -> str:
        payload = {
            "uid": str(self.uid),
            "type": "qr_presence",
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }

        token = jwt.encode(
            payload, settings.secret_key.get_secret_value(), algorithm="HS256"
        )

        self.token = token
        return token

    def generate_qr_data(self) -> str:
        return self._generate_signed_token()

    def generate_qr_code(self):
        pass

    def save(self):
        pass

    def __str__(self):
        return f"{self.titulo} - {self.comeca_as.strftime('%d/%m/%Y %H:%M')}"

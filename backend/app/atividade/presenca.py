from core.models import Base
from sqlalchemy import String,DateTime,ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from models import Atividade

class Presenca(Base):
    __tablename__ = "presenca"

    id:Mapped[int]=mapped_column(primary_key=True)
    nome:Mapped[str]=mapped_column(String(255),default="")
    email:Mapped[str]=mapped_column(String(255),default="")

    atividade_id:Mapped[int]=mapped_column(ForeignKey("atividade.id"),nullable=False)
    atividade: Mapped["Atividade"]=relationship(back_populates="registros_presenca")
    horario_registro:Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    horas:Mapped[int]=mapped_column(default=1)
    compartilhar_email:Mapped[bool]=mapped_column(default=False)

    def __str__(self):
        return f"{self.nome} ({self.email}) - {self.atividade.titulo}"





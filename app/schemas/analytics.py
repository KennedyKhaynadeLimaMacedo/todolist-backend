"""Contrato JSON da página Analytics.

Os campos têm o mesmo nome e o mesmo formato que a `AnalyticsPage` do
front-end já calcula hoje — na integração, ela só troca a fonte dos dados.
"""

from datetime import date

from pydantic import Field

from app.models.enums import PrioridadeTarefa
from app.schemas.base import EsquemaDeSaida


class ConcluidasNoDia(EsquemaDeSaida):
    """Quantas tarefas foram concluídas em um dia."""

    dia: date
    quantidade: int


class AnalyticsOut(EsquemaDeSaida):
    """Análises das tarefas do usuário, calculadas com pandas."""

    total: int
    concluidas: int
    taxa_conclusao: int = Field(description="Percentual de concluídas, de 0 a 100")
    concluidas_na_janela: int = Field(description="Soma de 'concluidasPorDia'")
    concluidas_por_dia: list[ConcluidasNoDia]
    pendentes_por_prioridade: dict[PrioridadeTarefa, int]
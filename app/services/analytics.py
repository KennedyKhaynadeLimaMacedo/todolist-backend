"""Análise de dados das tarefas com pandas — os números da página Analytics.

Transforma a lista de tarefas numa tabela e responde perguntas
sobre a tabela inteira de uma vez, sem for.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd

from app.models import Tarefa
from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.repositories import TarefaRepositorio


def arredondar(valor: float) -> int:
    """Arredonda como o Math.round do JavaScript: 12,5 → 13 (não 12).

    O round() do Python usa 'banker's rounding': 12,5 vira 12.
    math.floor(valor + 0.5) soma meio e corta para baixo, reproduzindo
    o comportamento do front-end.
    """
    return math.floor(valor + 0.5)


@dataclass(frozen=True)
class Analytics:
    """Resultado da análise das tarefas de um usuário."""

    total: int
    concluidas: int
    taxa_conclusao: int
    concluidas_na_janela: int
    concluidas_por_dia: list[dict]
    pendentes_por_prioridade: dict[PrioridadeTarefa, int]


class AnalyticsServico:
    """Calcula as análises da página Analytics a partir das tarefas do usuário."""

    def __init__(self, tarefas: TarefaRepositorio) -> None:
        self._tarefas = tarefas

    # --- a tabela

    @staticmethod
    def _montar_tabela(tarefas: list[Tarefa]) -> pd.DataFrame:
        """Transforma a lista de tarefas num DataFrame — uma linha por tarefa."""
        fuso_do_servidor = datetime.now().astimezone().tzinfo

        tabela = pd.DataFrame({
            "status":       [t.status.value for t in tarefas],
            "prioridade":   [t.prioridade for t in tarefas],
            "concluido_em": [t.concluido_em for t in tarefas],
        })

        tabela["concluido_em"] = pd.to_datetime(
            tabela["concluido_em"],
            utc=True,
        ).dt.tz_convert(fuso_do_servidor)

        # Só o dia da conclusão (sem hora), para agrupar por dia.
        tabela["dia_conclusao"] = tabela["concluido_em"].dt.date

        return tabela

    # --- as métricas

    @staticmethod
    def _concluidas_por_dia(concluidas: pd.DataFrame, dias: int, hoje: date) -> list[dict]:
        """Quantas tarefas foram concluídas em cada um dos últimos `dias` dias."""
        janela = [hoje - timedelta(days=n) for n in range(dias - 1, -1, -1)]

        contagem = (
            concluidas["dia_conclusao"]
            .value_counts()
            .reindex(janela, fill_value=0)
        )

        return [{"dia": dia, "quantidade": int(qtd)} for dia, qtd in contagem.items()]

    @staticmethod
    def _pendentes_por_prioridade(pendentes: pd.DataFrame) -> dict[PrioridadeTarefa, int]:
        """Quantas tarefas pendentes há em cada prioridade, da mais urgente à menor."""
        ordem = [p.value for p in sorted(PrioridadeTarefa, key=lambda p: p.peso)]

        contagem = pendentes["prioridade"].value_counts().reindex(ordem, fill_value=0)

        return {PrioridadeTarefa(prioridade): int(qtd) for prioridade, qtd in contagem.items()}

    def calcular(self, usuario_id: int, dias: int = 7, hoje: date | None = None) -> Analytics:
        """Calcula as análises da página Analytics a partir das tarefas do usuário."""
        hoje = hoje or date.today()
        tabela = self._montar_tabela(self._tarefas.todas_do_usuario(usuario_id))

        # tabela[concluida] devolve uma coluna de True/False, uma linha por tarefa.
        concluida  = tabela["status"] == StatusTarefa.CONCLUIDA.value
        concluidas = tabela[concluida]   # só as linhas em que o valor é True
        pendentes  = tabela[~concluida]  # ~ inverte: True vira False e vice-versa

        total   = len(tabela)
        por_dia = self._concluidas_por_dia(concluidas, dias, hoje)

        return Analytics(
            total=total,
            concluidas=len(concluidas),
            taxa_conclusao=arredondar(len(concluidas) / total * 100) if total else 0,
            concluidas_na_janela=sum(item["quantidade"] for item in por_dia),
            concluidas_por_dia=por_dia,
            pendentes_por_prioridade=self._pendentes_por_prioridade(pendentes),
        )
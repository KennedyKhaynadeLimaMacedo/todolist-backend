
"""Operações sobre as tarefas do usuário autenticado."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from app.core.exceptions import AcessoNaoAutorizado, TarefaNaoEncontrada
from app.models import Tarefa
from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.repositories import TarefaRepositorio


NAO_INFORMADO: Any = object()


@dataclass(frozen=True)
class AlteracoesDaTarefa:
    """Campos que um PATCH pediu para alterar."""

    titulo: Any = NAO_INFORMADO
    status: Any = NAO_INFORMADO
    prioridade: Any = NAO_INFORMADO
    prazo: Any = NAO_INFORMADO

    def informado(self, campo: str) -> bool:
        return getattr(self, campo) is not NAO_INFORMADO


@dataclass(frozen=True)
class PaginaDeTarefas:
    """Página de tarefas e quantidade total encontrada pelos filtros."""

    tarefas: list[Tarefa]
    total: int


class TarefaServico:
    """Operações sobre as tarefas do usuário autenticado."""

    def __init__(self, tarefas: TarefaRepositorio) -> None:
        self._tarefas = tarefas

    def criar(
        self,
        usuario_id: int,
        titulo: str,
        prioridade: PrioridadeTarefa,
        prazo: date | None,
    ) -> Tarefa:
        """Cria uma tarefa para o usuário autenticado."""

        tarefa = Tarefa(
            usuario_id=usuario_id,
            titulo=titulo,
            prioridade=prioridade,
            prazo=prazo,
        )
        return self._tarefas.salvar(tarefa)

    def listar(self, filtro: Any) -> list[Tarefa] | PaginaDeTarefas:
        """Lista tarefas por usuário, com filtros e paginação opcionais.

        Recebe um identificador inteiro para a listagem simples ou um objeto
        com os parâmetros de filtro enviado pela rota.
        """

        if isinstance(filtro, int):
            return self._tarefas.listar(filtro)

        resultado, total = self._tarefas.listar_com_filtros(
            usuario_id=filtro.usuario_id,
            status=filtro.status,
            prioridade=filtro.prioridade,
            prazo_ate=filtro.prazo_ate,
            busca=filtro.busca,
            ordenar_por=filtro.ordenar_por,
            ordem=filtro.ordem,
            limite=filtro.limite,
            deslocamento=filtro.deslocamento,
        )

        return PaginaDeTarefas(
            tarefas=resultado,
            total=total,
        )

    def buscar(self, tarefa_id: int, usuario_id: int) -> Tarefa:
        """Busca uma tarefa pertencente ao usuário."""

        tarefa = self._tarefas.buscar_por_id(tarefa_id)

        if tarefa is None:
            raise TarefaNaoEncontrada()

        if not tarefa.pertence_a(usuario_id):
            raise AcessoNaoAutorizado()

        return tarefa

    def atualizar(
        self,
        tarefa_id: int,
        usuario_id: int,
        alteracoes: AlteracoesDaTarefa,
    ) -> Tarefa:
        """Aplica as alterações informadas."""

        tarefa = self.buscar(tarefa_id, usuario_id)

        if alteracoes.informado("titulo"):
            tarefa.titulo = alteracoes.titulo

        if alteracoes.informado("prioridade"):
            tarefa.prioridade = alteracoes.prioridade

        if alteracoes.informado("prazo"):
            tarefa.prazo = alteracoes.prazo

        if alteracoes.informado("status"):
            tarefa.definir_status(StatusTarefa(alteracoes.status))

        return self._tarefas.salvar(tarefa)

    def remover(self, tarefa_id: int, usuario_id: int) -> None:
        """Remove uma tarefa pertencente ao usuário."""

        self._tarefas.remover(self.buscar(tarefa_id, usuario_id))

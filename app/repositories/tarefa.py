
"""Acesso aos dados de tarefa."""

from __future__ import annotations

from datetime import date

from app.models import Tarefa
from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.repositories.base import RepositorioBase


class TarefaRepositorio(RepositorioBase[Tarefa]):
    """Acesso aos dados de tarefa."""

    @property
    def modelo(self) -> type[Tarefa]:
        return Tarefa

    def buscar_por_id(self, identificador: int) -> Tarefa | None:
        """Busca uma tarefa pelo seu identificador."""

        return self.sessao.get(Tarefa, identificador)

    def listar(self, usuario_id: int) -> list[Tarefa]:
        """Lista as tarefas de um usuário."""

        return (
            self.sessao.query(Tarefa)
            .filter(Tarefa.usuario_id == usuario_id)
            .order_by(Tarefa.criado_em.desc(), Tarefa.id.desc())
            .all()
        )

    def listar_com_filtros(
        self,
        usuario_id: int,
        status: StatusTarefa | None = None,
        prioridade: PrioridadeTarefa | None = None,
        prazo_ate: date | None = None,
        busca: str | None = None,
        ordenar_por: str = "criado_em",
        ordem: str = "desc",
        limite: int = 100,
        deslocamento: int = 0,
    ) -> tuple[list[Tarefa], int]:
        """Lista tarefas aplicando filtros, ordenação e paginação.

        A consulta sempre fica restrita ao usuário autenticado.
        O total representa a quantidade encontrada antes da paginação.
        """

        consulta = self.sessao.query(Tarefa).filter(
            Tarefa.usuario_id == usuario_id
        )

        if status is not None:
            consulta = consulta.filter(Tarefa.status == status)

        if prioridade is not None:
            consulta = consulta.filter(Tarefa.prioridade == prioridade)

        if prazo_ate is not None:
            consulta = consulta.filter(Tarefa.prazo <= prazo_ate)

        if busca:
            consulta = consulta.filter(Tarefa.titulo.ilike(f"%{busca}%"))

        total = consulta.count()

        campos_ordenacao = {
            "criado_em": Tarefa.criado_em,
            "prazo": Tarefa.prazo,
            "prioridade": Tarefa.prioridade,
            "titulo": Tarefa.titulo,
            "atualizado_em": Tarefa.atualizado_em,
        }

        campo = campos_ordenacao.get(ordenar_por, Tarefa.criado_em)

        if ordem == "asc":
            consulta = consulta.order_by(campo.asc(), Tarefa.id.asc())
        else:
            consulta = consulta.order_by(campo.desc(), Tarefa.id.desc())

        tarefas = (
            consulta
            .offset(deslocamento)
            .limit(limite)
            .all()
        )

        return tarefas, total

    def todas_do_usuario(self, usuario_id: int) -> list[Tarefa]:
        """Busca todas as tarefas de um usuário para análise."""

        return (
            self.sessao.query(Tarefa)
            .filter(Tarefa.usuario_id == usuario_id)
            .order_by(Tarefa.criado_em.desc(), Tarefa.id.desc())
            .all()
        )

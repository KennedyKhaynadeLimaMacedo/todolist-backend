"""Endpoints de tarefas: todos exigem login."""
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any, Literal
from fastapi import APIRouter, Depends, Query, Response, status
from app.api.dependencies import UsuarioAtual, obter_analytics_servico, obter_tarefa_servico
from app.models.enums import PrioridadeTarefa, StatusTarefa
from app.schemas import AnalyticsOut, ResumoOut, TarefaCreate, TarefaOut, TarefaUpdate
from app.services import AlteracoesDaTarefa, AnalyticsServico, TarefaServico

CampoOrdenacao = Literal["criado_em", "prazo", "prioridade", "titulo", "atualizado_em"]
Ordem = Literal["asc", "desc"]


@dataclass
class FiltroDeTarefas:
    usuario_id: int
    status: StatusTarefa | None = None
    prioridade: PrioridadeTarefa | None = None
    prazo_ate: date | None = None
    busca: str | None = None
    ordenar_por: CampoOrdenacao = "criado_em"
    ordem: Ordem = "desc"
    limite: int = 100
    deslocamento: int = 0


router = APIRouter(
    prefix="/tasks",
    tags=["Tarefas"],
    responses={401: {"description": "Sem token, ou token inválido/expirado"}},
)
Servico = Annotated[TarefaServico, Depends(obter_tarefa_servico)]
_RESPOSTAS_DE_UMA_TAREFA = {
    403: {"description": "A tarefa pertence a outro usuário"},
    404: {"description": "Tarefa não encontrada"},
}


def _montar_alteracoes(dados: TarefaUpdate) -> AlteracoesDaTarefa:
    """Converte o corpo do PATCH em alterações de domínio."""
    return AlteracoesDaTarefa(**dados.model_dump(exclude_unset=True))


@router.post(
    "",
    response_model=TarefaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tarefa",
)
def criar_task(dados: TarefaCreate, usuario: UsuarioAtual, servico: Servico) -> TarefaOut:
    """Cria uma tarefa para o usuário logado. Nasce sempre pendente."""
    return servico.criar(
        usuario_id=usuario.id,
        titulo=dados.titulo,
        prioridade=dados.prioridade,
        prazo=dados.prazo,
    )


@router.get(
    "",
    response_model=list[TarefaOut],
    summary="Listar as tarefas do usuário logado",
)
def listar_tasks(
    usuario: UsuarioAtual,
    servico: Servico,
    response: Response,
    status_tarefa: Annotated[StatusTarefa | None, Query(alias="status")] = None,
    prioridade: Annotated[PrioridadeTarefa | None, Query()] = None,
    prazo_ate: Annotated[
        date | None,
        Query(alias="prazoAte", description="Somente tarefas com prazo até esta data"),
    ] = None,
    busca: Annotated[
        str | None,
        Query(max_length=200, description="Texto contido no título (sem diferenciar maiúsculas)"),
    ] = None,
    ordenar_por: Annotated[
        CampoOrdenacao, Query(alias="ordenarPor")
    ] = "criado_em",
    ordem: Annotated[Ordem, Query()] = "desc",
    limite: Annotated[int, Query(ge=1, le=1000, alias="limit")] = 100,
    deslocamento: Annotated[int, Query(ge=0, alias="offset")] = 0,
) -> list[TarefaOut]:
    """Lista as tarefas do usuário logado, com filtros e ordenação opcionais."""
    filtro = FiltroDeTarefas(
        usuario_id=usuario.id,
        status=status_tarefa,
        prioridade=prioridade,
        prazo_ate=prazo_ate,
        busca=(busca or "").strip() or None,
        ordenar_por=ordenar_por,
        ordem=ordem,
        limite=limite,
        deslocamento=deslocamento,
    )
    resultado: Any = servico.listar(filtro)
    if hasattr(resultado, "tarefas") and hasattr(resultado, "total"):
        response.headers["X-Total-Count"] = str(resultado.total)
        return resultado.tarefas
    response.headers["X-Total-Count"] = str(len(resultado))
    return resultado


@router.get(
    "/resumo",
    response_model=ResumoOut,
    summary="Resumo para o Painel",
)
def resumo_tasks(usuario: UsuarioAtual, servico: Servico) -> Any:
    """Total, pendentes, concluídas e atrasadas — os números da página Painel."""
    resumo_fn = getattr(servico, "resumo", None)
    if callable(resumo_fn):
        return resumo_fn(usuario.id)

    tarefas = servico.listar(usuario.id)
    hoje = date.today()
    concluidos = {"concluida", "concluída", "done", "completed"}
    total = len(tarefas)
    concluidas = sum(
        1 for t in tarefas if str(getattr(getattr(t, "status", None), "value", getattr(t, "status", ""))).lower() in concluidos
    )
    pendentes = total - concluidas
    atrasadas = sum(
        1
        for t in tarefas
        if getattr(t, "prazo", None) is not None
        and t.prazo < hoje
        and str(getattr(getattr(t, "status", None), "value", getattr(t, "status", ""))).lower() not in concluidos
    )
    return {
        "total": total,
        "pendentes": pendentes,
        "concluidas": concluidas,
        "atrasadas": atrasadas,
    }


@router.get(
    "/analytics",
    response_model=AnalyticsOut,
    summary="Análises para a página Analytics (calculadas com pandas)",
)
def analytics_tasks(
    usuario: UsuarioAtual,
    servico: Annotated[AnalyticsServico, Depends(obter_analytics_servico)],
    dias: Annotated[
        int, Query(ge=1, le=90, description="Tamanho da janela de 'concluídas por dia'")
    ] = 7,
) -> AnalyticsOut:
    """Taxa de conclusão, concluídas por dia e pendentes por prioridade."""
    return servico.calcular(usuario.id, dias=dias)


@router.get(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Consultar uma tarefa",
    responses=_RESPOSTAS_DE_UMA_TAREFA,
)
def buscar_task(tarefa_id: int, usuario: UsuarioAtual, servico: Servico) -> TarefaOut:
    """Devolve uma tarefa do usuário logado."""
    return servico.buscar(tarefa_id, usuario.id)


@router.patch(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Atualizar tarefa",
    responses=_RESPOSTAS_DE_UMA_TAREFA,
)
def atualizar_task(
    tarefa_id: int, dados: TarefaUpdate, usuario: UsuarioAtual, servico: Servico
) -> TarefaOut:
    """Atualiza parcialmente uma tarefa."""
    return servico.atualizar(tarefa_id, usuario.id, _montar_alteracoes(dados))


@router.delete(
    "/{tarefa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover tarefa",
    responses=_RESPOSTAS_DE_UMA_TAREFA,
)
def remover_task(tarefa_id: int, usuario: UsuarioAtual, servico: Servico) -> Response:
    """Remove uma tarefa definitivamente."""
    servico.remover(tarefa_id, usuario.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
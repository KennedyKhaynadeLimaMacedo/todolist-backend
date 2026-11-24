# Todo List API — Backend

API REST de gerenciamento de tarefas construída com Python, FastAPI, SQLAlchemy, Pydantic e pandas, desenvolvida no curso Desenvolvedor Full Stack — SENAC Minas Gerais (UC 2).

## Arquitetura em camadas

A aplicação segue separação em camadas para manter regras de domínio isoladas de HTTP e persistência:

- `app/api/` — rotas (`routers`), dependências (`UsuarioAtual`, injeção de serviços) e tratamento de erros HTTP.
- `app/schemas/` — contratos de entrada e saída com Pydantic (`EsquemaDeSaida`, `AnalyticsOut`, etc.).
- `app/services/` — regras de aplicação e análises de dados (`AnalyticsServico`, `TarefaServico`).
- `app/models/` — entidades de domínio com comportamento próprio (`Tarefa`, `Usuario`) e enumerações (`PrioridadeTarefa`, `StatusTarefa`).
- `app/repositories/` — acesso a dados via SQLAlchemy (`TarefaRepositorio`, etc.).
- `app/db/` — configuração de conexão, sessão e criação de tabelas.
- `app/core/` — configurações de ambiente, segurança/JWT e exceções de domínio.

## Pré-requisitos e instalação

- Python 3.12+ (ou ambiente compatível com as dependências do `requirements.txt`)
- `pip` e ambiente virtual (`venv`)

No Windows (PowerShell), na raiz do projeto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Para subir a API em desenvolvimento:


uvicorn app.main:app --reload

Documentação interativa disponível em http://127.0.0.1:8000/docs (ou http://localhost:8000/docs).


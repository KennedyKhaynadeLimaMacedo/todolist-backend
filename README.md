# Todo List API — Backend

API REST para gerenciamento de usuários e tarefas, desenvolvida em **Python** com **FastAPI**. O backend oferece cadastro e autenticação de usuários, além de operações para criar, consultar, atualizar e excluir tarefas.

A API utiliza autenticação por token **JWT**. Cada usuário pode acessar somente as próprias tarefas, e as senhas são armazenadas em formato de hash com **bcrypt**.

> **Status:** versão `0.9.0`. Este README documenta a estrutura, a configuração local, as funcionalidades e os endpoints descritos para esta versão do backend.

---

## 1. Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Linguagem principal |
| FastAPI | Construção da API REST |
| Uvicorn | Servidor ASGI para executar a aplicação |
| SQLAlchemy | Mapeamento e comunicação com o banco de dados |
| SQLite | Banco de dados para desenvolvimento local |
| PostgreSQL | Opção de banco de dados para hospedagem |
| Pydantic | Validação dos dados de entrada e saída |
| bcrypt | Hash de senhas |
| PyJWT | Geração e validação de tokens JWT |
| python-dotenv | Leitura de variáveis do arquivo `.env` |
| pytest | Execução dos testes automatizados |
| HTTPX | Cliente HTTP utilizado nos testes |

---

## 2. Arquitetura do projeto

O backend está organizado em camadas para separar responsabilidades e facilitar a manutenção.

```text
todo-list-backend-kennedy/
│
├── app/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── tasks.py
│   │   │   └── usuarios.py
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── datas.py
│   │   ├── exceptions.py
│   │   └── security.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── enums.py
│   │   ├── tarefa.py
│   │   └── usuario.py
│   │
│   ├── repositories/
│   │   ├── base.py
│   │   ├── tarefa.py
│   │   └── usuario.py
│   │
│   ├── schemas/
│   │   ├── base.py
│   │   ├── tarefa.py
│   │   └── usuario.py
│   │
│   ├── services/
│   │   ├── tarefa.py
│   │   └── usuario.py
│   │
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_dominio.py
│   └── test_seguranca.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

*Observação: a árvore acima representa a estrutura documentada para o projeto. Se algum arquivo tiver sido adicionado, removido ou renomeado na versão atual, atualize esta seção para refletir a estrutura real do repositório.*

### Responsabilidade de cada camada

- **API / Routers (`app/api/`):** recebe requisições HTTP, chama os serviços e devolve as respostas. Também reúne dependências para obter o banco de dados e o usuário autenticado.
- **Services (`app/services/`):** concentra as operações e regras de negócio, como cadastro, login e gerenciamento de tarefas.
- **Repositories (`app/repositories/`):** realiza o acesso ao banco de dados, incluindo consultas, gravações e exclusões.
- **Models (`app/models/`):** representa as entidades armazenadas no banco, como `Usuario` e `Tarefa`, além das enumerações de status e prioridade.
- **Schemas (`app/schemas/`):** define e valida os dados aceitos e devolvidos pela API com Pydantic.
- **Core (`app/core/`):** reúne configurações, funções de data e hora, segurança e exceções.
- **DB (`app/db/`):** configura a conexão, o mecanismo e as sessões do SQLAlchemy.
- **Tests (`tests/`):** contém os testes automatizados da API, das regras de domínio e da segurança.

### Fluxo de uma requisição

```text
Cliente / Frontend
       |
       v
  API / Router
       |
       v
    Service
       |
       v
  Repository
       |
       v
 Banco de dados
```

A resposta percorre o caminho inverso até chegar ao cliente. Essa separação evita misturar regras de negócio, rotas HTTP e consultas ao banco.

---

## 3. Funcionalidades

### Usuários

- Cadastro de novos usuários.
- Validação de nome, e-mail e senha.
- Normalização do e-mail para letras minúsculas.
- Verificação de e-mail já cadastrado.
- Armazenamento da senha em hash com bcrypt.
- Login com e-mail e senha.
- Geração de token de acesso JWT.
- Consulta dos dados do usuário autenticado.

### Tarefas

- Criar tarefas.
- Listar as tarefas do usuário autenticado.
- Consultar uma tarefa pelo ID.
- Atualizar parcialmente uma tarefa.
- Excluir uma tarefa.
- Definir prioridade.
- Definir prazo.
- Marcar uma tarefa como concluída ou pendente.
- Registrar a data de conclusão.
- Impedir que um usuário acesse ou altere tarefas de outra conta.

### Regras de negócio documentadas

- O e-mail deve ser único.
- Toda tarefa é criada com status `pendente`.
- A prioridade padrão é `media`.
- O usuário responsável pela tarefa é identificado pelo token, e não por um ID enviado no corpo da requisição.
- O título da tarefa não pode ficar vazio.
- Uma tarefa concluída registra a data e hora da conclusão.
- Ao reabrir uma tarefa, a data de conclusão é removida.
- As senhas não são devolvidas nas respostas da API.

---

## 4. Pré-requisitos

Antes de executar o projeto, tenha instalado:

- Python. Recomenda-se utilizar Python 3.12 para este ambiente.
- pip, gerenciador de pacotes do Python.
- Git, caso queira clonar o repositório.
- Um terminal, como PowerShell ou Prompt de Comando.

O SQLite é utilizado por meio do módulo `sqlite3` incluído no Python. Para utilizar PostgreSQL, também é necessário ter acesso a um banco PostgreSQL.

---

## 5. Instalação e execução local

Execute os comandos a partir da pasta raiz do repositório, onde estão `requirements.txt` e a pasta `app`.

### 5.1. Clonar o repositório

Use o endereço do repositório GitHub:

```bash
git clone URL_DO_REPOSITORIO
cd todo-list-backend-kennedy
```

Substitua `URL_DO_REPOSITORIO` pelo endereço real do repositório. Se o projeto já estiver no computador, abra o terminal diretamente na pasta raiz do repositório.

### 5.2. Criar o ambiente virtual

No Windows, utilizando PowerShell:

```powershell
py -3.12 -m venv .venv
```

No Linux ou macOS:

```bash
python3.12 -m venv .venv
```

### 5.3. Ativar o ambiente virtual

No Windows / PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Windows / Prompt de Comando:

```bat
.venv\Scripts\activate.bat
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Após a ativação, o nome `.venv` deverá aparecer no início da linha do terminal.

Se o PowerShell bloquear a execução do script, execute este comando somente na sessão atual do terminal e tente ativar novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 5.4. Instalar as dependências

Com o ambiente virtual ativado e estando na raiz do projeto:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` deve conter somente dependências válidas, uma por linha, com as versões ou restrições correspondentes. Antes de instalar, confira se não existem marcadores de conflito do Git, como `<<<<<<<`, `=======` ou `>>>>>>>`. Se existirem, resolva o conflito no arquivo e mantenha apenas a lista final de dependências.

### 5.5. Configurar as variáveis de ambiente

Na raiz do projeto, copie o arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

No Linux ou macOS:

```bash
cp .env.example .env
```

O arquivo `.env` deve ficar na raiz do projeto. Ele contém as configurações de conexão com o banco e autenticação.

### 5.6. Gerar o segredo JWT

Gere um segredo aleatório com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o valor gerado para a variável `JWT_SECRET` no arquivo `.env`. Não compartilhe esse valor e não o envie ao Git.

### 5.7. Iniciar a aplicação

Com o ambiente virtual ativado, execute na raiz do projeto:

```bash
python -m uvicorn app.main:app --reload
```

Por padrão, a API ficará disponível em:

```text
http://127.0.0.1:8000
```

Para utilizar outra porta, por exemplo `8001`:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Para interromper o servidor, pressione `CTRL + C`.

---

## 6. Configuração do banco de dados

O projeto documenta o uso de SQLite localmente e PostgreSQL em ambiente hospedado. A conexão é definida pela variável `DATABASE_URL`.

### 6.1. SQLite

O SQLite é a opção indicada para desenvolvimento local, pois não exige a instalação de um servidor de banco de dados.

No arquivo `.env`:

```env
DATABASE_URL=sqlite:///./todo_list.db
JWT_SECRET=COLOQUE_SEU_SEGREDO_GERADO
JWT_EXPIRA_MINUTOS=120
```

O arquivo `todo_list.db` será criado no diretório de execução quando necessário. As tabelas são preparadas durante a inicialização da aplicação, conforme a configuração do backend.

### 6.2. PostgreSQL no Render

Para utilizar PostgreSQL:

1. Crie ou acesse um banco PostgreSQL no Render.
2. Abra a área de conexões do banco.
3. Copie a URL de conexão apropriada para o ambiente em que a aplicação será executada.
4. Configure a variável `DATABASE_URL` no ambiente da aplicação, utilizando o formato de driver compatível com o projeto.

Formato documentado:

```env
DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@HOST/BANCO?sslmode=require
JWT_SECRET=COLOQUE_SEU_SEGREDO_GERADO
JWT_EXPIRA_MINUTOS=120
```

Substitua `USUARIO`, `SENHA`, `HOST` e `BANCO` pelos dados fornecidos pelo serviço de hospedagem. A dependência do driver PostgreSQL correspondente também deve estar presente no `requirements.txt`.

A URL interna do Render é indicada para serviços que se comunicam dentro da infraestrutura do Render. Para conexões externas, utilize a URL externa. Nunca publique credenciais reais do banco ou o segredo JWT.

### 6.3. Criação das tabelas

A aplicação utiliza `Base.metadata.create_all()` durante a inicialização para criar tabelas ausentes, conforme os modelos registrados.

Esse mecanismo não substitui um sistema de migrações. Alterações futuras na estrutura das tabelas podem exigir migrações ou atualização controlada do banco existente.

---

## 7. Documentação da API

Com o servidor em execução, a documentação interativa pode ser acessada pelos endereços:

**Swagger UI**

```text
http://127.0.0.1:8000/docs
```

**ReDoc**

```text
http://127.0.0.1:8000/redoc
```

O Swagger permite visualizar os endpoints, consultar parâmetros e enviar requisições para testar a API. Se o servidor estiver utilizando outra porta, substitua `8000` pela porta configurada.

---

## 8. Endpoints documentados

| Método | Rota | Descrição | Autenticação |
|---|---|---|---|
| GET | `/` | Verificar se a API está no ar | Não |
| POST | `/usuarios` | Cadastrar usuário | Não |
| POST | `/usuarios/login` | Realizar login | Não |
| GET | `/usuarios/me` | Consultar usuário autenticado | Sim |
| POST | `/tasks` | Criar tarefa | Sim |
| GET | `/tasks` | Listar tarefas do usuário | Sim |
| GET | `/tasks/{tarefa_id}` | Buscar tarefa pelo ID | Sim |
| PATCH | `/tasks/{tarefa_id}` | Atualizar tarefa | Sim |
| DELETE | `/tasks/{tarefa_id}` | Excluir tarefa | Sim |

As rotas de tarefas e a rota `/usuarios/me` exigem um token JWT válido.

---

## 9. Exemplos de utilização

Os exemplos abaixo ilustram o formato das requisições e respostas descritas para a API. Os IDs, tokens e datas são demonstrativos; as respostas reais dependem dos dados e da configuração do ambiente.

### 9.1. Verificar se a API está funcionando

**Requisição**

```http
GET /
```

**Resposta ilustrativa**

```json
{
  "mensagem": "Todo List API no ar",
  "documentacao": "/docs"
}
```

### 9.2. Cadastrar usuário

**Requisição**

```http
POST /usuarios
```

**Corpo JSON**

```json
{
  "nome": "Usuário Exemplo",
  "email": "usuario@example.com",
  "senha": "senha123"
}
```

**Resposta ilustrativa — `201 Created`**

```json
{
  "id": 1,
  "nome": "Usuário Exemplo",
  "email": "usuario@example.com",
  "criadoEm": "2026-11-26T12:00:00Z"
}
```

A senha e seu hash não são enviados na resposta.

### 9.3. Realizar login

**Requisição**

```http
POST /usuarios/login
```

**Corpo JSON**

```json
{
  "email": "usuario@example.com",
  "senha": "senha123"
}
```

**Resposta ilustrativa — `200 OK`**

```json
{
  "accessToken": "TOKEN_JWT_GERADO",
  "tokenType": "bearer",
  "expiraEm": "2026-11-26T14:00:00Z",
  "usuario": {
    "id": 1,
    "nome": "Usuário Exemplo",
    "email": "usuario@example.com",
    "criadoEm": "2026-11-26T12:00:00Z"
  }
}
```

O token recebido deve ser utilizado para acessar as rotas protegidas.

### 9.4. Autorizar as próximas requisições

No Swagger, clique em **Authorize** e informe o token de acesso recebido no login, no formato Bearer.

Em outros clientes HTTP, envie o cabeçalho:

```http
Authorization: Bearer TOKEN_JWT_GERADO
```

### 9.5. Consultar o usuário autenticado

**Requisição**

```http
GET /usuarios/me
```

**Cabeçalho**

```http
Authorization: Bearer TOKEN_JWT_GERADO
```

A rota retorna os dados do usuário correspondente ao token.

### 9.6. Criar tarefa

**Requisição**

```http
POST /tasks
```

**Corpo JSON**

```json
{
  "titulo": "Estudar Python",
  "prioridade": "alta",
  "prazo": "2026-12-10"
}
```

**Resposta ilustrativa — `201 Created`**

```json
{
  "id": 1,
  "usuarioId": 1,
  "titulo": "Estudar Python",
  "status": "pendente",
  "prioridade": "alta",
  "prazo": "2026-12-10",
  "criadoEm": "2026-11-26T12:00:00Z",
  "atualizadoEm": "2026-11-26T12:00:00Z",
  "concluidoEm": null
}
```

O campo `usuarioId` é definido pelo backend a partir do usuário autenticado e não deve ser enviado no corpo da criação.

A prioridade é opcional. Quando não informada, o valor padrão documentado é `media`. O prazo também é opcional.

### 9.7. Listar tarefas

**Requisição**

```http
GET /tasks
```

Retorna somente as tarefas pertencentes ao usuário autenticado. A API também informa a quantidade de resultados no cabeçalho `X-Total-Count`, conforme a implementação documentada.

### 9.8. Buscar uma tarefa pelo ID

**Requisição**

```http
GET /tasks/1
```

Retorna os dados da tarefa solicitada, desde que ela pertença ao usuário autenticado.

### 9.9. Atualizar uma tarefa

**Requisição**

```http
PATCH /tasks/1
```

**Corpo JSON**

```json
{
  "titulo": "Estudar FastAPI",
  "prioridade": "urgente",
  "status": "concluida"
}
```

O método `PATCH` permite alterar somente os campos enviados. Os campos não informados permanecem como estavam.

**Status aceitos**

- `pendente`
- `concluida`

**Prioridades aceitas**

- `baixa`
- `media`
- `alta`
- `urgente`

Quando o status passa para `concluida`, o sistema registra a data e hora da conclusão. Quando volta para `pendente`, essa data é removida.

Para alterar somente o prazo:

```json
{
  "prazo": "2026-12-15"
}
```

Para remover o prazo:

```json
{
  "prazo": null
}
```

### 9.10. Excluir uma tarefa

**Requisição**

```http
DELETE /tasks/1
```

Quando a exclusão é realizada com sucesso, a API retorna:

```http
204 No Content
```

Essa resposta não possui corpo.

---

## 10. Formato dos dados

Os schemas utilizam conversão automática de nomes de campos.

No código Python, os atributos seguem o padrão `snake_case`. Nas requisições e respostas JSON, os nomes são apresentados em `camelCase` quando aplicável.

| Código Python | JSON |
|---|---|
| `access_token` | `accessToken` |
| `usuario_id` | `usuarioId` |
| `criado_em` | `criadoEm` |
| `atualizado_em` | `atualizadoEm` |
| `concluido_em` | `concluidoEm` |

As datas de prazo utilizam o formato `AAAA-MM-DD`. Os campos de data e hora são representados em formato ISO 8601.

---

## 11. Autenticação e segurança

A autenticação utiliza tokens JWT assinados com o algoritmo HS256.

O processo documentado funciona da seguinte maneira:

1. O usuário realiza o cadastro.
2. A senha é transformada em hash com bcrypt.
3. No login, o sistema confere o e-mail e a senha.
4. Se as credenciais forem válidas, é emitido um token JWT.
5. O cliente envia o token no cabeçalho `Authorization`.
6. A API valida o token e identifica o usuário.
7. As operações com tarefas utilizam o ID desse usuário para limitar o acesso aos próprios registros.

### Medidas implementadas

- Senhas armazenadas em hash, sem armazenamento em texto puro.
- Validação de token JWT.
- Tempo de expiração configurável para os tokens.
- E-mail único por usuário.
- Rotas protegidas por autenticação.
- Verificação de propriedade das tarefas.
- Separação entre dados de entrada e dados de saída.
- Respostas de usuário sem senha ou hash.
- Configurações sensíveis mantidas em variáveis de ambiente.

O arquivo `.env` não deve ser enviado ao Git ou compartilhado publicamente.

---

## 12. Códigos de resposta HTTP

| Código | Significado | Situação |
|---|---|---|
| `200` | OK | Consulta ou login realizado |
| `201` | Created | Usuário ou tarefa criado |
| `204` | No Content | Tarefa excluída |
| `400` | Bad Request | Erro de domínio não classificado em outra categoria |
| `401` | Unauthorized | Token ausente, inválido ou expirado; credenciais incorretas |
| `404` | Not Found | Recurso não encontrado |
| `409` | Conflict | E-mail já cadastrado |
| `422` | Unprocessable Entity | Dados inválidos ou regra de negócio violada |

As respostas de erro de domínio utilizam o campo `detail`. Os erros de validação também podem trazer uma lista de detalhes no campo `erros`, conforme a implementação.

Exemplo:

```json
{
  "detail": "Token de acesso ausente."
}
```

---

## 13. Testes automatizados

O projeto documenta testes com `pytest` e `FastAPI TestClient`. Os testes utilizam um banco SQLite temporário, separado do banco utilizado durante o desenvolvimento.

Para executar todos os testes:

```bash
python -m pytest
```

Para visualizar os testes com mais detalhes:

```bash
python -m pytest -v
```

Arquivos de teste documentados:

- `test_api.py`: verifica os endpoints HTTP, o cadastro e as respostas da API.
- `test_dominio.py`: verifica regras de domínio relacionadas ao usuário.
- `test_seguranca.py`: verifica a geração e a validação de hashes de senha.
- `conftest.py`: configura o banco temporário e o cliente de testes.

---

## 14. Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL de conexão com o banco de dados |
| `JWT_SECRET` | Segredo utilizado para assinar os tokens |
| `JWT_EXPIRA_MINUTOS` | Tempo de validade do token em minutos |

Exemplo de configuração local:

```env
DATABASE_URL=sqlite:///./todo_list.db
JWT_SECRET=SEU_SEGREDO_GERADO
JWT_EXPIRA_MINUTOS=120
```

O valor de `JWT_SECRET` deve ter pelo menos 32 caracteres. Utilize um valor aleatório e mantenha-o privado.

---

## 15. Limitações e próximos passos

Possíveis melhorias futuras:

- Implementar migrações de banco de dados com Alembic.
- Ampliar a cobertura de testes para todas as operações de tarefas.
- Configurar CORS de acordo com a origem autorizada do frontend.
- Configurar logs e monitoramento.
- Publicar e configurar o serviço em ambiente de produção.
- Concluir a integração com o frontend.

A criação automática das tabelas não realiza migrações de alterações em tabelas existentes. Em caso de mudança nos modelos, é necessário tratar a atualização do banco de forma adequada.

---

## 16. Considerações finais

O **Todo List Backend** oferece uma estrutura organizada para o gerenciamento de usuários e tarefas. A arquitetura em camadas separa as responsabilidades da aplicação, enquanto o FastAPI disponibiliza os endpoints para comunicação com o frontend.

O SQLAlchemy permite trabalhar com diferentes bancos de dados, e o JWT e o bcrypt ajudam a proteger o acesso e as informações dos usuários.

---

**Projeto:** Todo List Backend  
**Versão da API:** `1.0.0`  
**Linguagem:** Python  
**Framework:** FastAPI
#   l y t h r a - f r o n t e n d  
 
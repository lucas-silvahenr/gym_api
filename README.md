# Gym API

API REST para gerenciamento de exercícios e treinos desenvolvida com
**FastAPI**.\
Este projeto foi criado como parte de um portfólio backend com foco em
demonstrar boas práticas de desenvolvimento, organização de código,
testes automatizados e containerização.

O objetivo é apresentar uma estrutura próxima de aplicações reais
utilizadas em produção.

------------------------------------------------------------------------

# Visão geral

A **Gym API** permite gerenciar exercícios e dados relacionados a
treinos através de endpoints HTTP seguindo princípios de APIs REST.

Este projeto demonstra conhecimentos práticos em:

-   desenvolvimento de APIs com Python
-   arquitetura organizada para aplicações backend
-   integração com banco de dados relacional
-   containerização com Docker
-   testes automatizados
-   gerenciamento de dependências

------------------------------------------------------------------------

# Tecnologias utilizadas

-   Python
-   FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Docker
-   Docker Compose
-   Poetry
-   Pytest

------------------------------------------------------------------------

# Funcionalidades

A API permite:

- Cadastro de usuários
- Autenticação com JWT
- CRUD de exercícios
- Criação e gerenciamento de treinos

------------------------------------------------------------------------

# Estrutura do projeto

     gym_api/
    │
    ├── gym_api/
    |   ├── routers/
    |   |   ├── auth.py
    |   │   ├── users.py
    |   │   └── workout.py
    |   |
    │   ├── app.py
    │   ├── database.py
    │   ├── models.py
    |   ├── schemas.py
    │   ├── security.py
    │   └── settings.py
    │
    ├── tests/
    |   ├── conftest.py
    |   ├── test_app.py
    |   ├── test_auth.py
    |   ├── test_db.py
    |   ├── test_security.py
    |   ├── test_users.py
    |   └── test_workout.py
    │
    ├── Dockerfile
    ├── compose.yaml
    ├── entrypoint.sh
    ├── pyproject.toml
    └── poetry.lock

------------------------------------------------------------------------

# Descrição dos Principais componentes

**gym_api/routers/**\
Definição das rotas da API.

**gym_api/app.py**\
Responsável por iniciar a aplicação FastAPI e registrar as rotas.

**gym_api/models.py**\
Definição das entidades do banco de dados.

**gym_api/database.py**\
Responsável pela configuração da conexão com o banco de dados e gerenciamento de sessões do SQLAlchemy.

**gym_api/schemas.py**\
Schemas utilizados para validação e serialização de dados utilizando Pydantic.

**gym_api/security.py**\
Arquivo responsável pela parte de autenticação JWT.


**tests/**\
Testes automatizados garantindo o funcionamento da aplicação.

------------------------------------------------------------------------


# Como executar o projeto

## 1. Clonar o repositório

    git clone https://github.com/lucas-silvahenr/gym_api.git
    cd gym_api

## 2. Executar com Docker

    docker compose up --build

A aplicação ficará disponível em:

    http://localhost:8000

------------------------------------------------------------------------

# Documentação da API

O FastAPI gera documentação automática para todos os endpoints.

Swagger UI

    http://localhost:8000/docs

ReDoc

    http://localhost:8000/redoc

------------------------------------------------------------------------

# Testes

Para executar os testes automatizados:

    pytest -s -x --cov=gym_api -vv

Os testes garantem que as rotas e regras de negócio da aplicação
funcionem corretamente.

------------------------------------------------------------------------

# Melhorias futuras

Algumas melhorias planejadas para evolução do projeto:

-   deploy em ambiente cloud
-   criação de treinos personalizados
-   adição de cache
-   adição de rate limit
-   paginação de resultados
-   aumento da cobertura de testes

------------------------------------------------------------------------

# Objetivo educacional

Este projeto foi desenvolvido como parte de um portfólio backend com o objetivo de demonstrar habilidades em:

- desenvolvimento de APIs REST
- arquitetura de aplicações backend
- autenticação com JWT
- integração com banco relacional
- testes automatizados
- containerização de aplicações
------------------------------------------------------------------------


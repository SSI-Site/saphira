#### BASE IMAGE ####
# Criamos um container com o uv ja instalado
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

# Flags que otimizam o funcionamento do uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Pasta de trabalho para o saphira
WORKDIR /app

# Cria um cache com pyproject.toml e uv.lock, instala as dependencias do projeto antes do projeto em si
# Isso ajuda no cache layer!
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY src/ /app

#### DEVELOPMENT ####
# Criamos uma imagem para development com o uv e as dev-dependencies
FROM base AS dev
# Copiamos o projeto com os tests
COPY tests/ /app/tests

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

#### BUILDER FOR PROD ####
FROM base AS builder

# Agora sim instalamos o projeto
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

#### PROD ####
# Criamos uma nova imagem sem o uv para ser melhorar o desempenho e o tamanho final do container
FROM python:3.12-slim-bookworm AS runner

# Otimizações do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cria um appuser, um usuário de baixa permissão para executar em produção
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

WORKDIR /app

# Copia o projeto baixado em builder para imagem atual
COPY --from=builder --chown=appuser:appuser /app /app

# Adiciona nossas dependencias para o $PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expoe a porta 8000 que será usada pelo saphira
EXPOSE 8000

# Rodamos em produção
CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "saphira.wsgi:application" ]

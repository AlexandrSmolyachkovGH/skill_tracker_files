FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl build-essential gcc libffi-dev libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /skill_tracker_file

COPY ./pyproject.toml ./poetry.lock ./


RUN poetry install --no-root

COPY . .
COPY .env .env

EXPOSE 8002
CMD ["uvicorn", "file_service.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]

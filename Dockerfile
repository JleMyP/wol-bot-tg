FROM python:3.9-slim as builder

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update \
 && apt-get install -y gcc libssl-dev libffi-dev \
 && pip install "cryptography<3.4" \
 && pip install poetry

WORKDIR /deps

COPY poetry.lock ./
COPY pyproject.toml ./

RUN poetry export -f requirements.txt -o requirements.txt --without-hashes \
 && pip wheel -w /wheels/ -r requirements.txt


FROM python:3.9-slim

WORKDIR /wheels
COPY --from=builder /wheels ./
COPY --from=builder /deps/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./ /app
WORKDIR /app

ENV PYTHONUNBUFFERED=1

CMD python main.py

FROM python:3.10.6-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app/

RUN apt-get update && \
    apt-get install -y \
    bash \
    build-essential \
    gcc \
    libffi-dev \
    musl-dev \
    openssl \
    gettext \
    libpq-dev \
    postgresql \
    postgresql-contrib

RUN pip install --upgrade pip
COPY ./src/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
COPY . .

EXPOSE 8000
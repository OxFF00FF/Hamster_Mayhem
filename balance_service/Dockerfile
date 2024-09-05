FROM python:3.9-alpine

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

COPY . /app

RUN pip install requests fake-useragent

COPY .env /app/.env

CMD ["python", "balance.py"]
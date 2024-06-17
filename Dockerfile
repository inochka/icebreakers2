FROM python:3.10.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/usr/src/app
WORKDIR $APP_HOME
ENV PYTHONPATH=${APP_HOME}

# ставим питон
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
       python3 \
       python3-pip \
       curl \
       ca-certificates

COPY . .

# Установка зависимостей Python
RUN pip install --upgrade pip \
    && pip install --retries=3 --no-cache-dir -r backend/requirements.txt

CMD ["/bin/sh", "-c", "$@"]

# Build dependencies
FROM python:3.10-slim AS build-env

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
      build-essential \
      pkg-config \
      cmake \
      gcc \
      libmariadb-dev \
      python3-dev \
      default-libmysqlclient-dev \
      libzip-dev \
      libjpeg-dev \
      vim

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Exec image
FROM python:3.10-slim

COPY --from=build-env /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build-env /usr/local/bin /usr/local/bin
COPY --from=build-env /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu
COPY --from=build-env /lib/x86_64-linux-gnu /lib/x86_64-linux-gnu

ADD . /app
WORKDIR /app

RUN chmod +x crawling_and_embedding.sh
RUN chmod +x /app/cgi-bin/*.py
RUN chmod -R 777 /app/cache

EXPOSE 8000

CMD ["python", "-u", "/app/server.py"]


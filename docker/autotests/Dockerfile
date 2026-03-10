FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pytest.ini conftest.py ./
COPY src ./src
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY docker/autotests/run-tests.sh /usr/local/bin/run-tests.sh
RUN chmod +x /usr/local/bin/run-tests.sh

CMD ["/usr/local/bin/run-tests.sh"]

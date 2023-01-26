FROM debian:testing-slim
LABEL maintainer="edenceHealth <info@edence.health>"

RUN set -eux; \
  export \
    AG="apt-get -yq" \
    DEBIAN_FRONTEND=noninteractive \
  ; \
  $AG update; \
  $AG upgrade; \
  $AG install --no-install-recommends \
    gcc \
    libmariadb-dev \
    mariadb-client \
    python3-dev \
    python3-pip \
  ; \
  rm -rf \
    /var/lib/apt/lists/* \
  ;

COPY requirements.txt /
RUN set -eux; \
  pip3 install -r /requirements.txt; \
  pip3 cache purge;

WORKDIR /app
COPY src/mysql2csv ./mysql2csv
ENV PYTHONPATH="/app"

WORKDIR /output
ENTRYPOINT ["python3", "-m", "mysql2csv"]

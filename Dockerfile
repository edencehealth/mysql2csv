FROM debian:testing-slim
LABEL maintainer="edenceHealth <info@edence.health>"

COPY requirements.txt /

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
  pip3 install -r /requirements.txt; \
  pip3 cache purge; \
  $AG purge \
    gcc \
    python3-dev \
  ; \
  $AG autoremove; \
  rm -rf \
    /var/lib/apt/lists/* \
  ;

WORKDIR /app
COPY src/mysql2csv ./mysql2csv
ENV PYTHONPATH="/app"

WORKDIR /output
ENTRYPOINT ["python3", "-m", "mysql2csv"]

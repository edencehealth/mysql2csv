# mysql2csv

This is a Docker utility for saving the contents of MySQL / MariaDB database
tables into CSV files. It is published publicly to
[Docker Hub at edence/mysql2csv](https://hub.docker.com/r/edence/mysql2csv).

## Configuration

The program accepts its configuration from environment variables and
command-line arguments.

### Command-line Arguments

The program produces the following usage documentation when invoked with the
`--help` and `-h` command-line arguments:

```
usage: mysql2csv [-h] [--loglevel LOG_LEVEL] [--host DB_HOST] [--user DB_USER]
                 [--password DB_PASSWORD] [--database DB_DATABASE]
                 [--chunksize CHUNK_SIZE] [--path OUTPUT_PATH]
                 [--csvdialect CSV_DIALECT] [--csvencoding CSV_ENCODING]
                 table_name [table_name ...]

generates CSV files from MySQL/MariaDB database tables

positional arguments:
  table_name            name of database table to copy into local CSV output
                        file (multiple can be specified)

options:
  -h, --help            show this help message and exit
  --loglevel LOG_LEVEL  determines how verbosely to log program operation;
                        possible values: "CRITICAL", "FATAL", "ERROR", "WARN",
                        "WARNING", "INFO", "DEBUG" (default: INFO)
  --host DB_HOST        network host to use when connecting to the database
                        (default: 127.0.0.1)
  --user DB_USER        username to use when connecting to the database
                        (default: root)
  --password DB_PASSWORD
                        password string to use when connecting to the database
                        (default: password)
  --database DB_DATABASE
                        database name to use after connecting to the database
                        (default: root)
  --chunksize CHUNK_SIZE
                        data retrieved from the server will be returned in
                        chunks of this many rows; using a larger chunk size
                        generally results in faster operation but uses more
                        memory; selecting an excessive size will result in the
                        program running out of memory (default: 1000)
  --path OUTPUT_PATH    the base output path to use when creating CSV files
                        (default: /output)
  --csvdialect CSV_DIALECT
                        python csv.writer dialect; possible values: "excel",
                        "excel-tab", "unix"; see:
                        https://docs.python.org/3/library/csv.html#csv.Dialect
                        (default: unix)
  --csvencoding CSV_ENCODING
                        character encoding used when writing CSV files
                        (default: utf8)

```

### Docker Compose Configuration

Here is an example of how the image can be deployed in a docker compose file:

```yaml
services:
  mysql2csv:
    environment:
      CHUNK_SIZE: 100000
      CSV_DIALECT: "excel"  # see also: unix ; https://docs.python.org/3/library/csv.html
      DB_DATABASE: "mysql"
      DB_HOST: "db"
      DB_PASSWORD: "testing"
      DB_USER: "root"
      LOG_LEVEL: "DEBUG"
    command:
      - time_zone
      - time_zone_transition
    volumes:
      - "./output:/output"
```
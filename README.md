# mysql2csv

This is a Docker utility for saving the contents of MySQL and MariaDB database
tables into CSV files.

## Configuration

The program accepts its configuration from environment variables and
command-line arguments.

### Command-line Arguments

The program produces the following usage documentation when invoked with the
`--help` and `-h` command-line arguments:

```
usage: mysql2csv [-h] [--debug] [--user USER] [--password PASSWORD]
                 [--host HOST] [--database DATABASE] [--path PATH]
                 [--csvdialect {excel,excel-tab,unix}]
                 [--csvencoding CSVENCODING]
                 [--loglevel {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG}]
                 table_name [table_name ...]

generates a CSV files from the MySQL/MariaDB databases

positional arguments:
  table_name            the name of the tables to create csv files for

options:
  -h, --help            show this help message and exit
  --debug               enable debug output (default: False)
  --user USER           username to use when connecting to the database
                        (default: root)
  --password PASSWORD   password string to use when connecting to the database
                        (default: testing)
  --host HOST           network host to use when connecting to the database
                        (default: db)
  --database DATABASE   database name to use after connecting to the database
                        (default: mysql)
  --path PATH           the base output path to use when creating csv files
                        (default: /output)
  --csvdialect {excel,excel-tab,unix}
                        the python csv.writer dialect. see:
                        https://docs.python.org/3/library/csv.html (default:
                        excel)
  --csvencoding CSVENCODING
                        the character encoding to use when writing the CSV files
                        (default: utf8)
  --loglevel {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG}
                        the python logging level to use (default: DEBUG)

```

### Docker Compose Configuration

Here is an example of how the image can be deployed in a docker compose file:

```yaml
services:
  mysql2csv:
    environment:
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
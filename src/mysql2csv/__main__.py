#!/usr/bin/env python3
""" utility for exporting mysql tables to csv files  """
import argparse
import csv
import logging
import os
import sys

import mariadb


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with sys.exit
    """
    argp = argparse.ArgumentParser(
        prog=__package__,
        description=("generates a CSV files from the MySQL/MariaDB databases"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argp.add_argument(
        "--debug",
        action="store_true",
        help="enable debug output",
    )
    argp.add_argument(
        "--user",
        default=os.environ.get("DB_USER", "root"),
        help="username to use when connecting to the database",
    )
    argp.add_argument(
        "--password",
        default=os.environ.get("DB_PASSWORD", "password"),
        help="password string to use when connecting to the database",
    )
    argp.add_argument(
        "--host",
        default=os.environ.get("DB_HOST", "127.0.0.1"),
        help="network host to use when connecting to the database",
    )
    argp.add_argument(
        "--database",
        default=os.environ.get("DB_DATABASE", "root"),
        help="database name to use after connecting to the database",
    )
    argp.add_argument(
        "--path",
        default=os.environ.get("OUTPUT_PATH", "/work"),
        help="the base output path to use when creating csv files",
    )
    argp.add_argument(
        "--csvdialect",
        default=os.environ.get("CSV_DIALECT", "excel"),
        help="the python csv.writer dialect. see: https://docs.python.org/3/library/csv.html",
    )
    argp.add_argument(
        "--loglevel",
        default=os.environ.get("LOG_LEVEL", "INFO"),
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="the python logging level to use",
    )
    argp.add_argument(
        "table_name",
        nargs="+",
        help="the name of the tables to create csv files for",
    )
    args = argp.parse_args()
    logging.basicConfig(level=args.loglevel)

    conn = mariadb.connect(
        user=args.user,
        password=args.password,
        host=args.host,
        database=args.database,
    )
    cur = conn.cursor()

    for table_name in args.table_name:
        logging.debug("starting on table: %s", table_name)
        cur.execute(f"SELECT * FROM {table_name}")
        fieldnames = [i[0] for i in cur.description]
        data = cur.fetchall()

        output_filename = os.path.join(args.path, table_name + ".csv")
        with open(output_filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, dialect=args.csvdialect)
            writer.writerow(fieldnames)
            writer.writerows(data)
        logging.info("wrote to file: %s", output_filename)

    conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())

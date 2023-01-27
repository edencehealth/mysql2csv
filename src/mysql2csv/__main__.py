#!/usr/bin/env python3
""" utility for exporting mysql tables to csv files  """
import argparse
import csv
import logging
import os
import sys
from typing import Sequence

import mariadb


def dump_tables(
    cnxn: mariadb.Connection,
    tables: Sequence[str],
    output_dir: str,
    dialect: str,
    encoding: str = "utf8",
):
    """
    given a database server connection and a list of table names, write a CSV
    file containing the complete contents of each table into the given output
    directory; the given csv.Dialect and character encoding are used to write
    the csv output files
    """
    for table_name in tables:
        logging.debug("dumping table: %s", table_name)
        cur = cnxn.cursor()

        # attempting to prevent injection... this could be improved
        esc_table_name = cnxn.escape_string(table_name)

        cur.execute(f"SELECT * FROM {esc_table_name}")  # nosec: escaping value
        fieldnames = [i[0] for i in cur.description]
        data = cur.fetchall()

        output_filename = os.path.join(output_dir, table_name + ".csv")
        with open(output_filename, "w", newline="", encoding=encoding) as csvfile:
            writer = csv.writer(csvfile, dialect=dialect)
            writer.writerow(fieldnames)
            writer.writerows(data)
        logging.info("wrote to file: %s", output_filename)


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
        default=os.environ.get("OUTPUT_PATH", os.getcwd()),
        help="the base output path to use when creating csv files",
    )
    argp.add_argument(
        "--csvdialect",
        default=os.environ.get("CSV_DIALECT", "unix"),
        choices=csv.list_dialects(),
        help=(
            "the python csv.writer dialect; "
            "see: https://docs.python.org/3/library/csv.html#csv.Dialect"
        ),
    )
    argp.add_argument(
        "--csvencoding",
        default=os.environ.get("CSV_ENCODING", "utf8"),
        help="the character encoding to use when writing the CSV files",
    )
    argp.add_argument(
        "--loglevel",
        default=os.environ.get("LOG_LEVEL", "INFO"),
        choices=list(logging._nameToLevel)[:-1],
        help="the python logging level to use",
    )
    argp.add_argument(
        "table_name",
        nargs="+",
        help="the name of the tables to create csv files for",
    )
    args = argp.parse_args()
    logging.basicConfig(level=args.loglevel)

    with mariadb.connect(
        user=args.user,
        password=args.password,
        host=args.host,
        database=args.database,
    ) as cnxn:
        dump_tables(
            cnxn,
            args.table_name,
            args.path,
            args.csvdialect,
            args.csvencoding,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())

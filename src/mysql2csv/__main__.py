#!/usr/bin/env python3
""" utility for exporting mysql tables to CSV files  """
import argparse
import csv
import logging
import os
import sys
from typing import Final, Sequence

import mariadb

LOG_FORMAT: Final = "%(asctime)s %(levelname)s %(message)s"


def dump_tables(
    cnxn: mariadb.Connection,
    tables: Sequence[str],
    output_dir: str,
    dialect: str,
    encoding: str = "utf8",
    chunksize: int = 1000,
    overwrite: bool = False,
):
    """
    given a database server connection and a list of table names, write a CSV
    file containing the complete contents of each table into the given output
    directory; the given csv.Dialect and character encoding are used to write
    the CSV output files
    """
    for table_name in tables:
        logging.debug("dumping table: %s", table_name)

        output_filename = os.path.join(output_dir, table_name + ".csv")
        if os.path.exists(output_filename):
            if overwrite:
                logging.warning(
                    "%s: overwriting existing output file %s",
                    table_name,
                    output_filename,
                )
            else:
                logging.warning(
                    "%s: skipping table because output file %s already exists",
                    table_name,
                    output_filename,
                )
                continue

        # see https://mariadb-corporation.github.io/mariadb-connector-python/cursor.html
        cur = cnxn.cursor()
        cur.arraysize = chunksize

        # attempting to prevent injection... this could be improved
        esc_table_name = cnxn.escape_string(table_name)

        cur.execute(
            f"SELECT * FROM {esc_table_name}",  # nosec: escaping value
            buffered=False,
        )
        fieldnames = [i[0] for i in cur.description]

        with open(output_filename, "w", newline="", encoding=encoding) as csvfile:
            writer = csv.writer(csvfile, dialect=dialect)
            writer.writerow(fieldnames)
            while data := cur.fetchmany():
                writer.writerows(data)
                logging.info(
                    "%s: wrote %s-row chunk to %s",
                    table_name,
                    len(data),
                    output_filename,
                )
        logging.info(
            "%s: finished dumping table to %s (%s rows)",
            table_name,
            output_filename,
            cur.rowcount,
        )


def quoted_list(input: Sequence[str]) -> str:
    """
    return a joined, comma-separated version of the given list of strings with
    each member in double quotes; NOTE: NOT SAFE FOR UNTRUSTED INPUTS!
    """
    return ", ".join([f'"{item}"' for item in input])


def parse_bool(argument: str) -> bool:
    """parses the given argument string and returns a boolean evaluation"""
    return argument.lower().strip() in ("1", "enable", "on", "true", "y", "yes")


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with sys.exit
    """
    log_level_choices = list(logging._nameToLevel)[:-1]
    dialect_choices = csv.list_dialects()

    argp = argparse.ArgumentParser(
        prog=__package__,
        description=("generates CSV files from MySQL/MariaDB database tables"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argp.add_argument(
        "--loglevel",
        default=os.environ.get("LOG_LEVEL", "INFO"),
        metavar="LOG_LEVEL",
        choices=log_level_choices,
        help=(
            "determines how verbosely to log program operation; "
            f"possible values: {quoted_list(log_level_choices)}"
        ),
    )
    argp.add_argument(
        "--host",
        default=os.environ.get("DB_HOST", "127.0.0.1"),
        metavar="DB_HOST",
        help="network host to use when connecting to the database",
    )
    argp.add_argument(
        "--user",
        default=os.environ.get("DB_USER", "root"),
        metavar="DB_USER",
        help="username to use when connecting to the database",
    )
    argp.add_argument(
        "--password",
        default=os.environ.get("DB_PASSWORD", "password"),
        metavar="DB_PASSWORD",
        help="password string to use when connecting to the database",
    )
    argp.add_argument(
        "--database",
        default=os.environ.get("DB_DATABASE", "root"),
        metavar="DB_DATABASE",
        help="database name to use after connecting to the database",
    )
    argp.add_argument(
        "--chunksize",
        type=int,
        default=int(os.environ.get("CHUNK_SIZE", "1000")),
        metavar="CHUNK_SIZE",
        help=(
            "data retrieved from the server will be returned in chunks of this many "
            "rows; using a larger chunk size generally results in faster operation "
            "but uses more memory; selecting an excessive size will result in the "
            "program running out of memory"
        ),
    )
    argp.add_argument(
        "--path",
        default=os.environ.get("OUTPUT_PATH", os.getcwd()),
        metavar="OUTPUT_PATH",
        help="the base output path to use when creating CSV files",
    )
    argp.add_argument(
        "--csvdialect",
        default=os.environ.get("CSV_DIALECT", "unix"),
        metavar="CSV_DIALECT",
        choices=dialect_choices,
        help=(
            "python csv.writer dialect; "
            f"possible values: {quoted_list(dialect_choices)}; "
            "see: https://docs.python.org/3/library/csv.html#csv.Dialect"
        ),
    )
    argp.add_argument(
        "--csvencoding",
        default=os.environ.get("CSV_ENCODING", "utf8"),
        metavar="CSV_ENCODING",
        help="character encoding used when writing CSV files",
    )
    argp.add_argument(
        "--overwrite",
        action=argparse.BooleanOptionalAction,
        default=parse_bool(os.environ.get("OVERWRITE", "0")),
        help=(
            "if output files for the given tables already exist, overwrite "
            "those files instead of skipping them"
        ),
    )
    argp.add_argument(
        "table_name",
        nargs="+",
        help=(
            "name of database table to copy into local CSV output file (multiple "
            "can be specified)"
        ),
    )
    args = argp.parse_args()
    logging.basicConfig(
        level=args.loglevel,
        format=LOG_FORMAT,
    )

    try:
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
                encoding=args.csvencoding,
                chunksize=args.chunksize,
                overwrite=args.overwrite,
            )
    except mariadb.Error as e:
        logging.error("database exception: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

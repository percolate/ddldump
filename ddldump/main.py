#!/usr/bin/env python
"""ddldump
Dump a clean version of the DDLs of your tables, so you can version them.

See <https://github.com/percolate/ddldump> for more info


Usage:
    ddldump [options] <DSN> [TABLE]
    ddldump [options] --diff=<FILE> <DSN> [TABLE]

Arguments:
    DSN   Database connection URL, see
          http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
    TABLE Optional table to dump. Dump all the database tables if none is
          specified

Options:
    -h --help       Show this screen.
    -v --verbose    Enable the debugging output.
    --diff=<FILE>   Compare the tables that exists in the database with the
                    dump in FILE. If there is a difference, throw an error.
                    This is useful to check if your database and your dump are
                    in sync, e.g. during your continuous integration.

"""
from __future__ import unicode_literals

import logging
import re
import sys
import difflib
from subprocess import Popen, PIPE

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from docopt import docopt
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql.expression import select, asc

from ddldump.constants import VERSION


class Database(object):
    """general class for Database operations"""

    @classmethod
    def from_dsn(cls, dsn_url):
        """
        Construct a `Database` instance from a parsed ini file section.
        """
        assert isinstance(dsn_url, str)

        engine = create_engine(dsn_url)
        meta = MetaData(bind=engine)

        if engine.name == "mysql":
            DatabaseEngine = MySQLDatabase
        elif engine.name == "postgresql":
            DatabaseEngine = PostgresDatabase
        else:
            print("ddldump does not support the {} dialect.".format(engine.name))

        return DatabaseEngine(engine, meta)

    def query_information_schema(self, table_name):
        """generates a basic query statement table in INFORMATION SCHEMA"""

        information_schema_table = Table(
            table_name, self.meta, schema=self.information_schema_name, autoload=True
        )

        return select([information_schema_table]).where(
            self.information_schema_where(information_schema_table)
        )

    def get_tables_and_views(self):
        """return alphabetically sorted list of tables"""
        statement = self.query_information_schema(self.information_schema_tables)

        statement = statement.order_by(
            # Order by TABLE TYPE to make sure TABLES come first, then VIEWS
            asc(self.information_schema_table_type),
            # then order each group alphabetically.
            asc(self.information_schema_table_name),
        )

        rows = self.engine.execute(statement)
        return [
            record[self.information_schema_table_name] for record in rows.fetchall()
        ]


class MySQLDatabase(Database):
    """MySQL operations"""

    information_schema_name = "information_schema"
    information_schema_views = "VIEWS"
    information_schema_view_name = "TABLE_NAME"
    information_schema_tables = "TABLES"
    information_schema_table_name = "TABLE_NAME"
    information_schema_table_type = "TABLE_TYPE"

    def __init__(self, engine, meta):
        """initializes"""
        assert engine.name == "mysql"

        self.engine = engine
        self.meta = meta

    def information_schema_where(self, table):
        """
        generates a database engine specific where clause
        for looking up INFORMATION SCHEMA records
        """
        return getattr(table.c, "TABLE_SCHEMA") == self.engine.url.database

    def show_create(self, table):
        """return per-table DDL"""
        result = self.engine.execute("SHOW CREATE TABLE `{}`;".format(table))
        row = result.first()
        table_ddl = row[1] + ";"
        # TODO for the future: add trigger look-ups here
        # result = engine.execute("SHOW TRIGGERS LIKE `{}`;".format(table))
        # TODO will need to make sure that before/after UPDATE/DELETE triggers

        return cleanup_table_ddl(table_ddl)


class PostgresDatabase(Database):
    """PostgreSQL operations"""

    information_schema_name = "information_schema"
    information_schema_views = "views"
    information_schema_view_name = "table_name"
    information_schema_tables = "tables"
    information_schema_table_name = "table_name"
    information_schema_table_type = "table_type"

    def __init__(self, engine, meta):
        """initializes"""
        assert engine.name == "postgresql"

        self.engine = engine
        self.meta = meta

    def information_schema_where(self, table):
        """
        generates a database engine specific where clause
        for looking up INFORMATION SCHEMA records
        """
        return getattr(table.c, "table_schema").notin_(
            ["pg_catalog", "information_schema"]
        )

    def show_create(self, table):
        """generates per-table DDL"""
        try:
            # Python 3
            ps = Popen(
                [
                    "pg_dump",
                    str(self.engine.url),
                    "-t",
                    table,
                    "--quote-all-identifiers",
                    "--no-owner",
                    "--no-privileges",
                    "--no-acl",
                    "--no-security-labels",
                    "--schema-only",
                ],
                stdout=PIPE,
                text=True,
            )
        except TypeError:
            # Python 2
            ps = Popen(
                [
                    "pg_dump",
                    str(self.engine.url),
                    "-t",
                    table,
                    "--quote-all-identifiers",
                    "--no-owner",
                    "--no-privileges",
                    "--no-acl",
                    "--no-security-labels",
                    "--schema-only",
                ],
                stdout=PIPE,
            )

        table_ddl_details = []
        # convert bytes to string so we can use the same code between Python 2/3
        raw_output = str(ps.communicate()[0])

        # Separate CREATE TABLE STATEMENT
        # Separating the CREATE TABLE statement and the rest of the details
        # from pg_dump output for better manipulation.
        create_table_start = raw_output[raw_output.find("CREATE TABLE") :]
        create_table_statement = create_table_start[: create_table_start.find(";") + 1]
        raw_output_without_table = raw_output.replace(create_table_statement, "")

        # Seprate CREATE SEQUENCE STATEMENTS
        # Each table can have more than one.
        raw_output_without_table_and_sequences = raw_output_without_table
        create_sequence_statements_list = []
        while raw_output_without_table_and_sequences.find("CREATE SEQUENCE") > 0:
            create_sequence_start = raw_output_without_table_and_sequences[
                raw_output_without_table_and_sequences.find("CREATE SEQUENCE") :
            ]
            create_sequence_statements_list.append(
                create_sequence_start[: create_sequence_start.find(";") + 1]
            )
            raw_output_without_table_and_sequences = raw_output_without_table_and_sequences.replace(
                create_sequence_statements_list[-1], ""
            )

        create_sequence_statements = "\n".join(create_sequence_statements_list)

        # Detect if this is a view
        view = False
        if raw_output_without_table_and_sequences.find("CREATE VIEW") > 0:
            view = True
        # Removing all of the empty space list members.
        filtered_raw_output_less_create_table = filter(
            None, raw_output_without_table_and_sequences.split("\n")
        )
        for op in filtered_raw_output_less_create_table:
            if op.startswith("ALTER TABLE ONLY") and op.find("nextval") > 0:
                table_ddl_details.append(op)

            if (
                not op.startswith(("ALTER TABLE ONLY", "COPY", "SET", r"\.", "--"))
                and "OWNER" not in op
            ):
                table_ddl_details.append(op)

        # ALTER TABLE ONLY + ADD CONSTRAINT come in two
        # rows with indentation.
        # Concatenating into one row.
        for idx, item in enumerate(table_ddl_details):
            if "ADD CONSTRAINT" in item:
                item = 'ALTER TABLE ONLY "public"."{}" {}'.format(table, item.strip())
                table_ddl_details[idx] = item

        if not view:
            table_ddl_details.sort()
        # need to move SQL statements with PRIMARY KEY to front
        for sql_statement in table_ddl_details:
            if "PRIMARY KEY" in sql_statement:
                table_ddl_details.insert(
                    0, table_ddl_details.pop(table_ddl_details.index(sql_statement))
                )
        table_ddl_details_str = "\n".join(table_ddl_details)

        return cleanup_table_ddl(
            "\n".join(
                filter(
                    None,
                    (
                        create_table_statement,
                        create_sequence_statements,
                        table_ddl_details_str,
                    ),
                )
            )
        )


def sort_table_keys(raw_ddl):
    """
    Sort the lines of the raw table DDL beginning with KEY, so that no matter
    what order the keys were added in, the resulting DDL outputs are
    identical.

    Args:
        raw_ddl (unicode)

    Returns:
        unicode
    """
    lines = raw_ddl.split("\n")
    key_lines = [(l, i) for i, l in enumerate(lines) if l.strip().startswith("KEY")]

    if not key_lines:
        return raw_ddl

    last_has_comma = key_lines[-1][0][-1] == ","
    sorted_key_lines = sorted(
        [(l if l[-1] != "," else l[:-1], i) for l, i in key_lines]
    )

    key_line_idxs = set([i for _, i in sorted_key_lines])
    for i, _ in enumerate(lines):
        if i in key_line_idxs:
            lines[i] = sorted_key_lines.pop(0)[0]
            if sorted_key_lines or last_has_comma:
                lines[i] += ","
    key_sorted_ddl = "\n".join(lines)

    return key_sorted_ddl


def cleanup_table_ddl(raw_ddl):
    """
    Given a raw DDL, clean it up to remove any varying piece, like AUTOINCs.

    Args:
        raw_ddl (unicode)

    Returns:
        unicode
    """
    key_sorted_ddl = sort_table_keys(raw_ddl)

    # Removing the AUTOINC state from CREATE TABLE statements
    clean_ddl = re.sub(r" AUTO_INCREMENT=\d+", "", key_sorted_ddl)

    # Removing the DEFINE clause from CREATE VIEW statements
    clean_ddl = re.sub(r" DEFINER=`\w+.*SQL", " SQL", clean_ddl)

    return clean_ddl


def main():
    """The main function"""
    args = docopt(__doc__, version="ddldump. {}".format(VERSION))
    dsn = args["<DSN>"]
    table = args["TABLE"]
    diff_file = args["--diff"]

    # If asked to be verbose, enable the debug logging
    if args["--verbose"]:
        logging.basicConfig(level=logging.DEBUG)

    # Get a connection to the database
    logging.debug("Connecting to %s", dsn)
    database = Database.from_dsn(dsn)

    # Figure out the list of tables to dump
    if not table:
        tables = database.get_tables_and_views()
    else:
        tables = [table]
    logging.debug("Got those tables: %s", tables)

    output = ""

    # Dump each table on stdout
    first_loop = True
    for table_name in tables:
        # We want a newline between tables
        if first_loop:
            first_loop = False
        else:
            output += "\n"

        output += "-- Create syntax for TABLE '{}'".format(table_name)
        output += "\n"
        output += "{}".format(database.show_create(table_name))
        output += "\n"

    if diff_file:
        # load the content of the given file to diff
        fh = open(diff_file, "r")
        content = fh.read().splitlines()
        fh.close()

        output = output.splitlines()

        # Get the db type for a pretty diff output
        parsed = urlparse(dsn)
        db_type = parsed.scheme

        # Compare it with the current state
        if content != output:
            diff_lines = difflib.unified_diff(
                content, output, fromfile=diff_file, tofile=db_type
            )
            for line in diff_lines:
                print(line)
            return 1

    else:
        # Don't let python add another \n character when printing
        if output.endswith("\n"):
            output = output[:-1]

        print(output)


if __name__ == "__main__":
    sys.exit(main())

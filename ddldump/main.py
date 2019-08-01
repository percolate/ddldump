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
import logging
import re
import sys
import difflib
from subprocess import Popen, PIPE
from urlparse import urlparse

from docopt import docopt
import sqlalchemy

from constants import VERSION


def get_db_connection(url):
    """
    Args:
        url (str)

    Returns:
        sqlalchemy.engine.base.Engine
    """
    assert isinstance(url, str)

    engine = sqlalchemy.create_engine(url)

    return engine


def get_tables_to_dump(engine):
    """
    Args:
        engine (sqlalchemy.engine.base.Engine)

    Returns:
        list: List of table names
    """
    assert isinstance(engine, sqlalchemy.engine.base.Engine)

    inspector = sqlalchemy.inspect(engine)
    tables = inspector.get_table_names()

    return tables


def get_table_ddl(engine, table):
    """
    Args:
        engine (sqlalchemy.engine.base.Engine)
        table (basestring)

    Returns:
        basestring
    """
    assert isinstance(engine, sqlalchemy.engine.base.Engine)
    assert isinstance(table, basestring)

    table_ddl = None

    if engine.name == 'mysql':
        result = engine.execute('SHOW CREATE TABLE `{}`;'.format(table))
        row = result.first()
        table_ddl = row[1] + ';'
    elif engine.name == 'postgresql':
        table_ddl = _show_create_postgresql(engine, table)
    else:
        print "ddldump does not support the {} dialect.".format(engine.name)

    return table_ddl


def _show_create_postgresql(engine, table):
    ps = Popen(
                    [
                        'pg_dump',
                        str(engine.url),
                        '-t', table,
                        '--quote-all-identifiers',
                        '--no-owner',
                        '--no-privileges',
                        '--no-acl',
                        '--no-security-labels',
                        '--schema-only'],
                    stdout=PIPE)

    table_ddl_details = []
    raw_output = ps.communicate()[0]
    start = raw_output[raw_output.find(u'CREATE TABLE'):]
    table_ddl_create = start[:start.find(";") + 1]

    # Separating the CREATE TABLE statement and the rest of the details
    # from pg_dump output for better manipulation.
    raw_output_less_create_table = raw_output.replace(
        table_ddl_create, ''
    )
    # Removing all of the empty space list members.
    filtered_raw_output_less_create_table = filter(
        None, raw_output_less_create_table.split('\n')
    )
    for op in filtered_raw_output_less_create_table:
        if not op.startswith(
                (u'ALTER TABLE ONLY',
                 u'COPY',
                 u'SET',
                 r'\.',
                 u'--')
        ) and u'OWNER' not in op:
            table_ddl_details.append(op)

    # ALTER TABLE ONLY + ADD CONSTRAINT come in two
    # rows with indentation.
    # Concatenating into one row.
    for idx, item in enumerate(table_ddl_details):
        if u'ADD CONSTRAINT' in item:
            item = u'ALTER TABLE ONLY "public"."{}" {}'.format(
                table, item.strip()
            )
            table_ddl_details[idx] = item

    table_ddl_details.sort()
    # need to move SQL statements with PRIMARY KEY to front
    for sql_statement in table_ddl_details:
        if u'PRIMARY KEY' in sql_statement:
            table_ddl_details.insert(
                0,
                table_ddl_details.pop(
                    table_ddl_details.index(sql_statement)
                )
            )
    table_ddl_details_str = "\n".join(table_ddl_details)
    return u'{}\n{}'.format(table_ddl_create, table_ddl_details_str)


def sort_table_keys(raw_ddl):
    """
    Sort the lines of the raw table DDL beginning with KEY, so that no matter
    what order the keys were added in, the resulting DDL outputs are
    identical.

    Args:
        raw_ddl (basestring)

    Returns:
        basestring
    """
    lines = raw_ddl.split("\n")
    key_lines = [
        (l, i)
        for i, l in enumerate(lines)
        if l.strip().startswith("KEY")
    ]

    if not key_lines:
        return raw_ddl

    last_has_comma = key_lines[-1][0][-1] == ','
    sorted_key_lines = sorted([
        (l if l[-1] != ',' else l[:-1], i)
        for l, i in key_lines
    ])

    key_line_idxs = set([i for _, i in sorted_key_lines])
    for i, _ in enumerate(lines):
        if i in key_line_idxs:
            lines[i] = sorted_key_lines.pop(0)[0]
            if sorted_key_lines or last_has_comma:
                lines[i] += ','
    key_sorted_ddl = "\n".join(lines)

    return key_sorted_ddl


def cleanup_table_ddl(raw_ddl):
    """
    Given a raw DDL, clean it up to remove any varying piece, like AUTOINCs.

    Args:
        raw_ddl (basestring)

    Returns:
        basestring
    """
    assert isinstance(raw_ddl, basestring)

    key_sorted_ddl = sort_table_keys(raw_ddl)

    # Removing the AUTOINC state from the CREATE TABLE
    clean_ddl = re.sub(r" AUTO_INCREMENT=\d+", u"", key_sorted_ddl)

    return clean_ddl


def main():
    """The main function"""
    args = docopt(__doc__, version="ddldump. {}".format(VERSION))
    dsn = args['<DSN>']
    table = args['TABLE']
    diff_file = args['--diff']

    # If asked to be verbose, enable the debug logging
    if args['--verbose']:
        logging.basicConfig(level=logging.DEBUG)

    # Get a connection to the database
    logging.debug("Connecting to %s", dsn)
    sqla = get_db_connection(dsn)

    # Figure out the list of tables to dump
    if not table:
        tables = get_tables_to_dump(sqla)
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

        raw_ddl = get_table_ddl(sqla, table_name)
        clean_ddl = cleanup_table_ddl(raw_ddl)
        output += "-- Create syntax for TABLE '{}'".format(table_name)
        output += "\n"
        output += "{}".format(clean_ddl)
        output += "\n"

    if diff_file:
        # load the content of the given file to diff
        fh = open(diff_file, 'r')
        content = fh.read().splitlines()
        fh.close()

        output = output.splitlines()

        # Get the db type for a pretty diff output
        parsed = urlparse(dsn)
        db_type = parsed.scheme

        # Compare it with the current state
        if content != output:
            diff_lines = difflib.unified_diff(content,
                                              output,
                                              fromfile=diff_file,
                                              tofile=db_type)
            for line in diff_lines:
                print line
            return 1

    else:
        # Don't let python add another \n character when printing
        if output.endswith('\n'):
            output = output[:-1]

        print output


if __name__ == "__main__":
    sys.exit(main())

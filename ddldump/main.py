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

    result = engine.execute('SHOW CREATE TABLE `{}`;'.format(table))
    row = result.first()
    table_ddl = row[1]

    return table_ddl


def cleanup_table_ddl(raw_ddl):
    """
    Given a raw DDL, clean it up to remove any varying piece, like AUTOINCs.

    Args:
        raw_ddl (basestring)

    Returns:
        basestring
    """
    assert isinstance(raw_ddl, basestring)

    # Removing the AUTOINC state from the CREATE TABLE
    clean_ddl = re.sub(' AUTO_INCREMENT=\d+', u'', raw_ddl)

    # Every query should end with a semicolon
    clean_ddl += ';'

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

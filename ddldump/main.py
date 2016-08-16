#!/usr/bin/env python
"""ddldump
Dump and version the DDLs of your tables.

See <https://github.com/percolate/ddldump> for more info


Usage:
    ddldump [options] <DSN> [TABLE]

Arguments:
    DSN   Database connection URL, see
          http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
    TABLE Optional table to dump. Dump all the database tables if none is
          specified

Options:
    -h --help   Show this screen.

"""
from docopt import docopt
from constants import VERSION


def main():
    args = docopt(__doc__, version="ddldump. {}".format(VERSION))


if __name__ == "__main__":
    sys.exit(main())

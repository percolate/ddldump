# ddldump

[![CircleCI](https://circleci.com/gh/percolate/ddldump.svg?style=svg)](https://circleci.com/gh/percolate/ddldump)

Dump and version the DDLs of your tables.

## Usage

```bash
ddldump <dsn> [table] > table.sql

# Dump all the table DDLs of a database
ddldump mysql://localhost/dbname > dbname.sql

# Dump a specific PostgreSQL table
ddldump postgresql://localhost/dbname cool_table > cool_table.sql
```

## Install

```bash
pip install ddldump
```

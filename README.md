# ddldump

[![CircleCI](https://circleci.com/gh/percolate/ddldump.svg?style=svg)](https://circleci.com/gh/percolate/ddldump)

Dump and version the DDLs of your tables.

## Usage

```bash
ddldump <dsn> [table] > table.sql
```

## Example

Dump all the table DDLs of the MySQL database `cooldb`:

```
ddldump mysql://localhost/cooldb > cooldb.sql

Dump the specific DDL of the `awesome` PostgreSQL table:

```bash
ddldump postgresql://localhost/mydb awesome > awesome.sql
```

## Install

```bash
pip install ddldump
```

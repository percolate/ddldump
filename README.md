# ddldump

[![CircleCI](https://circleci.com/gh/percolate/ddldump.svg?style=svg)](https://circleci.com/gh/percolate/ddldump)

Dump and version the DDLs of your tables, while cleaning the dumps of all the
varying stuff, like MySQL's AUTOINCs, that would make it hard to version and
check for differences during continuous integration.

## Usage

```bash
ddldump <dsn> [table] > table.sql
```

## Example

Dump all the table DDLs of the MySQL database `cooldb`:

```
ddldump mysql://localhost/cooldb > cooldb.sql
```

Dump the specific DDL of the `awesome` PostgreSQL table.
(requires `postgresql-client`, matching the server version, to be installed):

```bash
ddldump postgresql://localhost/mydb awesome > awesome.sql
```

Compare your dump with what's actually in your database:

```bash
$ ddldump --diff=cooldb.sql mysql://localhost/cooldb
--- mysql

+++ cooldb.sql

@@ -14,7 +14,7 @@


 -- Create syntax for TABLE 'user'
 CREATE TABLE `user` (
-  `id` bigint(20) unsigned COMMENT 'The user ID',
+  `id` bigint(20) unsigned NOT NULL COMMENT 'The user ID',
   `name` varchar(64) NOT NULL COMMENT 'The user name',
   PRIMARY KEY (`id`)
```

## Install

```bash
pip install ddldump
```

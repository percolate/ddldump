# circleci/cci-ddldump

This repository provides an image with the
[`ddldump`](https://github.com/percolate/ddldump) tool, and postgres and mysql clients.

## Usage

``` yaml
jobs:
  perc-service:
    docker:
      - image: prclt/ddldump:<insert_latest_version_here>
        aws_auth:
          aws_access_key_id: $AWS_ACCESS_KEY_ID
          aws_secret_access_key: $AWS_SECRET_ACCESS_KEY
      - image: cicleci/postgres
      - image: circleci/mysql

    steps:
      - run:
          name: Wait for mysql to come up
          command: dockerize -wait tcp://localhost:3306 -timeout 1m
      - run:
          name: Wait for postgres to come up
          command: dockerize -wait tcp://localhost:5432 -timeout 1m
      - run:
          name: Load postgres schema
          command: psql -h 127.0.0.1 -U postgres < <path/to/postgres/dumpfile.sql>
      - run:
          name: Run ddldump againt the postgres <dumpfile.sql>
          command: ddldump --diff=<path/to/postgres/dumpfile.sql> postgresql://postgres:postgres@127.0.0.1:5432
      - run:
          name: Create a mysql database for loading
          command: mysql -h 127.0.0.1 -e 'CREATE DATABASE IF NOT EXISTS `<db_name>`'
      - run:
          name: Load mysql schema (with foreign key checks disabled)
          command: |
            (echo "SET FOREIGN_KEY_CHECKS=0; "; cat <path/to/mysql/dumpfile.sql>)
            mysql -h 127.0.0.1 <db_name>
      - run:
          name: Run ddldump against the mysql <dumpfile.sql>
          command: ddldump --diff=<path/to/mysql/dumpfile.sql> mysql://:@127.0.0.1:3306/<db_name>
```

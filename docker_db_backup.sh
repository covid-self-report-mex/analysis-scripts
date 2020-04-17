#!/usr/bin/env bash

# load .env vars
if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

now=$(date -u +"%Y_%m_%d_%H_%M_%S")

mkdir -p backups/sql

## Backup
docker exec ${DOCKER_COVID_MYSQL} /usr/bin/mysqldump -u root --password=root ${DATABASE_NAME}  > backups/sql/backup-${DATABASE_NAME}-${now}.sql

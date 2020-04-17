#!/usr/bin/env bash

# You need to add the relative path to the backup as argument

# load .env vars
if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Restore
cat $1 | docker exec -i ${DOCKER_COVID_MYSQL} /usr/bin/mysql -u root --password=root ${DATABASE_NAME}

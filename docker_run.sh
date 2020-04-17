#!/usr/bin/env bash

# load .env vars
if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

docker rm ${DOCKER_COVID_MYSQL} --force
docker rm ${DOCKER_COVID_ADMIN}  --force

docker run --name ${DOCKER_COVID_MYSQL} -d -e MYSQL_ROOT_PASSWORD=root -p ${MYSQL_PORT}:3306 mysql
docker run --name ${DOCKER_COVID_ADMIN}  -d --link ${DOCKER_COVID_MYSQL}:db -p ${PHPMYADMIN_PORT}:80 phpmyadmin/phpmyadmin

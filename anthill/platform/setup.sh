#!/usr/bin/env bash

REDIS_DATABASES=32

function update_redis_databases {
    sed -iE "s/^databases [0-9]*$/databases ${REDIS_DATABASES}/" $1
}

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    apt install redis-server -y
    apt install rabbitmq-server -y
    apt install postgresql -y

    update_redis_databases /etc/redis/redis.conf

    service start redis-server
    service start rabbitmq-server
    service start postgresql

elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install redis
    brew install rabbitmq
    brew install postgres

    update_redis_databases /usr/local/etc/redis.conf

    brew services start redis
    brew services start rabbitmq
    brew services start postgres
fi


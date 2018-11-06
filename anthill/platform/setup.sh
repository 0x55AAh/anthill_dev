#!/usr/bin/env bash

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    apt install redis-server -y
    apt install rabbitmq-server -y
    apt install postgresql -y

    service start redis-server
    service start rabbitmq-server
    service start postgresql

elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install redis
    brew install rabbitmq
    brew install postgres

    brew services start redis
    brew services start rabbitmq
    brew services start postgres
fi


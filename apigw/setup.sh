#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_apigw -U postgres
createdb -U anthill_apigw anthill_apigw
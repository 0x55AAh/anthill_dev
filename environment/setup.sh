#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_environment -U postgres
createdb -U anthill_environment anthill_environment
#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_exec -U postgres
createdb -U anthill_exec anthill_exec
#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_backup -U postgres
createdb -U anthill_backup anthill_backup

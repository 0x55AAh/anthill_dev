#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_store -U postgres
createdb -U anthill_store anthill_store
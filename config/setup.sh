#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_config -U postgres
createdb -U anthill_config anthill_config
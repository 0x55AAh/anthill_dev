#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_report -U postgres
createdb -U anthill_report anthill_report
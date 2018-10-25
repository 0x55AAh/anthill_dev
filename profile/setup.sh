#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_profile -U postgres
createdb -U anthill_profile anthill_profile
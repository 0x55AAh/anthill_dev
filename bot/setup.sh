#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_bot -U postgres
createdb -U anthill_bot anthill_bot

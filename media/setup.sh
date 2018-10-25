#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_media -U postgres
createdb -U anthill_media anthill_media
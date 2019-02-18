#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_news -U postgres
createdb -U anthill_news anthill_news
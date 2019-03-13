#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_blog -U postgres
createdb -U anthill_blog anthill_blog
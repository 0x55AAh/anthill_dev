#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_admin -U postgres
createdb -U anthill_admin anthill_admin
#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_login -U postgres
createdb -U anthill_login anthill_login
#!/usr/bin/env bash

# Setup postgres database
createuser -d postgres -U anthill_discovery
createdb -U anthill_discovery anthill_discovery
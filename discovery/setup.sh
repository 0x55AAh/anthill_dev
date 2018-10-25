#!/usr/bin/env bash

# Setup postgres database
createuser -d postgres -U anthill_config
createdb -U anthill_config anthill_config
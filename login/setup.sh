#!/usr/bin/env bash

# Setup postgres database
createuser -d postgres -U anthill_dlc
createdb -U anthill_dlc anthill_dlc
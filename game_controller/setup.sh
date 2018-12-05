#!/usr/bin/env bash

# Setup postgres database
createuser -d anthill_game_controller -U postgres
createdb -U anthill_game_controller anthill_game_controller
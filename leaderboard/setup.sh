#!/usr/bin/env bash


# Setup postgres database
createuser -d anthill_leaderboard -U postgres
createdb -U anthill_leaderboard anthill_leaderboard
#!/usr/bin/env bash

OS=${OSTYPE//[0-9.-]*/}
python="/usr/bin/env python3"

case "$OS" in
    darwin|linux)
        echo "Starting installation script...";;
    *)
        echo "Unknown operating system $OSTYPE"
        exit 1
esac

if [[ "$OS" == "darwin" ]]; then
    if [[ $EUID -eq 0 ]]; then
        echo "Do not run this script as root." 2>&1
        exit 1
    fi
fi

# General setup
source anthill/framework/setup.sh
source anthill/platform/setup.sh

# Services setup
services=(
    "admin" "config" "discovery" "dlc" "event" "exec" "login"
    "media" "message" "profile" "promo" "social" "store"
)
for service in "${services[@]}"; do
    echo
	source ${service}/setup.sh
done

echo
echo "Updating geoip databases..."
eval ${python} "mmdb_update.py"

echo
echo "Installation completed."

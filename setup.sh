#!/usr/bin/env bash

OS=${OSTYPE//[0-9.-]*/}

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
source admin/setup.sh
source config/setup.sh
source discovery/setup.sh
source dlc/setup.sh
source event/setup.sh
source exec/setup.sh
source login/setup.sh
source media/setup.sh
source message/setup.sh
source profile/setup.sh
source promo/setup.sh
source social/setup.sh
source store/setup.sh
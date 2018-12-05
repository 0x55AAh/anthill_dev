#!/usr/bin/env bash

OS=${OSTYPE//[0-9.-]*/}

# Install packages
if [[ "$OS" == "darwin" ]]; then
    # MAGICK_HOME=/usr/local/opt/imagemagick@6
    brew install freetype imagemagick@6
fi

# Setup postgres database
createuser -d anthill_media -U postgres
createdb -U anthill_media anthill_media
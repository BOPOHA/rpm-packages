#!/bin/sh

export FREELENS_RESOURCES_PATH=/usr/lib64/freelens-native
exec /usr/bin/electron41 /usr/lib64/freelens-native/app.asar "$@"

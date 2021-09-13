#!/usr/bin/env bash

SCRIPT_DIR="$( dirname "${BASH_SOURCE[0]}" )"

echo building docs...
sphinx-apidoc -f -E -e -M -o ./docs/source/API ./pathex
cd ./${SCRIPT_DIR0}/docs
make $@

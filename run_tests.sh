#!/usr/bin/env bash

echo running unittests...
pytest --doctest-modules

SCRIPT_DIR="$( dirname "${BASH_SOURCE[0]}" )"

echo running tests to docs...
cd ./${SCRIPT_DIR0}/docs
make -C ./${SCRIPT_DIR0}/docs doctest

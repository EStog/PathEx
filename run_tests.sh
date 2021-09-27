#!/usr/bin/env bash

echo running unittests...
pytest --doctest-modules || exit 1

SCRIPT_DIR="$( dirname "${BASH_SOURCE[0]}" )"

echo running tests to docs...
rm -r ./${SCRIPT_DIR}/docs/source/API
cd ./${SCRIPT_DIR}/docs
make doctest

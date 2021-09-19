#!/usr/bin/env bash

echo running unittests...
pytest --doctest-modules --cov= --cov-report=xml

SCRIPT_DIR="$( dirname "${BASH_SOURCE[0]}" )"

echo running tests to docs...
sphinx-apidoc -f -E -e -M -o ./docs/source/API ./pathex
cd ./${SCRIPT_DIR}/docs
make doctest

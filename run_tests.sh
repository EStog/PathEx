#!/usr/bin/env bash

echo running unittests...
pytest --doctest-modules --cov= --cov-report=xml

SCRIPT_DIR="$( dirname "${BASH_SOURCE[0]}" )"

echo running tests to docs...
cd ./${SCRIPT_DIR0}/docs
make doctest

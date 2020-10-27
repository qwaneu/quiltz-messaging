#!/bin/bash
export PYTHONPATH=tests:src 
. venv/bin/activate
pip install -r requirements/dev.txt -r requirements/prod.txt

if [[ "$1" == "watch" ]]
then
   shift
   pytest-watch -- --disable-pytest-warnings $@
else
   pytest --disable-pytest-warnings --junitxml=reports/test-report.xml $@
fi

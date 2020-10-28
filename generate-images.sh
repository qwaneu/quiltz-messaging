#!/bin/bash
plantuml -tsvg README.md
mv *.svg doc/images/
plantuml -tsvg doc/*.md
mv doc/*.svg doc/images
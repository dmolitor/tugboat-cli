#!/usr/bin/env bash

tugboat create \
  -e .dockerignore \
  -e Dockerfile \
  -e .DS_Store \
  -e dockerize.py \
  -e "*.csv" \
  ./examples/cleaning_and_viz/

tugboat build \
  -d ./examples/cleaning_and_viz/Dockerfile \
  -n clean_and_viz \
  --build-context ./examples/cleaning_and_viz

tugboat binderize ./examples/cleaning_and_viz
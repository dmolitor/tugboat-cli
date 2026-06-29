#!/usr/bin/env bash

tugboat create \
  -e .dockerignore \
  -e Dockerfile \
  -e .DS_Store \
  -e dockerize.py \
  -e "*.png" \
  --no-detect-r \
  ./examples/housing/

tugboat build \
  -d ./examples/housing/Dockerfile \
  -n housing \
  --build-context ./examples/housing

tugboat binderize --no-detect-python ./examples/housing
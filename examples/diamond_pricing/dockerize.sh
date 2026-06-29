#!/usr/bin/env bash

tugboat create \
  -e .dockerignore \
  -e Dockerfile \
  -e .DS_Store \
  -e dockerize.py \
  -e "*.png" \
  --no-detect-python \
  ./examples/diamond_pricing/

tugboat build \
  -d ./examples/diamond_pricing/Dockerfile \
  -n diamond_pricing \
  --build-context ./examples/diamond_pricing

tugboat binderize --no-detect-python ./examples/diamond_pricing
#!/bin/bash

# Fixes the openapi_spec.yaml file to include response types
python scripts/fix_openapi_spec.py

# Gets the necessary models for the APIs we want to generate
MODELS=$(python scripts/get_necessary_models.py --spec openapi_spec.yaml --apis system)

# Generates the Python SDK
openapi-generator-cli \
generate -i openapi_spec.yaml \
-g python \
-c config.yaml \
-o src \
--skip-validate-spec \
--global-property supportingFiles,apis=system,models=$MODELS

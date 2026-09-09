#!/bin/bash

# Applies all spec fixes (missing 200 responses, missing enum values,
# dropped enum constraints, psaTicketId typed as integer)
uv run python scripts/fix_openapi_spec.py

# Gets the necessary models for the APIs we want to generate
MODELS=$(uv run python scripts/get_necessary_models.py --spec openapi_spec.yaml --apis system,management,devices,queries)

# Generates the Python SDK
openapi-generator-cli \
generate -i openapi_spec.yaml \
-g python \
-c config.yaml \
-o src \
--skip-validate-spec \
--global-property supportingFiles,apis=system:management:devices:queries,models=$MODELS

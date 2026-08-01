#!/bin/bash

# Fixes the openapi_spec.yaml file to include response types
uv run python scripts/fix_openapi_spec.py

# Inserts missing enum values into the openapi_spec.yaml file
uv run python scripts/add_missing_enum_values.py

# Types psaTicketId as integer (the upstream spec says bare object)
uv run python scripts/fix_psa_ticket_id_type.py

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

#!/bin/bash

MODELS=$(python scripts/get_necessary_models.py --spec openapi_spec.yaml --apis system)

openapi-generator-cli \
generate -i openapi_spec.yaml \
-g python \
-c config.yaml \
-o src \
--skip-validate-spec \
--global-property supportingFiles,apis=system,models=$MODELS

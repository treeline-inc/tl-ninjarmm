import argparse
import pathlib
import json
import re
from ruamel.yaml import YAML


def extract_model_names_from_json(json_data):
    """
    Extract model names from JSON data that references #/components/schemas/<model_name>

    Args:
        json_data: Dictionary or object that can be serialized to JSON

    Returns:
        set: Set of model names found in the JSON data
    """
    # Flatten the dictionary into a string
    json_str = json.dumps(json_data)
    # Models that we want will be of the form #/components/schemas/<model_name>
    models = re.findall(r"#/components/schemas/([a-zA-Z0-9_]+)", json_str)
    return set(models)


def validate_models_exist(models, schemas_map, context=""):
    """
    Validate that all models exist in the schemas map

    Args:
        models: Set of model names to validate
        schemas_map: Dictionary of available schemas
        context: Optional context string for error messages

    Raises:
        ValueError: If any model is not found in schemas_map
    """
    missing_models = [model for model in models if model not in schemas_map]
    if missing_models:
        context_msg = f" in {context}" if context else ""
        raise ValueError(
            f"Model(s) {', '.join(missing_models)} not found in spec{context_msg}"
        )


def collect_models_from_endpoint(endpoint_data, apis_to_generate):
    """
    Collect all model names from an endpoint's request bodies and responses

    Args:
        endpoint_data: Dictionary containing endpoint methods
        apis_to_generate: Set of API tags to include

    Returns:
        set: Set of model names found in the endpoint
    """
    models = set()

    for method, method_data in endpoint_data.items():
        # Skip if method isn't tagged with an API we are generating
        method_tags = method_data.get("tags", [])
        if not any(tag in apis_to_generate for tag in method_tags):
            continue

        # Check request body
        if "requestBody" in method_data:
            models.update(extract_model_names_from_json(method_data["requestBody"]))

        # Check responses
        for response_data in method_data.get("responses", {}).values():
            models.update(extract_model_names_from_json(response_data))

    return models


def main(spec: pathlib.Path, apis: str):
    apis_to_generate = apis.split(",")
    yaml = YAML(typ="safe")
    with open(spec, "r") as f:
        spec_data = yaml.load(f)

    # Get all API tags. Each endpoint has a tag.
    api_tags = [item["name"] for item in spec_data["tags"]]

    for api in apis_to_generate:
        if api not in api_tags:
            raise ValueError(f"API {api} not found in spec")

    # Collect initial models from endpoints
    models_to_generate = set()
    for endpoint_data in spec_data["paths"].values():
        models_to_generate.update(
            collect_models_from_endpoint(endpoint_data, apis_to_generate)
        )

    schemas_map = spec_data["components"]["schemas"]
    validate_models_exist(models_to_generate, schemas_map, "initial collection")

    # Iteratively find all model dependencies
    while True:
        new_models_to_generate = set()
        for model in models_to_generate:
            if model in schemas_map and "properties" in schemas_map[model]:
                new_models_to_generate.update(
                    extract_model_names_from_json(schemas_map[model]["properties"])
                )

        # Check if we found any new models
        if new_models_to_generate.issubset(models_to_generate):
            # No new models found, we're done
            break

        # Validate new models before adding them
        validate_models_exist(
            new_models_to_generate, schemas_map, "dependency resolution"
        )

        # Add new models and continue iterating
        models_to_generate.update(new_models_to_generate)

    print(":".join(sorted(models_to_generate)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spec",
        help="The OpenAPI spec to generate the SDK for",
        default="openapi_spec.yaml",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--apis",
        help="The APIs to generate the SDK for, separated by commas",
        default="system",
        type=str,
    )
    args = parser.parse_args()

    main(args.spec, args.apis)

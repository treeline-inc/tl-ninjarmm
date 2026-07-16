import argparse
from pathlib import Path
from ruamel.yaml import YAML

# values Ninjarmm API returns that are not in the OpenAPI spec
MISSING_ENUM_VALUES = {
    "nodeClass": ["AOSP"],
}


def add_missing_enum_values(openapi_path):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = False
    yaml.default_flow_style = False

    with open(openapi_path, "r") as f:
        data = yaml.load(f)

    added = 0

    def walk(node, prop_name):
        nonlocal added
        if isinstance(node, dict):
            if "enum" in node and prop_name in MISSING_ENUM_VALUES:
                for value in MISSING_ENUM_VALUES[prop_name]:
                    if value not in node["enum"]:
                        node["enum"].append(value)
                        added += 1
            for key, value in node.items():
                # An array's `items` schema carries the parent property's name.
                walk(value, prop_name if key == "items" else key)
        elif isinstance(node, list):
            for item in node:
                walk(item, prop_name)

    walk(data, None)

    with open(openapi_path, "w") as f:
        yaml.dump(data, f)
    return added


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add missing enum values to OpenAPI spec"
    )
    parser.add_argument(
        "--spec",
        default="openapi_spec.yaml",
        type=Path,
        help="Path to the OpenAPI spec to patch",
    )

    args = parser.parse_args()
    openapi_path = args.spec

    count = add_missing_enum_values(openapi_path)
    print(f"Added {count} missing enum value(s) to {openapi_path}")

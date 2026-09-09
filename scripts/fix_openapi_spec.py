import argparse
from pathlib import Path
from ruamel.yaml import YAML
import re

ANCHOR_FMT = "id{:03d}"

# values Ninjarmm API returns that are not in the OpenAPI spec
MISSING_ENUM_VALUES = {
    "nodeClass": ["AOSP"],
}

# Properties whose spec enums Ninjarmm extends without publishing the new
# values. These are vendor-extensible lists, so enumerating them is a losing
# race (see TRE-3709: activityType=MAINTENANCE_MODE and
# statusCode=MAINTENANCE_MODE_COMPLETED failed the whole activities page).
# Dropping the enum removes the generated validator; the fields still generate
# as Optional[StrictStr], so nothing else about the typing changes.
DROPPED_ENUM_CONSTRAINTS = {"activityType", "statusCode"}


def add_200_responses(data):
    paths = data.get("paths", {})
    anchor_counter = 1
    added = 0

    for _, methods in paths.items():
        for _, op in methods.items():
            if not isinstance(op, dict):
                continue
            responses = op.get("responses")

            # Skip if there are no responses or no default response
            if not isinstance(responses, dict):
                continue
            if "default" not in responses:
                continue

            # Make the 200 response the default response
            has_2xx = any(
                re.match(r"^2\\d\\d$", str(code)) for code in responses.keys()
            )
            if not has_2xx:
                if "200" not in responses:
                    added += 1
                default_block = responses["default"]
                anchor = default_block.yaml_anchor()
                if anchor is None or anchor.value is None:
                    default_block.yaml_set_anchor(
                        ANCHOR_FMT.format(anchor_counter), always_dump=True
                    )
                    anchor_counter += 1

                responses["200"] = default_block

    return added


def add_missing_enum_values(data):
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
    return added


def drop_enum_constraints(data):
    dropped = 0

    def walk(node, prop_name):
        nonlocal dropped
        if isinstance(node, dict):
            if "enum" in node and prop_name in DROPPED_ENUM_CONSTRAINTS:
                node.pop("enum")
                dropped += 1
            for key, value in node.items():
                # An array's `items` schema carries the parent property's name.
                walk(value, prop_name if key == "items" else key)
        elif isinstance(node, list):
            for item in node:
                walk(item, prop_name)

    walk(data, None)
    return dropped


def fix_psa_ticket_id_type(data):
    # The upstream spec types psaTicketId as a bare object, but the API
    # returns the PSA ticket id as a plain integer (verified against
    # ConnectWise-linked alerts in production; see TRE-3193). The generated
    # Dict[str, Any] typing makes pydantic reject every alert that carries a
    # ticket id.
    fixed = 0

    def walk(node):
        nonlocal fixed
        if isinstance(node, dict):
            properties = node.get("properties")
            if isinstance(properties, dict):
                psa_ticket_id = properties.get("psaTicketId")
                if (
                    isinstance(psa_ticket_id, dict)
                    and psa_ticket_id.get("type") == "object"
                ):
                    psa_ticket_id["type"] = "integer"
                    psa_ticket_id["format"] = "int32"
                    fixed += 1
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return fixed


def fix_openapi_spec(openapi_path):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = False
    yaml.default_flow_style = False

    with open(openapi_path, "r") as f:
        data = yaml.load(f)

    responses_added = add_200_responses(data)
    enum_values_added = add_missing_enum_values(data)
    enum_constraints_dropped = drop_enum_constraints(data)
    psa_ticket_ids_fixed = fix_psa_ticket_id_type(data)

    with open(openapi_path, "w") as f:
        yaml.dump(data, f)

    print(f"Added {responses_added} missing 200 response(s)")
    print(f"Added {enum_values_added} missing enum value(s)")
    print(f"Dropped {enum_constraints_dropped} enum constraint(s)")
    print(f"Fixed {psa_ticket_ids_fixed} psaTicketId type(s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply all fixes to the OpenAPI spec")
    parser.add_argument(
        "--spec",
        default="openapi_spec.yaml",
        type=Path,
        help="Path to the OpenAPI spec to patch",
    )

    args = parser.parse_args()
    fix_openapi_spec(args.spec)

import argparse
from pathlib import Path
from ruamel.yaml import YAML

# The upstream spec types psaTicketId as a bare object, but the API returns
# the PSA ticket id as a plain integer (verified against ConnectWise-linked
# alerts in production; see TRE-3193). The generated Dict[str, Any] typing
# makes pydantic reject every alert that carries a ticket id.


def fix_psa_ticket_id_type(openapi_path):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = False
    yaml.default_flow_style = False

    with open(openapi_path, "r") as f:
        data = yaml.load(f)

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

    with open(openapi_path, "w") as f:
        yaml.dump(data, f)
    return fixed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Type psaTicketId properties as integer in the OpenAPI spec"
    )
    parser.add_argument(
        "--spec",
        default="openapi_spec.yaml",
        type=Path,
        help="Path to the OpenAPI spec to patch",
    )

    args = parser.parse_args()
    openapi_path = args.spec

    count = fix_psa_ticket_id_type(openapi_path)
    print(f"Fixed {count} psaTicketId type(s) in {openapi_path}")

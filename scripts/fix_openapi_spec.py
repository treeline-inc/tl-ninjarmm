import sys
from ruamel.yaml import YAML
import re

ANCHOR_FMT = "id{:03d}"


def add_200_responses(openapi_path):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = False
    yaml.default_flow_style = False

    # Load the openapi_spec.yaml file
    with open(openapi_path, "r") as f:
        data = yaml.load(f)

    paths = data.get("paths", {})
    anchor_counter = 1

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
                default_block = responses["default"]
                anchor = default_block.yaml_anchor()
                if anchor is None or anchor.value is None:
                    default_block.yaml_set_anchor(
                        ANCHOR_FMT.format(anchor_counter), always_dump=True
                    )
                    anchor_counter += 1

                responses["200"] = default_block

    with open(openapi_path, "w") as f:
        yaml.dump(data, f)


if __name__ == "__main__":
    openapi_path = sys.argv[1] if len(sys.argv) > 1 else "openapi_spec.yaml"
    add_200_responses(openapi_path)
    print(f"Added missing 200 responses to {openapi_path}")

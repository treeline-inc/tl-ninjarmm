import sys
from ruamel.yaml import YAML
import re


def add_200_responses(openapi_path):
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(openapi_path, "r") as f:
        data = yaml.load(f)

    paths = data.get("paths", {})
    for path, methods in paths.items():
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            responses = op.get("responses")
            if not isinstance(responses, dict):
                continue
            has_default = "default" in responses
            has_2xx = any(
                re.match(r"^2\\d\\d$", str(code)) for code in responses.keys()
            )
            if has_default and not has_2xx:
                responses["200"] = responses["default"]

    with open(openapi_path, "w") as f:
        yaml.dump(data, f)


if __name__ == "__main__":
    openapi_path = sys.argv[1] if len(sys.argv) > 1 else "openapi_spec.yaml"
    add_200_responses(openapi_path)
    print(f"Added missing 200 responses to {openapi_path}")

#!/bin/bash

openapi-generator-cli generate -i openapi_spec.yaml -g python -c config.yaml -o src --skip-validate-spec

# Remove file tl_ninjarmm_README.md
rm src/tl_ninjarmm_README.md

# Remove all files from src/tl_ninjarmm/api that are not __init__.py or system_api.py
find src/tl_ninjarmm/api -type f ! -name '__init__.py' ! -name 'system_api.py' -delete
# Update the __init__.py file to remove the imports that are not needed
sed -i '/^from tl_ninjarmm\.api\..* import/d' src/tl_ninjarmm/api/__init__.py
# Add back the specific import we want to keep
echo "from tl_ninjarmm.api.system_api import SystemApi" >> src/tl_ninjarmm/api/__init__.py

# --- Remove unused model files in src/tl_ninjarmm/models based on system_api.py usage ---

# Step 1: Get all directly imported models in system_api.py
used_models=$(grep -oP 'from tl_ninjarmm.models.\K([a-zA-Z0-9_]+)' src/tl_ninjarmm/api/system_api.py | sort -u)

# Step 2: Recursively collect all model dependencies using Python, including dynamically imported models
all_used_models=$(python3 - <<END
import os
import re
from collections import deque

MODELS_DIR = 'src/tl_ninjarmm/models'
visited = set()
todo = deque(set('''$used_models'''.split()))

while todo:
    model = todo.popleft()
    if model in visited:
        continue
    visited.add(model)
    model_file = os.path.join(MODELS_DIR, f"{model}.py")
    if not os.path.isfile(model_file):
        continue
    
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Check for regular imports
        for line in content.split('\n'):
            m = re.match(r"from tl_ninjarmm.models.([a-zA-Z0-9_]+) import", line)
            if m:
                dep = m.group(1)
                if dep not in visited:
                    todo.append(dep)
        
        # Check for dynamic imports (import_module calls)
        dynamic_imports = re.findall(r'import_module\("tl_ninjarmm\.models\.([a-zA-Z0-9_]+)"\)', content)
        for dep in dynamic_imports:
            if dep not in visited:
                todo.append(dep)

print("\n".join(sorted(visited)))
END
)

# Step 3: Remove all model files not in the used set
for f in src/tl_ninjarmm/models/*.py; do
    fname=$(basename "$f" .py)
    if [[ "$fname" == "__init__" ]]; then
        continue
    fi
    if ! grep -qx "$fname" <<< "$all_used_models"; then
        echo "Removing unused model: $f"
        rm "$f"
    fi
done

# Step 4: Clean up __init__.py in models folder to remove unused imports
init_file=src/tl_ninjarmm/models/__init__.py
if [ -f "$init_file" ]; then
    tmp_init=$(mktemp)
    while IFS= read -r line; do
        if [[ "$line" =~ ^from\ tl_ninjarmm\.models\.([a-zA-Z0-9_]+)\ import ]]; then
            model_name=$(echo "$line" | sed -E 's/^from tl_ninjarmm\.models\.([a-zA-Z0-9_]+) import.*/\1/')
            if ! grep -qx "$model_name" <<< "$all_used_models"; then
                continue  # skip unused import
            fi
        fi
        echo "$line" >> "$tmp_init"
    done < "$init_file"
    mv "$tmp_init" "$init_file"
fi

# Remove all lines after __version__ in __init__.py in tl_ninjarmm folder
sed -i '/^__version__/q' src/tl_ninjarmm/__init__.py

# Add imports and __all__ to the main tl_ninjarmm/__init__.py
main_init_file=src/tl_ninjarmm/__init__.py

# Get all model imports from models/__init__.py
models_init_file=src/tl_ninjarmm/models/__init__.py
model_imports=""
if [ -f "$models_init_file" ]; then
    # Extract the full import lines and the class names
    model_imports=$(grep -E '^from tl_ninjarmm\.models\.[a-zA-Z0-9_]+ import' "$models_init_file")
fi

# Get all api imports from api/__init__.py
api_init_file=src/tl_ninjarmm/api/__init__.py
api_imports=""
if [ -f "$api_init_file" ]; then
    # Extract the full import lines and the class names
    api_imports=$(grep -E '^from tl_ninjarmm\.api\.[a-zA-Z0-9_]+ import' "$api_init_file")
fi

# Add imports to main __init__.py
if [ -f "$main_init_file" ]; then
    # Add model imports
    if [ -n "$model_imports" ]; then
        echo "" >> "$main_init_file"
        echo "# Import all models" >> "$main_init_file"
        echo "$model_imports" >> "$main_init_file"
    fi
    
    # Add api imports
    if [ -n "$api_imports" ]; then
        echo "" >> "$main_init_file"
        echo "# Import all APIs" >> "$main_init_file"
        echo "$api_imports" >> "$main_init_file"
    fi
    
    # Extract class names for __all__
    model_classes=$(echo "$model_imports" | grep -oP 'import \K([A-Za-z0-9_, ]+)' | tr ',' ' ' | tr -s ' ' '\n' | grep -v '^$' | sort -u)
    api_classes=$(echo "$api_imports" | grep -oP 'import \K([A-Za-z0-9_, ]+)' | tr ',' ' ' | tr -s ' ' '\n' | grep -v '^$' | sort -u)
    
    # Create __all__ list
    echo "" >> "$main_init_file"
    echo "__all__ = [" >> "$main_init_file"
    
    # Add model classes to __all__
    for class in $model_classes; do
        echo "    \"$class\"," >> "$main_init_file"
    done
    
    # Add api classes to __all__
    for class in $api_classes; do
        echo "    \"$class\"," >> "$main_init_file"
    done
    
    echo "]" >> "$main_init_file"
fi


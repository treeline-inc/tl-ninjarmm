#!/usr/bin/env bash

set -e

target_dir="$HOME/.config/graphite"
config_file="$target_dir/user_config"

# Ensure the target directory exists
if ! mkdir -p "$target_dir"; then
  echo "Error: Failed to create directory '$target_dir'" >&2
  exit 1 # Exit with an error code, but postStart will handle it
fi
echo "Ensured directory exists: $target_dir"

# Check if GRAPHITE_TOKEN is set
if [ -n "$GRAPHITE_TOKEN" ]; then
  # Check if the config file already exists
  if [ -f "$config_file" ]; then
    # Update the authToken using jq
    if jq --arg token "$GRAPHITE_TOKEN" '.authToken = $token' "$config_file" > temp_config && mv temp_config "$config_file"; then
      printf "Graphite user_config updated successfully at '%s'.\n" "$config_file"
    else
      printf "Error: Failed to update Graphite user_config at '%s'.\n" "$config_file" >&2
      exit 1 # Exit with an error code
    fi
  else
    # Create the user_config file
    if printf '{\n  "authToken": "%s"\n}\n' "$GRAPHITE_TOKEN" > "$config_file"; then
      printf "Graphite user_config created successfully at '%s'.\n" "$config_file"
    else
      printf "Error: Failed to create Graphite user_config at '%s'.\n" "$config_file" >&2
      exit 1 # Exit with an error code
    fi
  fi
else
  echo "GRAPHITE_TOKEN is not set; skipping user_config creation/update."
fi

exit 0
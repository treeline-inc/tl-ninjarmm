#!/usr/bin/env bash
set -euo pipefail

echo "Running post-start script..."

sudo chown -R vscode /persistent-cache

# Project root
PROJECT_ROOT="/workspaces/$(basename "$(pwd)")"

# Install zoxide
curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh

# Setup zshrc
CUSTOM_ZSHRC=~/.oh-my-zsh/custom/z.zsh
cp "${PROJECT_ROOT}/.devcontainer/zshrc" ${CUSTOM_ZSHRC}
gt completion >> ${CUSTOM_ZSHRC}

# Install fzf
rm -rf ~/.fzf
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install --all

# Install pre-commmit
uv tool install pre-commit

# Install pre-commit hooks
pre-commit install --install-hooks

# To make it easy to use an external terminal to connect to the container
printenv > .devcontainer/container.env

# Configure graphite.
echo "Setting up Graphite configuration..."
bash "${PROJECT_ROOT}/.devcontainer/setupGraphite.sh"
graphite_setup_result=$?

if [ "$graphite_setup_result" -eq 0 ]; then
  echo "Graphite configuration setup completed successfully."
else
  echo "Warning: Graphite configuration setup failed (exit code: $graphite_setup_result). Continuing with other tasks."
fi

echo "Post-start setup complete!"
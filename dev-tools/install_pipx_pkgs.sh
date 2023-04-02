#!/usr/bin/env bash

set -eou pipefail

while read pkg; do    
  $HOME/.local/bin/pipx install $pkg
done < ./dev-tools/dev-requirements-pipx.txt

# plugins
$HOME/.local/bin/pipx inject mypy pydantic

echo "Specified pipx package installations complete!"

#!/usr/bin/env bash
# Test: models-registry.json is valid JSON with required fields
set -euo pipefail
REPO_ROOT="${1:-.}"

REGISTRY="$REPO_ROOT/shared/models-registry.json"

python -c "
import json, sys, os
path = os.path.normpath(sys.argv[1])
data = json.load(open(path))
assert 'last_updated' in data, 'missing last_updated'
assert 'models' in data, 'missing models'
assert len(data['models']) > 0, 'no models defined'
for mid, info in data['models'].items():
    assert 'context_window' in info, f'{mid} missing context_window'
    assert 'format' in info, f'{mid} missing format'
print(f'Registry OK: {len(data[\"models\"])} models')
" "$REGISTRY"

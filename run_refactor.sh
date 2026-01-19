#!/bin/bash
# Get absolute path to refactor_v2
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$BASE_DIR/backend"

# Add BOTH refactor_v2 (for 'backend' package imports) 
# AND refactor_v2/backend (for 'services', 'routers' top-level imports)
export PYTHONPATH="$BASE_DIR:$BACKEND_DIR:$PYTHONPATH"

# Go to backend directory to help uvicorn find local configs if needed
cd "$BACKEND_DIR"

# Run uvicorn
# We use main:app. Since we are in backend dir, and backend dir is in PYTHONPATH, this works for 'services' imports.
# And since refactor_v2 is in PYTHONPATH, 'from backend.core' should also work.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

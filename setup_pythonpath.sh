#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Export the PYTHONPATH with the necessary directories
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/packages/backend:$SCRIPT_DIR/packages/backend/src:$PYTHONPATH"

echo "PYTHONPATH has been set to: $PYTHONPATH"
echo "Use 'source setup_pythonpath.sh' to set up your environment"

# If argument is provided, execute it with the updated PYTHONPATH
if [ $# -gt 0 ]; then
    echo "Running command: $@"
    exec "$@"
fi 
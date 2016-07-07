#!/bin/sh

echo "WARNING: This command is deprecated and will be removed in a future version of Rudder."
echo "WARNING: Use $(dirname $0)/rudder-sign instead."
echo ""
echo "Redirecting to $(dirname $0)/rudder-sign..."
echo ""

"$(dirname $0)/rudder-sign" "$@"

#!/bin/bash
node server.js &
NODE_PID=$!
python -m backend.main &
PYTHON_PID=$!
sleep 4
echo "=== Node PID: $NODE_PID Python PID: $PYTHON_PID ==="
# Keep container alive as long as Node.js is running
while kill -0 $NODE_PID 2>/dev/null; do
  sleep 5
done

#!/bin/bash
if command -v redis-server &> /dev/null; then
    redis-server --daemonize yes
    echo "Redis server started in the background."
else
    echo "Redis server not found. Please install Redis."
    exit 1
fi
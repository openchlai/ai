#!/bin/sh
set -e

# Default values if not provided
export VITE_API_HOST=${VITE_API_HOST:-sauti.mglsd.go.ug}
export VITE_API_BASE_PATH=${VITE_API_BASE_PATH:-https://sauti.mglsd.go.ug/helpline/api/}

echo "🔧 Configuring Nginx with Host: $VITE_API_HOST and Base Path: $VITE_API_BASE_PATH"

# Replace variables in the template and output to standard nginx.conf
envsubst '${VITE_API_HOST} ${VITE_API_BASE_PATH}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

echo "🚀 Starting Nginx..."
exec "$@"

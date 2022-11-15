#!/bin/bash

echo "balenaLabs dashboard version: $(cat VERSION)"

# configure Python packages PATH
export PYTHONPATH=/usr/src/python-packages/

# grafana settings
export GF_PATHS_DATA="${BB_DATA_DIR:=/data}/dashboard"
export GF_SERVER_HTTP_PORT="${BB_DASHBOARD_PORT:=80}"
export GF_AUTH_ANONYMOUS_ENABLED=true

python3 update-dashboards.py &

exec /usr/sbin/grafana-server -homepath /usr/share/grafana

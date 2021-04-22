#!/bin/bash

# grafana settings
export GF_PATHS_DATA="${BB_DATA_DIR:=/data}/dashboard"
export GF_SERVER_HTTP_PORT="${BB_DASHBOARD_PORT:=80}"
export GF_AUTH_ANONYMOUS_ENABLED=true


python update-dashboards.py &


exec grafana-server -homepath /share/grafana
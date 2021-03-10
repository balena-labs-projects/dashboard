#!/bin/bash
# configure PATH and library path and python settings
export PATH=/usr/local/bin/:/usr/bin/:$PATH
export LD_LIBRARY_PATH=/usr/local/lib
export PYTHONHOME=/usr/local/
export PYTHONPATH=/usr/local/lib/python3.7/site-packages


# grafana settings
export GF_PATHS_DATA="${BB_DATA_DIR:=/data}/dashboard"
export GF_SERVER_HTTP_PORT="${BB_DASHBOARD_PORT:=80}"
export GF_AUTH_ANONYMOUS_ENABLED=true


python update-dashboards.py &

exec grafana-server -homepath /usr/share/grafana

#!/bin/bash
python update-dashboards.py &
exec grafana-server -homepath /usr/share/grafana
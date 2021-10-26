#!/bin/sh

version="7.3.0"
outfile="/tmp/grafana.deb"
download_base="https://dl.grafana.com/oss/release/"
case $1 in
   "rpi")  package_file="grafana-rpi_${version}_armhf.deb"
       ;;
   "aarch64") package_file="grafana_${version}_arm64.deb"
       ;;
   "amd64") package_file="grafana_${version}_amd64.deb"
       ;;
   "armv7hf") package_file="grafana_${version}_armhf.deb"
       ;;
   *) echo >&2 "error: unsupported architecture ($1)"; exit 1 ;; 
esac
curl -s "${download_base}${package_file}" -o "${outfile}"
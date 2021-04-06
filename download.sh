#!/bin/sh
version="7.1.3"
outfile="/tmp/grafana.deb"
download_base="https://dl.grafana.com/oss/release/"
case $1 in
   rpi)  package_file="grafana-rpi_${version}_armhf.deb"
       ;;
   aarch64) package_file="grafana_${version}_arm64.deb"
       ;;
   armv7hf) package_file="grafana_${version}_armhf.deb"
       ;;
   amd64) package_file="grafana_${version}_amd64.deb"
       ;;
   *) echo "unsupported architecture!"
esac
curl -s "${download_base}${package_file}" -o "${outfile}"

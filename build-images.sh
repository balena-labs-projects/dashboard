#!/bin/bash
set -e

function build_and_push_image () {
  local DOCKER_REPO=$1
  local BALENA_ARCH=$2
  local DOCKER_ARCH=$3

  echo "Building for platform $DOCKER_ARCH(balena arch: $BALENA_ARCH), pushing to $DOCKER_REPO/dashboard"

  sed "s/%%BALENA_ARCH%%/$BALENA_ARCH/g" ./Dockerfile.template > ./Dockerfile.$BALENA_ARCH
  # sed -i.bak "s/%%BALENA_ARCH%%/$BALENA_ARCH/g" ./Dockerfile.$BALENA_MACHINE_NAME && rm ./Dockerfile.$BALENA_MACHINE_NAME.bak
  docker buildx build -t $DOCKER_REPO/dashboard:$BALENA_ARCH --load --platform $DOCKER_ARCH --file Dockerfile.$BALENA_ARCH .

  # echo "Publishing..."
  docker push $DOCKER_REPO/dashboard:$BALENA_ARCH

  echo "Cleaning up..."
  rm Dockerfile.$BALENA_ARCH
}

function create_and_push_manifest() {
  docker manifest create $DOCKER_REPO/dashboard:latest --amend $DOCKER_REPO/dashboard:aarch64 --amend $DOCKER_REPO/dashboard:armv7hf --amend $DOCKER_REPO/dashboard:amd64
  docker manifest push $DOCKER_REPO/dashboard:latest
}

# YOu can pass in a repo (such as a test docker repo) or accept the default
DOCKER_REPO=${1:-balenablocks}

build_and_push_image $DOCKER_REPO "aarch64" "linux/arm64" 
build_and_push_image $DOCKER_REPO "armv7hf" "linux/arm/v7" 
build_and_push_image $DOCKER_REPO "amd64" "linux/amd64"

create_and_push_manifest
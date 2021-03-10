#!/bin/bash
set -e

function build_and_push_image () {
  local DOCKER_REPO=$1
  local BALENA_MACHINE_NAME=$2
  local DOCKER_ARCH=$3
  local BALENA_ARCH=$4

  echo "Building for machine name $BALENA_MACHINE_NAME, platform $DOCKER_ARCH, pushing to $DOCKER_REPO/dashboard"

  sed "s/%%BALENA_MACHINE_NAME%%/$BALENA_MACHINE_NAME/g" ./Dockerfile.template > ./Dockerfile.$BALENA_MACHINE_NAME
  sed -i.bak "s/%%BALENA_ARCH%%/$BALENA_ARCH/g" ./Dockerfile.$BALENA_MACHINE_NAME && rm ./Dockerfile.$BALENA_MACHINE_NAME.bak
  docker buildx build -t $DOCKER_REPO/dashboard:$BALENA_MACHINE_NAME --load --platform $DOCKER_ARCH --file Dockerfile.$BALENA_MACHINE_NAME .

  echo "Publishing..."
  docker push $DOCKER_REPO/dashboard:$BALENA_MACHINE_NAME

  echo "Cleaning up..."
  rm Dockerfile.$BALENA_MACHINE_NAME
}

function create_and_push_manifest() {
  docker manifest create $DOCKER_REPO/dashboard:latest --amend $DOCKER_REPO/dashboard:raspberrypi3 --amend $DOCKER_REPO/dashboard:raspberrypi4-64
  docker manifest push $DOCKER_REPO/dashboard:latest
}

# YOu can pass in a repo (such as a test docker repo) or accept the default
DOCKER_REPO=${1:-balenablocks}

build_and_push_image $DOCKER_REPO "raspberrypi4-64" "linux/arm64" "aarch64"
build_and_push_image $DOCKER_REPO "raspberrypi3" "linux/arm/v7" "armv7hf"
create_and_push_manifest
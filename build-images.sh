#!/bin/bash
set -e

function build_and_push_image () {
  local DOCKER_REPO=$1
  local BALENA_MACHINE_NAME=$2
  local DOCKER_ARCH=$3

  echo "Building for machine name $BALENA_MACHINE_NAME, platform $DOCKER_ARCH using dockerfile from $DOCKERFILE_DIR, pushing to $DOCKER_REPO/balenalabs-dashboard"

  sed "s/%%BALENA_MACHINE_NAME%%/$BALENA_MACHINE_NAME/g" ./Dockerfile.template > ./Dockerfile.$BALENA_MACHINE_NAME
  docker buildx build -t $DOCKER_REPO/balenalabs-dashboard:$BALENA_MACHINE_NAME --platform $DOCKER_ARCH --file Dockerfile.$BALENA_MACHINE_NAME .

  echo "Publishing..."
  docker push $DOCKER_REPO/balenalabs-dashboard:$BALENA_MACHINE_NAME

  echo "Cleaning up..."
  rm Dockerfile.$BALENA_MACHINE_NAME
}

# YOu can pass in a repo (such as a test docker repo) or accept the default
DOCKER_REPO=${1:-balenaplayground}

# build_and_push_image $DOCKER_REPO "raspberrypi4-64" "linux/arm64"
build_and_push_image $DOCKER_REPO "raspberrypi3" "linux/arm/v7"
#!/usr/bin/env bash
set -eo pipefail
#set -x

export ROS_DISTRO=${ROS_DISTRO:-"jazzy"}
export BRANCH_NAME=${BRANCH_NAME:-"${ROS_DISTRO}"}
export SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}
export ROS_IMAGE=${ROS_IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/ros"}
export DISCOVERY_IMAGE=${DISCOVERY_IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/dds-discovery"}


docker buildx build \
  --platform=linux/amd64 \
  --push \
  --tag "${ROS_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --build-arg ROS_DISTRO="${ROS_DISTRO}" \
  --file ./docker/ros2.Dockerfile \
  ./docker

docker buildx build \
  --platform=linux/amd64 \
  --push \
  --tag "${DISCOVERY_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --build-arg ROS_DISTRO="${ROS_DISTRO}" \
  --file ./docker/discovery.Dockerfile \
  ./docker

echo "Images built and pushed:"
echo "  ROS Image: ${ROS_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"
echo "  Discovery Image: ${DISCOVERY_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"

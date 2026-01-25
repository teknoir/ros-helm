#!/usr/bin/env bash
set -eo pipefail
#set -x

export ROS_DISTRO=${ROS_DISTRO:-"jazzy"}
export BRANCH_NAME=${BRANCH_NAME:-"${ROS_DISTRO}"}
export SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}
export IMAGE=${ROS_IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/ros-tb3-headless"}

docker buildx build \
  --platform=linux/amd64 \
  --push \
  --tag "${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --build-arg ROS_DISTRO="${ROS_DISTRO}" \
  .

echo "Images built and pushed:"
echo "  Image: ${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"

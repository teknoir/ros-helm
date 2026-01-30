#!/usr/bin/env bash
set -eo pipefail
#set -x

export NVIROS_ARTIFACT="nviros-humanoid"
export ROS_DISTRO=${ROS_DISTRO:-"jazzy"}
export BRANCH_NAME=${BRANCH_NAME:-"${ROS_DISTRO}"}
export SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}
export IMAGE=${ROS_IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/nviros-humanoid"}

docker buildx build \
  --platform=linux/amd64 \
  --push \
  --tag "${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --build-arg ROS_DISTRO="${ROS_DISTRO}" \
  --build-arg NVIROS_ARTIFACT="${NVIROS_ARTIFACT}" \
  .

echo "Images built and pushed:"
echo "  Image: ${IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"

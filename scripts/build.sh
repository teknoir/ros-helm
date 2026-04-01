#!/usr/bin/env bash
set -eo pipefail
#set -x

export ROS_DISTRO=${ROS_DISTRO:-"jazzy"}
export BRANCH_NAME=${BRANCH_NAME:-"${ROS_DISTRO}"}
export SHORT_SHA=${SHORT_SHA:-$(date +%Y%m%d-%H%M%S)}
export ROS_IMAGE=${ROS_IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/ros"}
export NVIROS_IMAGE=${NVIROS_IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/nviros"}
export ZENOH_ROUTER_IMAGE=${ZENOH_ROUTER_IMAGE:-"us-docker.pkg.dev/teknoir/gcr.io/zenoh-router"}


docker buildx build \
  --platform=linux/arm64/v8,linux/amd64 \
  --push \
  --tag "${ROS_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --build-arg ROS_DISTRO="${ROS_DISTRO}" \
  --file ./docker/ros2.Dockerfile \
  ./docker

docker buildx build \
  --platform=linux/arm64/v8,linux/amd64 \
  --push \
  --tag "${NVIROS_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --build-arg ROS_DISTRO="${ROS_DISTRO}" \
  --build-arg BASE_IMAGE="${ROS_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --file ./docker/nviros.Dockerfile \
  ./docker

docker buildx build \
  --platform=linux/arm64/v8,linux/amd64 \
  --push \
  --tag "${ZENOH_ROUTER_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}" \
  --build-arg ROS_DISTRO="${ROS_DISTRO}" \
  --file ./docker/zenoh-router.Dockerfile \
  ./docker

echo "Images built and pushed:"
echo "  ROS Image:          ${ROS_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"
echo "  NVIROS Image:       ${NVIROS_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"
echo "  Zenoh Router Image: ${ZENOH_ROUTER_IMAGE}:${BRANCH_NAME}-${SHORT_SHA}"

# ROS 2 base image + Kubernetes-friendly defaults
#
# Build:
#   docker build -f Dockerfile.ros2 -t your-registry/ros2-app:jazzy .
#
# Run locally (example):
#   docker run --rm -it your-registry/ros2-app:jazzy ros2 --help

ARG ROS_DISTRO=jazzy
FROM ros:${ROS_DISTRO}-ros-base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Kubernetes-friendly defaults:
# - Explicitly choose Fast DDS RMW (needed if you rely on ROS_DISCOVERY_SERVER).
# - Allow network comms (not localhost-only).
# - Prefer UDPv4 only by default (avoid SHM surprises in containers unless you opt in).
#
# Notes:
# - ROS_DISCOVERY_SERVER is NOT set here; the Helm chart sets it to the in-cluster service DNS.
ENV \
  ROS_DISTRO=${ROS_DISTRO} \
  ROS_DOMAIN_ID=0 \
  ROS_LOCALHOST_ONLY=0 \
  RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  PYTHONUNBUFFERED=1

# tini for proper signal handling (SIGTERM) + optional demo node for quick smoke tests
RUN apt-get update && apt-get install -y --no-install-recommends \
      tini \
      ros-${ROS_DISTRO}-demo-nodes-cpp \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for common PodSecurity defaults
RUN groupadd --gid 10001 ros \
    && useradd  --uid 10001 --gid 10001 -m ros \
    && mkdir -p /ros_ws \
    && chown -R ros:ros /ros_ws

COPY ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

WORKDIR /ros_ws
USER 10001:10001

ENTRYPOINT ["/usr/bin/tini", "--", "/ros_entrypoint.sh"]
CMD ["bash"]
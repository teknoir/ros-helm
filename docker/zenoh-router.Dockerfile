# Zenoh router for ROS2 in Kubernetes.
# Replaces the Fast DDS Discovery Server with a TCP-friendly cloud-native alternative.
#
# Build:
#   docker build -f zenoh-router.Dockerfile -t your-registry/zenoh-router:jazzy .

ARG ROS_DISTRO=jazzy
FROM ros:${ROS_DISTRO}-ros-base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      tini \
      ros-${ROS_DISTRO}-rmw-zenoh-cpp \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10002 zenoh \
    && useradd --uid 10002 --gid 10002 -m zenoh \
    && mkdir -p /data /config \
    && chown -R zenoh:zenoh /data /config

WORKDIR /data
USER 10002:10002

# Zenoh router listens on TCP 7447 by default (much more K8s-friendly than DDS UDP 11811)
EXPOSE 7447/tcp

ENTRYPOINT ["/usr/bin/tini", "--"]
# RMW_ZENOH_ROUTER_CONFIG_URI can be set to override the config file path
CMD ["bash", "-lc", "source /opt/ros/${ROS_DISTRO}/setup.bash && exec ros2 run rmw_zenoh_cpp rmw_zenohd"]

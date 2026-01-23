# Fast DDS Discovery Server container.
#
# Build:
#   docker build -f Dockerfile.fastdds-discovery-server -t your-registry/fastdds-discovery-server:jazzy .
#
# The Discovery Server uses UDP by default and (if no port is specified by clients)
# Fast DDS uses UDP port 11811 by default for ROS_DISCOVERY_SERVER.  [oai_citation:4‡fast-dds.docs.eprosima.com](https://fast-dds.docs.eprosima.com/en/latest/fastdds/env_vars/env_vars.html)

ARG ROS_DISTRO=jazzy
FROM ros:${ROS_DISTRO}-ros-base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

ENV \
  ROS_DISTRO=${ROS_DISTRO} \
  ROS_DOMAIN_ID=0 \
  FASTDDS_BUILTIN_TRANSPORTS=UDPv4

RUN apt-get update && apt-get install -y --no-install-recommends \
      tini \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10002 fastdds \
    && useradd  --uid 10002 --gid 10002 -m fastdds \
    && mkdir -p /data \
    && chown -R fastdds:fastdds /data

WORKDIR /data
USER 10002:10002

EXPOSE 11811/udp

# Foreground server process (Kubernetes-friendly)
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "-lc", "source /opt/ros/${ROS_DISTRO}/setup.bash && exec fastdds discovery"]
ARG ROS_DISTRO=jazzy
FROM nvcr.io/nvidia/isaac-sim:5.1.0

ENV \
  ROS_DISTRO=jazzy \
  ROS_DOMAIN_ID=0 \
  ROS_LOCALHOST_ONLY=0 \
  RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  PYTHONUNBUFFERED=1

USER root
# tini for proper signal handling (SIGTERM) + optional demo node for quick smoke tests
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    git \
    unzip \
    tar \
    wget \
    curl \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

COPY nviros_entrypoint.sh /nviros_entrypoint.sh
RUN chmod +x /nviros_entrypoint.sh

USER isaac-sim

ENTRYPOINT ["/usr/bin/tini", "--", "/nviros_entrypoint.sh"]
CMD ["bash"]
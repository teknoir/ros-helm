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
# - Use Zenoh RMW for cloud-native, TCP-based discovery (no multicast required).
# - Allow network comms (not localhost-only).
# - ZENOH_CONFIG is NOT set here; the Helm chart mounts a client config pointing to the in-cluster router.
ENV \
  ROS_DISTRO=${ROS_DISTRO} \
  ROS_DOMAIN_ID=0 \
  ROS_LOCALHOST_ONLY=0 \
  RMW_IMPLEMENTATION=rmw_zenoh_cpp \
  PYTHONUNBUFFERED=1

# tini for proper signal handling (SIGTERM) + optional demo node for quick smoke tests
RUN apt-get update && apt-get install -y --no-install-recommends \
      tini \
      build-essential \
      cmake \
      git \
      unzip \
      wget \
      curl \
      vim \
      nano \
      locales \
      sudo \
      v4l-utils \
      python3-pip \
      python3-dev \
      python3-venv \
      python-is-python3 \
      python3-colcon-common-extensions \
      python3-rosdep \
      python3-vcstool \
      ros-${ROS_DISTRO}-ament-cmake \
      ros-${ROS_DISTRO}-ament-cmake-clang-format \
      ros-${ROS_DISTRO}-ament-cmake-cpplint \
      ros-${ROS_DISTRO}-ament-cmake-cppcheck \
      ros-${ROS_DISTRO}-ament-cmake-flake8 \
      ros-${ROS_DISTRO}-ament-cmake-pep257 \
      ros-${ROS_DISTRO}-ament-lint \
      ros-${ROS_DISTRO}-ament-lint-auto \
      ros-${ROS_DISTRO}-ament-lint-common \
      ros-${ROS_DISTRO}-rmw-zenoh-cpp \
      ros-${ROS_DISTRO}-demo-nodes-cpp \
      ros-${ROS_DISTRO}-demo-nodes-py \
      ros-${ROS_DISTRO}-foxglove-bridge \
      ros-${ROS_DISTRO}-image-tools \
      ros-${ROS_DISTRO}-v4l2-camera \
      ros-${ROS_DISTRO}-desktop \
      ros-${ROS_DISTRO}-rqt \
      ros-${ROS_DISTRO}-rqt-common-plugins \
      ros-${ROS_DISTRO}-navigation2 \
      ros-${ROS_DISTRO}-ros2bag \
      ros-${ROS_DISTRO}-cartographer-ros \
      ros-${ROS_DISTRO}-cartographer \
      ros-${ROS_DISTRO}-slam-toolbox \
      ros-${ROS_DISTRO}-ros-gz \
      ros-${ROS_DISTRO}-gazebo-* \
      ros-${ROS_DISTRO}-turtlebot3 \
      ros-${ROS_DISTRO}-turtlebot3-* \
      ros-${ROS_DISTRO}-nav2-bringup \
      ros-${ROS_DISTRO}-rviz2 \
    && rm -rf /var/lib/apt/lists/*

# Install useful Python packages for ROS 2 development
RUN pip3 install --no-cache-dir --break-system-packages --ignore-installed \
    'setuptools<80,>=30.3.0' \
    pytest \
    pytest-cov \
    pytest-mock \
    flake8 \
    mypy \
    black \
    isort \
    pylint \
    ipython \
    jupyter \
    'rosbags>=0.9.11' \
    colcon-ros \
    colcon-cmake \
    colcon-python-setup-py \
    colcon-mixin \
    colcon-ros-bundle \
    colcon-argcomplete \
    ;

COPY ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

WORKDIR /ros_ws

ENTRYPOINT ["/usr/bin/tini", "--", "/ros_entrypoint.sh"]
CMD ["bash"]
#!/usr/bin/env bash
set -euo pipefail

# Temporarily disable 'nounset' while sourcing ROS setup scripts
set +u
./setup_ros_env.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/isaac-sim/exts/isaacsim.ros2.bridge/${ROS_DISTRO}/lib
set -u

/bin/bash -c "$@"
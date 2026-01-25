#!/usr/bin/env bash
set -euo pipefail

# Temporarily disable 'nounset' while sourcing ROS setup scripts
set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Source overlay if present (e.g. after colon build to /ros_ws/install)
if [ -f "/ros_ws/install/setup.bash" ]; then
  source "/ros_ws/install/setup.bash"
fi
set -u

/bin/bash -c "$@"
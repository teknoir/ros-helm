#!/usr/bin/env bash
set -euo pipefail

# Source the ROS installation
# shellcheck disable=SC1090
source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Source overlay if present (e.g. after colcon build to /ros_ws/install)
if [ -f "/ros_ws/install/setup.bash" ]; then
  # shellcheck disable=SC1090
  source "/ros_ws/install/setup.bash"
fi

exec "$@"
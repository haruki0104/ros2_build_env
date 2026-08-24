#!/bin/bash
set -e

# Source the main ROS 2 installation (use POSIX "." and setup.sh so this
# script also works when invoked with sh/dash, not just bash)
if [ -f "/opt/ros/$ROS_DISTRO/setup.bash" ]; then
    . "/opt/ros/$ROS_DISTRO/setup.bash"
fi

# Source the colcon workspace if it has been built
if [ -f "/workspace/colcon_ws/install/setup.bash" ]; then
    . "/workspace/colcon_ws/install/setup.bash"
fi

# Execute the passed command
exec "$@"

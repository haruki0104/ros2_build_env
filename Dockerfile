# Use ROS 2 Jazzy as the default base (supports rmw_zenoh_cpp natively)
ARG ROS_DISTRO=jazzy
FROM ros:${ROS_DISTRO}

# Set non-interactive timezone/frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and development tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    cmake \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    clang \
    llvm \
    pkg-config \
    libssl-dev \
    # The three RMW implementations
    ros-${ROS_DISTRO}-rmw-fastrtps-cpp \
    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
    ros-${ROS_DISTRO}-rmw-zenoh-cpp \
    && rm -rf /var/lib/apt/lists/*

# Add convenient aliases for switching RMWs in the terminal
RUN echo "\n# Easy ROS 2 RMW switching aliases\n\
alias use_fastdds='export RMW_IMPLEMENTATION=rmw_fastrtps_cpp && ros2 daemon stop && echo \"Active RMW: rmw_fastrtps_cpp (FastDDS)\"'\n\
alias use_cyclonedds='export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp && ros2 daemon stop && echo \"Active RMW: rmw_cyclonedds_cpp (CycloneDDS)\"'\n\
alias use_zenoh='export RMW_IMPLEMENTATION=rmw_zenoh_cpp && ros2 daemon stop && echo \"Active RMW: rmw_zenoh_cpp (Zenoh)\"'\n\
\n\
echo \"===============================================\"\n\
echo \"🚀 Welcome to ROS 2 & Zenoh Build Environment\"\n\
echo \"-----------------------------------------------\"\n\
echo \"Available RMW implementations:\"\n\
echo \"  1. FastDDS    -> run: use_fastdds\"\n\
echo \"  2. CycloneDDS -> run: use_cyclonedds\"\n\
echo \"  3. Zenoh      -> run: use_zenoh\"\n\
echo \"===============================================\"\n" >> /etc/bash.bashrc

# Install Rust (necessary for compiling zenoh-bridge-ros2dds or other Rust packages from source)
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable \
    && chmod -R a+w $RUSTUP_HOME $CARGO_HOME

# Initialize rosdep (if not already done in the base image)
RUN if [ ! -r /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
        rosdep init; \
    fi && rosdep update

# Set up the working directory inside the container
WORKDIR /workspace

# Set the default entrypoint to source ROS 2 and setup bash environment
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

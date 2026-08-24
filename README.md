# ROS 2 & Zenoh Build Environment (macOS + Docker)

This repository sets up a complete ROS 2 build environment integrated with **Zenoh** (both `rmw_zenoh_cpp` and `zenoh-bridge-ros2dds`) on macOS. 

Since ROS 2 is not natively supported on macOS, the setup uses a Linux-based Docker environment. By mounting the host directory, all built packages, libraries, and binaries are immediately exported and accessible on your host machine under `colcon_ws/`.

---

## 🏗️ Architecture Overview

```
ros2_build_env_ws/
├── Dockerfile              # Developer image with ROS 2, Rust, and Zenoh dependencies
├── docker-compose.yml      # Manages container lifecycle, host mounts, and host networking
├── entrypoint.sh           # Automatically sources ROS 2 and workspace installations
└── colcon_ws/              # ROS 2 workspace mounted on the host
    └── src/                # Put your custom ROS 2 packages and clone repos here
```

> **Note:** Because macOS has a different processor architecture/kernel than the Linux container, you cannot execute the built Linux binaries directly on macOS. However, mounting ensures that all source files, configurations, and build outputs are safely exported to the host directory for code editing, deployment packaging, or mounting in other containers.

---

## 🛠️ Step-by-Step Setup

### 1. Build and Start the Environment

1. Navigate to your workspace directory on macOS:
   ```bash
   cd /Users/patrick/Workspace/workspace_ros2/ros2_build_env_ws
   ```
2. Build the Docker image:
   ```bash
   docker compose build
   ```
3. Start the build container interactively:
   ```bash
   docker compose run --rm ros2_builder bash
   ```
   *You will now be inside the container terminal at the `/workspace/colcon_ws` directory.*

---

### 2. Building Custom ROS 2 Packages

Once inside the container, you can build your packages:

1. Clone or place your ROS 2 packages in `colcon_ws/src/` (on the host or in the container).
2. Inside the container, run:
   ```bash
   colcon build --symlink-install
   ```
3. The build artifacts (`build/`, `install/`, `log/`) will immediately appear on your macOS host under `colcon_ws/`.

---

### 3. Integrating Zenoh Bridge (`zenoh-bridge-ros2dds`)

The Zenoh bridge acts as a translator between traditional ROS 2 DDS networks and Zenoh. Since Rust is installed inside the builder image, you can compile it from source easily:

1. From the host or inside the container, clone the bridge repo into your source directory:
   ```bash
   cd /workspace/colcon_ws/src
   git clone https://github.com/eclipse-zenoh/zenoh-plugin-ros2dds.git
   ```
2. Build the bridge using Cargo inside the container:
   ```bash
   cd zenoh-plugin-ros2dds
   cargo build --release
   ```
3. The compiled binary will be located at:
   `/workspace/colcon_ws/src/zenoh-plugin-ros2dds/target/release/zenoh-bridge-ros2dds`
   And it will be fully accessible on your host machine under the corresponding path.

To run the bridge:
```bash
./target/release/zenoh-bridge-ros2dds
```

---

### 4. Switching RMW Implementations (FastDDS, CycloneDDS, Zenoh)

Inside the interactive build container, you can instantly switch the active middleware for your ROS 2 nodes using pre-configured helper aliases. Each alias sets the correct `RMW_IMPLEMENTATION` variable and stops any background ROS 2 daemons to apply the changes cleanly:

*   **FastDDS** (Default):
    ```bash
    use_fastdds
    ```
*   **CycloneDDS**:
    ```bash
    use_cyclonedds
    ```
*   **Zenoh**:
    ```bash
    use_zenoh
    ```

---

### 5. Using Zenoh as the Native Middleware (`rmw_zenoh_cpp`)

Instead of bridging DDS, you can use Zenoh as the underlying middleware directly (replacing FastDDS/CycloneDDS). The Docker environment comes with `rmw-zenoh-cpp` pre-installed.

1. **Start the Zenoh Router**:
   Zenoh requires a routing daemon to manage discovery:
   ```bash
   ros2 run rmw_zenoh_cpp rmw_zenohd
   ```
2. **Run ROS 2 Nodes with Zenoh**:
   In another container terminal, export the environment variable and run your nodes:
   ```bash
   export RMW_IMPLEMENTATION=rmw_zenoh_cpp
   ros2 run demo_nodes_cpp talker
   ```
   And in another window:
   ```bash
   export RMW_IMPLEMENTATION=rmw_zenoh_cpp
   ros2 run demo_nodes_cpp listener
   ```

---

## 💡 Troubleshooting & Tips

* **Network Mode:** Always run Docker with `--network host` (configured by default in `docker-compose.yml`). This is critical because DDS and Zenoh discover other nodes via multicast, which standard Docker bridge networks block.
* **Changing ROS Distro:** If you need to build for a different ROS 2 version (e.g. Humble), simply edit `docker-compose.yml` to change `ROS_DISTRO=jazzy` to `ROS_DISTRO=humble` and run `docker compose build` again.

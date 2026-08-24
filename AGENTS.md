# AGENTS.md

## What this repo is

Docker-based ROS 2 build environment for macOS. ROS 2 doesn't run natively on macOS, so all builds happen inside a Linux container. `colcon_ws/` is volume-mounted so build artifacts appear on the host.

## Key commands

```bash
# From the host (macOS):
docker compose build                    # build/rebuild the image
docker compose run --rm ros2_builder bash  # enter interactive build shell

# Inside the container (at /workspace/colcon_ws):
colcon build --symlink-install          # build all packages in colcon_ws/src/
```

## RMW switching (inside container only)

Three RMW implementations are pre-installed. Use these aliases:

- `use_fastdds` (default)
- `use_cyclonedds`
- `use_zenoh`

Each sets `RMW_IMPLEMENTATION` and stops the ROS 2 daemon.

## Gotchas

- **Host networking is mandatory.** `docker-compose.yml` sets `network_mode: "host"`. DDS/Zenoh discover nodes via multicast, which bridge networks block. Do not remove this.
- **Linux binaries can't run on macOS.** Built artifacts are for deployment/mounting, not local execution.
- **ROS distro** is Jazzy by default. Change `ROS_DISTRO` in both `Dockerfile` and `docker-compose.yml`, then `docker compose build`.
- **Zenoh router** is required when using `rmw_zenoh_cpp`: `ros2 run rmw_zenoh_cpp rmw_zenohd`.
- **Zenoh bridge** (DDS-to-Zenoh translator) must be compiled from source via `cargo build --release` inside the container. Rust is pre-installed.
- `entrypoint.sh` sources `/opt/ros/$ROS_DISTRO/setup.sh` and `colcon_ws/install/setup.sh` automatically. It uses POSIX `.`/`setup.sh` (not bash-only `source`/`setup.bash`) so it works under both bash and sh/dash.

## Structure

- `Dockerfile` — ROS 2 Jazzy image with all three RMW impls, Rust, build tools
- `docker-compose.yml` — container config, host mounts, host networking
- `entrypoint.sh` — sources ROS 2 and workspace setup on shell entry
- `colcon_ws/src/` — custom ROS 2 packages go here (empty by default)
- `.github/workflows/ci.yml` — CI: lint, test, compose validation, docker build
- `tests/` — pytest suite (config in `pyproject.toml`)
- `requirements.txt` / `requirements-dev.txt` — Python deps for `pdf_to_docx.py` + lint/test tools
- `pdf_to_docx.py` — unrelated utility (PDF→DOCX converter)

## Git flow

- `main` — stable releases only
- `dev` — **default branch**; all integration happens here
- **Every feature implementation must get its own `feat/<short-description>` branch off `dev`.** Never commit features directly to `dev` or `main`.
- Bug fixes use `fix/<short-description>` branches off `dev`
- Open a PR back to `dev` when done; CI must be green before merging

## Lint, test & CI

GitHub Actions CI (`.github/workflows/ci.yml`) runs on pushes/PRs to `main` and `dev`:

- ruff — Python lint (config: `pyproject.toml`)
- pytest — Python tests (`tests/`)
- shellcheck — `entrypoint.sh`
- hadolint — `Dockerfile` (config: `.hadolint.yaml`)
- yamllint — YAML files (config: `.yamllint.yml`)
- `docker compose config -q` — compose file validation
- `docker build .` — full image build check

Run everything locally before pushing:

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
yamllint .
docker run --rm -v "$PWD:/mnt" koalaman/shellcheck:stable /mnt/entrypoint.sh
docker run --rm -v "$PWD:/repo" -w /repo hadolint/hadolint hadolint Dockerfile
docker compose config -q
```

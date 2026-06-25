# NVIROS Humanoid Example Image

Example NVIROS workload demonstrating a humanoid-robot ROS2 stack on GPU-capable edge devices.

- Repository: `ghcr.io/teknoir/ros-helm/nviros-humanoid-example`
- Dockerfile: `docker/src/nviros-humanoid-example/Dockerfile`
- Tags: `beta`, `latest`

## Use on an edge device

Run it as a `ros` chart instance with `nviros: true`, placed on a GPU/Jetson node via
`nodeSelector`. Use it as a starting point for custom humanoid pipelines.

See the [ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the full deployable manifest.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.

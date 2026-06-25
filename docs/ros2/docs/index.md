# ROS2 Image

Base ROS2 container image used by the `ros` Helm chart instances on edge devices.

- Repository: `ghcr.io/teknoir/ros-helm/ros2`
- Dockerfile: `docker/ros2.Dockerfile`
- Tags: `beta`, `latest`

## Use on an edge device

This image is the default runtime for `ros` chart `instances`. Deploy it through the Teknoir
platform with a K3s `HelmChart` resource and set it via `defaults.image`:

```yaml
defaults:
  image:
    repository: ghcr.io/teknoir/ros-helm/ros2
    tag: beta
```

See the [ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the full deployable manifest.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.

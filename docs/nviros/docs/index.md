# NVIROS Image

NVIDIA-enabled ROS2 container image (GPU / Isaac workloads) for edge devices such as
Jetson-class hardware.

- Repository: `ghcr.io/teknoir/ros-helm/nviros`
- Dockerfile: `docker/nviros.Dockerfile`
- Tags: `beta`, `latest`

## Use on an edge device

Run NVIROS workloads as a `ros` chart instance with `nviros: true` and place them on
GPU-capable nodes via `nodeSelector`:

```yaml
instances:
  - name: isaac-sim
    nviros: true
    commands:
      - ./runheadless.sh -v
```

See the [ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the full deployable manifest.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.

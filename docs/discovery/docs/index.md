# Discovery Image

Container image for the DDS Discovery Server, which centralizes ROS2 peer discovery so nodes
find each other reliably on constrained edge networks.

- Repository: `ghcr.io/teknoir/ros-helm/discovery`
- Dockerfile: `docker/discovery.Dockerfile`
- Tags: `beta`, `latest`

## Use on an edge device

Enabled through the `ros` chart's `discoveryServer` settings; `instances` then connect to it
automatically. Override the address only when pointing at an external server:

```yaml
discoveryServer:
  enabled: true
# defaults.discoveryServerAddress: "custom-discovery-server:11811"
```

See the [ROS2 HelmChart](../../ros2-helm/docs/index.md) docs for the full deployable manifest.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.

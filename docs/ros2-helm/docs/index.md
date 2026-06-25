# ROS2 HelmChart

The `ros` Helm chart packages ROS2 workloads so they can be deployed and switched as one
rollout on edge devices through the Teknoir platform.

- Registry: `teknoir.github.io/ros-helm`
- Chart: `ros`
- Version: `0.0.0-dds-beta.6`

## Deploy on an edge device

On a K3s edge device, commit/apply a `HelmChart` resource (via Devstudio `add-app` or GitOps).
The chart holds the static service definitions; only override the minimal per-device values.

```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: ros
  namespace: default
spec:
  repo: https://teknoir.github.io/ros-helm
  chart: ros
  version: 0.0.0-dds-beta.6
  targetNamespace: default
  valuesContent: |-
    defaults:
      imagePullSecrets:
        - name: teknoir-pullsecret
      nodeSelector:
        kubernetes.io/hostname: teknoir-master
    instances:
      - name: foxglove-bridge
        superClient: "TRUE"
        commands:
          - ros2 launch foxglove_bridge foxglove_bridge_launch.xml use_sim_time:=True port:=8765
        nodePorts:
          - name: http-fg-bridge
            port: 8765
            targetPort: 8765
            nodePort: 31765
```

Add more `instances` (with `commands` and optional `artifacts`) for your robot use case.
Switching from one `ros` HelmChart to another cleans up the previous release and rolls out the
new one. Visualize topics with Foxglove via `tnctl port-forward <device-name> 8765:31765`.

Reference: Teknoir Workshop 2 — Software Management and Helm Deployment Workflows.

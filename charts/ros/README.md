# Nvidia Isaac ROS Helm Chart

This chart deploys the ROS to a Kubernetes cluster.

> The implementation of the Helm chart is right now the bare minimum to get it to work.
> The Helm Chart is not meant to be infinitely configurable, but to provide a quick way to deploy NVIROS to a Kubernetes cluster.

## Usage in Teknoir platform
Use the HelmChart to deploy the ROS to a Device.

```yaml
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: ros
  namespace: default
spec:
  repo: https://teknoir.github.io/ros-helm
  chart: ros
  targetNamespace: default
  valuesContent: |-
    # Examples TBD
```

## Adding the repository

```bash
helm repo add teknoir-ros https://teknoir.github.io/ros-helm/
```

## Installing the chart

```bash
helm install ros teknoir-ros/ros -f values.yaml
```
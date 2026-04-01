# Zenoh router with REST + WebSocket (remote_api) plugins.
# Extends eclipse/zenoh with libzenoh_plugin_remote_api.so, which is not
# bundled in the upstream image but is published as a binary release on GitHub.
#
# ZENOH_VERSION must match the version in eclipse/zenoh:${ZENOH_VERSION}.
# Check with: docker run --rm eclipse/zenoh:latest zenohd --version
#
# Build:
#   docker buildx build \
#     --platform=linux/arm64/v8,linux/amd64 \
#     --build-arg ZENOH_VERSION=1.8.0 \
#     -f zenoh-router.Dockerfile -t your-registry/zenoh-router:1.8.0 .

ARG ZENOH_VERSION=1.8.0

# --- Download stage: fetch the remote_api plugin for the target arch ---
FROM alpine:3 AS plugin
ARG ZENOH_VERSION
ARG TARGETARCH
RUN apk add --no-cache wget unzip \
    && case "${TARGETARCH}" in \
         amd64) ARCH="x86_64-unknown-linux-musl-standalone"    ;; \
         arm64) ARCH="aarch64-unknown-linux-musl-standalone"   ;; \
         *) echo "Unsupported arch: ${TARGETARCH}" && exit 1 ;; \
       esac \
    && wget -q \
         "https://download.eclipse.org/zenoh/zenoh-plugin-remote-api/${ZENOH_VERSION}/zenoh-ts-${ZENOH_VERSION}-${ARCH}.zip" \
         -O /tmp/plugin.zip \
    && unzip /tmp/plugin.zip -d /tmp/plugin

# --- Final image: eclipse/zenoh + remote_api plugin alongside the REST plugin ---
FROM eclipse/zenoh:${ZENOH_VERSION}
COPY --from=plugin /tmp/plugin/libzenoh_plugin_remote_api.so /libzenoh_plugin_remote_api.so

EXPOSE 7447/tcp
EXPOSE 8000/tcp
EXPOSE 10000/tcp

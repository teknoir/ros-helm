FROM alpine:3

ARG TARGETARCH

RUN  apk add --no-cache rsync

COPY tb3_headless_launch /src/tb3_headless_launch

CMD ["sh", "-c", "mkdir -p /ros_ws/src/tb3_headless_launch && rsync --checksum --itemize-changes --delete-before -avhr /src/tb3_headless_launch/ /ros_ws/src/tb3_headless_launch/"]

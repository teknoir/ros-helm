FROM alpine:3

ARG NVIROS_ARTIFACT=nviros-example
ENV NVIROS_ARTIFACT=${NVIROS_ARTIFACT}
ENV NVIROS_ARTIFACT_FULLPATH="/isaac-sim/teknoir-examples/${NVIROS_ARTIFACT}"

RUN  apk add --no-cache rsync

COPY ${NVIROS_ARTIFACT} /src/${NVIROS_ARTIFACT}

CMD ["sh", "-c", "mkdir -p ${NVIROS_ARTIFACT_FULLPATH} && rsync --checksum --itemize-changes --delete-before -avhr /src/${NVIROS_ARTIFACT}/ ${NVIROS_ARTIFACT_FULLPATH}/ && chown -R 1234:1234 ${NVIROS_ARTIFACT_FULLPATH}"]

FROM debian:bookworm-slim

LABEL maintainer="nomapa223@gmail.com"
LABEL description="MechanicsDSL embedded cross-compilation environment for ARM/Raspberry Pi"

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    cmake \
    make \
    ninja-build \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install mechanicsdsl-core --break-system-packages

WORKDIR /workspace

ENV CC=arm-linux-gnueabihf-gcc
ENV CXX=arm-linux-gnueabihf-g++

CMD ["/bin/bash"]

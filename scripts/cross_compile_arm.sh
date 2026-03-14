#!/bin/bash
# cross_compile_arm.sh
# --------------------
# Cross-compiles mechanicsdsl-embedded for ARM (Raspberry Pi) using Docker.
# Outputs binaries to build_arm/ for scp transfer to the device.
#
# Usage:
#   ./scripts/cross_compile_arm.sh
#   ./scripts/cross_compile_arm.sh --clean

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$REPO_ROOT/build_arm"

echo "MechanicsDSL embedded — ARM cross-compilation"
echo "Repository: $REPO_ROOT"
echo ""

if [[ "$1" == "--clean" ]]; then
    echo "Cleaning build directory..."
    rm -rf "$BUILD_DIR"
fi

# Check Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker not found. Install Docker and retry."
    exit 1
fi

# Build Docker image if not present
if ! docker image inspect mechanicsdsl-embedded:latest &> /dev/null; then
    echo "Building Docker cross-compilation image..."
    docker build -t mechanicsdsl-embedded:latest "$REPO_ROOT/docker/"
fi

# Run cross-compilation
echo "Cross-compiling for ARM..."
docker run --rm \
    -v "$REPO_ROOT:/workspace" \
    -w /workspace \
    mechanicsdsl-embedded:latest \
    bash -c "
        mkdir -p build_arm && cd build_arm &&
        cmake .. \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_C_COMPILER=arm-linux-gnueabihf-gcc \
            -DCMAKE_CXX_COMPILER=arm-linux-gnueabihf-g++ \
            -DCMAKE_SYSTEM_NAME=Linux \
            -DCMAKE_SYSTEM_PROCESSOR=armv7l \
            2>&1 &&
        make -j\$(nproc) 2>&1
    "

echo ""
echo "Build complete. Binaries in: $BUILD_DIR"
echo ""
echo "To deploy to Raspberry Pi:"
echo "  scp $BUILD_DIR/pendulum_rpi pi@<rpi-ip>:~/mechanicsdsl/"
echo "  ssh pi@<rpi-ip> 'sudo ~/mechanicsdsl/pendulum_rpi'"

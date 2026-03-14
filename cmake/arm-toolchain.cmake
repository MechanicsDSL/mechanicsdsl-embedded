# arm-toolchain.cmake
# --------------------
# CMake toolchain file for ARM cross-compilation (Raspberry Pi 3B+/4).
# Used by the Docker cross-compilation environment.
#
# Usage:
#   cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/arm-toolchain.cmake

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR armv7l)

# Cross-compilation toolchain
set(CMAKE_C_COMPILER   arm-linux-gnueabihf-gcc)
set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)
set(CMAKE_STRIP        arm-linux-gnueabihf-strip)

# Root filesystem (set to your RPi sysroot if available)
# set(CMAKE_SYSROOT /path/to/rpi-sysroot)

# ARM Cortex-A72 (RPi 4) optimisation flags
set(CMAKE_C_FLAGS_INIT
    "-march=armv8-a+crc -mtune=cortex-a72 -mfpu=neon-fp-armv8 -mfloat-abi=hard -O3 -ffast-math")
set(CMAKE_CXX_FLAGS_INIT ${CMAKE_C_FLAGS_INIT})

# Search behaviour — don't look in host paths
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

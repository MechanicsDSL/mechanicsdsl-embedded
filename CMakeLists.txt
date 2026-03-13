cmake_minimum_required(VERSION 3.16)
project(mechanicsdsl_pendulum_rpi VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Release build with Raspberry Pi ARM optimisations by default
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# ARM NEON optimisation flags for Raspberry Pi 3B+/4
if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm|aarch64")
  set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -mfpu=neon -ffast-math")
  message(STATUS "ARM/NEON optimisations enabled")
else()
  set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -ffast-math")
endif()

# ---------------------------------------------------------------------------
# pigpio dependency
# ---------------------------------------------------------------------------
find_library(PIGPIO_LIB NAMES pigpio REQUIRED
  HINTS /usr/lib /usr/local/lib)
find_path(PIGPIO_INCLUDE NAMES pigpio.h
  HINTS /usr/include /usr/local/include)

if(NOT PIGPIO_LIB OR NOT PIGPIO_INCLUDE)
  message(FATAL_ERROR
    "pigpio not found. Install with: sudo apt-get install pigpio libpigpio-dev")
endif()

# ---------------------------------------------------------------------------
# pendulum_rpi executable
# MechanicsDSL-generated equations of motion for simple pendulum
# ---------------------------------------------------------------------------
add_executable(pendulum_rpi
  examples/raspberry_pi_pendulum/pendulum_rpi.cpp
)

target_include_directories(pendulum_rpi PRIVATE ${PIGPIO_INCLUDE})

target_link_libraries(pendulum_rpi
  PRIVATE
    ${PIGPIO_LIB}
    pthread
    m
)

target_compile_options(pendulum_rpi PRIVATE -Wall -Wextra -Wpedantic)

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
install(TARGETS pendulum_rpi DESTINATION bin)

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "pigpio: ${PIGPIO_LIB}")

# ---------------------------------------------------------------------------
# Usage hint
# ---------------------------------------------------------------------------
add_custom_target(run_pendulum
  COMMAND sudo ./pendulum_rpi
  DEPENDS pendulum_rpi
  COMMENT "Running pendulum simulation (requires root for pigpio + RT scheduling)"
)

# Changelog

## [Unreleased]

### Added
- `examples/arduino_pendulum/pendulum_realtime.ino` — MPU6050 + RK4 at 250 Hz
- `examples/arduino_double_pendulum/double_pendulum.ino` — double pendulum at 200 Hz
- `examples/raspberry_pi_pendulum/pendulum_rpi.cpp` — pigpio + POSIX RT + NEON
- `examples/raspberry_pi_double_pendulum/double_pendulum_rpi.cpp` — double pendulum on RPi
- `CMakeLists.txt` — ARM-optimised CMake build with pigpio
- `docker/Dockerfile` — ARM cross-compilation environment
- `docker/docker-compose.yml` — cross-compile and code-generate services
- `scripts/cross_compile_arm.sh` — one-command ARM build via Docker
- `tests/test_eom.py` — pytest suite validating EOM physics correctness
- Example READMEs for all examples

## [0.1.0] — 2026-03-13

- Initial repository scaffold

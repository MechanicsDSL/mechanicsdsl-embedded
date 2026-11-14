# Changelog

## [0.2.0] - 2026-11-14

### Added
- `c_header` target: portable single-header C99 (`--precision float|double`) with RK4, energy function and common-subexpression elimination. Compiled with `-Werror -pedantic` and checked against a Python reference in the test suite.
- `rust_no_std` target: a `#![no_std]` Cargo crate on `libm` (no allocator), with its own `cargo test`.
- `inspect`, `budget` (ops per RK4 step, MFLOP/s needed, RAM), `verify` (RK4 energy drift at a chosen dt; exit code 4 on failure) and `presets` commands.
- Shared bridge to core: energy E = sum(qdot dL/dqdot) - L derived from the Lagrangian, a `conservative` flag, `simulate()` (fixed-step RK4 reference), `energy_drift()`, `operation_count()`, `list_presets()`, and `CompiledSystem.describe()`.
- Core's mass-matrix output (`__mass_matrix__`, used for large systems such as the three-body `figure8` preset) is converted to explicit accelerations, so every core preset now generates.

### Fixed
- `get_example_path()` looked for a local clone one directory above the repository.
- `tests/test_eom.py::test_energy_conservation` was a strict xfail blamed on core. The test read core's interleaved state `[theta1, theta1_dot, theta2, theta2_dot]` positionally; read by name, core's double-pendulum EOM conserves energy and the test passes.
- Generated code can no longer collide with user names: internal identifiers are `mdsl_`-prefixed (a coordinate named `y` previously broke compilation).

### Infrastructure
- CI workflow: pytest on Python 3.9-3.12 (Linux) plus Windows and macOS, a syntax/undefined-name lint, and an sdist/wheel build check.
- Dependabot (pip and GitHub Actions), issue and PR templates, pre-commit config, `SECURITY.md`, `CODE_OF_CONDUCT.md`.
- Single-source version (`_version.py`, read by hatch); requires `mechanicsdsl-core>=2.1.4`.

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

<p align="center">
  <img src="https://raw.githubusercontent.com/MechanicsDSL/mechanicsdsl/main/docs/images/logo.png" alt="MechanicsDSL Logo" width="360">
</p>

<h1 align="center">mechanicsdsl-embedded</h1>

<p align="center">
  <em>Deploy MechanicsDSL simulations to Arduino, Raspberry Pi, and ARM edge devices.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-planned-lightgrey" alt="Status: Planned">
  <img src="https://img.shields.io/badge/targets-Arduino%20%7C%20RPi%20%7C%20ARM-blue" alt="Targets">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <a href="https://github.com/MechanicsDSL/mechanicsdsl"><img src="https://img.shields.io/badge/core-mechanicsdsl-blue" alt="Core Package"></a>
</p>

---

## Overview

`mechanicsdsl-embedded` extends the MechanicsDSL compiler toolchain to embedded and edge platforms. Write your physical system once in DSL notation; generate optimized, dependency-free C++ or `no_std` Rust ready to flash to a microcontroller or deploy to a Raspberry Pi.

This repository targets closed-loop control applications, real-time robotics, science fair hardware builds, and any scenario where simulation needs to run on the device — not in the cloud.

---

## Planned Capabilities

### Code Generation
- **Arduino C++** — Single-file `.ino` output with no heap allocation, fixed-point arithmetic options, and serial logging hooks
- **Raspberry Pi C++** — CMake projects with pigpio integration, real-time scheduling support, and GPIO output for actuator control
- **ARM / NEON** — Auto-detected SIMD intrinsics for Cortex-A series; cross-compilation toolchain configurations included
- **`no_std` Rust** — Microcontroller targets via `embedded-hal`; Cargo project scaffolding with Embassy async runtime support

### Sensor Integration
- **IMU fusion** — MPU6050, BNO055, and ICM-42688 examples with complementary and Kalman filter state estimation
- **Encoder feedback** — Quadrature encoder reading with velocity estimation for pendulum and motor control examples
- **Serial telemetry** — Structured output for real-time logging and visualization over USB/UART

### Example Projects
- Real-time inverted pendulum stabilization on Raspberry Pi
- Double pendulum chaos demonstration with LED visualization on Arduino
- IMU-driven rigid body orientation estimation
- Coupled oscillator parameter estimation from sensor data

---

## Relationship to Core Package

This repository provides deployment infrastructure and examples. The symbolic derivation, constraint handling, and code generation engine lives in [mechanicsdsl](https://github.com/MechanicsDSL/mechanicsdsl). Install the core package to generate embedded targets:

```bash
pip install mechanicsdsl-core[embedded]
```

---

## Status

This repository is in the planning stage. Development will begin following stabilization of the embedded code generation backends in the core package. Watch this repository or the [core repo](https://github.com/MechanicsDSL/mechanicsdsl) for updates.

---

## Contributing

Contributions welcome — particularly from those with embedded hardware experience. See [CONTRIBUTING.md](https://github.com/MechanicsDSL/mechanicsdsl/blob/main/CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://github.com/MechanicsDSL/mechanicsdsl">Core Package</a> ·
  <a href="https://mechanicsdsl.readthedocs.io">Documentation</a> ·
  <a href="https://doi.org/10.5281/zenodo.17771040">Zenodo DOI</a>
</p>

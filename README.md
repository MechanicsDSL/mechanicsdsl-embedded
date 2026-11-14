<p align="center">
  <img src="https://raw.githubusercontent.com/MechanicsDSL/mechanicsdsl/main/docs/images/logo.png" alt="MechanicsDSL Logo" width="360">
</p>

<h1 align="center">mechanicsdsl-embedded</h1>

<p align="center">
  <em>Deploy MechanicsDSL simulations to Arduino, Raspberry Pi, and ARM edge devices.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-active-green" alt="Active">
  <img src="https://img.shields.io/badge/targets-Arduino%20%7C%20RPi%20%7C%20ARM-blue" alt="Targets">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <a href="https://github.com/MechanicsDSL/mechanicsdsl"><img src="https://img.shields.io/badge/core-mechanicsdsl-blue" alt="Core Package"></a>
</p>

## Overview

`mechanicsdsl-embedded` provides deployment infrastructure and examples for running MechanicsDSL-generated simulations on embedded and edge platforms. Write your physical system once in DSL notation; generate optimized, dependency-free C++ or `no_std` Rust ready to flash or deploy.

All examples originate from MechanicsDSL DSL specifications, the originating spec is included as a comment in every generated source file.

---

## Examples

### Arduino

| Example | System | Rate | Hardware |
|---------|--------|------|----------|
| [`arduino_pendulum/`](examples/arduino_pendulum/) | Simple pendulum + MPU6050 IMU | 250 Hz | Arduino Uno |
| [`arduino_double_pendulum/`](examples/arduino_double_pendulum/) | Double pendulum (chaotic) | 200 Hz | Arduino Mega 2560 |

### Raspberry Pi

| Example | System | Rate | Features |
|---------|--------|------|---------|
| [`raspberry_pi_pendulum/`](examples/raspberry_pi_pendulum/) | Simple pendulum | 250 Hz | pigpio, POSIX RT scheduling, NEON, GPIO energy alert |
| [`raspberry_pi_double_pendulum/`](examples/raspberry_pi_double_pendulum/) | Double pendulum | 200 Hz | pigpio, POSIX RT scheduling, GPIO energy alert |

---

## Repository Structure

```
mechanicsdsl-embedded/
├── examples/
│   ├── arduino_pendulum/          .ino + README
│   ├── arduino_double_pendulum/   .ino + README
│   ├── raspberry_pi_pendulum/     .cpp + README
│   └── raspberry_pi_double_pendulum/ .cpp + README
├── cmake/
│   └── arm-toolchain.cmake        ARM cross-compilation toolchain
├── docker/
│   ├── Dockerfile                 ARM cross-compilation environment
│   └── docker-compose.yml
├── scripts/
│   ├── cross_compile_arm.sh       One-command ARM build via Docker
│   └── monitor_serial.py          Real-time serial CSV plotter
├── docs/
│   ├── getting_started.md
│   └── hardware_guide.md          Wiring, platform support, performance notes
└── tests/
    └── test_eom.py                Physics correctness via SciPy reference
```

---

## Quick Start

### Arduino

1. Open `examples/arduino_pendulum/pendulum_realtime.ino` in Arduino IDE
2. Select board and port → Upload
3. Open Serial Monitor at 115200 baud

### Raspberry Pi

```bash
sudo apt-get install pigpio libpigpio-dev cmake g++
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo ./pendulum_rpi
```

### ARM Cross-Compilation (from x86 host)

```bash
./scripts/cross_compile_arm.sh
scp build_arm/pendulum_rpi pi@<ip>:~/
ssh pi@<ip> "sudo ~/pendulum_rpi"
```

### Real-Time Serial Monitor

```bash
pip install pyserial matplotlib numpy
python scripts/monitor_serial.py --port /dev/ttyUSB0
```

---

## Testing (no hardware required)

```bash
pip install pytest numpy scipy
pytest tests/ -v
```

Physics correctness is validated against SciPy reference integrations, period accuracy, energy conservation, equilibrium stability.

---

## Code Generation

`mechanicsdsl-embed` compiles any `.msl` spec (or core preset) through
`mechanicsdsl-core` and emits source for the chosen target:

```bash
pip install mechanicsdsl-embedded
mechanicsdsl-embed targets
mechanicsdsl-embed generate pendulum --target arduino -o build/
mechanicsdsl-embed generate pendulum --target raspberry_pi -o build/
mechanicsdsl-embed generate my_system.msl --target c_header --precision float -o build/
mechanicsdsl-embed generate double_pendulum --target rust_no_std -o crates/
```

| Target | Output | Notes |
|--------|--------|-------|
| `arduino` | `.ino` sketch | core `ArduinoGenerator`, serial plotter output |
| `raspberry_pi` | `.cpp` | core `ARMGenerator`, NEON |
| `arm_bare` | `.cpp` | core `ARMGenerator`, Cortex-M, no OS |
| `c_header` | single `.h` | portable C99, `float` or `double`, RK4 + energy, CSE-optimised; works on any MCU |
| `rust_no_std` | Cargo crate | `#![no_std]`, no allocator, `libm` only; Cortex-M / RISC-V |

### Before you flash: inspect, budget, verify

```bash
mechanicsdsl-embed inspect double_pendulum                      # coordinates, parameters, EOM, energy
mechanicsdsl-embed budget double_pendulum --rate 1000 --mflops 20   # ops/step, MFLOP/s needed, RAM
mechanicsdsl-embed verify double_pendulum --dt 0.001 --duration 10  # RK4 energy drift at your dt
```

`budget` counts floating-point operations after common-subexpression
elimination, which is what the generated code actually executes. `verify`
integrates with the same fixed-step RK4 the generated code uses and fails
(exit code 4) if energy drift exceeds `--tolerance`, so you can choose a
timestep on the desktop instead of on the bench.

### How generated code is checked

The test suite compiles every `c_header` output with
`gcc -std=c99 -Wall -Wextra -Werror -pedantic`, runs 1000 RK4 steps, and
compares the state with a Python RK4 reference (double precision to 1e-12,
float to 1e-4). Rust expressions are evaluated numerically against SymPy, and
the crate is built with `cargo test` in CI where a Rust toolchain exists.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Hardware validation on new platforms especially welcome.

## License

MIT License; see [LICENSE](LICENSE).

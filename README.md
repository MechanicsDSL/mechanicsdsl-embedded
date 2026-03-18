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

## Who's Using MechanicsDSL?

We can see from our download analytics that MechanicsDSL is being used across **54+ countries** and mirrored by institutions worldwide — but PyPI doesn't tell us who you are.

If you're using MechanicsDSL in research, education, industry, or a personal project, we'd love to hear from you. It takes 60 seconds and helps guide the project's direction.

**[→ Tell us about your use case](https://tally.so/r/XxqOqP)**

*All responses are voluntary and confidential. We will not contact you without permission.*

---

## Overview

`mechanicsdsl-embedded` provides deployment infrastructure and examples for running MechanicsDSL-generated simulations on embedded and edge platforms. Write your physical system once in DSL notation; generate optimized, dependency-free C++ or `no_std` Rust ready to flash or deploy.

All examples originate from MechanicsDSL DSL specifications — the originating spec is included as a comment in every generated source file.

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

Physics correctness is validated against SciPy reference integrations — period accuracy, energy conservation, equilibrium stability.

---

## Code Generation

All examples can be regenerated from DSL specifications:

```bash
pip install mechanicsdsl-core[embedded]
mechanicsdsl generate pendulum.msl --target arduino
mechanicsdsl generate pendulum.msl --target raspberry_pi
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Hardware validation on new platforms especially welcome.

## License

MIT License — see [LICENSE](LICENSE).

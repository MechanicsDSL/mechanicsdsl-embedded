# Getting Started with mechanicsdsl-embedded

## Overview

This repository provides MechanicsDSL-generated simulation code for Arduino, Raspberry Pi, and ARM edge devices. All examples originate from DSL specifications processed by the MechanicsDSL compiler — no manual physics derivation required.

---

## Arduino

### Requirements
- Arduino IDE 2.x
- MPU6050 library (optional, for IMU examples)

### Quick Start

1. Open `examples/arduino_pendulum/pendulum_realtime.ino` in Arduino IDE
2. Select your board and port
3. Upload and open Serial Monitor at 115200 baud
4. View real-time CSV: `t_ms, theta_sim, theta_imu, omega, energy`

---

## Raspberry Pi

### Requirements

```bash
sudo apt-get install pigpio libpigpio-dev cmake g++ build-essential
```

### Build and Run

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo ./pendulum_rpi
```

Output at 250 Hz: `t_s, theta, omega, energy, drift`

---

## ARM Cross-Compilation (from x86 host)

```bash
# Build Docker cross-compilation image and compile
./scripts/cross_compile_arm.sh

# Deploy to Raspberry Pi
scp build_arm/pendulum_rpi pi@<ip>:~/
ssh pi@<ip> "sudo ~/pendulum_rpi"
```

---

## Running Tests

```bash
pip install pytest numpy scipy
pytest tests/ -v
```

---

## Adding a New Example

1. Create a new DSL specification: `examples/<n>/system.msl`
2. Run `mechanicsdsl generate system.msl --target arduino` (or `raspberry_pi`, `cpp`)
3. Add a `README.md` documenting hardware requirements and wiring
4. Add physics correctness tests to `tests/test_eom.py`

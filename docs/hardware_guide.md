# Hardware Guide

## Supported Platforms

| Platform | Status | Integration rate | Notes |
|----------|--------|-----------------|-------|
| Arduino Uno R3 | ✅ Tested | 200 Hz | Single pendulum only |
| Arduino Mega 2560 | ✅ Tested | 200 Hz | Double pendulum supported |
| Raspberry Pi 3B+ | ✅ Tested | 250 Hz | Requires pigpio + root |
| Raspberry Pi 4 | ✅ Tested | 500 Hz | Cortex-A72, NEON available |
| Arduino Nano | ⚠️ Limited | 100 Hz | Limited SRAM |
| STM32 (Nucleo) | 🔄 Planned | 1 kHz | |
| ESP32 | 🔄 Planned | 500 Hz | WiFi telemetry |

---

## MPU6050 IMU Wiring

### Arduino Uno / Nano

```
MPU6050 VCC  →  3.3V (NOT 5V — will damage sensor)
MPU6050 GND  →  GND
MPU6050 SDA  →  A4
MPU6050 SCL  →  A5
MPU6050 AD0  →  GND (sets I2C address to 0x68)
```

### Raspberry Pi (GPIO header)

```
MPU6050 VCC  →  Pin 1  (3.3V)
MPU6050 GND  →  Pin 6  (GND)
MPU6050 SDA  →  Pin 3  (GPIO2, I2C1 SDA)
MPU6050 SCL  →  Pin 5  (GPIO3, I2C1 SCL)
```

Enable I2C on RPi:
```bash
sudo raspi-config  # Interface Options → I2C → Enable
```

---

## Energy Alert LED Wiring (Raspberry Pi)

GPIO17 (Pin 11) goes HIGH when Noether energy drift exceeds the configured tolerance.

```
GPIO17 (Pin 11) → 220Ω resistor → LED anode
LED cathode → GND (Pin 9)
```

---

## Performance Notes

### Arduino Uno

The Uno uses single-precision float (32-bit). For the double pendulum, consider:
- Using Arduino Mega 2560 for better timing margin
- Reducing integration rate to 100 Hz if timing jitter occurs
- Disabling Serial output during time-critical sections

### Raspberry Pi

Always run with `sudo` for:
- pigpio GPIO access
- `SCHED_FIFO` real-time thread priority

Check CPU governor is set to performance:
```bash
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

---

## Calibrating the IMU

The MPU6050 raw accelerometer output needs calibration for accurate angle estimation. A simple static calibration:

```cpp
// Read 1000 samples at rest and compute offsets
// See examples/arduino_pendulum/pendulum_realtime.ino for implementation
```

For a physical pendulum, the simulated angle `theta_sim` should track `theta_imu` closely when parameters match the real system.

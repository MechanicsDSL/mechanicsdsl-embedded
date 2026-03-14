# Raspberry Pi Pendulum Example

Real-time simple pendulum simulation on Raspberry Pi with pigpio, POSIX real-time scheduling, and ARM NEON optimisation.

## Requirements

```bash
sudo apt-get update
sudo apt-get install pigpio libpigpio-dev cmake g++ build-essential
```

## Build

```bash
cd mechanicsdsl-embedded
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

## Run

```bash
sudo ./pendulum_rpi | tee pendulum_log.csv
```

Root is required for pigpio and POSIX `SCHED_FIFO` real-time scheduling.

## Output

CSV streamed to stdout at 250 Hz:

```
t_s,theta_rad,omega_rad_s,energy_J,energy_drift
0.004000,0.299804,-0.039240,0.365310,0.0000e+00
0.008000,0.299216,-0.078439,0.365312,5.4e-07
...
```

GPIO pin 17 goes HIGH if energy drift exceeds the configured tolerance — useful as a hardware alert for numerical instability.

## Parameters

Edit `pendulum_rpi.cpp`:

```cpp
static constexpr double M_MASS = 1.0;    // kg
static constexpr double L_LEN  = 0.25;   // m
static constexpr double G_GRAV = 9.81;   // m/s^2
static constexpr double DRIFT_TOL = 1e-4;
```

Then rebuild with `make -j$(nproc)`.

## DSL Specification

```
\system{pendulum}
\parameter{m}{1.0}{kg}
\parameter{l}{0.25}{m}
\lagrangian{0.5*m*l^2*\dot{theta}^2 - m*g*l*(1-cos(theta))}
\target{raspberry_pi}
```

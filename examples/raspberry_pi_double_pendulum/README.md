# Raspberry Pi Double Pendulum Example

Real-time double pendulum simulation on Raspberry Pi at 200 Hz with POSIX real-time scheduling, pigpio GPIO, and energy drift monitoring.

## Requirements

```bash
sudo apt-get install pigpio libpigpio-dev cmake g++ build-essential
```

## Build

```bash
cd mechanicsdsl-embedded
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make double_pendulum_rpi -j$(nproc)
```

## Run

```bash
sudo ./double_pendulum_rpi | tee dp_log.csv
```

CSV output at 200 Hz:
```
t_s,theta1_rad,theta2_rad,omega1_rad_s,omega2_rad_s,energy_J,energy_drift
```

## Chaos Note

With default initial conditions ($\theta_1^0 = 0.8$ rad, $\theta_2^0 = 0.4$ rad) the system is in the chaotic regime. The Lyapunov time is approximately 3–5 s — trajectories diverge exponentially from nearby initial conditions.

GPIO pin 17 goes HIGH if energy drift exceeds tolerance, indicating numerical instability.

## DSL Specification

```
\system{double_pendulum}
\parameter{m}{1.0}{kg}
\parameter{l}{0.3}{m}
\lagrangian{
    0.5*m*l^2*(2*\dot{theta1}^2 + \dot{theta2}^2
               + 2*\dot{theta1}*\dot{theta2}*cos(theta1-theta2))
    + m*g*l*(2*cos(theta1) + cos(theta2))
}
\target{raspberry_pi}
```

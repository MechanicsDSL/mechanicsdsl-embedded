# Arduino Pendulum Example

Real-time simple pendulum simulation on Arduino with MPU6050 IMU feedback.

## Hardware

| Component | Notes |
|-----------|-------|
| Arduino Uno R3 (or compatible) | Tested on Uno and Nano |
| MPU6050 IMU | I2C, address 0x68 |
| USB cable | For serial monitoring |

## Wiring

```
MPU6050 VCC  →  3.3V
MPU6050 GND  →  GND
MPU6050 SDA  →  A4  (Uno/Nano)
MPU6050 SCL  →  A5  (Uno/Nano)
```

## Upload

1. Open `pendulum_realtime.ino` in Arduino IDE
2. Select board: **Arduino Uno** (or your board)
3. Select port
4. Upload

## Serial Output

Open Serial Monitor at **115200 baud**. CSV output:

```
t_ms,theta_sim_rad,theta_imu_rad,omega_sim_rad_s,energy_J
4,0.300000,0.298431,0.000000,0.365714
8,0.300000,0.299102,-0.039240,0.365714
...
```

Use Arduino Serial Plotter to visualise `theta_sim_rad` vs `theta_imu_rad` in real-time.

## Parameters

Edit the top of `pendulum_realtime.ino`:

```cpp
const float M_MASS = 1.0f;   // kg
const float L_LEN  = 0.25f;  // m — match your physical pendulum length
const float G_GRAV = 9.81f;  // m/s^2
```

## DSL Specification

```
\system{pendulum}
\parameter{m}{1.0}{kg}
\parameter{l}{0.25}{m}
\lagrangian{0.5*m*l^2*\dot{theta}^2 - m*g*l*(1-cos(theta))}
\target{arduino}
```

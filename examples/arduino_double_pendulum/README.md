# Arduino Double Pendulum Example

Real-time double pendulum simulation at 200 Hz on Arduino Mega 2560.

## Hardware

| Component | Notes |
|-----------|-------|
| Arduino Mega 2560 | Recommended — Uno may be too slow at 200 Hz |
| USB cable | For serial monitoring |

## Upload

1. Open `double_pendulum.ino` in Arduino IDE
2. Select board: **Arduino Mega 2560**
3. Upload
4. Open Serial Monitor at **115200 baud**

## Serial Output

```
t_ms,theta1,theta2,omega1,omega2,energy
5,0.80000,0.40000,0.00000,0.00000,-15.23440
10,0.79980,0.39951,-0.02943,-0.02971,-15.23440
...
```

Use **Serial Plotter** to visualise `theta1` and `theta2` simultaneously.

## Chaos Warning

With the default initial conditions ($\theta_1^0 = 0.8$ rad, $\theta_2^0 = 0.4$ rad) the motion is chaotic — `theta1` and `theta2` will appear irregular and never repeat. This is correct behaviour, not a bug.

## Parameters

Edit the top of `double_pendulum.ino`:

```cpp
const float M_MASS = 1.0f;   // kg
const float L_LEN  = 0.3f;   // m
const float G_GRAV = 9.81f;  // m/s^2
```

For small initial angles (e.g. 0.1 rad) the motion becomes near-periodic and regular.

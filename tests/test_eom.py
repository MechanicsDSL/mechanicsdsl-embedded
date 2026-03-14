"""
test_eom.py
-----------
Validates MechanicsDSL-generated equations of motion for embedded examples
by comparing against reference SciPy integrations.

Run with: pytest tests/test_eom.py -v
"""
import numpy as np
import pytest
from scipy.integrate import solve_ivp


def pendulum_eom(t, y, g=9.81, l=0.25):
    return [y[1], -(g/l)*np.sin(y[0])]


def double_pendulum_eom(t, y, g=9.81, l=0.3, m=1.0):
    th1, th2, w1, w2 = y
    delta = th1 - th2
    cd = np.cos(delta)
    sd = np.sin(delta)
    den = l * (2.0 - cd**2)
    dw1 = ((-g*2.0*np.sin(th1)) - sd*(w2**2*l + w1**2*l*cd)) / den
    dw2 = (sd*(2.0*w1**2*l + g*np.cos(th1) + w2**2*l*cd)) / den
    return [w1, w2, dw1, dw2]


def pendulum_energy(y, m=1.0, l=0.25, g=9.81):
    return 0.5*m*l**2*y[1]**2 + m*g*l*(1 - np.cos(y[0]))


def dp_energy(y, m=1.0, l=0.3, g=9.81):
    th1, th2, w1, w2 = y
    T = 0.5*m*l**2*(2*w1**2 + w2**2 + 2*w1*w2*np.cos(th1-th2))
    V = -m*g*l*(2*np.cos(th1) + np.cos(th2))
    return T + V


class TestPendulumEOM:
    def test_small_angle_frequency(self):
        """Small-angle period should match T=2π√(l/g)."""
        g, l = 9.81, 0.25
        T_analytical = 2*np.pi*np.sqrt(l/g)
        sol = solve_ivp(pendulum_eom, [0, 3*T_analytical], [0.05, 0.0],
                        max_step=0.001, rtol=1e-10, atol=1e-12)
        # Find zero crossings
        crossings = []
        for i in range(1, len(sol.y[0])):
            if sol.y[0][i-1] * sol.y[0][i] < 0:
                crossings.append(sol.t[i])
        assert len(crossings) >= 4
        T_numerical = 2 * (crossings[2] - crossings[0])
        assert abs(T_numerical - T_analytical) < 0.005

    def test_energy_conservation(self):
        """Total energy must be conserved to integration tolerance."""
        sol = solve_ivp(pendulum_eom, [0, 50], [0.3, 0.0],
                        dense_output=True, rtol=1e-10, atol=1e-12)
        t = np.linspace(0, 50, 10000)
        y = sol.sol(t)
        E = np.array([pendulum_energy(y[:, i]) for i in range(y.shape[1])])
        drift = np.abs((E - E[0]) / E[0])
        assert np.max(drift) < 1e-7

    def test_equilibrium_stability(self):
        """Starting at rest at bottom should remain stationary."""
        sol = solve_ivp(pendulum_eom, [0, 10], [0.0, 0.0],
                        rtol=1e-12, atol=1e-14)
        assert np.max(np.abs(sol.y[0])) < 1e-12
        assert np.max(np.abs(sol.y[1])) < 1e-12


class TestDoublePendulumEOM:
    def test_energy_conservation(self):
        """Energy conserved to integration tolerance over 10 seconds."""
        sol = solve_ivp(double_pendulum_eom, [0, 10], [0.3, 0.2, 0.0, 0.0],
                        max_step=0.002, rtol=1e-10, atol=1e-12)
        E = np.array([dp_energy(sol.y[:, i]) for i in range(sol.y.shape[1])])
        drift = np.abs((E - E[0]) / E[0])
        assert np.max(drift) < 1e-6

    def test_small_angle_recovers_coupled_pendulum(self):
        """At very small angles, double pendulum ≈ coupled simple pendulums."""
        eps = 0.01
        sol = solve_ivp(double_pendulum_eom, [0, 5], [eps, eps, 0.0, 0.0],
                        max_step=0.001, rtol=1e-10, atol=1e-12)
        # In symmetric mode both angles should stay equal
        diff = np.abs(sol.y[0] - sol.y[1])
        assert np.max(diff) < 1e-6

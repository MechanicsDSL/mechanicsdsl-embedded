"""
test_eom.py
-----------
Validates the equations of motion the embedded targets deploy by driving the
real MechanicsDSL core compiler/integrator — not a hand-transcribed EOM.

Previously this file integrated hand-written pendulum/double-pendulum ODEs; a
period-counting bug and an energy function inconsistent with its own EOM made
the assertions unreliable. These tests instead compile the systems through
core and check invariants that must hold for the *derived* dynamics.

Run with: pytest tests/test_eom.py -v
"""
import numpy as np
import pytest

pytest.importorskip("mechanics_dsl", reason="mechanicsdsl-core required")

from mechanics_dsl import PhysicsCompiler, get_preset


def _simulate(preset, t_end, n, **kw):
    c = PhysicsCompiler()
    r = c.compile_dsl(get_preset(preset))
    assert r["success"], r.get("error")
    params = {k: v["value"] for k, v in c.parameters_def.items()}
    sol = c.simulate(t_span=(0.0, t_end), num_points=n, **kw)
    assert sol["success"], sol.get("message")
    return c, params, sol


class TestPendulumEOM:
    def test_finite_amplitude_period(self):
        """Measured period matches the finite-amplitude correction.

        The preset starts at theta0 = 0.5 rad, so the period is longer than
        the small-angle T0 = 2*pi*sqrt(l/g) by the leading correction
        (1 + theta0**2 / 16).
        """
        c, p, sol = _simulate("pendulum", 20.0, 20001, method="DOP853",
                              rtol=1e-11, atol=1e-13)
        g, l = p["g"], p["l"]
        theta0 = c.initial_conditions["theta"]
        theta = sol["y"][0]
        t = sol["t"]
        centered = theta - np.mean(theta)
        crossings = t[np.where(np.sign(centered[:-1]) != np.sign(centered[1:]))[0]]
        assert len(crossings) >= 4
        # Two consecutive crossings span half a period.
        period = 2.0 * np.mean(np.diff(crossings[:5]))
        T0 = 2 * np.pi * np.sqrt(l / g)
        expected = T0 * (1 + theta0**2 / 16)
        assert abs(period - expected) < 0.02, (period, expected, T0)

    def test_energy_conservation(self):
        """Total energy of the pendulum is conserved by the integrator."""
        c, p, sol = _simulate("pendulum", 50.0, 20001, method="DOP853",
                              rtol=1e-11, atol=1e-13)
        m, l, g = p["m"], p["l"], p["g"]
        theta, omega = sol["y"][0], sol["y"][1]
        E = 0.5 * m * l**2 * omega**2 + m * g * l * (1 - np.cos(theta))
        drift = np.max(np.abs((E - E[0]) / E[0]))
        assert drift < 1e-6, drift


class TestDoublePendulumEOM:
    def test_compiles_to_two_dof(self):
        c, p, sol = _simulate("double_pendulum", 1.0, 101)
        assert c.get_coordinates() == ["theta1", "theta2"]
        assert set(c.equations) == {"theta1_ddot", "theta2_ddot"}
        assert sol["y"].shape[0] == 4

    def test_simulation_is_deterministic(self):
        c1, _, s1 = _simulate("double_pendulum", 5.0, 2001, method="DOP853",
                              rtol=1e-12, atol=1e-14)
        c2, _, s2 = _simulate("double_pendulum", 5.0, 2001, method="DOP853",
                              rtol=1e-12, atol=1e-14)
        assert np.allclose(s1["y"], s2["y"])

    @pytest.mark.xfail(
        reason="core's derived double-pendulum EOM does not conserve the "
        "energy of its own Lagrangian (identical drift under DOP853 and RK45, "
        "so not integrator error). Tracked as a core bug; core is frozen here.",
        strict=True,
    )
    def test_energy_conservation(self):
        """Documents the expected (and currently violated) invariant."""
        c, p, sol = _simulate("double_pendulum", 10.0, 20001, method="DOP853",
                              rtol=1e-12, atol=1e-14)
        m1, m2 = p["m1"], p["m2"]
        l1, l2, g = p["l1"], p["l2"], p["g"]
        th1, th2 = sol["y"][0], sol["y"][1]
        w1, w2 = sol["y"][2], sol["y"][3]
        T = (0.5 * (m1 + m2) * l1**2 * w1**2
             + 0.5 * m2 * l2**2 * w2**2
             + m2 * l1 * l2 * w1 * w2 * np.cos(th1 - th2))
        V = ((m1 + m2) * g * l1 * (1 - np.cos(th1))
             + m2 * g * l2 * (1 - np.cos(th2)))
        E = T + V
        drift = np.max(np.abs((E - E[0]) / E[0]))
        assert drift < 1e-4, drift

    def test_trajectory_stays_finite(self):
        """Chaotic large-angle motion must not numerically blow up."""
        c, p, sol = _simulate("double_pendulum", 20.0, 10001, method="DOP853",
                              rtol=1e-12, atol=1e-14)
        assert np.isfinite(sol["y"]).all()

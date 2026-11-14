"""
test_generation.py
-------------------
Exercises the *real* generation pipeline: DSL spec -> mechanicsdsl-core
compiler -> embedded source. These tests fail if the bridge to core breaks
or if generation stops embedding the compiled equations of motion.

Run with: pytest tests/test_generation.py -v
"""
import os

import pytest

core = pytest.importorskip(
    "mechanics_dsl", reason="mechanicsdsl-core required for generation tests"
)

from mechanicsdsl_embedded import compile_spec, list_targets
from mechanicsdsl_embedded.cli import main as cli_main


def test_compile_preset_shapes():
    system = compile_spec("pendulum")
    assert system.coordinates == ["theta"]
    assert "theta_ddot" in system.equations
    assert system.state_dim == 2
    # The gravitational parameter must survive compilation.
    assert pytest.approx(system.parameters["g"], rel=1e-6) == 9.81


def test_double_pendulum_is_two_dof():
    system = compile_spec("double_pendulum")
    assert len(system.coordinates) == 2
    assert set(system.equations) == {
        f"{c}_ddot" for c in system.coordinates
    }


def test_arduino_source_embeds_real_eom(tmp_path):
    rc = cli_main(
        ["generate", "pendulum", "--target", "arduino", "-o", str(tmp_path)]
    )
    assert rc == 0
    ino = tmp_path / "simple_pendulum.ino"
    assert ino.exists()
    text = ino.read_text()
    # Real derived physics, not a canned template: restoring torque ~ sin(theta)
    assert "sin(theta)" in text
    assert "computeDerivatives" in text


@pytest.mark.parametrize("target", ["arduino", "raspberry_pi", "arm_bare"])
def test_every_target_generates(tmp_path, target):
    rc = cli_main(
        ["generate", "pendulum", "--target", target, "-o", str(tmp_path)]
    )
    assert rc == 0
    produced = list(tmp_path.iterdir())
    assert produced, f"target {target} produced no output"


def test_all_registered_targets_are_generatable(tmp_path):
    # Guards against a target being added to the registry but not the CLI.
    for target in list_targets():
        rc = cli_main(
            ["generate", "pendulum", "--target", target, "-o", str(tmp_path / target)]
        )
        assert rc == 0, f"target {target} not wired into generation"

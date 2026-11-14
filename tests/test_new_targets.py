"""
test_new_targets.py
-------------------
Portable C99 header, no_std Rust crate, and the inspect/budget/verify tools.

Generated code is checked *numerically*: the C header is compiled and run
when a C compiler is on PATH (always true on the CI Linux runners) and its
state after 1000 RK4 steps is compared with the bridge's Python RK4; Rust
expressions are evaluated through a literal translation to Python, and the
crate is built with ``cargo test`` when cargo is available.
"""
import json
import math
import random
import re
import shutil
import subprocess

import pytest

pytest.importorskip("mechanics_dsl", reason="mechanicsdsl-core required")

from mechanicsdsl_embedded import (  # noqa: E402
    compile_spec,
    energy_drift,
    expr_to_rust,
    numeric_energy,
    render_c_header,
    simulate,
)
from mechanicsdsl_embedded.cli import budget_report, main as cli_main  # noqa: E402

PRESETS = ["pendulum", "double_pendulum", "coupled_oscillators",
           "damped_oscillator", "projectile", "figure8"]
CC = shutil.which("gcc") or shutil.which("cc") or shutil.which("clang")


@pytest.fixture(scope="module", params=PRESETS)
def system(request):
    return compile_spec(request.param)


# ---------------------------------------------------------------- bridge ---
def test_mass_matrix_presets_become_explicit():
    s = compile_spec("figure8")
    assert set(s.equations) == {f"{c}_ddot" for c in s.coordinates}
    assert s.dof == 6


def test_energy_is_conserved_for_conservative_presets(system):
    drift = energy_drift(system, t_end=2.0, dt=1e-3)
    assert drift is not None
    if system.conservative:
        assert drift < 1e-8, f"{system.name}: drift {drift:.2e}"


def test_damping_is_flagged_non_conservative():
    s = compile_spec("damped_oscillator")
    assert s.conservative is False
    assert energy_drift(s, t_end=5.0) > 0.1  # it really does lose energy


# -------------------------------------------------------------- C header ---
@pytest.mark.parametrize("precision", ["double", "float"])
def test_c_header_structure(system, precision):
    hdr = render_c_header(system, precision)
    assert f"{system.name}_rk4_step" in hdr
    assert f"{system.name.upper()}_STATE_DIM {system.state_dim}" in hdr
    if precision == "float":
        body = hdr.split("*/", 1)[1]  # skip the banner comment
        assert not re.search(r"\bdouble\b", body), "stray double in float header"


def _run_c(system, precision, steps, dt, tmp_path):
    tag = f"{system.name}_{precision}"
    (tmp_path / f"{tag}.h").write_text(render_c_header(system, precision), encoding="utf-8")
    e_call = (f'printf(" %.17g", (double){system.name}_energy(y, &p));'
              if system.energy is not None else "")
    src = "\n".join([
        "#include <stdio.h>",
        f'#include "{tag}.h"',
        "int main(void) {",
        f"  {system.name}_params_t p = {system.name}_default_params();",
        f"  {precision} y[{system.state_dim}]; int i, k;",
        f"  {system.name}_initial_state(y);",
        f"  for (k = 0; k < {steps}; ++k) {system.name}_rk4_step(y, ({precision}){dt!r}, &p);",
        f'  for (i = 0; i < {system.state_dim}; ++i) printf("%.17g ", (double)y[i]);',
        f"  {e_call}",
        '  printf("\\n"); return 0;',
        "}",
    ])
    (tmp_path / "main.c").write_text(src, encoding="utf-8")
    exe = tmp_path / "main.bin"
    subprocess.run([CC, "-std=c99", "-Wall", "-Wextra", "-Werror", "-pedantic", "-O2",
                    str(tmp_path / "main.c"), "-o", str(exe), "-lm"],
                   check=True, capture_output=True, text=True)
    out = subprocess.run([str(exe)], check=True, capture_output=True, text=True).stdout
    return [float(v) for v in out.split()]


@pytest.mark.skipif(CC is None, reason="no C compiler on PATH")
@pytest.mark.parametrize("precision,tol", [("double", 1e-12), ("float", 1e-4)])
def test_c_header_compiles_and_matches_reference(system, precision, tol, tmp_path):
    steps, dt = 1000, 1e-3
    vals = _run_c(system, precision, steps, dt, tmp_path)
    _, Y = simulate(system, t_end=steps * dt, dt=dt)
    ref = list(Y[-1])
    state = vals[:system.state_dim]
    scale = max(1.0, max(abs(v) for v in ref))
    assert max(abs(a - b) for a, b in zip(state, ref)) / scale < tol
    if system.energy is not None:
        E = numeric_energy(system)(Y[-1])
        assert abs(vals[-1] - E) / max(1.0, abs(E)) < tol


# ------------------------------------------------------------------ Rust ---
def _rust_to_python(src: str) -> str:
    src = re.sub(r"_f64", "", src)
    return (src.replace("libm::fabs", "abs").replace("libm::", "math.")
               .replace("core::f64::consts::PI", "math.pi")
               .replace("core::f64::consts::E", "math.e"))


def test_rust_expressions_match_sympy(system):
    rng = random.Random(0)
    exprs = list(system.equations.values())
    if system.energy is not None:
        exprs.append(system.energy)
    for e in exprs:
        py = _rust_to_python(expr_to_rust(e))
        syms = list(e.free_symbols)
        for _ in range(10):
            vals = {str(s): rng.uniform(0.3, 2.0) for s in syms}
            want = float(e.subs({s: vals[str(s)] for s in syms}))
            got = eval(py, {"math": math}, vals)  # noqa: S307 - generated by us
            assert abs(got - want) <= 1e-12 * max(1.0, abs(want))


def test_rust_crate_is_no_std(tmp_path):
    rc = cli_main(["generate", "double_pendulum", "-t", "rust_no_std", "-o", str(tmp_path)])
    assert rc == 0
    lib = (tmp_path / "double_pendulum_dynamics" / "src" / "lib.rs").read_text()
    cargo = (tmp_path / "double_pendulum_dynamics" / "Cargo.toml").read_text()
    assert "#![no_std]" in lib
    assert "libm::sin(" in lib and ".sin()" not in lib  # no std float methods
    assert 'libm = "0.2"' in cargo


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo not on PATH")
def test_rust_crate_builds_and_tests(tmp_path):
    assert cli_main(["generate", "double_pendulum", "-t", "rust_no_std",
                     "-o", str(tmp_path)]) == 0
    subprocess.run(["cargo", "test", "--quiet"], cwd=tmp_path / "double_pendulum_dynamics",
                   check=True, capture_output=True, text=True, timeout=600)


# ----------------------------------------------------------------- tools ---
def test_budget_report_scales_with_rate():
    s = compile_spec("double_pendulum")
    slow, fast = budget_report(s, 100, 10.0), budget_report(s, 1000, 10.0)
    assert fast["mflop_per_s_required"] == pytest.approx(10 * slow["mflop_per_s_required"])
    assert slow["ops_per_rk4_step"] > 4 * slow["ops_per_accel"]
    assert slow["max_rate_hz_estimate"] == pytest.approx(fast["max_rate_hz_estimate"])


def test_cli_budget_json(capsys):
    assert cli_main(["budget", "pendulum", "--json"]) == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep["transcendental_per_accel"] == 1  # one sin(theta)


def test_cli_inspect_and_presets(capsys):
    assert cli_main(["inspect", "pendulum"]) == 0
    out = capsys.readouterr().out
    assert "theta_ddot" in out and "Energy" in out
    assert cli_main(["presets"]) == 0
    assert "double_pendulum" in capsys.readouterr().out


def test_cli_verify_passes_and_fails():
    assert cli_main(["verify", "pendulum", "--duration", "2"]) == 0
    # A huge step must trip the tolerance.
    assert cli_main(["verify", "pendulum", "--duration", "20", "--dt", "0.5",
                     "--tolerance", "1e-9"]) == 4


def test_cli_rejects_bad_dsl(capsys):
    assert cli_main(["inspect", r"\system{broken} \lagrangian{"]) == 1

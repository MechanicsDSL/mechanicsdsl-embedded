"""
_rustgen.py
-----------
``#![no_std]`` Rust crate generator.

``f64::sin`` and friends live in ``std``, not ``core``, so a bare-metal crate
cannot use them. This generator prints every transcendental as a call into the
pure-Rust ``libm`` crate (``libm::sin(x)``), small integer powers as explicit
multiplications, and everything else as plain ``f64`` arithmetic, giving a
crate that builds for ``thumbv7em-none-eabihf``, ``riscv32imac-unknown-none-elf``
and other targets without an allocator or OS.

Generated crate layout::

    <system>_dynamics/
      Cargo.toml        (depends on libm only)
      src/lib.rs        (Params, initial_state, accel, deriv, rk4_step, energy)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import sympy as sp
from sympy.printing.str import StrPrinter

if TYPE_CHECKING:
    from ._bridge import CompiledSystem


_LIBM = {
    "sin": "sin", "cos": "cos", "tan": "tan", "asin": "asin", "acos": "acos",
    "atan": "atan", "atan2": "atan2", "sinh": "sinh", "cosh": "cosh",
    "tanh": "tanh", "exp": "exp", "log": "log", "floor": "floor",
    "ceiling": "ceil", "Abs": "fabs",
}


class RustNoStdPrinter(StrPrinter):
    """Print SymPy expressions as ``no_std`` Rust ``f64`` expressions."""

    printmethod = "_rust_nostd"

    def _print_Symbol(self, expr):
        return expr.name

    def _print_Integer(self, expr):
        return f"{int(expr)}.0_f64"

    def _print_Float(self, expr):
        text = repr(float(expr))
        if "e" not in text and "." not in text and "inf" not in text and "nan" not in text:
            text += ".0"
        return f"{text}_f64"

    def _print_Rational(self, expr):
        return f"({expr.p}.0_f64 / {expr.q}.0_f64)"

    def _print_Pi(self, expr):
        return "core::f64::consts::PI"

    def _print_Exp1(self, expr):
        return "core::f64::consts::E"

    def _print_Function(self, expr):
        name = expr.func.__name__
        if name not in _LIBM:
            raise NotImplementedError(f"no libm mapping for function '{name}'")
        args = ", ".join(self._print(a) for a in expr.args)
        return f"libm::{_LIBM[name]}({args})"

    def _print_Pow(self, expr):
        base, exp = expr.base, expr.exp
        b = self.parenthesize(base, 1000) if not base.is_Atom else self._print(base)
        if base.is_Atom and base.is_number:
            b = f"({self._print(base)})"
        if exp == sp.Rational(1, 2) or exp == sp.Float(0.5):
            return f"libm::sqrt({self._print(base)})"
        if exp == sp.Rational(-1, 2) or exp == sp.Float(-0.5):
            return f"(1.0_f64 / libm::sqrt({self._print(base)}))"
        if exp.is_number and float(exp).is_integer() and 1 <= abs(float(exp)) <= 4:
            k = int(abs(float(exp)))
            prod = " * ".join([b] * k)
            return f"({prod})" if float(exp) > 0 else f"(1.0_f64 / ({prod}))"
        return f"libm::pow({self._print(base)}, {self._print(exp)})"

    def _print_Basic(self, expr):
        raise NotImplementedError(f"cannot print {type(expr).__name__} as Rust")


def expr_to_rust(expr: "sp.Expr") -> str:
    """Convert one SymPy expression to a ``no_std`` Rust expression."""
    return RustNoStdPrinter().doprint(expr)


def _crate_name(system: "CompiledSystem") -> str:
    return f"{system.name}_dynamics"


def _bindings(system: "CompiledSystem", used: set, q: str, qd: str) -> list:
    lines = []
    for i, c in enumerate(system.coordinates):
        if c in used:
            lines.append(f"    let {c}: f64 = {q}[{i}];")
        if f"{c}_dot" in used:
            lines.append(f"    let {c}_dot: f64 = {qd}[{i}];")
    for p in sorted(system.parameters):
        if p in used:
            lines.append(f"    let {p}: f64 = mdsl_p.{p};")
    return lines


def _cse(exprs, printer):
    temps, reduced = sp.cse(exprs, symbols=sp.numbered_symbols("mdsl_t"))
    lines = [f"    let {s}: f64 = {printer.doprint(v)};" for s, v in temps]
    return lines, [printer.doprint(e) for e in reduced]


def render_lib_rs(system: "CompiledSystem") -> str:
    pr = RustNoStdPrinter()
    n, D = system.dof, system.state_dim
    params = sorted(system.parameters)
    lit = (lambda v: pr.doprint(sp.Float(v)))

    fields = "\n".join(
        f"    /// {system.units.get(p) or 'dimensionless'}\n    pub {p}: f64," for p in params
    )
    defaults = "\n".join(f"            {p}: {lit(system.parameters[p])}," for p in params)
    init = ", ".join(lit(v) for v in system.initial_state())

    accel_exprs = [system.equations[f"{c}_ddot"] for c in system.coordinates]
    used = set().union(*[{str(s) for s in e.free_symbols} for e in accel_exprs])
    temps, accel = _cse(accel_exprs, pr)
    accel_body = "\n".join(_bindings(system, used, "mdsl_q", "mdsl_qd") + temps)

    energy_fn = ""
    if system.energy is not None:
        e_used = {str(s) for s in system.energy.free_symbols}
        e_temps, (e_expr,) = _cse([system.energy], pr)
        e_body = "\n".join(_bindings(system, e_used, "mdsl_y", f"mdsl_y[{n}..]") + e_temps)
        energy_fn = f"""
/// Jacobi energy `E = sum(qdot * dL/dqdot) - L`; conserved for conservative
/// systems, so its drift measures integration error.
pub fn energy(mdsl_y: &[f64; STATE_DIM], mdsl_p: &Params) -> f64 {{
{e_body}
    {e_expr}
}}
"""

    src = "\n".join(f"//!     {ln}" for ln in system.source.splitlines())
    accel_vals = ", ".join(accel)
    return f"""\
//! `{system.name}` dynamics - auto-generated by mechanicsdsl-embedded. DO NOT EDIT BY HAND.
//!
//! `#![no_std]`, no allocator; transcendental functions come from the `libm` crate.
//! Equations of motion derived by mechanicsdsl-core from:
//!
{src}
#![no_std]
#![allow(non_snake_case, unused_variables, clippy::all)]

/// Number of generalized coordinates.
pub const DOF: usize = {n};
/// Phase-space dimension; state layout is `[{", ".join(system.state_names)}]`.
pub const STATE_DIM: usize = {D};

/// Physical parameters.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Params {{
{fields}
}}

impl Default for Params {{
    fn default() -> Self {{
        Self {{
{defaults}
        }}
    }}
}}

/// Initial state from the DSL spec.
pub fn initial_state() -> [f64; STATE_DIM] {{
    [{init}]
}}

/// Generalized accelerations from positions and velocities.
pub fn accel(mdsl_q: &[f64], mdsl_qd: &[f64], mdsl_p: &Params) -> [f64; DOF] {{
{accel_body}
    [{accel_vals}]
}}

/// First-order right-hand side.
pub fn deriv(mdsl_y: &[f64; STATE_DIM], mdsl_p: &Params) -> [f64; STATE_DIM] {{
    let mdsl_qdd = accel(&mdsl_y[..DOF], &mdsl_y[DOF..], mdsl_p);
    let mut mdsl_out = [0.0_f64; STATE_DIM];
    for mdsl_i in 0..DOF {{
        mdsl_out[mdsl_i] = mdsl_y[DOF + mdsl_i];
        mdsl_out[DOF + mdsl_i] = mdsl_qdd[mdsl_i];
    }}
    mdsl_out
}}

/// One classic fixed-step RK4 step, in place.
pub fn rk4_step(mdsl_y: &mut [f64; STATE_DIM], mdsl_dt: f64, mdsl_p: &Params) {{
    let mut mdsl_tmp = [0.0_f64; STATE_DIM];
    let mdsl_k1 = deriv(mdsl_y, mdsl_p);
    for mdsl_i in 0..STATE_DIM {{ mdsl_tmp[mdsl_i] = mdsl_y[mdsl_i] + 0.5 * mdsl_dt * mdsl_k1[mdsl_i]; }}
    let mdsl_k2 = deriv(&mdsl_tmp, mdsl_p);
    for mdsl_i in 0..STATE_DIM {{ mdsl_tmp[mdsl_i] = mdsl_y[mdsl_i] + 0.5 * mdsl_dt * mdsl_k2[mdsl_i]; }}
    let mdsl_k3 = deriv(&mdsl_tmp, mdsl_p);
    for mdsl_i in 0..STATE_DIM {{ mdsl_tmp[mdsl_i] = mdsl_y[mdsl_i] + mdsl_dt * mdsl_k3[mdsl_i]; }}
    let mdsl_k4 = deriv(&mdsl_tmp, mdsl_p);
    for mdsl_i in 0..STATE_DIM {{
        mdsl_y[mdsl_i] += mdsl_dt / 6.0
            * (mdsl_k1[mdsl_i] + 2.0 * mdsl_k2[mdsl_i] + 2.0 * mdsl_k3[mdsl_i] + mdsl_k4[mdsl_i]);
    }}
}}
{energy_fn}
#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn rk4_step_is_finite() {{
        let p = Params::default();
        let mut y = initial_state();
        for _ in 0..1000 {{
            rk4_step(&mut y, 1e-3, &p);
        }}
        assert!(y.iter().all(|v| v.is_finite()));
    }}
}}
"""


def render_cargo_toml(system: "CompiledSystem") -> str:
    return f"""[package]
name = "{_crate_name(system)}"
version = "0.1.0"
edition = "2021"
description = "{system.name} dynamics generated by MechanicsDSL (no_std)"
license = "MIT"

[dependencies]
libm = "0.2"

[lib]
path = "src/lib.rs"
"""


def write_crate(system: "CompiledSystem", out_dir: str) -> Dict[str, str]:
    """Write the crate under ``out_dir``; return ``{relative_path: absolute_path}``."""
    import os

    root = os.path.join(out_dir, _crate_name(system))
    os.makedirs(os.path.join(root, "src"), exist_ok=True)
    files = {
        "Cargo.toml": render_cargo_toml(system),
        os.path.join("src", "lib.rs"): render_lib_rs(system),
    }
    written = {}
    for rel, text in files.items():
        path = os.path.join(root, rel)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        written[rel] = path
    return written

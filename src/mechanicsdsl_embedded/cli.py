"""
cli.py
------
Command-line interface for ``mechanicsdsl-embedded``.

Compiles a DSL spec through ``mechanicsdsl-core`` and emits ready-to-build
source for an embedded target, plus tooling to inspect, cost and verify a
system before it goes on hardware.

Usage
-----
    mechanicsdsl-embed targets
    mechanicsdsl-embed presets
    mechanicsdsl-embed generate pendulum --target arduino -o build/
    mechanicsdsl-embed generate pendulum --target c_header --precision float -o build/
    mechanicsdsl-embed generate double_pendulum --target rust_no_std -o crates/
    mechanicsdsl-embed inspect double_pendulum
    mechanicsdsl-embed budget double_pendulum --rate 1000 --mflops 20
    mechanicsdsl-embed verify double_pendulum --dt 0.001 --duration 10
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from ._bridge import (
    CompiledSystem,
    CoreNotInstalled,
    DSLCompileError,
    compile_spec,
    energy_drift,
    list_presets,
    operation_count,
)
from ._targets import _TARGETS, list_targets


def _emit_arduino(system: CompiledSystem, out_path: str, *, servo_pin: Optional[int]) -> str:
    from mechanics_dsl.codegen import ArduinoGenerator

    gen = ArduinoGenerator(
        system_name=system.name,
        coordinates=system.coordinates,
        parameters=system.parameters,
        initial_conditions=system.initial_conditions,
        equations=system.equations,
        use_serial_plotter=True,
        servo_pin=servo_pin,
    )
    gen.generate(out_path)
    return out_path


def _emit_arm(system: CompiledSystem, out_path: str, *, target: str, embedded: bool) -> str:
    from mechanics_dsl.codegen import ARMGenerator

    gen = ARMGenerator(
        system_name=system.name,
        coordinates=system.coordinates,
        parameters=system.parameters,
        initial_conditions=system.initial_conditions,
        equations=system.equations,
        target=target,
        use_neon=not embedded,
        embedded=embedded,
    )
    gen.generate(out_path)
    return out_path


def _compile(spec: str) -> Optional[CompiledSystem]:
    try:
        return compile_spec(spec)
    except CoreNotInstalled as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
    except DSLCompileError as exc:
        print(f"DSL compilation failed: {exc}", file=sys.stderr)
        return None


def _generate(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1

    target = args.target
    os.makedirs(args.out, exist_ok=True)

    if target == "arduino":
        written = _emit_arduino(system, os.path.join(args.out, f"{system.name}.ino"),
                                servo_pin=args.servo_pin)
    elif target == "raspberry_pi":
        written = _emit_arm(system, os.path.join(args.out, f"{system.name}.cpp"),
                            target="raspberry_pi", embedded=False)
    elif target == "arm_bare":
        written = _emit_arm(system, os.path.join(args.out, f"{system.name}.cpp"),
                            target="cortex_m", embedded=True)
    elif target == "c_header":
        from ._cgen import render_c_header

        written = os.path.join(args.out, f"{system.name}.h")
        with open(written, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_c_header(system, precision=args.precision))
    elif target == "rust_no_std":
        from ._rustgen import write_crate

        files = write_crate(system, args.out)
        written = os.path.dirname(files["Cargo.toml"])
    else:  # pragma: no cover - argparse restricts choices
        print(f"Unsupported target '{target}'.", file=sys.stderr)
        return 1

    print(f"Compiled '{system.name}' ({system.dof} DOF: {', '.join(system.coordinates)})")
    print(f"Generated {target} source -> {written}")
    return 0


def _targets(_: argparse.Namespace) -> int:
    print("Supported embedded targets:")
    for name, info in _TARGETS.items():
        print(f"  {name:<14} {info['description']}")
    return 0


def _presets(_: argparse.Namespace) -> int:
    print("Presets shipped with mechanicsdsl-core:")
    for name in list_presets():
        print(f"  {name}")
    return 0


def _inspect(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1
    print(system.describe())
    return 0


def budget_report(system: CompiledSystem, rate_hz: float, mflops: Optional[float]) -> dict:
    """Arithmetic cost of running ``system`` with RK4 at ``rate_hz``.

    One RK4 step evaluates the acceleration 4 times and performs
    ``11 * state_dim`` additional multiply/adds for the stage combinations.
    """
    ops = operation_count(system)
    per_step = 4 * ops["ops"] + 11 * system.state_dim
    report = {
        "system": system.name,
        "ops_per_accel": ops["ops"],
        "transcendental_per_accel": ops["transcendental"],
        "cse_temporaries": ops["temporaries"],
        "ops_per_rk4_step": per_step,
        "rate_hz": rate_hz,
        "mflop_per_s_required": per_step * rate_hz / 1e6,
        "state_bytes_double": 8 * system.state_dim,
        "rk4_scratch_bytes_double": 8 * 5 * system.state_dim,
    }
    if mflops:
        report["cpu_mflops"] = mflops
        report["cpu_load_estimate"] = report["mflop_per_s_required"] / mflops
        report["max_rate_hz_estimate"] = mflops * 1e6 / per_step
    return report


def _budget(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1
    rep = budget_report(system, args.rate, args.mflops)
    if args.json:
        print(json.dumps(rep, indent=2))
        return 0
    print(f"Cost budget for '{system.name}' (RK4, counted after CSE)")
    print(f"  ops per acceleration call   {rep['ops_per_accel']}"
          f"  ({rep['transcendental_per_accel']} transcendental)")
    print(f"  ops per RK4 step            {rep['ops_per_rk4_step']}")
    print(f"  at {args.rate:g} Hz you need      {rep['mflop_per_s_required']:.4f} MFLOP/s")
    print(f"  RAM: state {rep['state_bytes_double']} B, RK4 scratch "
          f"{rep['rk4_scratch_bytes_double']} B (double; halve for float)")
    if args.mflops:
        print(f"  CPU load at {args.mflops:g} MFLOP/s   {100 * rep['cpu_load_estimate']:.2f}%")
        print(f"  max rate estimate           {rep['max_rate_hz_estimate']:.0f} Hz")
    print("  (arithmetic only; a transcendental costs 10-100x an add on FPU-less parts)")
    return 0


def _verify(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1
    drift = energy_drift(system, t_end=args.duration, dt=args.dt)
    print(f"'{system.name}': RK4 at dt={args.dt:g} s for {args.duration:g} s")
    if drift is None:
        print("  no Lagrangian available; energy check skipped")
        return 0
    print(f"  relative energy drift: {drift:.3e}")
    if not system.conservative:
        print("  system declares forces/damping: energy is not expected to be conserved")
        return 0
    if drift > args.tolerance:
        print(f"  FAIL: drift exceeds tolerance {args.tolerance:g}; reduce --dt", file=sys.stderr)
        return 4
    print(f"  OK (tolerance {args.tolerance:g})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-embed",
        description="Generate embedded C/C++/Rust from MechanicsDSL specifications.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("targets", help="List supported embedded targets").set_defaults(func=_targets)
    sub.add_parser("presets", help="List core presets").set_defaults(func=_presets)

    spec_help = ("Path to a .msl file, a raw DSL string, or a core preset name "
                 "(e.g. 'pendulum', 'double_pendulum').")

    p_gen = sub.add_parser("generate", help="Generate embedded code from a DSL spec")
    p_gen.add_argument("spec", help=spec_help)
    p_gen.add_argument("--target", "-t", required=True, choices=list_targets(),
                       help="Deployment target")
    p_gen.add_argument("--out", "-o", default=".", help="Output directory")
    p_gen.add_argument("--servo-pin", type=int, default=None,
                       help="(arduino) PWM pin for servo feedback output")
    p_gen.add_argument("--precision", choices=["double", "float"], default="double",
                       help="(c_header) floating-point precision")
    p_gen.set_defaults(func=_generate)

    p_ins = sub.add_parser("inspect", help="Print coordinates, parameters, EOM and energy")
    p_ins.add_argument("spec", help=spec_help)
    p_ins.set_defaults(func=_inspect)

    p_bud = sub.add_parser("budget", help="Estimate arithmetic cost and RAM for RK4")
    p_bud.add_argument("spec", help=spec_help)
    p_bud.add_argument("--rate", type=float, default=1000.0, help="Control-loop rate [Hz]")
    p_bud.add_argument("--mflops", type=float, default=None,
                       help="Sustained MFLOP/s of the target CPU, for a load estimate")
    p_bud.add_argument("--json", action="store_true", help="Machine-readable output")
    p_bud.set_defaults(func=_budget)

    p_ver = sub.add_parser("verify", help="Check energy conservation of RK4 at a given dt")
    p_ver.add_argument("spec", help=spec_help)
    p_ver.add_argument("--dt", type=float, default=1e-3, help="Timestep [s]")
    p_ver.add_argument("--duration", type=float, default=10.0, help="Simulated time [s]")
    p_ver.add_argument("--tolerance", type=float, default=1e-6,
                       help="Maximum acceptable relative energy drift")
    p_ver.set_defaults(func=_verify)
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

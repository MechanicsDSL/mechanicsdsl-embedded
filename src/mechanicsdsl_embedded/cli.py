"""
cli.py
------
Command-line interface for ``mechanicsdsl-embedded``.

Unlike the previous placeholder, this CLI performs *real* code generation:
it compiles a DSL spec through ``mechanicsdsl-core`` and drives the core
``ArduinoGenerator`` / ``ARMGenerator`` backends to emit ready-to-flash
source for the requested embedded target.

Usage
-----
    mechanicsdsl-embed targets
    mechanicsdsl-embed generate pendulum --target arduino -o build/
    mechanicsdsl-embed generate my_system.msl --target raspberry_pi -o build/
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from ._bridge import CompiledSystem, CoreNotInstalled, DSLCompileError, compile_spec
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


def _generate(args: argparse.Namespace) -> int:
    try:
        system = compile_spec(args.spec)
    except CoreNotInstalled as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except DSLCompileError as exc:
        print(f"DSL compilation failed: {exc}", file=sys.stderr)
        return 1

    target = args.target
    ext = _TARGETS[target]["output_ext"]
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, f"{system.name}{ext}")

    if target == "arduino":
        written = _emit_arduino(system, out_path, servo_pin=args.servo_pin)
    elif target == "raspberry_pi":
        written = _emit_arm(system, out_path, target="raspberry_pi", embedded=False)
    elif target == "arm_bare":
        written = _emit_arm(system, out_path, target="cortex_m", embedded=True)
    else:  # pragma: no cover - argparse restricts choices
        print(f"Unsupported target '{target}'.", file=sys.stderr)
        return 1

    dof = len(system.coordinates)
    print(f"Compiled '{system.name}' ({dof} DOF: {', '.join(system.coordinates)})")
    print(f"Generated {target} source -> {written}")
    return 0


def _targets(_: argparse.Namespace) -> int:
    print("Supported embedded targets:")
    for name, info in _TARGETS.items():
        print(f"  {name:<16} {info['description']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-embed",
        description="Generate embedded C/C++ from MechanicsDSL specifications.",
    )
    sub = parser.add_subparsers(dest="command")

    p_targets = sub.add_parser("targets", help="List supported embedded targets")
    p_targets.set_defaults(func=_targets)

    p_gen = sub.add_parser("generate", help="Generate embedded code from a DSL spec")
    p_gen.add_argument(
        "spec",
        help="Path to a .msl file, a raw DSL string, or a core preset name "
        "(e.g. 'pendulum', 'double_pendulum').",
    )
    p_gen.add_argument(
        "--target", "-t", required=True, choices=list_targets(),
        help="Deployment target",
    )
    p_gen.add_argument("--out", "-o", default=".", help="Output directory")
    p_gen.add_argument(
        "--servo-pin", type=int, default=None,
        help="(arduino) PWM pin for servo feedback output",
    )
    p_gen.set_defaults(func=_generate)
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

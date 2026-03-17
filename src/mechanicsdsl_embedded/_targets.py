"""
_targets.py
-----------
Target platform registry and utilities for mechanicsdsl-embedded.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional


_TARGETS: Dict[str, Dict] = {
    "arduino": {
        "description": "Arduino Uno / Mega (AVR, ARM)",
        "output_ext": ".ino",
        "examples": ["arduino_pendulum", "arduino_double_pendulum"],
    },
    "raspberry_pi": {
        "description": "Raspberry Pi (ARM Cortex-A, Raspbian/Ubuntu)",
        "output_ext": ".cpp",
        "examples": ["raspberry_pi_pendulum", "raspberry_pi_double_pendulum"],
    },
    "arm_bare": {
        "description": "Bare-metal ARM (Cortex-M, no OS)",
        "output_ext": ".cpp",
        "examples": [],
    },
}


def list_targets() -> List[str]:
    """Return all supported embedded deployment targets."""
    return sorted(_TARGETS.keys())


def get_example_path(target: str, example: str) -> Optional[Path]:
    """
    Return the path to a bundled example for a given target.

    Parameters
    ----------
    target : str
        Target platform name. Use list_targets() to see available options.
    example : str
        Example name.

    Returns
    -------
    Path or None
    """
    if target not in _TARGETS:
        raise ValueError(f"Unknown target '{target}'. Available: {list_targets()}")
    pkg_dir = Path(__file__).parent
    ex_dir = pkg_dir / "examples" / example
    if ex_dir.exists():
        return ex_dir
    repo_root = pkg_dir.parent.parent.parent.parent
    local = repo_root / "examples" / example
    if local.exists():
        return local
    return None


def main() -> None:
    """Entry point for mechanicsdsl-embed CLI."""
    import argparse
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-embed",
        description="MechanicsDSL embedded deployment tools"
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("targets", help="List supported embedded targets")

    gen = sub.add_parser("generate", help="Generate embedded code from DSL spec")
    gen.add_argument("spec", help="Path to .msl DSL specification file")
    gen.add_argument("--target", "-t", required=True,
                     choices=list_targets(), help="Deployment target")
    gen.add_argument("--out", "-o", default=".", help="Output directory")

    args = parser.parse_args()

    if args.command == "targets":
        print("Supported embedded targets:")
        for t, info in _TARGETS.items():
            print(f"  {t:<16} {info['description']}")

    elif args.command == "generate":
        try:
            import mechanicsdsl
            mechanicsdsl.generate(args.spec, target=args.target, out=args.out)
        except ImportError:
            print("mechanicsdsl-core is required for code generation.")
            print("Install with: pip install mechanicsdsl-core[embedded]")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

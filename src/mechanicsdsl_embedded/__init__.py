"""
mechanicsdsl-embedded
---------------------
Embedded and edge deployment tools for MechanicsDSL.
Supports Arduino, Raspberry Pi, and ARM cross-compilation.

Quick start:
    pip install mechanicsdsl-embedded
    mechanicsdsl-embed generate pendulum.msl --target arduino
    mechanicsdsl-embed generate pendulum.msl --target raspberry_pi
    mechanicsdsl-embed generate pendulum.msl --target c_header --precision float
    mechanicsdsl-embed generate pendulum.msl --target rust_no_std

    # Examples and documentation:
    # https://github.com/MechanicsDSL/mechanicsdsl-embedded
"""

import os
import sys

from mechanicsdsl_embedded._version import __version__
from mechanicsdsl_embedded._targets import list_targets, get_example_path
from mechanicsdsl_embedded._bridge import (
    CompiledSystem,
    CoreNotInstalled,
    DSLCompileError,
    compile_spec,
    energy_drift,
    list_presets,
    numeric_energy,
    numeric_rhs,
    operation_count,
    simulate,
)
from mechanicsdsl_embedded._cgen import render_c_header
from mechanicsdsl_embedded._rustgen import expr_to_rust, render_lib_rs, write_crate

__all__ = [
    "__version__",
    "list_targets",
    "get_example_path",
    "compile_spec",
    "list_presets",
    "simulate",
    "numeric_rhs",
    "numeric_energy",
    "energy_drift",
    "operation_count",
    "render_c_header",
    "expr_to_rust",
    "render_lib_rs",
    "write_crate",
    "CompiledSystem",
    "CoreNotInstalled",
    "DSLCompileError",
]


def _show_survey_banner():
    if (
        os.environ.get("MECHANICSDSL_NO_BANNER") or
        os.environ.get("CI") or
        os.environ.get("CONTINUOUS_INTEGRATION") or
        not sys.stdout.isatty()
    ):
        return

    import pathlib
    flag = pathlib.Path.home() / ".mechanicsdsl" / ".survey_shown"
    if flag.exists():
        return

    flag.parent.mkdir(exist_ok=True)
    flag.touch()

    print(
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        " MechanicsDSL is used across 54+ countries —\n"
        " but we don't know who you are.\n"
        " 60 seconds: [https://tally.so/r/XxqOqP]\n"
        " Suppress: MECHANICSDSL_NO_BANNER=1\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

_show_survey_banner()

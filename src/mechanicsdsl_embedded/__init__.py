"""
mechanicsdsl-embedded
---------------------
Embedded and edge deployment tools for MechanicsDSL.
Supports Arduino, Raspberry Pi, and ARM cross-compilation.

Quick start:
    pip install mechanicsdsl-embedded
    mechanicsdsl-embed generate pendulum.msl --target arduino
    mechanicsdsl-embed generate pendulum.msl --target raspberry_pi

    # Examples and documentation:
    # https://github.com/MechanicsDSL/mechanicsdsl-embedded
"""

from mechanicsdsl_embedded._version import __version__
from mechanicsdsl_embedded._targets import list_targets, get_example_path

__all__ = ["__version__", "list_targets", "get_example_path"]

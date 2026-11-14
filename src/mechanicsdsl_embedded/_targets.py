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
    "c_header": {
        "description": "Portable single-header C99, any MCU (--precision float|double)",
        "output_ext": ".h",
        "examples": [],
    },
    "rust_no_std": {
        "description": "#![no_std] Rust crate on libm (Cortex-M, RISC-V, ...)",
        "output_ext": "_dynamics/",
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
    repo_root = pkg_dir.parent.parent
    local = repo_root / "examples" / example
    if local.exists():
        return local
    return None

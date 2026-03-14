"""
conftest.py
-----------
Shared pytest fixtures for mechanicsdsl-embedded test suite.
"""
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def repo_root():
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def examples_dir(repo_root):
    return repo_root / "examples"


@pytest.fixture(scope="session")
def arduino_examples(examples_dir):
    return sorted(examples_dir.glob("arduino_*"))


@pytest.fixture(scope="session")
def rpi_examples(examples_dir):
    return sorted(examples_dir.glob("raspberry_pi_*"))

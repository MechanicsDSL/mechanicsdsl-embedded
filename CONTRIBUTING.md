# Contributing to mechanicsdsl-embedded

## Hardware Contributions

The most valuable contributions to this repository are tested examples on real hardware:

- **New Arduino examples** — different MCU targets, sensor integrations, display outputs
- **Raspberry Pi examples** — different control topologies, sensor fusion approaches
- **New embedded targets** — STM32, ESP32, Nordic nRF52, Teensy

## What to Include

For each new example:

1. **Source code** in `examples/<target_name>/`
2. **README.md** with:
   - Hardware requirements and wiring diagram
   - Build/flash instructions
   - Expected serial output
   - DSL specification that generated the code
3. **Physics correctness tests** in `tests/test_eom.py`

## Code Generation

All examples should originate from a MechanicsDSL DSL specification. Include the originating spec as a comment at the top of each generated file:

```cpp
/**
 * DSL specification:
 *   \system{...}
 *   \lagrangian{...}
 *   \target{arduino}
 */
```

## Testing Without Hardware

The `tests/test_eom.py` suite validates physics correctness using SciPy as reference — no hardware required. Run before submitting:

```bash
pip install pytest numpy scipy
pytest tests/ -v
```

## Pull Request Guidelines

- Note which hardware you tested on (model, OS, toolchain version)
- Include serial output sample in the PR description
- If the example requires hardware not everyone has, mark it clearly in the README

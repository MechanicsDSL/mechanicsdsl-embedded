#!/usr/bin/env python3
"""
monitor_serial.py
-----------------
Real-time serial monitor for MechanicsDSL Arduino/RPi examples.
Reads CSV data from serial port and plots live using matplotlib.

Usage:
    python scripts/monitor_serial.py --port /dev/ttyUSB0 --baud 115200
    python scripts/monitor_serial.py --port COM3 --baud 115200  # Windows
    python scripts/monitor_serial.py --file pendulum_log.csv    # replay from file
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def parse_args():
    parser = argparse.ArgumentParser(description="MechanicsDSL serial monitor")
    parser.add_argument("--port", default=None, help="Serial port (e.g. /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--file", default=None, help="Replay from CSV file")
    parser.add_argument("--max-points", type=int, default=2000,
                        help="Maximum points in rolling buffer")
    return parser.parse_args()


def open_source(args):
    """Return an iterable line source (serial or file)."""
    if args.file:
        print(f"Replaying from: {args.file}")
        return open(args.file)
    try:
        import serial
    except ImportError:
        print("Error: pyserial not installed. Run: pip install pyserial")
        sys.exit(1)
    print(f"Opening {args.port} at {args.baud} baud...")
    return serial.Serial(args.port, args.baud, timeout=2)


def main():
    args = parse_args()
    if args.port is None and args.file is None:
        print("Error: provide --port or --file")
        sys.exit(1)

    source = open_source(args)
    N = args.max_points

    # Read header
    if hasattr(source, 'readline'):
        header = source.readline()
        if isinstance(header, bytes):
            header = header.decode('utf-8', errors='replace')
        cols = [c.strip() for c in header.strip().split(',')]
    else:
        cols = []

    print(f"Columns: {cols}")

    buf = {c: [] for c in cols}

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))
    fig.suptitle("MechanicsDSL — Real-time Serial Monitor", fontsize=12)

    def update(_):
        try:
            line = source.readline()
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace')
            vals = [float(v) for v in line.strip().split(',')]
            if len(vals) == len(cols):
                for c, v in zip(cols, vals):
                    buf[c].append(v)
                    if len(buf[c]) > N:
                        buf[c].pop(0)
        except (ValueError, Exception):
            return

        if len(buf.get(cols[0], [])) < 2:
            return

        t = np.array(buf[cols[0]])
        for ax in axes:
            ax.cla()

        # Plot angular coordinates
        angle_cols = [c for c in cols if 'theta' in c.lower() or 'angle' in c.lower()]
        for c in angle_cols[:4]:
            axes[0].plot(t, np.array(buf[c]), lw=0.8, label=c)
        axes[0].set_ylabel('Angle (rad)')
        axes[0].legend(fontsize=8)
        axes[0].set_title('Angular coordinates')

        # Plot energy
        energy_cols = [c for c in cols if 'energy' in c.lower() or 'drift' in c.lower()]
        for c in energy_cols[:2]:
            axes[1].plot(t, np.array(buf[c]), lw=0.8, label=c)
        axes[1].set_xlabel(cols[0])
        axes[1].set_ylabel('Energy (J) / Drift')
        axes[1].legend(fontsize=8)
        axes[1].set_title('Energy (Noether monitor)')

        plt.tight_layout(rect=[0,0,1,0.95])

    ani = animation.FuncAnimation(fig, update, interval=20, cache_frame_data=False)
    plt.show()


if __name__ == "__main__":
    main()

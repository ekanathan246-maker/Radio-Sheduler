#!/usr/bin/env python3
"""
Test script for TDMA Scheduler
"""

import subprocess
import sys

# Sample test coordinates (16 nodes in a grid pattern)
test_coordinates = '''{
    "Node_01": [0.0, 0.0],
    "Node_02": [300.0, 0.0],
    "Node_03": [600.0, 0.0],
    "Node_04": [900.0, 0.0],
    "Node_05": [0.0, 300.0],
    "Node_06": [300.0, 300.0],
    "Node_07": [600.0, 300.0],
    "Node_08": [900.0, 300.0],
    "Node_09": [0.0, 600.0],
    "Node_10": [300.0, 600.0],
    "Node_11": [600.0, 600.0],
    "Node_12": [900.0, 600.0],
    "Node_13": [0.0, 900.0],
    "Node_14": [300.0, 900.0],
    "Node_15": [600.0, 900.0],
    "Node_16": [900.0, 900.0]
}'''

# Run the scheduler
result = subprocess.run(
    [sys.executable, 'tdma_scheduler.py', '--coordinates', test_coordinates],
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")

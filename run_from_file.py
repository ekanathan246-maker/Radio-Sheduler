#!/usr/bin/env python3
"""
Convenience script to run TDMA scheduler with coordinates from a JSON file
"""

import json
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_from_file.py <coordinates_file.json> [--range <meters>]")
        sys.exit(1)

    json_file = sys.argv[1]
    radio_range = "500.0"

    # Parse optional range argument
    if "--range" in sys.argv:
        range_index = sys.argv.index("--range")
        if range_index + 1 < len(sys.argv):
            radio_range = sys.argv[range_index + 1]

    try:
        # Read coordinates from JSON file
        with open(json_file, 'r') as f:
            coordinates = json.load(f)

        # Convert to JSON string
        coord_string = json.dumps(coordinates)

        # Run the scheduler
        result = subprocess.run(
            [sys.executable, 'tdma_scheduler.py', '--coordinates', coord_string, '--range', radio_range],
            capture_output=False
        )

        sys.exit(result.returncode)

    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{json_file}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

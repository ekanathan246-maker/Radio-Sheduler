#!/usr/bin/env python3
"""
TDMA Schedule Planner and Optimizer
Implements Distance-2 Graph Coloring for wireless network scheduling
to avoid interference in TDMA networks.
"""

import json
import sys
import argparse
from typing import Dict, List, Tuple, Set
import networkx as nx


class TDMAScheduler:
    """
    TDMA Scheduler that uses Distance-2 Graph Coloring to assign time slots
    to radio nodes while avoiding interference.
    """

    def __init__(self, radio_range: float = 500.0):
        """
        Initialize the TDMA scheduler.

        Args:
            radio_range: Maximum communication range in meters (default: 500m)
        """
        self.radio_range = radio_range
        self.graph = nx.Graph()
        self.node_coordinates = {}
        self.slot_assignments = {}
        self.schedule_matrix = []

    def parse_coordinates(self, coord_json: str) -> Dict[str, Tuple[float, float]]:
        """
        Parse node coordinates from JSON string.

        Args:
            coord_json: JSON string with node coordinates

        Returns:
            Dictionary mapping node names to (x, y) coordinates
        """
        try:
            coords = json.loads(coord_json)
            node_coords = {}
            for node_name, coordinates in coords.items():
                if len(coordinates) == 2:
                    node_coords[node_name] = (float(coordinates[0]), float(coordinates[1]))
                else:
                    raise ValueError(f"Invalid coordinates for {node_name}")
            return node_coords
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate Euclidean distance between two coordinates.

        Args:
            coord1: (x, y) tuple
            coord2: (x, y) tuple

        Returns:
            Euclidean distance in meters
        """
        return ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5

    def build_communication_graph(self, node_coords: Dict[str, Tuple[float, float]]) -> nx.Graph:
        """
        Build a graph where edges represent direct communication links
        (nodes within radio range of each other).

        Args:
            node_coords: Dictionary of node coordinates

        Returns:
            NetworkX graph with communication edges
        """
        self.graph = nx.Graph()
        self.node_coordinates = node_coords

        # Add all nodes
        for node_name in node_coords:
            self.graph.add_node(node_name)

        # Add edges for nodes within radio range
        node_list = list(node_coords.keys())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                node1 = node_list[i]
                node2 = node_list[j]
                distance = self.calculate_distance(node_coords[node1], node_coords[node2])
                if distance <= self.radio_range:
                    self.graph.add_edge(node1, node2)

        return self.graph

    def build_distance2_graph(self, comm_graph: nx.Graph) -> nx.Graph:
        """
        Build a Distance-2 graph where nodes are connected if they are
        within 2 hops in the communication graph.

        This captures both:
        - Direct link interference (Distance-1)
        - Hidden terminal interference (Distance-2)

        Args:
            comm_graph: Original communication graph

        Returns:
            Distance-2 graph
        """
        d2_graph = nx.Graph()

        # Add all nodes
        for node in comm_graph.nodes():
            d2_graph.add_node(node)

        # Add edges for nodes within 2 hops
        for node1 in comm_graph.nodes():
            # Get 2-hop neighbors
            two_hop_neighbors = set()
            one_hop = set(comm_graph.neighbors(node1))
            two_hop_neighbors.update(one_hop)

            for neighbor in one_hop:
                two_hop_neighbors.update(comm_graph.neighbors(neighbor))

            # Node1 conflicts with all nodes in its 2-hop neighborhood
            for node2 in two_hop_neighbors:
                if node1 != node2:
                    d2_graph.add_edge(node1, node2)

        return d2_graph

    def dsatur_coloring(self, graph: nx.Graph) -> Dict[str, int]:
        """
        Apply DSATUR (Degree of Saturation) graph coloring algorithm.
        This is a well-known heuristic that often produces better colorings
        than simple degree-based ordering.

        DSATUR selects the uncolored node with the highest saturation degree
        (number of different colors used by its neighbors), breaking ties
        by degree.

        Args:
            graph: Graph to color

        Returns:
            Dictionary mapping node names to slot numbers
        """
        coloring = {}
        uncolored = set(graph.nodes())

        while uncolored:
            # Find node with maximum saturation degree
            max_saturation = -1
            max_degree = -1
            selected_node = None

            for node in uncolored:
                # Calculate saturation degree (number of different colors in neighbors)
                neighbor_colors = set()
                for neighbor in graph.neighbors(node):
                    if neighbor in coloring:
                        neighbor_colors.add(coloring[neighbor])

                saturation = len(neighbor_colors)
                degree = graph.degree(node)

                # Select node with highest saturation, break ties by degree
                if saturation > max_saturation or (saturation == max_saturation and degree > max_degree):
                    max_saturation = saturation
                    max_degree = degree
                    selected_node = node

            # Assign the smallest available color to selected node
            neighbor_colors = set()
            for neighbor in graph.neighbors(selected_node):
                if neighbor in coloring:
                    neighbor_colors.add(coloring[neighbor])

            color = 0
            while color in neighbor_colors:
                color += 1

            coloring[selected_node] = color
            uncolored.remove(selected_node)

        return coloring

    def apply_spatial_reuse_optimization(self, d2_graph: nx.Graph, initial_coloring: Dict[str, int]) -> Dict[str, int]:
        """
        Optimize coloring to enable spatial reuse by attempting to reassign
        colors to reduce total number of slots.

        This is a post-processing optimization that tries to:
        1. Identify slots that can be merged
        2. Reassign nodes to enable spatial reuse

        Args:
            d2_graph: Distance-2 conflict graph
            initial_coloring: Initial slot assignments

        Returns:
            Optimized slot assignments
        """
        coloring = initial_coloring.copy()

        # Multiple passes of optimization
        improved = True
        iteration = 0
        max_iterations = 10

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1

            # Try to reassign nodes to earlier slots
            for node in sorted(coloring.keys(), key=lambda x: coloring[x], reverse=True):
                current_slot = coloring[node]

                # Try to assign to an earlier slot
                for target_slot in range(current_slot):
                    # Check if this would cause conflicts
                    conflict = False
                    for neighbor in d2_graph.neighbors(node):
                        if neighbor in coloring and coloring[neighbor] == target_slot:
                            conflict = True
                            break

                    if not conflict:
                        # Safe to reassign
                        coloring[node] = target_slot
                        improved = True
                        break

        # Re-compact the coloring to remove gaps
        used_slots = sorted(set(coloring.values()))
        slot_mapping = {old: new for new, old in enumerate(used_slots)}
        for node in coloring:
            coloring[node] = slot_mapping[coloring[node]]

        return coloring

    def generate_schedule_matrix(self, slot_assignments: Dict[str, int]) -> List[List[int]]:
        """
        Generate the Slot × Node binary matrix from slot assignments.

        Args:
            slot_assignments: Dictionary mapping node names to slot numbers

        Returns:
            2D list representing the schedule matrix
        """
        # Get sorted node names and number of slots
        node_names = sorted(slot_assignments.keys())
        num_slots = max(slot_assignments.values()) + 1

        # Initialize matrix with zeros
        matrix = [[0] * len(node_names) for _ in range(num_slots)]

        # Fill matrix: matrix[slot][node_index] = 1 if node uses this slot
        for node, slot in slot_assignments.items():
            node_index = node_names.index(node)
            matrix[slot][node_index] = 1

        return matrix

    def optimize_schedule(self, coord_json: str) -> Tuple[Dict[str, int], List[List[int]]]:
        """
        Main optimization pipeline:
        1. Parse coordinates
        2. Build communication graph
        3. Build distance-2 conflict graph
        4. Apply graph coloring
        5. Optimize for spatial reuse
        6. Generate schedule matrix

        Args:
            coord_json: JSON string with node coordinates

        Returns:
            Tuple of (slot_assignments, schedule_matrix)
        """
        # Parse coordinates
        node_coords = self.parse_coordinates(coord_json)

        # Build communication graph
        comm_graph = self.build_communication_graph(node_coords)

        # Build distance-2 conflict graph
        d2_graph = self.build_distance2_graph(comm_graph)

        # Apply DSATUR graph coloring (better heuristic than simple degree-based)
        initial_coloring = self.dsatur_coloring(d2_graph)

        # Optimize for spatial reuse
        optimized_coloring = self.apply_spatial_reuse_optimization(d2_graph, initial_coloring)

        self.slot_assignments = optimized_coloring

        # Generate schedule matrix
        self.schedule_matrix = self.generate_schedule_matrix(optimized_coloring)

        return optimized_coloring, self.schedule_matrix

    def verify_conflict_free(self, slot_assignments: Dict[str, int]) -> bool:
        """
        Verify that the schedule is conflict-free by checking
        the distance-2 constraint.

        Args:
            slot_assignments: Slot assignments to verify

        Returns:
            True if conflict-free, False otherwise
        """
        # Rebuild distance-2 graph
        d2_graph = self.build_distance2_graph(self.graph)

        # Check for conflicts
        for node1 in d2_graph.nodes():
            for node2 in d2_graph.neighbors(node1):
                if slot_assignments[node1] == slot_assignments[node2]:
                    return False

        return True

    def print_report(self):
        """
        Print the optimization report in the specified format.
        """
        print("=" * 70)
        print("TDMA TOPOLOGY OPTIMIZATION REPORT".center(70))
        print("=" * 70)
        print(f"Total Nodes Processed   : {len(self.node_coordinates)}")
        print(f"Configured Radio Range  : {self.radio_range} meters")
        print(f"Optimized Frame Length  : {max(self.slot_assignments.values()) + 1} unique timeslots (Lower is better)")
        print("-" * 70)
        print("NODE -> SLOT ASSIGNMENTS:")

        # Print slot assignments in sorted order
        for node in sorted(self.slot_assignments.keys()):
            print(f"{node}: Slot {self.slot_assignments[node]}")

        print("\nSTRUCTURAL TDMA SCHEDULE MATRIX (Slot x Node Boolean Matrix):")

        # Print matrix header
        node_names = sorted(self.slot_assignments.keys())
        header = "Slot \\ Node |"
        for node in node_names:
            header += f" {node[-2:]} |"
        print(header)
        print("-" * (len(header)))

        # Print matrix rows
        for slot_idx, row in enumerate(self.schedule_matrix):
            row_str = f"Slot {slot_idx:02d}        |"
            for val in row:
                row_str += f" {val}  |"
            print(row_str)

        print("-" * 70)

        # Verify conflict-free
        is_conflict_free = self.verify_conflict_free(self.slot_assignments)
        if is_conflict_free:
            print("Execution finalized cleanly. Schedule verified conflict-free.")
        else:
            print("WARNING: Schedule contains conflicts!")

        print("=" * 70)


def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description='TDMA Schedule Planner and Optimizer - Generate conflict-free TDMA schedules'
    )
    parser.add_argument(
        '--coordinates',
        type=str,
        required=True,
        help='JSON string with node coordinates, e.g., \'{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0]}\''
    )
    parser.add_argument(
        '--range',
        type=float,
        default=500.0,
        help='Radio range in meters (default: 500.0)'
    )

    args = parser.parse_args()

    try:
        # Create scheduler
        scheduler = TDMAScheduler(radio_range=args.range)

        # Optimize schedule
        scheduler.optimize_schedule(args.coordinates)

        # Print report
        scheduler.print_report()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

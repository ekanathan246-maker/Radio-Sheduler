#!/usr/bin/env python3
"""
Tests for the TDMA Scheduler.
"""

import json

from tdma_scheduler import TDMAScheduler


# 16-node test topology
TEST_COORDINATES = {
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
    "Node_16": [900.0, 900.0],
}


def create_scheduler():
    """Create a scheduler using the required 500 m range."""
    return TDMAScheduler(radio_range=500.0)


def test_node_count():
    """The input must contain exactly 16 nodes."""

    scheduler = create_scheduler()

    coordinates = json.dumps(TEST_COORDINATES)

    node_coords = scheduler.parse_coordinates(coordinates)

    assert len(node_coords) == 16

    print("PASS: 16 nodes loaded")


def test_communication_graph():
    """Nodes within 500 m should have communication links."""

    scheduler = create_scheduler()

    coordinates = json.dumps(TEST_COORDINATES)

    node_coords = scheduler.parse_coordinates(coordinates)

    graph = scheduler.build_communication_graph(node_coords)

    assert graph.number_of_nodes() == 16

    # Node 01 and Node 02 are 300 m apart.
    assert graph.has_edge("Node_01", "Node_02")

    # Node 01 and Node 03 are 600 m apart.
    assert not graph.has_edge("Node_01", "Node_03")

    print("PASS: 500 m communication range works")


def test_distance2_graph():
    """Distance-2 conflicts should be present."""

    scheduler = create_scheduler()

    coordinates = json.dumps(TEST_COORDINATES)

    node_coords = scheduler.parse_coordinates(coordinates)

    graph = scheduler.build_communication_graph(node_coords)

    d2_graph = scheduler.build_distance2_graph(graph)

    # Node 01 and Node 03 are not directly connected,
    # but they are two hops apart through Node 02.
    assert not graph.has_edge("Node_01", "Node_03")
    assert d2_graph.has_edge("Node_01", "Node_03")

    print("PASS: Distance-2 conflicts work")


def test_schedule():
    """The generated schedule must be conflict-free."""

    scheduler = create_scheduler()

    coordinates = json.dumps(TEST_COORDINATES)

    assignments, matrix = scheduler.optimize_schedule(coordinates)

    assert len(assignments) == 16

    assert scheduler.verify_conflict_free(assignments)

    print("PASS: Schedule is conflict-free")


def test_each_node_has_one_slot():
    """Every node must receive exactly one slot."""

    scheduler = create_scheduler()

    coordinates = json.dumps(TEST_COORDINATES)

    assignments, matrix = scheduler.optimize_schedule(coordinates)

    assert len(assignments) == 16

    # Every node has exactly one integer slot.
    for node, slot in assignments.items():
        assert isinstance(slot, int)
        assert slot >= 0

    print("PASS: Every node has exactly one slot")


def test_schedule_matrix():
    """The schedule matrix must contain one 1 for every node."""

    scheduler = create_scheduler()

    coordinates = json.dumps(TEST_COORDINATES)

    assignments, matrix = scheduler.optimize_schedule(coordinates)

    # 16 columns, one for each node.
    assert len(matrix[0]) == 16

    # Every node must appear exactly once in the matrix.
    for column in range(16):
        column_sum = sum(row[column] for row in matrix)
        assert column_sum == 1

    # Matrix must contain only 0 and 1.
    for row in matrix:
        for value in row:
            assert value in (0, 1)

    print("PASS: Schedule matrix is valid")


def test_optimal_slot_count_for_sample():
    """
    For this specific topology, the Distance-2 conflict graph
    contains a 9-node clique, so at least 9 slots are required.

    The current scheduler also produces 9 slots.
    """

    scheduler = create_scheduler()

    coordinates = json.dumps(TEST_COORDINATES)

    assignments, matrix = scheduler.optimize_schedule(coordinates)

    number_of_slots = max(assignments.values()) + 1

    assert number_of_slots == 9

    print("PASS: Sample topology uses 9 slots")


if __name__ == "__main__":

    tests = [
        test_node_count,
        test_communication_graph,
        test_distance2_graph,
        test_schedule,
        test_each_node_has_one_slot,
        test_schedule_matrix,
        test_optimal_slot_count_for_sample,
    ]

    print("=" * 60)
    print("TDMA SCHEDULER TESTS")
    print("=" * 60)

    for test in tests:
        test()

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
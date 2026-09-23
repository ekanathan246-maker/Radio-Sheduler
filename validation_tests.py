#!/usr/bin/env python3
"""
Comprehensive validation tests for TDMA Scheduler
Tests correctness, edge cases, and algorithm properties
"""

import json
import sys
from tdma_scheduler import TDMAScheduler


def test_basic_functionality():
    """Test basic functionality with simple 3-node scenario"""
    print("Test 1: Basic 3-node scenario")
    coords = '{"Node_A":[0.0,0.0],"Node_B":[200.0,0.0],"Node_C":[400.0,0.0]}'
    scheduler = TDMAScheduler(radio_range=500.0)
    scheduler.optimize_schedule(coords)
    print(f"  Slots used: {max(scheduler.slot_assignments.values()) + 1}")
    print(f"  Conflict-free: {scheduler.verify_conflict_free(scheduler.slot_assignments)}")
    print("  [PASS]" if scheduler.verify_conflict_free(scheduler.slot_assignments) else "  [FAIL]")
    return scheduler.verify_conflict_free(scheduler.slot_assignments)


def test_direct_interference():
    """Test that directly connected nodes get different slots"""
    print("\nTest 2: Direct interference (nodes within range)")
    coords = '{"Node_01":[0.0,0.0],"Node_02":[100.0,0.0]}'
    scheduler = TDMAScheduler(radio_range=500.0)
    scheduler.optimize_schedule(coords)
    slot1 = scheduler.slot_assignments["Node_01"]
    slot2 = scheduler.slot_assignments["Node_02"]
    different = (slot1 != slot2)
    print(f"  Node_01: Slot {slot1}, Node_02: Slot {slot2}")
    print(f"  Different slots: {different}")
    print("  [PASS]" if different else "  [FAIL]")
    return different


def test_hidden_terminal():
    """Test that 2-hop nodes get different slots"""
    print("\nTest 3: Hidden terminal problem (2-hop interference)")
    # A -> B -> C chain, A and C should have different slots
    coords = '{"Node_A":[0.0,0.0],"Node_B":[250.0,0.0],"Node_C":[500.0,0.0]}'
    scheduler = TDMAScheduler(radio_range=500.0)
    scheduler.optimize_schedule(coords)
    slotA = scheduler.slot_assignments["Node_A"]
    slotC = scheduler.slot_assignments["Node_C"]
    different = (slotA != slotC)
    print(f"  Node_A: Slot {slotA}, Node_C: Slot {slotC}")
    print(f"  Different slots (2-hop): {different}")
    print("  [PASS]" if different else "  [FAIL]")
    return different


def test_spatial_reuse():
    """Test that distant nodes can share slots"""
    print("\nTest 4: Spatial reuse (nodes >2 hops can share slots)")
    # 4 nodes in a line, A-B-C-D, A and D should be able to share
    coords = '{"Node_A":[0.0,0.0],"Node_B":[300.0,0.0],"Node_C":[600.0,0.0],"Node_D":[900.0,0.0]}'
    scheduler = TDMAScheduler(radio_range=500.0)
    scheduler.optimize_schedule(coords)
    slotA = scheduler.slot_assignments["Node_A"]
    slotD = scheduler.slot_assignments["Node_D"]
    can_share = (slotA == slotD)
    print(f"  Node_A: Slot {slotA}, Node_D: Slot {slotD}")
    print(f"  Can share slots: {can_share}")
    print("  [PASS]" if can_share else "  [FAIL] (not necessarily wrong, but shows no spatial reuse)")
    return can_share


def test_isolated_nodes():
    """Test that isolated nodes can share slots"""
    print("\nTest 5: Isolated nodes (far apart, can share)")
    coords = '{"Node_01":[0.0,0.0],"Node_02":[2000.0,0.0]}'
    scheduler = TDMAScheduler(radio_range=500.0)
    scheduler.optimize_schedule(coords)
    slot1 = scheduler.slot_assignments["Node_01"]
    slot2 = scheduler.slot_assignments["Node_02"]
    can_share = (slot1 == slot2)
    print(f"  Node_01: Slot {slot1}, Node_02: Slot {slot2}")
    print(f"  Can share slots: {can_share}")
    print("  [PASS]" if can_share else "  [FAIL]")
    return can_share


def test_16_node_grid():
    """Test the specified 16-node grid scenario"""
    print("\nTest 6: 16-node grid (specification test)")
    coords = json.dumps({
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
    })
    scheduler = TDMAScheduler(radio_range=500.0)
    scheduler.optimize_schedule(coords)
    num_slots = max(scheduler.slot_assignments.values()) + 1
    conflict_free = scheduler.verify_conflict_free(scheduler.slot_assignments)
    print(f"  Nodes: 16, Slots: {num_slots}")
    print(f"  Conflict-free: {conflict_free}")
    print("  [PASS]" if conflict_free else "  [FAIL]")
    return conflict_free


def test_slot_efficiency():
    """Test that scheduler doesn't use unnecessary slots"""
    print("\nTest 7: Slot efficiency check")
    # Simple linear chain: should use minimal slots
    coords = '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0]}'
    scheduler = TDMAScheduler(radio_range=500.0)
    scheduler.optimize_schedule(coords)
    num_slots = max(scheduler.slot_assignments.values()) + 1
    # For 3 nodes in a line, we should use at most 3 slots (ideally 2)
    efficient = num_slots <= 3
    print(f"  Slots used: {num_slots} (expected <= 3)")
    print(f"  Efficient: {efficient}")
    print("  [PASS]" if efficient else "  [FAIL]")
    return efficient


def test_graph_structure():
    """Test that the graph structure is built correctly"""
    print("\nTest 8: Graph structure validation")
    coords = '{"Node_01":[0.0,0.0],"Node_02":[200.0,0.0],"Node_03":[600.0,0.0]}'
    scheduler = TDMAScheduler(radio_range=500.0)
    node_coords = scheduler.parse_coordinates(coords)
    comm_graph = scheduler.build_communication_graph(node_coords)

    # Node_01 and Node_02 should be connected (200m < 500m)
    # Node_01 and Node_03 should be connected (600m > 500m, actually not connected)
    edge_01_02 = comm_graph.has_edge("Node_01", "Node_02")
    edge_01_03 = comm_graph.has_edge("Node_01", "Node_03")

    print(f"  Edge 01-02: {edge_01_02} (expected True)")
    print(f"  Edge 01-03: {edge_01_03} (expected False)")
    correct = (edge_01_02 and not edge_01_03)
    print("  [PASS]" if correct else "  [FAIL]")
    return correct


def run_all_tests():
    """Run all validation tests"""
    print("=" * 70)
    print("TDMA SCHEDULER VALIDATION TESTS")
    print("=" * 70)

    tests = [
        test_basic_functionality,
        test_direct_interference,
        test_hidden_terminal,
        test_spatial_reuse,
        test_isolated_nodes,
        test_16_node_grid,
        test_slot_efficiency,
        test_graph_structure
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append(False)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Scheduler is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Review the output above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

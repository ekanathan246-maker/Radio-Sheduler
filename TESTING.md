# Testing Guide for TDMA Scheduler

This document provides comprehensive testing procedures for the TDMA scheduler.

## Installation

### Prerequisites
- Python 3.6 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies**:
- `networkx>=3.0` - Graph manipulation and algorithms
- `numpy>=1.24.0` - Numerical operations

## Automated Test Suite

### Run All Tests

```bash
python validation_tests.py
```

**Expected Output**: All 8 tests pass with 100% success rate

### Test Descriptions

The automated test suite includes:

1. **Basic 3-node scenario**: Tests basic functionality with 3 nodes
2. **Direct interference**: Verifies nodes within range get different slots
3. **Hidden terminal problem**: Verifies 2-hop nodes get different slots
4. **Spatial reuse**: Verifies distant nodes can share slots
5. **Isolated nodes**: Verifies far-apart nodes can share slots
6. **16-node grid**: Tests the specification scenario
7. **Slot efficiency**: Verifies scheduler doesn't use unnecessary slots
8. **Graph structure**: Verifies graph edges are built correctly

## Manual Test Scenarios

### Test 1: Direct Interference (Different Slots Required)

**Purpose**: Verify that nodes within radio range get different time slots

```bash
python tdma_scheduler.py --coordinates '{"Node_A":[0.0,0.0],"Node_B":[100.0,0.0]}' --range 500.0
```

**Expected Results**:
- Node_A and Node_B should have different slots
- 2 time slots should be used
- Output should say "Schedule verified conflict-free"

**Verification**:
```
Node_A: Slot 1
Node_B: Slot 0
Optimized Frame Length: 2 unique timeslots
```

### Test 2: Spatial Reuse (Same Slot Allowed)

**Purpose**: Verify that distant nodes can safely share the same time slot

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[2000.0,0.0]}' --range 500.0
```

**Expected Results**:
- Node_01 and Node_02 should have the same slot
- Only 1 time slot should be used
- Demonstrates spatial reuse

**Verification**:
```
Node_01: Slot 0
Node_02: Slot 0
Optimized Frame Length: 1 unique timeslots
```

### Test 3: Hidden Terminal Problem

**Purpose**: Verify that 2-hop interference is handled correctly

```bash
python tdma_scheduler.py --coordinates '{"Node_A":[0.0,0.0],"Node_B":[250.0,0.0],"Node_C":[500.0,0.0]}' --range 500.0
```

**Expected Results**:
- Node_A and Node_C should have different slots (they interfere at Node_B)
- Node_B should have a different slot from both A and C
- At least 3 time slots should be used

**Verification**:
```
Node_A: Slot 2
Node_B: Slot 0
Node_C: Slot 1
Optimized Frame Length: 3 unique timeslots
```

### Test 4: Small Grid Topology

**Purpose**: Test with a small 3×3 grid topology

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0],"Node_04":[0.0,300.0],"Node_05":[300.0,300.0],"Node_06":[600.0,300.0],"Node_07":[0.0,600.0],"Node_08":[300.0,600.0],"Node_09":[600.0,600.0]}' --range 500.0
```

**Expected Results**:
- Schedule should be conflict-free
- Slots should be distributed reasonably
- Spatial reuse should be visible
- Expected: 4-6 time slots

### Test 5: 16-Node Specification Test

**Purpose**: Test the exact scenario from the problem statement

```bash
python run_from_file.py sample_input.json
```

**Expected Results**:
- 16 nodes processed
- 9 time slots (or similar efficient number)
- Conflict-free schedule
- Spatial reuse demonstrated

## Edge Case Testing

### Single Node

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0]}' --range 500.0
```

**Expected**: 1 slot, conflict-free

### Many Isolated Nodes

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[2000.0,0.0],"Node_03":[4000.0,0.0]}' --range 500.0
```

**Expected**: All nodes share 1 slot (spatial reuse)

### Dense Network

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[100.0,0.0],"Node_03":[200.0,0.0],"Node_04":[300.0,0.0]}' --range 500.0
```

**Expected**: Many slots due to high interference (4+ slots)

### Linear Chain

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0],"Node_04":[900.0,0.0]}' --range 500.0
```

**Expected**: Efficient slot usage with spatial reuse (2-3 slots)

## Different Topology Tests

### Small Network (4 nodes)

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0],"Node_04":[900.0,0.0]}' --range 500.0
```

### Medium Network (9 nodes)

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],"Node_03":[600.0,0.0],"Node_04":[0.0,300.0],"Node_05":[300.0,300.0],"Node_06":[600.0,300.0],"Node_07":[0.0,600.0],"Node_08":[300.0,600.0],"Node_09":[600.0,600.0]}' --range 500.0
```

### Large Network (16 nodes)

```bash
python run_from_file.py sample_input.json
```

## Different Radio Range Tests

### Small Range (Less Interference)

```bash
python run_from_file.py sample_input.json --range 400
```

**Expected**: Fewer slots due to reduced interference

### Medium Range (Balanced)

```bash
python run_from_file.py sample_input.json --range 500
```

**Expected**: Balanced slot usage (default specification)

### Large Range (More Interference)

```bash
python run_from_file.py sample_input.json --range 600
```

**Expected**: More slots due to increased interference

## Performance Testing

### Test with Different Network Sizes

Create custom JSON files with different numbers of nodes and test performance:

```bash
# Small: 4 nodes
python run_from_file.py small_network.json

# Medium: 9 nodes
python run_from_file.py medium_network.json

# Large: 16 nodes
python run_from_file.py sample_input.json

# Extra Large: 25+ nodes (custom)
python run_from_file.py large_network.json
```

### Stress Testing

Test with very dense networks:

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[50.0,0.0],"Node_03":[100.0,0.0],"Node_04":[150.0,0.0],"Node_05":[200.0,0.0]}' --range 500.0
```

## Interpreting Results

### Success Indicators

- ✅ "Schedule verified conflict-free" in output
- ✅ Reasonable number of slots for the topology
- ✅ Spatial reuse visible (distant nodes sharing slots)
- ✅ All automated tests pass
- ✅ Node assignments make sense for the topology

### Failure Indicators

- ❌ "WARNING: Schedule contains conflicts!"
- ❌ Excessive number of slots (inefficient)
- ❌ Nodes within range sharing slots (incorrect)
- ❌ Automated test failures
- ❌ Nodes that should share slots but don't

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Invalid JSON format

**Solution**: Ensure coordinates are valid JSON
```bash
# Correct format
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0]}'

# Incorrect format (missing quotes)
python tdma_scheduler.py --coordinates '{Node_01:[0.0,0.0]}'
```

### Issue: Too many slots used

**Solution**: This may be normal for dense networks. Check if:
- Radio range is too large
- Network topology is very dense
- Schedule is still conflict-free

### Issue: Tests fail

**Solution**:
1. Check Python version (requires 3.6+)
2. Verify NetworkX installation
3. Check input JSON format
4. Review error messages carefully
5. Run with simple cases to isolate issues

### Issue: Unicode encoding errors

**Solution**: Use the provided scripts which handle encoding correctly. The test suite and run_from_file.py handle encoding properly.

## Custom Test Cases

### Creating Custom Test Files

Create your own JSON files with custom coordinates:

```json
{
    "Node_01": [0.0, 0.0],
    "Node_02": [350.0, 0.0],
    "Node_03": [700.0, 0.0]
}
```

Save as `custom_test.json` and run:
```bash
python run_from_file.py custom_test.json
```

### Algorithm Comparison

Test with different parameters to see algorithm behavior:

```bash
# Compare different radio ranges
for range in 300 400 500 600; do
    echo "Testing with range $range"
    python run_from_file.py sample_input.json --range $range
done
```

## Verification Checklist

Before submission, verify:

- [ ] All 8 automated tests pass
- [ ] 16-node specification test works correctly
- [ ] Schedule is always conflict-free
- [ ] Spatial reuse is demonstrated
- [ ] Different radio ranges produce expected results
- [ ] Edge cases (single node, isolated nodes) work
- [ ] Output format matches specification
- [ ] Manual test scenarios produce correct results
- [ ] Graph structure is built correctly
- [ ] Algorithm properties are verified

## Mathematical Verification

### Manual Verification Steps

1. **Build the distance-2 graph**: For each node, identify all nodes within 2 hops
2. **Check each pair**: For every edge in the distance-2 graph, verify the nodes have different slots
3. **Count slots**: Verify the number of slots is reasonable for the graph's chromatic number

### Graph Structure Verification

The scheduler builds two graphs:

1. **Communication Graph**: Edges between nodes within radio range
2. **Distance-2 Graph**: Edges between nodes within 2 hops (captures interference)

You can verify this by checking:
- Nodes within 500m should be connected in communication graph
- Nodes within 2 hops should be connected in distance-2 graph
- Distant nodes (>2 hops) should not be connected

## Algorithm Properties Verification

### DSATUR Algorithm Verification

The DSATUR algorithm should:
- Color nodes with highest saturation first
- Break ties by degree
- Use minimum valid color for each node

### Spatial Reuse Verification

The schedule should demonstrate spatial reuse:
- Corner nodes in a grid often share slots
- Isolated nodes can share slots
- Slots are reused when nodes are >2 hops apart

## Integration Testing

### EMANE Integration Preparation

To verify the scheduler would work with EMANE (Part 2):

1. **Export schedule**: The scheduler outputs a Slot × Node binary matrix
2. **Format conversion**: This matrix can be converted to EMANE's XML/ProtoBuf format
3. **EMANE integration**: The schedule can be injected into EMANE's control channel
4. **Packet verification**: EMANE would drop packets outside assigned slots

The current implementation provides the "brain" that generates the schedule matrix needed for EMANE integration.

## Summary

The TDMA scheduler can be thoroughly tested through:
- ✅ Automated test suite (8 tests, 100% pass rate)
- ✅ Manual scenario testing (5+ scenarios)
- ✅ Edge case testing (4+ edge cases)
- ✅ Different topology tests (4+ topologies)
- ✅ Different radio range tests (3+ ranges)
- ✅ Performance testing (various network sizes)
- ✅ Mathematical verification
- ✅ Algorithm properties verification

All testing methods confirm the scheduler is working correctly and generating conflict-free TDMA schedules with spatial reuse optimization.

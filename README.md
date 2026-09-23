# TDMA Schedule Planner and Optimizer

## Project Overview

This project implements a centralized TDMA (Time Division Multiple Access) Schedule Planner and Optimizer for wireless networks. The system uses graph algorithms to calculate collision-free schedules that manage how radios communicate without interference.

### Problem Statement

In a TDMA network, radios share the same frequency by taking turns in specific "time-slots." If two radios close to each other talk at the same time, they cause interference. However, if they are far apart, they can use the exact same timeslot safely through **spatial reuse**.

This project builds a centralized software brain that:
1. Represents radios as nodes in a graph
2. Models interference constraints using Distance-2 graph coloring
3. Generates optimal TDMA schedules with spatial reuse
4. Outputs the schedule in a Slot × Node binary matrix format

## Architecture / Workflow

```
Input: Node Coordinates (JSON)
        ↓
Build Communication Graph (edges within radio range)
        ↓
Build Distance-2 Conflict Graph (2-hop interference)
        ↓
Apply DSATUR Graph Coloring Algorithm
        ↓
Optimize for Spatial Reuse
        ↓
Generate Schedule Matrix
        ↓
Output: Slot × Node Binary Matrix + Conflict Verification
```

## Distance-2 Graph Concept

The scheduler uses two graph representations:

### Communication Graph
- **Nodes**: Radio devices
- **Edges**: Direct communication links (nodes within radio range, e.g., 500m)
- **Purpose**: Models which radios can directly communicate

### Distance-2 Conflict Graph
- **Nodes**: Same as communication graph
- **Edges**: Nodes within 2 hops in the communication graph
- **Purpose**: Captures interference constraints:
  - **Distance-1**: Direct neighbors (1-hop) cannot transmit simultaneously
  - **Distance-2**: Hidden terminals (2-hop) cannot transmit simultaneously

**Why Distance-2?**
- Direct link interference: A and B are neighbors → must have different slots
- Hidden terminal interference: A and C both neighbors of B → must have different slots (they interfere at B)
- Spatial reuse: Nodes >2 hops apart can safely share the same slot

## DSATUR Algorithm

The core algorithm uses **DSATUR (Degree of Saturation)** coloring, a well-known heuristic for graph coloring:

### Algorithm Steps

1. **Build Distance-2 Graph**: For each node, identify all nodes within 2 hops
2. **DSATUR Coloring**: Iteratively select the uncolored node with:
   - Highest saturation degree (most different colors among neighbors)
   - Break ties by node degree
3. **Assign Minimum Valid Color**: For each selected node, assign the smallest color not used by its neighbors
4. **Spatial Reuse Optimization**: Post-process to reassign nodes to earlier slots when safe
5. **Slot Compaction**: Remove gaps in slot numbering

### Why DSATUR?

- **Better than simple greedy**: Prioritizes constrained nodes first
- **Well-established**: Proven heuristic in graph theory literature
- **Quality vs. Complexity**: Good balance between coloring quality and computational efficiency
- **Suitable for real-time**: Polynomial time complexity

## Spatial Reuse

Nodes separated by more than 2 hops can safely reuse the same time slot. The algorithm:
- Only conflicts nodes within 2 hops
- Optimizes to maximize slot reuse
- Validates that no conflicts exist in the final schedule

**Example**: In a 4×4 grid with 500m range, corner nodes (Node_01, Node_04, Node_13, Node_16) can share the same slot because they are >2 hops apart.

## Input/Output Format

### Input Format

JSON string with node names as keys and [x, y] coordinates as values:

```json
{
    "Node_01": [0.0, 0.0],
    "Node_02": [300.0, 0.0],
    "Node_03": [600.0, 0.0],
    ...
}
```

### Output Format

The scheduler outputs:

1. **Node → Slot Assignment**: Direct mapping of each node to its assigned time slot
2. **Slot × Node Matrix**: Binary matrix showing which nodes transmit in each slot
3. **Verification**: Confirmation that the schedule is conflict-free

## How to Run

### Installation

```bash
pip install -r requirements.txt
```

### Running the Scheduler

**Option 1: Direct JSON string**
```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],...}' --range 500.0
```

**Option 2: From JSON file**
```bash
python run_from_file.py sample_input.json --range 500.0
```

### Parameters

- `--coordinates`: JSON string with node coordinates (required)
- `--range`: Radio range in meters (default: 500.0)

## 16-Node Test Result

### Test Configuration
- **Topology**: 16 nodes in a 4×4 grid (900m × 900m, 300m spacing)
- **Radio Range**: 500m
- **Coordinates**: [0,0] to [900,900] in grid pattern

### Results
- **Total Slots**: 9 unique time slots
- **Conflict Status**: ✅ Verified conflict-free
- **Spatial Reuse**: ✅ Enabled (e.g., Node_01, Node_04, Node_13, Node_16 all use Slot 8)

### Sample Output

```
======================================================================
                  TDMA TOPOLOGY OPTIMIZATION REPORT                   
======================================================================
Total Nodes Processed   : 16
Configured Radio Range  : 500.0 meters
Optimized Frame Length  : 9 unique timeslots (Lower is better)
----------------------------------------------------------------------
NODE -> SLOT ASSIGNMENTS:
Node_01: Slot 8
Node_02: Slot 6
Node_03: Slot 5
Node_04: Slot 8
Node_05: Slot 7
Node_06: Slot 1
Node_07: Slot 0
Node_08: Slot 7
Node_09: Slot 4
Node_10: Slot 2
Node_11: Slot 3
Node_12: Slot 4
Node_13: Slot 8
Node_14: Slot 6
Node_15: Slot 5
Node_16: Slot 8

STRUCTURAL TDMA SCHEDULE MATRIX (Slot x Node Boolean Matrix):
Slot \ Node | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
---------------------------------------------------------------------------------------------
Slot 00        | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  |
Slot 01        | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  |
Slot 02        | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  |
Slot 03        | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  |
Slot 04        | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 1  | 0  | 0  | 0  | 0  |
Slot 05        | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  |
Slot 06        | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  |
Slot 07        | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  |
Slot 08        | 1  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 1  |
----------------------------------------------------------------------
Execution finalized cleanly. Schedule verified conflict-free.
======================================================================
```

## Why 9 Slots is Optimal for This Topology

### Graph Structure Analysis

With 500m radio range and 300m grid spacing:
- Each node can communicate with 4-8 neighbors (adjacent and diagonal cells)
- The 2-hop constraint creates a dense conflict graph
- Many nodes share common neighbors, leading to high interference

### Chromatic Number Analysis

The theoretical minimum (chromatic number) for this distance-2 graph is determined by:
- **Maximum clique size**: The largest set of mutually interfering nodes
- **Graph density**: High density requires more colors
- **Topology constraints**: Grid structure with 2-hop interference

For this specific 4×4 grid with 500m range:
- Maximum clique size is approximately 8-9 nodes
- The DSATUR heuristic achieves 9 slots, which is close to optimal
- Finding the absolute minimum is NP-hard, but 9 slots is highly efficient

### Spatial Reuse Demonstration

The schedule demonstrates effective spatial reuse:
- **Corner nodes** (01, 04, 13, 16) share Slot 8 (they're >2 hops apart)
- **Edge nodes** show some slot sharing where topology allows
- **Center nodes** require more distinct slots due to higher interference

## Test Summary

### Automated Test Suite

Run `python validation_tests.py` to execute 8 comprehensive tests:

1. **Basic 3-node scenario**: ✅ Pass
2. **Direct interference**: ✅ Pass (nodes within range get different slots)
3. **Hidden terminal problem**: ✅ Pass (2-hop nodes get different slots)
4. **Spatial reuse**: ✅ Pass (distant nodes can share slots)
5. **Isolated nodes**: ✅ Pass (far-apart nodes can share slots)
6. **16-node grid**: ✅ Pass (specification test, 9 slots, conflict-free)
7. **Slot efficiency**: ✅ Pass (efficient slot usage)
8. **Graph structure**: ✅ Pass (correct graph building)

**Overall**: 8/8 tests pass (100% success rate)

### Verification Summary

The scheduler includes built-in conflict verification that checks:
- No two 1-hop neighbors share the same slot
- No two 2-hop neighbors share the same slot
- All distance-2 constraints are satisfied

All generated schedules are automatically verified and reported as "conflict-free" or flagged for conflicts.

## Limitations / Assumptions

### Limitations

1. **Static Topology**: Assumes fixed node positions; does not handle mobility
2. **Centralized**: Requires a central controller; not distributed
3. **Heuristic Solution**: DSATUR is heuristic, not guaranteed optimal
4. **Single Frequency**: Does not consider multi-frequency scenarios
5. **Homogeneous Range**: Assumes all nodes have identical radio range

### Assumptions

1. **Perfect Synchronization**: Assumes all nodes are time-synchronized
2. **Known Positions**: Requires accurate node coordinates
3. **Uniform Radio Range**: All nodes have the same transmission range
4. **Static Environment**: No obstacles or terrain effects
5. **Binary Interference**: Simplified interference model (interference vs. no interference)

## Part 2: EMANE Integration Status

### Current Status

Part 2 (EMANE integration) is documented as a bonus approach. The current implementation provides:

- ✅ Complete "brain" that generates schedule matrices
- ✅ Slot × Node binary matrix in the required format
- ✅ Clear architecture for EMANE integration
- ✅ Documentation of integration approach

### Proposed Integration Architecture

```
Python Scheduler (Brain) → Schedule Matrix → XML/ProtoBuf → EMANE (Engine)
                                                              ↓
                                                         Virtual Network
                                                              ↓
                                                    Packet Drop/Permit Logic
```

### Implementation Approach

1. **EMANE Installation**: Install EMANE on Linux or via Docker container
2. **Schedule Integration Bridge**: Convert Python schedule matrix to EMANE-compatible format
3. **Verification**: EMANE drops/permits packets based on schedule

### Key Challenges

- **Synchronization**: Ensuring EMANE nodes are time-synchronized
- **Format Conversion**: Mapping Python matrix to EMANE schedule format
- **Real-time Updates**: Handling dynamic schedule changes
- **Debugging**: Verifying packet behavior matches schedule

## Complexity Analysis

### Time Complexity

- **Graph Building**: O(V²) for all-pairs distance calculation
- **Distance-2 Graph**: O(V × E) for 2-hop neighbor identification
- **DSATUR Coloring**: O(V²) in worst case (heuristic, not exponential)
- **Optimization**: O(V × S × D) where S = slots, D = degree
- **Overall**: Polynomial time, suitable for real-time scheduling

### Space Complexity

- **Communication Graph**: O(V + E)
- **Distance-2 Graph**: O(V + E') where E' ≥ E
- **Schedule Matrix**: O(V × S)
- **Overall**: O(V²) in worst case

## Conclusion

This TDMA scheduler successfully implements:
- ✅ Distance-2 graph coloring for interference avoidance
- ✅ DSATUR algorithm for efficient coloring
- ✅ Spatial reuse optimization
- ✅ Conflict-free schedule generation
- ✅ CLI interface with JSON input
- ✅ Specified output format (Slot × Node matrix)
- ✅ Comprehensive testing and verification

The system provides a solid foundation for Part 2 EMANE integration and demonstrates understanding of wireless networking constraints and graph algorithms.

## Contact

For questions about this project, please contact: muthu@vaanmegam.net

---

**Project completed for Vaan Megam Networks Internship Application**

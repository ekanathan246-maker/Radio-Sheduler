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

## Technical Approach

### 1. Graph Representation

The network is modeled using NetworkX graphs:

- **Communication Graph**: Nodes represent radios, edges represent direct communication links (nodes within 500m radio range)
- **Distance-2 Conflict Graph**: Nodes are connected if they are within 2 hops, capturing both:
  - **Direct Link Interference (Distance-1)**: Two nodes directly connected must have different time slots
  - **Hidden Terminal Interference (Distance-2)**: Two nodes sharing a common neighbor must have different time slots (they interfere at the shared neighbor)

### 2. Distance-2 Graph Coloring Algorithm

The core algorithm uses **DSATUR (Degree of Saturation)** coloring:

1. **Build Distance-2 Graph**: For each node, identify all nodes within 2 hops
2. **DSATUR Coloring**: Iteratively select the uncolored node with:
   - Highest saturation degree (most different colors among neighbors)
   - Break ties by node degree
3. **Assign Minimum Valid Color**: For each selected node, assign the smallest color not used by its neighbors
4. **Spatial Reuse Optimization**: Post-process to reassign nodes to earlier slots when safe
5. **Slot Compaction**: Remove gaps in slot numbering

### 3. Spatial Reuse

Nodes separated by more than 2 hops can safely reuse the same time slot. The algorithm:
- Only conflicts nodes within 2 hops
- Optimizes to maximize slot reuse
- Validates that no conflicts exist in the final schedule

## Implementation Details

### File Structure

```
TDMA/
├── tdma_scheduler.py      # Main scheduler implementation
├── requirements.txt       # Python dependencies
├── test_scheduler.py      # Test script
└── README.md             # This documentation
```

### Key Components

#### TDMAScheduler Class

- `parse_coordinates()`: Parses JSON node coordinates
- `calculate_distance()`: Computes Euclidean distance between nodes
- `build_communication_graph()`: Creates graph with edges for nodes within radio range
- `build_distance2_graph()`: Creates conflict graph for 2-hop interference
- `dsatur_coloring()`: Implements DSATUR graph coloring algorithm
- `apply_spatial_reuse_optimization()`: Post-processes to enable spatial reuse
- `generate_schedule_matrix()`: Creates Slot × Node binary matrix
- `verify_conflict_free()`: Validates schedule against interference constraints

### Dependencies

- **NetworkX**: Graph manipulation and algorithms
- **NumPy**: Numerical operations (optional, for future extensions)

## Usage

### Installation

```bash
pip install -r requirements.txt
```

### Running the Scheduler

```bash
python tdma_scheduler.py --coordinates '{"Node_01":[0.0,0.0],"Node_02":[300.0,0.0],...}' --range 500.0
```

### Parameters

- `--coordinates`: JSON string with node coordinates (required)
- `--range`: Radio range in meters (default: 500.0)

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

## Sample Output

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
...
Node_16: Slot 8

STRUCTURAL TDMA SCHEDULE MATRIX (Slot x Node Boolean Matrix):
Slot \ Node | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
---------------------------------------------------------------------------------------------
Slot 00        | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  |
Slot 01        | 0  | 0  | 0  | 0  | 0  | 0  | 1  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  | 0  |
...
----------------------------------------------------------------------
Execution finalized cleanly. Schedule verified conflict-free.
======================================================================
```

## Design Process and Thought Process

### 1. Initial Problem Analysis

**Challenge**: Generate collision-free TDMA schedules for wireless networks where:
- Direct neighbors (1-hop) cannot transmit simultaneously
- Hidden terminals (2-hop) cannot transmit simultaneously
- Distant nodes (>2-hop) can reuse the same slot

**Key Insight**: This is a graph coloring problem where:
- Nodes = Radio devices
- Edges = Interference constraints (1-hop + 2-hop)
- Colors = Time slots

### 2. Algorithm Selection

**Why DSATUR?**
- Simple greedy coloring (largest degree first) produces suboptimal results
- DSATUR is a well-known heuristic that often produces better colorings
- It prioritizes nodes with most constraints (highest saturation)
- Good balance between quality and computational complexity

**Why Distance-2 Graph?**
- Direct 1-hop edges capture direct interference
- Adding 2-hop edges captures hidden terminal problem
- This matches the physical reality of wireless interference

### 3. Optimization Strategy

**Spatial Reuse**:
- Built into the algorithm by only constraining 2-hop neighbors
- Post-processing optimization tries to reassign nodes to earlier slots
- Slot compaction removes gaps to minimize total slots

**Heuristics Applied**:
1. DSATUR for initial coloring (quality-focused)
2. Iterative reassignment (efficiency-focused)
3. Slot compaction (optimization-focused)

### 4. Implementation Considerations

**Error Handling**:
- JSON parsing validation
- Coordinate format validation
- Conflict verification after optimization

**Extensibility**:
- Configurable radio range
- Modular algorithm components
- Clear separation of concerns

**Performance**:
- Efficient graph operations using NetworkX
- O(V + E) complexity for graph building
- Polynomial time for coloring (heuristic, not exponential)

## Test Results

### Test Scenario: 16 Nodes in 4×4 Grid

**Configuration**:
- 16 nodes in a 900m × 900m grid (300m spacing)
- Radio range: 500m
- Grid pattern: [0,0] to [900,900]

**Results**:
- **Total Slots**: 9 unique time slots
- **Conflict Status**: Verified conflict-free
- **Spatial Reuse**: Enabled (e.g., Node_01, Node_04, Node_13, Node_16 all use Slot 8)

**Analysis**:
- With 500m range and 300m spacing, each node can communicate with neighbors in adjacent cells
- The 2-hop constraint creates a dense conflict graph
- 9 slots is reasonable for this topology (theoretical minimum depends on graph structure)
- Spatial reuse is clearly demonstrated by corner nodes sharing slots

## Part 2: EMANE Integration (Bonus Approach)

### Overview

Part 2 involves integrating the Python scheduler with EMANE (Extendable Mobile Ad-hoc Network Emulator) for physical simulation.

### Proposed Architecture

```
Python Scheduler (Brain) → Schedule Matrix → XML/ProtoBuf → EMANE (Engine)
                                                              ↓
                                                         Virtual Network
                                                              ↓
                                                    Packet Drop/Permit Logic
```

### Implementation Approach

1. **EMANE Installation**:
   - Install EMANE on Linux or via Docker container
   - Configure TDMA Radio Model XML profiles
   - Define slot duration (1ms), frame structure, and frequencies

2. **Schedule Integration Bridge**:
   - Convert Python schedule matrix to EMANE-compatible format
   - Generate XML or ProtoBuf schedule events
   - Inject schedule into EMANE via control channel

3. **Verification**:
   - EMANE drops packets when node transmits outside its assigned slot
   - Packets are permitted when node transmits in its assigned slot
   - Monitor packet delivery to validate schedule correctness

### Key Challenges

- **Synchronization**: Ensuring EMANE nodes are time-synchronized
- **Format Conversion**: Mapping Python matrix to EMANE schedule format
- **Real-time Updates**: Handling dynamic schedule changes
- **Debugging**: Verifying packet behavior matches schedule

### Recommended References

- [EMANE TDMA BDCE Model Guide](https://emane.io/tdma-radio-model)
- EMANE Documentation for schedule event formats
- NetworkX Documentation for graph algorithms

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

## Future Enhancements

1. **Dynamic Scheduling**: Support for mobile nodes with changing topology
2. **Multi-frequency**: Extend to frequency division multiplexing
3. **Priority-based Scheduling**: Assign slots based on traffic priority
4. **Machine Learning**: Use ML to predict optimal slot assignments
5. **Visualization**: GUI for schedule visualization and topology display

## Conclusion

This TDMA scheduler successfully implements:
- ✅ Distance-2 graph coloring for interference avoidance
- ✅ DSATUR algorithm for efficient coloring
- ✅ Spatial reuse optimization
- ✅ Conflict-free schedule generation
- ✅ CLI interface with JSON input
- ✅ Specified output format (Slot × Node matrix)

The system provides a solid foundation for Part 2 EMANE integration and demonstrates understanding of wireless networking constraints and graph algorithms.

## Contact

For questions about this project, please contact: muthu@vaanmegam.net

---

**Project completed for Vaan Megam Networks Internship Application**

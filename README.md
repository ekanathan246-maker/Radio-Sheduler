TDMA Schedule Planner

This project assigns recurring transmission slots to a set of wireless radios. It builds a communication graph from node coordinates, derives the two-hop interference constraints, and uses graph coloring to produce a schedule. The same Node-to-Slot assignment can be exported as an EMANE TDMA schedule.

Scheduling model

Each input radio is a graph node. Radios at or within the configured range (500 m by default) are connected by an edge. The scheduler then creates a conflict graph: radios connected directly, or connected through one common neighbor, must use different slots.

The scheduler compares First-Fit, Largest-Degree-First, and DSATUR coloring. It compacts each result by moving radios into earlier slots when that move preserves the conflict constraints, then selects the valid assignment with the fewest slots. Radios without a conflict can share a slot.

Coloring is a hard optimization problem, so these strategies are heuristics. The largest clique in the conflict graph gives a lower bound on the number of slots. When the schedule uses that many slots, the result is optimal for the modeled topology. A positive gap means a better schedule may exist.

Architecture

flowchart LR
    relay["Other relay"]
    redis[("Redis")]
    api["Go / Gin API"]
    mongo[("MongoDB")]
    react["React client"]

    relay -->|"idempotent LSN snapshot + publish"| redis
    redis -->|"Pub/Sub"| api
    api -->|"versioned WebSocket"| react
    react -->|"REST + secure cookies"| api
    api -->|"transaction: vote + outbox"| mongo
    api -->|"claim pending event"| redis
    api -->|"reconnect state"| react

Requirements

Python 3.9 or newer

Packages listed in requirements.txt

EMANE is needed only to load and run the generated schedule in an emulator

Install

python -m venv .venv

Activate the environment, then install the dependencies:

# Linux or macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Generate a schedule

Run the supplied 16-radio example from the repository root:

python run_demo.py --input sample_input.json --range 500 --output-dir outputs

The report includes the node assignments, slot matrix, strategy comparison, conflict counts, validation results, clique lower bound, and optimality gap. The command writes these files to outputs/:

File

Contents

result.json

Coordinates, graph edges, assignments, matrix, and summary metrics

metrics.json

Conflict, validation, slot reuse, and lower-bound metrics

schedule_matrix.csv

Binary Slot-by-Node matrix

benchmark.csv

Coloring strategy slot counts and runtimes for the input topology

tdma-schedule.xml

EMANE schedule generated from the selected assignment

communication_topology.svg

Direct radio links

distance2_conflict_graph.svg

Direct and two-hop conflicts

slot_colored_topology.svg

Topology with nodes colored by assigned slot

slot_occupancy.svg

Number of radios assigned to each slot

algorithm_comparison.svg

Slot count and runtime by coloring strategy

The CLI can also take coordinates directly:

python tdma_scheduler.py --coordinates '{"Node_01":[0,0],"Node_02":[300,0]}' --range 500

To compare the algorithms over sparse, dense, linear, hidden-terminal, isolated, grid, and seeded random topologies, including 25- and 50-radio cases, run:

python benchmark_scenarios.py --output outputs/scenario_benchmark.csv

EMANE

Node names ending in a number map to that EMANE NEM id (Node_01 maps to NEM 1). The XML generator rejects names without a numeric suffix and duplicate NEM ids. It also reads the generated XML back and checks that each NEM has the same slot as the Python assignment.

With the EMANE platform and radio model configured, deliver the generated schedule using:

emaneevent-tdmaschedule outputs/tdma-schedule.xml -i <event-device>

Inspect the TDMA scheduler accept and reject counters with emanesh. The configuration files and notes are in emane/. For the schedule format and EMANE-specific requirements, see the EMANE TDMA Radio Model guide.

Scope

Connectivity is modeled as a symmetric distance threshold. This project does not calculate propagation loss, traffic demand, link asymmetry, or per-slot payload capacity. The schedule guarantees the stated distance-2 graph constraint; it does not model every source of radio interference.

Source files

tdma_scheduler.py contains the graph construction, coloring, validation, metrics, and exporters.

run_demo.py runs the optimizer and writes its report and artifacts.

benchmark_scenarios.py runs the multi-topology comparison.

sample_input.json contains the 4-by-4 example topology.

test_scheduler.py and validation_tests.py contain the existing checks.

emane/ contains the sample platform, NEM, transport, and radio-model configuration.

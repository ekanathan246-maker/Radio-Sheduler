import json
import networkx as nx
from tdma_scheduler import TDMAScheduler

# Load coordinates
with open("sample_input.json", "r") as f:
    coordinates = json.load(f)

scheduler = TDMAScheduler(radio_range=500)

node_coords = scheduler.parse_coordinates(
    json.dumps(coordinates)
)

# Build graphs
comm_graph = scheduler.build_communication_graph(node_coords)
d2_graph = scheduler.build_distance2_graph(comm_graph)

# Find a large clique
clique = nx.approximation.max_clique(d2_graph)

print("\nCOLORING ANALYSIS")
print("=" * 50)

print("Nodes:", d2_graph.number_of_nodes())
print("Conflict edges:", d2_graph.number_of_edges())

print("\nLarge clique found:")
print(sorted(clique))
print("Clique size:", len(clique))

print("\nTherefore:")
print(f"Minimum possible slots >= {len(clique)}")

# Run your actual scheduler
assignments, matrix = scheduler.optimize_schedule(
    json.dumps(coordinates)
)

print("\nDSATUR + spatial reuse result:")
print("Slots used:", max(assignments.values()) + 1)

print("\nAssignments:")
for node in sorted(assignments):
    print(f"{node}: Slot {assignments[node]}")
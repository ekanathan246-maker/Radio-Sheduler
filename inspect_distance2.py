import json
from tdma_scheduler import TDMAScheduler

# Load coordinates
with open("sample_input.json", "r") as f:
    coordinates = json.load(f)

# Create scheduler
scheduler = TDMAScheduler(radio_range=500)

# Parse coordinates
node_coords = scheduler.parse_coordinates(
    json.dumps(coordinates)
)

# Build communication graph
comm_graph = scheduler.build_communication_graph(node_coords)

# Build Distance-2 graph
d2_graph = scheduler.build_distance2_graph(comm_graph)

print("\nDISTANCE-2 CONFLICT GRAPH")
print("=" * 50)

for node in sorted(d2_graph.nodes()):
    neighbors = sorted(d2_graph.neighbors(node))
    print(f"{node}: {neighbors}")

print("\nTOTAL NODES :", d2_graph.number_of_nodes())
print("TOTAL CONFLICT EDGES :", d2_graph.number_of_edges())
import json
from tdma_scheduler import TDMAScheduler

# Load input
with open("sample_input.json", "r") as f:
    coordinates = json.load(f)

# Create scheduler
scheduler = TDMAScheduler(radio_range=500)

# Build communication graph
graph = scheduler.build_communication_graph(
    scheduler.parse_coordinates(json.dumps(coordinates))
)

print("\nDIRECT COMMUNICATION LINKS")
print("=" * 40)

for node in sorted(graph.nodes()):
    neighbors = sorted(graph.neighbors(node))
    print(f"{node}: {neighbors}")

print("\nTOTAL NODES :", graph.number_of_nodes())
print("TOTAL LINKS :", graph.number_of_edges())
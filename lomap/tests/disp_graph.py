import yaml
import matplotlib.pyplot as plt
from lomap.classes import Model  # Assuming the `model.py` file is in the same directory
from lomap.classes.ts import Ts
import networkx as nx

# Load the YAML file using the Model class
# Load the YAML file using the Ts class
filename = "my_network.yaml"  # Path to your YAML file

try:
    # Load the transition system
    ts = Ts.load(filename)
except Exception as e:
    print(f"Error loading the YAML file: {e}")
    exit()

# Display graph details (optional)
print(f"Nodes: {list(ts.g.nodes(data=True))}")
print(f"Edges: {list(ts.g.edges(data=True))}")

# Visualize the graph using matplotlib
try:
    ts.visualize(edgelabel='weight', draw='matplotlib')
    plt.show()
except Exception as e:
    print(f"Error visualizing the graph: {e}")

plt.savefig("graph.png")
print("Graph saved as graph.png")






myvar=2
if myvar==1:
# Load the model
    try:
        model = Model.load(filename)
    except Exception as e:
        print(f"Error loading the YAML file: {e}")
        exit()

    # Check the graph details
    print(f"Model Name: {model.name}")
    print(f"Nodes: {list(model.g.nodes(data=True))}")
    print(f"Edges: {list(model.g.edges(data=True))}")

    # Visualize the graph
    pos = {node: data["location"] for node, data in model.g.nodes(data=True)}
    nx.draw(model.g, pos, with_labels=True, node_size=50, font_size=8, node_color="lightblue")
    plt.title(model.name)
    plt.show()
    plt.savefig("graph.png")
    print("Graph saved as graph.png")


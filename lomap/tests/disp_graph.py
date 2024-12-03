import yaml
import os
import matplotlib.pyplot as plt
from lomap.classes import Model  # Assuming the `model.py` file is in the same directory
from lomap.classes.ts import Ts
import networkx as nx
from lomap.classes.automata import Fsa
from lomap.algorithms import product
from lomap.algorithms.dijkstra import source_to_target_dijkstra
import numpy as np

# Load the YAML file using the Ts class
filename = "tests/my_network.yaml"  # Path to your YAML file
run_directory=os.getcwd()
file_path=os.path.join(run_directory, 'tests/my_network.yaml')
try:
    # Load the transition system
    ts = Ts.load(file_path)
except Exception as e:
    print(f"Error loading the YAML file: {e}")
    exit()

# Display graph details (optional)
print(f"Nodes: {list(ts.g.nodes(data=True))}")
print(f"Edges: {list(ts.g.edges(data=True))}")

# Visualize the graph using matplotlib
try:
    ts.visualize(edgelabel='weight', draw='matplotlib')
    plt.title("Transition System")  # Add title for clarity
    plt.savefig("graph.png")  # Save the first graph
    print("Graph saved as graph.png")
    plt.clf()  # Clear the current figure to avoid overlap
except Exception as e:
    print(f"Error visualizing the graph: {e}")

# Define the specification and create FSA automaton
spec = 'G((!r U (F g24 & F g40)) & X (F (r & X gr)))'
#spec= '  (gr && X (g13 && X (r && X (g13 && X gr))))'
#spec ='F (g12 && F g24) || F (g24 && F g12) && X (F r)'
fsa = Fsa()  # Create an Fsa object
fsa.from_formula(spec)

# Display FSA details
print(f"FSA Size: {fsa.size()}")

# Visualize the FSA
try:
    fsa.visualize(draw='matplotlib')
    plt.title("FSA Automaton")  # Add title for clarity
    plt.savefig("fsa2.png")  # Save the FSA graph
    print("FSA automaton saved as fsa.png")
    plt.clf()  # Clear the figure after saving
except Exception as e:
    print(f"Error visualizing the FSA automaton: {e}")


myvar2=2
if myvar2==2:
    pa=product.ts_times_fsa(ts,fsa)
    print(pa.size())
    pa.visualize(draw='matplotlib')
    plt.show()
    plt.title("PA Automaton")  # Add title for clarity
    plt.savefig("pa.png")  # Save the FSA graph
    plt.clf()  # Clear the figure after saving



# Extract initial and final states
init_state = list(pa.init)[0]  # Assuming a single initial state
final_states = list(pa.final)  # List of final states

if not final_states:
    print("No final states found in the product automaton.")
    exit()

# Find the optimal path using Dijkstra's algorithm
optimal_paths = []
optimal_costs = []

for final_state in final_states:
    try:
        # Compute the shortest path and its cost
        cost, path = source_to_target_dijkstra(
            G=pa.g, 
            source=init_state, 
            target=final_state, 
            weight_key='weight'
        )
        optimal_paths.append(path)
        optimal_costs.append(cost)
    except Exception as e:
        print(f"Error finding path to final state {final_state}: {e}")

# Find the path with the minimum cost
if optimal_costs:
    min_cost_index = optimal_costs.index(min(optimal_costs))
    optimal_path = optimal_paths[min_cost_index]
    print(f"Optimal Path: {optimal_path}")
    print(f"Optimal Cost: {optimal_costs[min_cost_index]}")
else:
    print("No feasible paths to final states found.")









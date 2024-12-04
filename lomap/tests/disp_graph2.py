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
file_path=os.path.join(run_directory, 'package.yaml')
file_path2=os.path.join(run_directory, 'my_network_directed.yaml')
try:
    # Load the transition system
    ts = Ts.load(file_path)
    ts2= Ts.load(file_path2)
    
    # fsa_pickup = Fsa(multi=False)
    # fsa_pickup.from_formula('F (pick1 & F (pick2 & F dropoff)) | F (pick2 & F (pick1 & F dropoff))')
    # fsa_pickup.save('fsa_pickup.yaml')
    # print('Saved FSA pick!')
    fsa_pickup = Fsa.load('fsa_pickup.yaml')
except Exception as e:
    print(f"Error loading the YAML file: {e}")
    exit()

packages = {
    'pick1' : 'G24',
    'pick2' : 'G40',
    'dropoff' : 'R'
}

for label, state in packages.items():
    ts2.g.node[state]['prop'].add(label)

def product_transition_data(current_state, next_state):
    '''Returns the default data to store for a transition of a product.

    Parameters
    ----------
    current_state, next_state: hashable
        The endpoint states of the transition.

    Returns
    -------
        Dictionary containing the data to be stored.
    '''
    ts_current, fsa_current = current_state
    ts_next, fsa_next = next_state

    ts_weight = ts2.g[ts_current][ts_next]['weight']
    fsa_weight = fsa_pickup.g[fsa_current][fsa_next]['weight']

    return {'weight': ts_weight + fsa_weight}

ts_prod = product.ts_times_fsa(ts2, fsa_pickup, get_transition_data=product_transition_data)
print('TS prod done!', ts_prod.size())

exit()

ts_prod=product.ts_times_ts((ts,ts2))
# Display graph details (optional)
print(f"Nodes: {list(ts_prod.g.nodes(data=True))}")
print(f"Edges: {list(ts_prod.g.edges(data=True))}")

# Visualize the graph using matplotlib
try:
    ts_prod.visualize(edgelabel='weight', draw='matplotlib')
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
    pa=product.ts_times_fsa(ts_prod,fsa)
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









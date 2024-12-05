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
import itertools as it

# Load the YAML file using the Ts class
filename = "tests/my_network.yaml"  # Path to your YAML file
run_directory=os.getcwd()
#file_path=os.path.join(run_directory, 'package.yaml')
file_path2=os.path.join(run_directory, 'tests/my_network_directed.yaml')
try:
    # Load the transition system
    #ts = Ts.load(file_path)
    ts2= Ts.load(file_path2)
    
    # fsa_pickup = Fsa(multi=False)
    # fsa_pickup.from_formula('F (pick1 & F (pick2 & F dropoff)) | F (pick2 & F (pick1 & F dropoff))')
    # fsa_pickup.save('fsa_pickup.yaml')
    # print('Saved FSA pick!')
    # fsa_pickup = Fsa.load('tests/fsa_pickup.yaml')
except Exception as e:
    print(f"Error loading the YAML file: {e}")
    exit()


print(f"Nodes: {list(ts2.g.nodes(data=True))}")
#print(f"Edges: {list(ts2.g.edges(data=True))}")

packages = [
    ('pick1', ['G24'], 2),
    ('pick2', ['G40'], 5),
]
dropoff = 'R'

def ts_product_packages(ts, packages, dropoff): #translate to math for final write up look at picture
    
    ts_prod = Ts(multi=False, directed=True)

    dim = len(packages)

    ts_init = next(iter(ts.init))
    ts_prod.init = [(ts_init, (0,) * dim)]
    
    # states of product
    for state in ts.g.nodes(data=False):
        print(state)
        for pick in it.product((0, 1), repeat=dim):
            ts_prod.g.add_node((state, pick))
            # node_name = str(state)  # Get the node name as a string
            # if node_name.startswith('G'):
            #     ts_prod.g.node[(state, pick)]['prop'] = node_name.lower()
            # elif node_name == 'R':
            #     ts_prod.g.node[(state, pick)]['prop'] = 'r'
            # else:
            ts_prod.g.node[(state, pick)]['prop'] = {}  # Default if no specific rule
    
    #  label the initial state with 'gr'
    ts_prod.g.node[(ts_init, (0,) * dim)]['prop'] = {'gr'}

    package_weights = np.array([pck[2] for pck in packages]) #changed pkg[] to pck[]
    # transitions of product
    for ts_current, ts_next, data in ts.g.edges(data=True):
        ts_weight = data['weight']
        for pick in it.product((0, 1), repeat=dim):
            pick_weight = ts_weight + np.dot(package_weights, pick)
            ts_prod.g.add_edge((ts_current, pick), (ts_next, pick), weight=pick_weight)
    
    for pick in it.product((0, 1), repeat=dim):
        for k in range(dim):
            if pick[k] == 0:
                next_pick = list(pick)
                next_pick[k] = 1
                next_pick = tuple(next_pick)
            locations = packages[k][1]
            pick_weight = np.dot(package_weights, next_pick)
            for state in locations:
                ts_prod.g.add_edge((state, pick), (state, next_pick), weight=pick_weight)
                # update labels for states where packages are picked up 
                ts_prod.g.node[(state, next_pick)]['prop'] = {packages[k][0]}
    
    ts_prod.g.add_edge((dropoff, (1,)*dim), (dropoff, (0,)*dim), weight=0)

    ts_prod.g.node[(dropoff, (0,)*dim)]['prop'] = {'r'}


    return ts_prod

ts_prod = ts_product_packages(ts2, packages, dropoff)

# print('is SC:', nx.is_strongly_connected(ts_prod.g)) # SANITY CHECK

# Display graph details (optional)


print(f"Nodes: {list(ts_prod.g.nodes(data=True))}")
ts_prod_init = next(iter(ts_prod.g.node))
print(ts_prod_init)
node_key = ('GR', (0, 0))
node_data = ts_prod.g.node[ts_prod_init].get('prop', set())  # Access the node's data
print(node_data)
#print(f"Edges: {list(ts_prod.g.edges(data=True))}")

# print('----------\n\n')

# for node, data in ts_prod.g.nodes(data=True):
#     print(f'Node: {node}, data: {data}')
# exit()

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
# spec = 'G((!r U (F pick1 & F pick2)) & X (F (r & X gr)))'
spec = '(F pick1 && F pick2)'
#spec= '  (gr && X (g13 && X (r && X (g13 && X gr))))'
#spec ='F (g12 && F g24) || F (g24 && F g12) && X (F r)'
fsa = Fsa(multi=False)  # Create an Fsa object
fsa.from_formula(spec)

# Display FSA details
print(f"FSA Size: {fsa.size()}")

# print(fsa)
# exit()

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
    pa = product.ts_times_fsa(ts_prod, fsa)
    print(pa.size(), ts_prod.size(), fsa.size())
    print(pa.directed, pa.multi)
    print(pa.init)
    print(pa.final)
    pa.visualize(draw='matplotlib')
    plt.show()
    plt.title("PA Automaton")  # Add title for clarity
    plt.savefig("pa.png")  # Save the FSA graph
    plt.clf()  # Clear the figure after saving
    print(f"Nodes: {list(pa.g.nodes(data=True))}")
    #print(f"Edges: {list(pa.g.edges(data=True))}")


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









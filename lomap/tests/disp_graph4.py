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
from mpl_toolkits.mplot3d import Axes3D
from itertools import permutations


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


#print(f"Nodes: {list(ts2.g.nodes(data=True))}")
#print(f"Edges: {list(ts2.g.edges(data=True))}")

packages = [
    ('pick1', ['G67'], 400),
    ('pick2', ['G27'], 3),
]
dropoff = 'R'

def ts_product_packages(ts, packages, dropoff): #translate to math for final write up look at picture
    
    ts_prod = Ts(multi=False, directed=True)

    dim = len(packages)

    ts_init = next(iter(ts.init))
    ts_prod.init = [(ts_init, (0,) * dim)]
    
    # states of product
    for state in ts.g.nodes(data=False):
        #print(state)
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

    positions_3d = {}
    for state, attrs in ts_prod.g.nodes(data=True):  # Unpack node and its attributes
        if isinstance(state, tuple) and len(state) == 2:  # Ensure the state is a tuple (state, pick)
            graph_state, pick = state  # Unpack the state tuple
            #print("Graph State:", graph_state, "Pick:", pick)
            
            # Ensure the pick is a tuple (binary vector)
            if isinstance(pick, tuple):
                x, y = ts.g.node[graph_state]['location']  # Extract 2D location from the original graph
                z = int("".join(map(str, pick)), 2)  # Convert binary vector to an integer (Z-axis level)
                #print(f"3D Position for ({graph_state}, {pick}): ({x}, {y}, {z})")
                
                # Store the 3D position in the dictionary
                positions_3d[(graph_state, pick)] = (x, y, z)

    return ts_prod, positions_3d

def visualize_3d_ts(ts_prod, positions_3d):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot nodes
    for (node, coord) in positions_3d.items():
        x, y, z = coord
        ax.scatter(x, y, z, color='red', s=50)
        ax.text(x, y, z, f"{node}", fontsize=8)

    # Plot edges
    for (u, v, data) in ts_prod.g.edges(data=True):
        x_coords = [positions_3d[u][0], positions_3d[v][0]]
        y_coords = [positions_3d[u][1], positions_3d[v][1]]
        z_coords = [positions_3d[u][2], positions_3d[v][2]]
        ax.plot(x_coords, y_coords, z_coords, color='blue', alpha=0.6)

    # Label axes
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")
    ax.set_title("3D Transition System with FSA States")

    plt.show()

def visualize_3d_pa(ts_prod, positions_3d, highlight_edges):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Convert the highlight edges to a set for quick lookup
    for i in range(len(highlight_edges)-1):
        node1=highlight_edges[i]
        node2=highlight_edges[i+1]
        
        
    highlight_set = set((highlight_edges[i][0], highlight_edges[i+1][0]) for i in range(len(highlight_edges)-1))
    #print(highlight_set)
    final_nodes=set(final_node[0] for final_node in highlight_edges)
    # Plot nodes
    for (node, coord) in positions_3d.items():
        x, y, z = coord
        #print(node)
        if node in final_nodes: 
            ax.scatter(x, y, z, color='red', s=50)
            ax.text(x, y, z, f"{node}", fontsize=8)

    # Plot edges
    for (u, v, data) in ts_prod.g.edges(data=True):
        x_coords = [positions_3d[u][0], positions_3d[v][0]]
        y_coords = [positions_3d[u][1], positions_3d[v][1]]
        z_coords = [positions_3d[u][2], positions_3d[v][2]]
        
        # Check if the edge is in the highlight list
        if (u, v) in highlight_set:
            #print(u,v)
            ax.plot(x_coords, y_coords, z_coords, color='green', alpha=0.8, linewidth=2)
        #else:
            
            #ax.plot(x_coords, y_coords, z_coords, color='blue', alpha=0.6)

    # Label axes
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")
    ax.set_title("3D Transition System with FSA States")

    plt.show()


def generate_formula(packages, final_states=["r", "gr"]):
    """
    Generate a formula for all permutations of pick states and final states.
    
    Parameters:
        picks (list): List of pick states (e.g., ["pick1", "pick2", "pick3"]).
        final_states (list): List of final states (e.g., ["r", "gr"]).
    
    Returns:
        str: The generated formula.
    """

    picks = [pkg[0] for pkg in packages]
    # Generate all permutations of the pick states
    permutations_list = permutations(picks)
    
    # Construct the formula for each permutation
    sub_formulas = []
    for perm in permutations_list:
        # Count total nested "F (" layers
        open_parentheses = len(perm)  # Total number of opening parentheses
        
        # Build nested formula
        nested_formula = " & F ( ".join(perm) + " & F ( " + " & F ".join(final_states)
        
        # Close all opened parentheses
        nested_formula += ")" * open_parentheses  # Correctly close the parentheses
        
        # Wrap in "F()"
        sub_formulas.append(f"F({nested_formula})")
    
    # Join all sub-formulas with OR
    return " || ".join(sub_formulas)

# Example Usage

formula = generate_formula(packages)
print(formula)

ts_prod, positions_3d = ts_product_packages(ts2, packages, dropoff)
visualize_3d_ts(ts_prod,positions_3d)

# print('is SC:', nx.is_strongly_connected(ts_prod.g)) # SANITY CHECK

# Display graph details (optional)


#print(f"Nodes: {list(ts_prod.g.nodes(data=True))}")
ts_prod_init = next(iter(ts_prod.g.node))
#print(ts_prod_init)
node_key = ('GR', (0, 0))
node_data = ts_prod.g.node[ts_prod_init].get('prop', set())  # Access the node's data
#print(node_data)
#print(f"Edges: {list(ts_prod.g.edges(data=True))}")

# print('----------\n\n')

# for node, data in ts_prod.g.nodes(data=True):
#     print(f'Node: {node}, data: {data}')
# exit()

# Visualize the graph using matplotlib
try:
    ts2.visualize(edgelabel='weight', draw='matplotlib')
    plt.title("Transition System")  # Add title for clarity
    plt.savefig("graph.png")  # Save the first graph
    print("Graph saved as graph.png")
    plt.clf()  # Clear the current figure to avoid overlap
except Exception as e:
    print(f"Error visualizing the graph: {e}")

# Define the specification and create FSA automaton
#spec = 'G((!r U (F pick1 & F pick2)) & X (F (r & X gr)))'
#spec = 'F( pick1 & F (pick2 & F (r & F gr))) || F( pick2 & F (pick1 & F (r & F gr)))'
#spec= 'F(F pick1 & F pick2) & F (r & F gr)'
#spec = ''
#spec = '(F pick1 && F pick2)'
#spec= '  (gr && X (g13 && X (r && X (g13 && X gr))))'
#spec ='F (g12 && F g24) || F (g24 && F g12) && X (F r)'
spec = generate_formula(packages)
print(spec)
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
    #print(pa.directed, pa.multi)
    #print(pa.init)
    #print(pa.final)
    #pa.visualize(draw='matplotlib')
    #plt.show()
    #plt.title("PA Automaton")  # Add title for clarity
    #plt.savefig("pa.png")  # Save the FSA graph
    #plt.clf()  # Clear the figure after saving
    #print(f"Nodes: {list(pa.g.nodes(data=True))}")
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
    visualize_3d_pa(ts_prod,positions_3d,optimal_path)
else:
    print("No feasible paths to final states found.")













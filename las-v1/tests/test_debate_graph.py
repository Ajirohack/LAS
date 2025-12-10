import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../las_core")))

try:
    from agents.hierarchical_graph import graph
    print("Graph compiled successfully.")
    
    # Print graph nodes to verify structure
    print("Graph nodes:", graph.nodes.keys())
    
    # Optional: Visualize graph if possible (requires graphviz)
    # print(graph.get_graph().draw_ascii())
    
except Exception as e:
    print(f"Failed to compile graph: {e}")
    sys.exit(1)

import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../las_core")))

try:
    from agents.hierarchical_graph import graph
    print("Graph compiled successfully.")
    
    # Print graph nodes to verify structure
    nodes = graph.nodes.keys()
    print("Graph nodes:", nodes)
    
    if "AdHocWorker" in nodes:
        print("SUCCESS: AdHocWorker found in graph.")
    else:
        print("FAILURE: AdHocWorker NOT found in graph.")
        sys.exit(1)
        
except Exception as e:
    print(f"Failed to compile graph: {e}")
    sys.exit(1)

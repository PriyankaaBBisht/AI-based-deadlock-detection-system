
import networkx as nx

class DeadlockDetector:
    def __init__(self):
        self.rag = nx.DiGraph()

    def add_process(self, process):
        self.rag.add_node(process, type='process')

    def add_resource(self, resource):
        self.rag.add_node(resource, type='resource')

    def request_resource(self, process, resource):
        self.rag.add_edge(process, resource)

    def assign_resource(self, resource, process):
        self.rag.add_edge(resource, process)

    def detect_deadlock(self):
        try:
            cycles = list(nx.simple_cycles(self.rag))
            for cycle in cycles:
                if any(self.rag.nodes[n]['type'] == 'process' for n in cycle):
                    return cycle
            return None
        except:
            return None

    def resolve_deadlock(self, cycle):
        for node in cycle:
            if self.rag.nodes[node]['type'] == 'process':
                self.rag.remove_node(node)
                break

    def clear_graph(self):
        self.rag.clear()

from collections import defaultdict
import os

NEG = '-'

class dir_graph:
    def __init__(self):
        '''
        Graph is a dictionary of sets, with key = node 1 and value = set of nodes that node 1 is directed to (ie. G=(V,E)).
        Nodes is a set of all nodes (ie. all literals, positive and negative treated as separate entities)
        '''
        self.graph = defaultdict(set)
        self.nodes = set()

    # performance: O(1)
    def add_edge(self, l1, l2):
        '''
        Adds an edge to the graph.
        If literals are not yet present in the graph, new nodes are added as well.
        '''
        self.graph[l1].add(l2)
        self.nodes.add(l1)
        self.nodes.add(l2)

    # performance: O(|V|+|E|)
    def dfs(self, visited, stack, scc):
        '''
        Loops through all nodes to conduct a depth-first search
        '''
        for node in self.nodes:
            if node not in visited:
                self.dfs_visit(visited, node, stack, scc)

    def dfs_visit(self, visited, node, stack, scc):
        '''
        Recursive depth-first search that is used to create 
        the stack for Kosaraju's Algorithm later on and 
        identify Strong Connected Components.

        The stack is created such that the node/literal with the 
        lowest end time is at the bottom of the stack.
        '''
        if node not in visited:
            visited.append(node)
            for neighbour in self.graph[node]:
                self.dfs_visit(visited, neighbour, stack, scc)
            stack.append(node)
            scc.append(node)
        return visited

    # performance: O(|V|+|E|)
    def transpose(self):
        '''
        Returns a transposed graph. 
        
        Directions in a transposed graph are the opposite of those in the original graph.
        '''
        transposed_graph = self.__class__()
        for node in self.graph:
            for neighbour in self.graph[node]:
                transposed_graph.add_edge(neighbour, node)
        return transposed_graph
    
    # performance: O(|V|+|E|) for a directed graph G=(V,E)
    def get_sccs(self):
        '''
        Implements Kosaraju's Algorithm to find all Strongly Connected Components.

        We first get the stack of nodes obtained from depth-first search of the original tree, 
        whereby this stack has nodes with earliest end time at the bottom.

        Next, we transpose the graph, and go through the entire stack node by node, 
        conducting a depth-first search at each node if that node has not been visited. 
        A Strong Connected Component is identified when all nodes involved in the current round
        of depth-first search have been visited. This repeats until all nodes in the stack have 
        been popped.
        '''
        stack = []
        sccs = []
        self.dfs([], stack, [])
        t_g = self.transpose()
        visited = []
        while stack:
            node = stack.pop()
            if node not in visited:
                scc = []
                scc.append(node)
                t_g.dfs_visit(visited, node, [], scc)
                sccs.append(scc)
        return sccs

### END OF DIR_GRAPH CLASS

def double_neg(literal):
    '''
    Formats literals appropriately when double negatives are present
    eg. --3 => 3
    '''
    return literal.replace((NEG+NEG), '')


def contradicts(sccs):
    '''
    Checks for contradiction in a list of Strongly Connected Components.

    A contradiction occurs when within a Strongly Connected Component, 
    there exists both A and not A. 
    eg. there is a contradiction in the SCC [1, 2, -1], while there is no contradiction in the SCC [1, 2, 3]
    '''
    for scc in sccs:
        for l1 in scc:
            for l2 in scc[scc.index(l1):]:
                if l2 == double_neg(NEG + l1):
                    return True
    return False

def get_values(variables, sccs):
    '''
    Returns the values of each variable assuming that the original CNF was satisfiable
    '''
    result = [0] * len(variables)
    for scc in sccs:
        for l in scc:
            if l[0] == NEG:
                result[int(l[1:])-1] = '0'
            else:
                result[int(l)-1] = '1'
    
    return result
        

def parse_cnf(f):
    '''
    Takes a CNF file object as argument and parses the cnf file 
    to return a list of variables and the CNF formula
    '''
    variables = []
    formula = []
    current_clause = []
    for line in f.readlines():
        line = line.strip()
        if line[:2] == 'p ':
            _, __, var_num, ___ = line.split(' ')
            variables = [str(i) for i in range(1, int(var_num)+1)]
        elif line[:2] != 'c ':
            clause = line.split(' ')
            k = 0
            for j in range(len(clause)):
                if clause[j] == '0':
                    formula.append(current_clause + clause[k:j])
                    k = j+1
                    current_clause = []
            current_clause = clause[k:]

    return variables, formula


def main():
    # parse file
    f = open(f"{os.path.dirname(os.path.relpath(__file__))}\\test.cnf", 'r')
    variables, formula = parse_cnf(f)

    # create implication graph based on CNF formula
    graph = dir_graph()
    for clause in formula:
        if len(clause) == 2:
            l1, l2 = clause
            graph.add_edge(double_neg(NEG+l1), l2)
            graph.add_edge(double_neg(NEG+l2), l1)
        else:
            graph.add_edge(double_neg(NEG+clause[0]), clause[0])

    # identify all Strongly Connected Components in the graph
    sccs = graph.get_sccs()

    # check for contradictions
    if not contradicts(sccs):
        # output both satisfiability result and the variable values
        result = get_values(variables, sccs)
        print("SATISFIABLE")
        print(' '.join(result))
    else:
        # output satisfiability result
        print("NOT SATISFIABLE")


main()
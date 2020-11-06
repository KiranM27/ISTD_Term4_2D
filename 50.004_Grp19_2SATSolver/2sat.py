'''
Some .cnf test cases:

1. 5 variable CNF UNSAT by Xin Yi
p cnf 5 8
1 2 0
-2 -3 0
2 -4 0
1 -5 0
5 -4 0
3 -1 0
1 4 0
-3 4 0

2. 5 variable CNF SAT by Xin Yi
p cnf 5 7
1 2 0
-2 -3 0
2 -4 0
1 -5 0
5 -4 0
3 -1 0
1 4 0

3. 5 variable CNF from https://www.geeksforgeeks.org/2-satisfiability-2-sat-problem/
p cnf 5 7
1 -2 0
2 -1 0
3 -2 0
5 -3 0
-4 -5 0
3 4 0
4 -3 0
'''

from collections import defaultdict
import os
import time

NEG = '-'

class dir_graph:
    def __init__(self):
        '''
        Graph is a dictionary of sets, with key = node 1 and value = set of nodes that node 1 is directed to (ie. G=(V,E)).
        Nodes is a set of all nodes (ie. all literals, positive and negative treated as separate entities)
        '''
        self.graph = defaultdict(set)
        self.nodes = set()

    def add_edge(self, l1, l2):
        '''
        Adds an edge to the graph.
        If literals are not yet present in the graph, new nodes are added as well.
        '''
        self.graph[l1].add(l2)
        self.nodes.add(l1)
        self.nodes.add(l2)

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
        earliest end time is at the bottom of the stack.

        The deepest node is the first one to be appended to scc. 
        '''
        if node not in visited:
            visited.append(node)
            for neighbour in self.graph[node]:
                self.dfs_visit(visited, neighbour, stack, scc)
            stack.append(node)
            scc.append(node)
        return visited

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
        while len(stack) > 0:
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

def get_values(var_num, sccs):
    '''
    Returns the values of each variable assuming that the original CNF was satisfiable
    '''
    result = ['0'] * var_num
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
    var_num = '0'
    formula = []
    current_clause = []
    for line in f.readlines():
        line = line.strip()
        if line[:2] == 'p ':
            _, __, var_num, ___ = line.split(' ')
        elif line[:2] != 'c ':
            clause = line.split(' ')
            k = 0
            for j in range(len(clause)):
                if clause[j] == '0':
                    formula.append(current_clause + clause[k:j])
                    k = j+1
                    current_clause = []
            current_clause = clause[k:]
    return int(var_num), formula


def main():
    start_time = time.time()
    # parse file
    f = open(f"{os.path.dirname(os.path.relpath(__file__))}\\test.cnf", 'r')
    var_num, formula = parse_cnf(f)
    algo_start_time = time.time()
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
        result = get_values(var_num, sccs)
        print("SATISFIABLE")
        print(' '.join(result))
    else:
        # output satisfiability result
        print("NOT SATISFIABLE")
    end_time = time.time()
    print(f'Time taken from opening: {(end_time - start_time)*1000:.5f}')
    print(f'Time taken for algo: {(end_time - algo_start_time)*1000:.5f}')
    print(f'{(end_time - start_time)*1000:.5f} {(end_time - algo_start_time)*1000:.5f}')


main()
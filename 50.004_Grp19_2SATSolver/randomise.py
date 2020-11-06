import random
import time
import os

# in_data = ['c horn? no', 'c forced? no', 'c mixed sat? no', 'c clause length = 3', 'c', 'p cnf 8  4', '1 2 0', '3 -4 0', '-5 -6 0', '-8 7 0']

def parseCNF(f):
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

def SAT2solver(clauses, varNo, noOfTries):
    # set all variables to false
    cnf_arr = [-1] * varNo
    sat = True
    for _ in range(noOfTries):
        sat = True
        for clause in clauses:
            var1 = int(clause[0])
            var2 = int(clause[1])
            # get both variables in a clause
            first = var1 * cnf_arr[abs(var1) - 1]
            second = var2 * cnf_arr[abs(var2) - 1]
            
            # checking for sat
            if (first < 1) and (second < 1):
                sat = False
                # clause is not sat
                # randomly choose 1 variable in the clause to flip sign
                n = random.randint(0, 1)
                if n == 0:
                    cnf_arr[abs(var1) - 1] = random.choice([-1, 1])
                else:
                    cnf_arr[abs(var2) - 1] = random.choice([-1, 1])
                break
    if sat:
        print ("satisfied")
        return cnf_arr
    else:
        print ("not sat / tired of flipping coins")
        return None


f = open(f"{os.path.dirname(os.path.relpath(__file__))}\\test.cnf", 'r')
varNo, clauses = parseCNF(f)
start_time = time.time()
print(SAT2solver(clauses, varNo, 10))
end_time = time.time()
print(f'Time taken: {(end_time - start_time)*1000:.5f}ms')


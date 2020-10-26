package sat;

import immutable.EmptyImList;
import immutable.ImList;
import sat.env.Bool;
import sat.env.Environment;
import sat.formula.Clause;
import sat.formula.Formula;
import sat.formula.Literal;
import sat.formula.NegLiteral;
import java.util.Iterator;

import sat.formula.Clause;
import sat.formula.Formula;
import sat.formula.Literal;
import sat.formula.NegLiteral;

/**
 * A simple DPLL SAT solver. See http://en.wikipedia.org/wiki/DPLL_algorithm
 */

/*
        If there are no clauses, the formula is trivially satisfiable.
        If there is an empty clause, the clause list is unsatisfiable fail and backtrack.
        (use empty clause to denote a clause evaluated to FALSE based on the variable binding in the environment)
        Otherwise, find the smallest clause (by number of literals).
            o If the clause has only one literal, bind its variable in the environment so that the
            clause is satisfied, substitute for the variable in all the other clauses (using the
            suggested substitute() method), and recursively call solve().
            o Otherwise, pick an arbitrary literal from this small clause:
                 First try setting the literal to TRUE, substitute for it in all the clauses, then
                solve() recursively.
                 If that fails, then try setting the literal to FALSE, substitute, and solve() recursively
        */

        /* important observations:
        1) in a cnf, if one of the clauses is false, then entire formula is always false
        2) in a clause, if one literal is true, the entire clause can be removed
        3) in a clause, if one literal is false, the literal can be removed */

public class SATSolver {
    /**
     * Solve the problem using a simple version of DPLL with backtracking and
     * unit propagation. The returned environment binds literals of class
     * bool.Variable rather than the special literals used in clausification of
     * class clausal.Literal, so that clients can more readily use it.
     * 
     * @return an environment for which the problem evaluates to Bool.TRUE, or
     *         null if no such environment exists.
     */
    public static Environment solve(Formula formula) {
        if (formula.getSize() == 0) return new Environment();
        Environment returnEnv = solve(formula.getClauses(), new Environment());
        return returnEnv;
    }

    /**
     * Takes a partial assignment of variables to values, and recursively
     * searches for a complete satisfying assignment.
     * 
     * @param clauses
     *            formula in conjunctive normal form
     * @param env
     *            assignment of some or all variables in clauses to true or
     *            false values.
     * @return an environment for which all the clauses evaluate to Bool.TRUE,
     *         or null if no such environment exists.
     */
    private static Environment solve(ImList<Clause> clauses, Environment env) {
        Iterator iterator = clauses.iterator();
        Environment newEnv = env;
        if(clauses.isEmpty()){
            return env;
        }

        Clause minClause = null;
        Clause curClause;
        ImList<Clause> unitClauses = new EmptyImList<Clause>();
        int minimum = (int)Double.POSITIVE_INFINITY;
        while (iterator.hasNext()) {
            curClause = (Clause)iterator.next();
            if (curClause != null && curClause.isEmpty()) {
                // fail => backtrack
                return null;
            }
            if (curClause != null && curClause.isUnit()) {
                for (Clause c:unitClauses) {
                    if (c.chooseLiteral().negates(curClause.chooseLiteral())) {
                        // fail if 2 unit clauses negate each other
                        return null;
                    }
                }
                unitClauses = unitClauses.add(curClause);
            }
            else
                if (curClause != null && unitClauses.isEmpty() && curClause.size() <= minimum) {
                minimum = curClause.size();
                minClause = curClause;
            }
        }
        ImList clauseList = clauses;

        if (!unitClauses.isEmpty()) {
            for (Clause c:unitClauses) {
                Literal l = c.chooseLiteral();
                newEnv = newEnv.put(l.getVariable(), l instanceof NegLiteral ? Bool.FALSE : Bool.TRUE);
                clauseList = substitute(clauseList, l);
            }
            return solve(clauseList, newEnv);
        } else if (minClause != null && !minClause.isUnit()){ // not unit clause case
                Literal literal = minClause.chooseLiteral();
                newEnv = env.putTrue(literal.getVariable()); //first try by putting positive literal in temp env with existing env as base, if fail(NULL) backtrack and try negative, if fail(backtrack to env) then that clause will always fail = no way to pass
                clauseList = substitute(clauses, literal instanceof NegLiteral ? literal.getNegation() : literal); //create new clause list, removing all the positive versions of the literal chosen
                newEnv = solve(clauseList, newEnv);
                if (newEnv == null) { // if newenv is null, then try negative ver.
                    newEnv = env.putFalse(literal.getVariable());  //retry newenv with false case when true case fails
                    clauseList = substitute(clauses, literal instanceof NegLiteral ? literal : literal.getNegation());
                    return solve(clauseList, newEnv);
                }
                return newEnv;
            }

        return env;
    }

    /**
     * given a clause list and literal, produce a new list resulting from
     * setting that literal to true
     *
     * @param clauses
     *            , a list of clauses
     * @param l
     *            , a literal to set to true
     * @return a new list of clauses resulting from setting l to true
     */
    private static ImList<Clause> substitute(ImList<Clause> clauses,
                                             Literal l) {
        Iterator iterator = clauses.iterator();
        Clause clause;
        ImList returnList = new EmptyImList();
        while (iterator.hasNext()) {
            clause = (Clause)iterator.next();
            if (clause != null) {
                returnList = returnList.add(clause.reduce(l));
            }
        }

        return returnList;
    }
}
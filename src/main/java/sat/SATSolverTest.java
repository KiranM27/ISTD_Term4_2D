package sat;

/*
import static org.junit.Assert.*;

import org.junit.Test;
*/

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

import sat.env.Environment;
import sat.env.Variable;
import sat.formula.Literal;
import sat.formula.PosLiteral;
import sat.formula.Formula;
import sat.formula.Clause;



public class SATSolverTest {
    Literal a = PosLiteral.make("a");
    Literal b = PosLiteral.make("b");
    Literal c = PosLiteral.make("c");
    Literal na = a.getNegation();
    Literal nb = b.getNegation();
    Literal nc = c.getNegation();
	
	// TODO: add the main method that reads the .cnf file and calls SATSolver.solve to determine the satisfiability
    public static void main(String[] args) throws IOException {
        String currentLocation = System.getProperty("user.dir");
        String directory;
        if (args.length!=0) directory = args[0];
        else directory = currentLocation + "\\code2d\\src\\main\\java\\sat\\s8Sat.cnf";
        File newFile;
        Scanner thisScanner = null;
        try {
            newFile = new File(directory);
            thisScanner = new Scanner(newFile);
            String[] newLineArray = thisScanner.nextLine().split("\\s+");
            while (newLineArray[0].equals("c") || newLineArray[0].equals("C")) {
                newLineArray = thisScanner.nextLine().split("\\s+");
            }
            Integer variableCount = Integer.parseInt(newLineArray[2]);
            Formula newFormula = new Formula();
            Clause newClause = new Clause();
            String newLine;
            while (thisScanner.hasNextLine()) { //to prevent thisScanner from over reading and creating error
                newLine = thisScanner.nextLine();
                if (newLine.length() == 0) { //if the newline is empty, read the next line in .cnf file
                    continue;
                }
                newLineArray = newLine.split("\\s+");
                for (String element: newLineArray) {
                    if (element.equals("")) continue; //if element is an empty String, move on to next element
                    if (element.equals("0")) { //if the element is a 0, means that its time to add the clause in, and restart a new clause
                        newFormula = newFormula.addClause(newClause);
                        newClause = new Clause();
                        continue;
                    } //if not, its a valid number
                    Integer newNumber = Integer.parseInt(element); //the element in Integer format
                    Literal newLiteral = PosLiteral.make(Integer.toString(Math.abs(newNumber)));//makes literal instance
                    if (newNumber >0) newClause = newClause.add(newLiteral);
                    else newClause = newClause.add(newLiteral.getNegation());
                }
            }
            System.out.println("SAT solver starts!!!");
            long started = System.nanoTime();
            Environment solution = SATSolver.solve(newFormula);
            long time = System.nanoTime();
            long timeTaken= time - started;
            System.out.println("Time:" + timeTaken/1000000.0 + "ms");
            if (solution == null) {
                System.out.println("Not satisfiable");
            }
            else {
                System.out.println("Satisfiable");
                FileWriter newWriter = new FileWriter("BoolAssignment.text");
                newWriter.write("Solution to the boolean equation\n");
                for (Integer i = 1;i<=variableCount;i++) {
                    Variable check = new Variable(i.toString());
                    newWriter.write( i.toString() + ":" +solution.get(check).toString() +"\n");
                }
                newWriter.close();
            }
        } finally {
            if (thisScanner != null) thisScanner.close();
        }
    }

    public void testSATSolver1(){
    	// (a v b)
    	Environment e = SATSolver.solve(makeFm(makeCl(a,b)));
/*
    	assertTrue( "one of the literals should be set to true",
    			Bool.TRUE == e.get(a.getVariable())
    			|| Bool.TRUE == e.get(b.getVariable())	);
*/
    }


    public void testSATSolver2(){
    	// (~a)
    	Environment e = SATSolver.solve(makeFm(makeCl(na)));
/*
    	assertEquals( Bool.FALSE, e.get(na.getVariable()));
*/
    }

    private static Formula makeFm(Clause... e) {
        Formula f = new Formula();
        for (Clause c : e) {
            f = f.addClause(c);
        }
        return f;
    }

    private static Clause makeCl(Literal... e) {
        Clause c = new Clause();
        for (Literal l : e) {
            c = c.add(l);
        }
        return c;
    }



}
package sat;


import sat.env.Environment;
import sat.env.Variable;

public class myClass {
    public static void main(String args[]) {
        Environment thisEnv = new Environment();
        Variable c = new Variable("c");
        System.out.println(thisEnv.get(c));
    }
}

from z3 import *

a, b, c = Ints("x y z")
x, y, z = Bools("a b c")
q = BitVec("q", 16)
s = Solver()
expr = And(
    Or([x, y, z]),
    Or(x, And(y, z)),    
    q > 5
)
print(expr.sexpr())

bv_solver = Then('simplify', 'bit-blast', 'tseitin-cnf', 'simplify')

print(bv_solver(expr))

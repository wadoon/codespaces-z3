#!/usr/bin/python3
from io import StringIO

import yaml, sys
from z3 import *
import random
import argparse

rand = random.Random()

cli_parser = argparse.ArgumentParser("gengoals.py",
                                     description="""This scripts reads a specification from a yaml, and uses to the 
                                     result field (and z3) to generate goals. The given yaml will be updated """)
cli_parser.add_argument("--num", "-n", action='store', default=3, type=int)
cli_parser.add_argument("file", help="YAML file", metavar="FILENAME")

s = Solver()


def make_var(x, t):
    if t == 'int':
        return Int(x)
    else:
        return Bool(x)


def rand_eq(decl):
    if is_int(decl):
        return decl == rand.randint(-100, 100)
    else:  # is_bool(decl)
        return decl == BoolVal(1 == rand.randint(0, 1))


def yaml_value(val):
    if is_int(val):
        return int(str(val))
    else:
        bool(str(val))


if __name__ == '__main__':
    ns = cli_parser.parse_args()
    num = ns.num

    with open(ns.file) as fh:
        spec = yaml.safe_load(fh)

    result = spec['result']
    print(f"# generated {num} goals for result {result} ")

    inputs = {x: make_var(x, t) for x, t in spec['inputs'].items()}
    outputs = {x: make_var(x, t) for x, t in spec['outputs'].items()}
    all = {}
    all.update(inputs)
    all.update(outputs)

    eq = parse_smt2_string(f'(assert {result})', sorts={}, decls=all)
    s.add(eq)

    for round in range(num):
        assum = [rand_eq(decl) for decl in inputs.values()]
        print("Assume:", assum)
        ans = s.check(assum)
        if ans == sat:
            m = s.model()
            goal = {x: yaml_value(m[d]) for x, d in all.items()}
            print("Result: ", goal)
            spec['goals'].append(goal)
        else:
            print("# unexpected unsat!")
            sys.exit(1)

    dump = StringIO()
    yaml.safe_dump(spec, dump)
    with open(ns.file, 'w') as fh:
        fh.write(dump.getvalue())

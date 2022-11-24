#!/usr/bin/python3

import sys
import yaml
from typing import Dict, List
from z3 import *

# Read the specification given via stdin
spec = yaml.safe_load(sys.stdin)
inputs: Dict[str, str] = spec['inputs']
outputs: Dict[str, str] = spec['outputs']
goals: List[Dict[str, str]] = spec['goals']
layers = int(spec['layers'])
width = int(spec['width'])

s = Solver()

# TODO Encode the given specification into SMT constraints

ans = s.check()

if ans == sat:
    model = s.model()
    # TODO synthesize the function given the SMT model
    fn = "true"
    print(f"Synthesize function is:\n{fn}") # last line is "true"
else:
    print('not realizable')

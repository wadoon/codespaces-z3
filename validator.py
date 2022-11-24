#!/usr/bin/python3

import argparse
import io
import subprocess
import time
from pathlib import Path
from statistics import mean, stdev, median

import yaml

# STATISTICS
ERRORS = 0
SUCCESS = 0
FAILURE = 0
TIMINGS = []


def validate(filename: Path, ns: argparse.Namespace):
    global ERRORS, SUCCESS, FAILURE, TIMINGS

    fsynth = Path(ns.fsynth).absolute()
    fsynth_prefix = ns.fsynth_prefix
    filter = ns.filter

    cli = f"cat {filename.absolute()} | {filter} | {fsynth_prefix} python3 {fsynth} | tail -n 1"
    print("Execute: ", cli)
    start = time.process_time()
    status, out = subprocess.getstatusoutput(cli)
    stop = time.process_time()

    if status != 0:
        ERRORS = ERRORS + 1
        return

    print("Took: ", stop - start, "ms")
    TIMINGS.append(stop - start)

    print("Solution: ", out)
    check(filename, out)


NOT_REALIZABLE = 'not realizable'


def check(filename, last_line):
    global SUCCESS, FAILURE
    last_line = last_line.strip()
    import z3
    with open(filename) as fh:
        spec = yaml.safe_load(fh)
    result: str = spec['result']

    if result == NOT_REALIZABLE:
        if last_line == NOT_REALIZABLE:
            SUCCESS += 1
        else:
            FAILURE += 1
        return
    elif last_line == NOT_REALIZABLE:
        FAILURE += 1
        return

    smt = io.StringIO()
    for x, t in list(spec['inputs'].items()) + list(spec['outputs'].items()):
        type = t.capitalize()
        smt.write(f"(declare-const {x} {type})\n")

    smt.write(f"(assert (not (= {result} {last_line})))")

    # SMT test
    # print(smt.getvalue())

    s = z3.Solver()
    s.from_string(smt.getvalue())
    ans = s.check()
    print("Result: ", ans)
    if ans == z3.unsat:
        SUCCESS += 1
    else:
        print("Model:", s.model())
        FAILURE += 1


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser("validator.py",
                                         description="""This scripts validates a given solution against a set of function specifications.""")
    cli_parser.add_argument("--fsynth", help="path to the fsynth.py", metavar="fsynth.py")
    cli_parser.add_argument("--fsynth-prefix", help="programs to sandbox fsynth", metavar="commands", default="")
    cli_parser.add_argument("--filter", help="Command or script to filter the YAML input", metavar="command",
                            default="cat")
    cli_parser.add_argument("files", action='append', help="YAML files", metavar="FILENAME")

    ns = cli_parser.parse_args()

    for fil in ns.files:
        validate(Path(fil), ns)

    print("Statistics:")
    print("ERRORS:", ERRORS)
    print("SUCCESS:", SUCCESS)
    print("FAILURE:", FAILURE)
    if len(TIMINGS) <= 1:
        std = 0
    else:
        std = stdev(TIMINGS)
    print(f"Timings: mean={mean(TIMINGS)} std={std} median={median(TIMINGS)}")

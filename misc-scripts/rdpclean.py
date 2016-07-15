#!/usr/bin/env python
from __future__ import print_function

import os
from subprocess import check_output, CalledProcessError
from shlex import split as shplit
import re
import argparse

"""
Look for xrdp processes with no parent or child processes. Check for Z state.
"""

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='List or kill xrdp processes, '
                                     'particularly those with no child processes.')
    ckq = parser.add_mutually_exclusive_group()  # cannot kill quietly
    ckq.add_argument('--kill-singletons', dest='kill', action='store_true',
                       help='Kill xrdp processes with no child processes')
    ckq.add_argument('--quiet', '-q', action='store_true',
                       help='Just list the singletons')


    parser.add_argument('--debug', action='store_true',
                       help='Show debug output')
    
    ARGS = parser.parse_args()

    if not (ARGS.kill or ARGS.quiet or ARGS.debug):
        print("xrdp process list:\n(Use --help for option list.)\n")
    
    procs_cmd = 'ps --no-heading ax -o ppid,pid,command'
    # trim, split from the left twice only
    proc_cmd = "ps --no-heading --pid={pid} -o state,stat"
    # trim, split
    
    pids = set()
    with os.popen(procs_cmd) as procs:
        for p in procs:
            p = p.strip()
            ppid, pid, cmd = re.split("\s+", p, maxsplit=2)
            if cmd == '/usr/sbin/xrdp':
                pids.add(pid)
            if ARGS.debug:
                print(p)
        # Get pid(s)
        if ARGS.debug:
            print(pids)
    
    
    parents = set()
    # Check the process states
    for pid in pids:
        proc = check_output(shplit(proc_cmd.format(pid=pid)))
        proc = proc.strip()
        state, stat = re.split(b"\s+", proc, maxsplit=1)
        state = state.decode('utf8')
        stat = stat.decode('utf8')
        if not (ARGS.quiet or ARGS.kill):
            if "Z" in state or "Z" in stat:
                print(pid, "is a zombie!")
            else:
                print(pid, "has state", state)
    
    # Check for processes with those pids as ppids (is a parent)
    with os.popen(procs_cmd) as procs:
        for p in procs:
            p = p.strip()
            ppid, cpid, cmd = re.split("\s+", p, maxsplit=2)
            if ppid in pids:
                if not (ARGS.quiet or ARGS.kill):
                    print(ppid, "is a parent of", cpid, cmd)
                parents.add(ppid)
    
    nonparents = pids - parents
    
    if nonparents:
        if not (ARGS.quiet or ARGS.kill):
            print(" ".join(nonparents),
                    "is not a parent" if len(nonparents) == 1
                    else "are not parents")
        elif ARGS.quiet:
            print(" ".join(nonparents))
        elif ARGS.kill:
            try:
                check_output(['kill'] + list(nonparents))
            except CalledProcessError as e:
                print(e.output)
                print("Could not kill at least some of the processes", 
                      ", ".join(nonparents))

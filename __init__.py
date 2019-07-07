#!/usr/bin/python

import lldb
import os

def rel_path_to(file):
  return os.path.join(os.path.dirname(__file__), file)

scripts = [
  "lldo.py",
]

for script in scripts:
  lldb.debugger.HandleCommand("command script import %s" % rel_path_to(script))

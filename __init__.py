#!/usr/bin/python

import lldb
import fblldb
import os

def rel_path_to(file):
  return os.path.join(os.path.dirname(__file__), file)

def run(command):
  lldb.debugger.HandleCommand(command)


# define handy aliases
run("command alias alias command alias")  # define an alias called `alias` that can be used to define an alias
run("alias reload_lldbinit command source ~/.lldbinit")
run("alias history command history")
run("alias import command script import")
run("alias shell platform shell")

run("alias ps expression -O -l Swift --")   # like po but use Swift

# TODO: (re)set target language

scripts = [
  "swift_helper/load_swift.py",
  "loadimage.py",
]

for script in scripts:
  run("import %s" % rel_path_to(script))

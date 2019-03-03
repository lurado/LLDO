import lldb
import re
import textwrap
import os
import glob

def __lldb_init_module(debugger, internal_dict):
  commands = [
    psource_folder,
    load_actions
  ]
  for function in commands:
    function.__doc__ = re.sub("([^\n])\n([^\n])", "\g<1> \g<2>", textwrap.dedent(function.__doc__))
    debugger.HandleCommand("command script add -f {0}.{1} {1}".format(__name__, function.__name__))


def source_folder(result):
  result = lldb.SBCommandReturnObject()
  lldb.debugger.GetCommandInterpreter().HandleCommand("source info", result)
  source_info = result.GetOutput()
  if not source_info.startswith("Lines found in"):
    result.SetError("Unable to determine source location. Did you stop at a breakpoint in your project?")
    return

  pattern = re.compile("\[.+?\): (/.*?/)[^/]*\n")
  match = pattern.search(source_info)
  if match is None:
    result.SetError("Could not derive project path from source info.")
    return

  path = match.group(1)
  return path

def psource_folder(debugger, args, ctx, result, _):
  """
  Prints the source folder path of the current breakpoint.

  This command is only able to derive the source folder location while the application is paused at a breakpoint in the application.
  That means every breakpoint you set in your sources in Xcode will work.
  Pausing the application via Debug > Pause will NOT work.
  """
  path = source_folder(result)
  if not result.Succeeded():
    return

  result.AppendMessage(path)

def load_actions(debugger, args, ctx, result, _):
  """
  Loads LLDB actions from a folder.

  Usage: load_actions <path>

  Creates an LLDB alias for every `.lldb` file in the given directory, named after the file, that executes that file.
  For example a `login.lldb` file will create a `login` alias that executes the `login.lldb` file.
  
  The path may be absolute or relative.
  If it's relative, the command tries to resolve it from the source location of the current breakpoint.
  Say your breakpoint is in `/MyProject/Source/AppDelegate.swift` and your actions are in `/MyProject/lldb_actions`, you need to pass `../lldb_actions`.
  """
  path = args

  if not os.path.isabs(path):
    project_path = source_folder(result)
    if not result.Succeeded():
      return
    path = os.path.join(project_path, path)

    actions = glob.glob(os.path.join(path, "*.lldb"))
    if not actions:
      result.SetError("No actions found in {0}".format(path))
      return

    for action_path in actions:
      print("Loading {0}".format(action_path))
      action_name = os.path.splitext(os.path.basename(action_path))[0]
      alias = "command alias {0} command source {1}".format(action_name, action_path)
      debugger.HandleCommand(alias)

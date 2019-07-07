import lldb
import os
import re
import textwrap
import glob

kNoResult = 0x1001

def __lldb_init_module(debugger, internal_dict):
  commands = [
    lldo,
    load_lldo_actions,
    load_swift_file,
    load_swift_runtime
  ]
  for function in commands:
    function.__doc__ = re.sub("([^\n])\n([^\n])", "\g<1> \g<2>", textwrap.dedent(function.__doc__))
    debugger.HandleCommand("command script add -f {0}.{1} {1}".format(__name__, function.__name__))


def _rel_path_to(file):
  return os.path.join(os.path.dirname(__file__), file)


def _load_swift_file(path, ctx, result):
  with open(os.path.expanduser(path)) as f:
    contents = f.read()

  options = lldb.SBExpressionOptions()
  options.SetLanguage(lldb.eLanguageTypeSwift)
  error = ctx.frame.EvaluateExpression(contents, options).error

  if error.fail and error.value != kNoResult:
    result.SetError(error)


def loaded_libs():
  result = lldb.SBCommandReturnObject()
  lldb.debugger.GetCommandInterpreter().HandleCommand("image list", result)
  pattern = re.compile(".*?([^/]+\.dylib)$")
  lines = [l.strip() for l in result.GetOutput().split("\n")]
  matches = filter(lambda x: x is not None, map(lambda l: pattern.match(l), lines))
  return map(lambda m: m.group(1), matches)


def source_folder(result):
  source_info_result = lldb.SBCommandReturnObject()
  lldb.debugger.GetCommandInterpreter().HandleCommand("source info", source_info_result)
  source_info = source_info_result.GetOutput()
  if source_info is None or not source_info.startswith("Lines found in"):
    result.SetError("Unable to determine source location. Did you stop at a breakpoint in your project?")
    return

  pattern = re.compile("\[.+?\): (/.*?/)[^/]*\n")
  match = pattern.search(source_info)
  if match is None:
    result.SetError("Could not derive project path from source info.")
    return

  path = match.group(1)
  return path

def stopped_at_source_location():
  return source_folder(lldb.SBCommandReturnObject()) is not None


def load_swift_file(debugger, path, ctx, result, _):
  """
  Loads definitions from a `.swift` file.
  
  Usage: load_swift_file </path/to/file.swift>
  
  Load the contents of file at the given path and evaluates it in the context of the current debugger context.
  However LLDB expression evaluation is scoped. 
  So definitions from one expression evaluation don't carry over to the next one.
  That means any types or functions defined in your Swift files won't be available to you after you loaded them.
  But there are two ways to work around this.
  First: Everything that's prefixed with `$` will be added to the global scope and be available after the evaluation ended.
  Unfortunately Swift does not allow function or type names to start with a `$` (outside LLDB) and throws many errors which makes working in Xcode rather unpleasant and pretty much pointless.
  Which leaves option two: Put everything into extensions as they also outlive their direct evaluation scope.
  """

  _load_swift_file(path, ctx, result)


def lldo(debugger, args, ctx, result, _):
  """
  Loads LLDO

  Usage: lldo [<actions_path>]

  Loading LLDO means two things:

  1. Loading the Swift helpers. For a detailed description of the available helpers check the documentation at https://lurado.github.io/LLDO/
  2. Loading the LLDO actions from `actions_path`. See the help of `load_lldo_actions` for details.
  """

  load_swift_runtime(debugger, None, ctx, result, None)
  if not result.Succeeded():
    return

  files = glob.glob(os.path.join(_rel_path_to("lldo_helpers"), "*.swift"))

  for file in files:
    _load_swift_file(_rel_path_to(file), ctx, result)
    if not result.Succeeded():
      return
  
  print("LLDO successfully loaded.")

  path_given = len(args) > 0
  if stopped_at_source_location() or path_given:
    load_lldo_actions(debugger, args, ctx, result, None)
  else:
    print("Not stopped at a source location, not loading actions.")


def load_lldo_actions(debugger, args, ctx, result, _):
  """
  Loads LLDO actions from a folder.

  Usage: load_lldo_actions [<path>]

  Creates an LLDB alias for every `.swift` file in the given directory, named after the file, that executes that file.
  For example a `login.swift` file will create a `login` alias that executes the `login.swift` file.
  
  The path may be absolute or relative.
  If it's relative, the command tries to resolve it from the source location of the current breakpoint.
  Say your breakpoint is in `/MyProject/MyApp/AppDelegate.swift` and your actions are in `/MyProject/lldo_actions`, you need to pass `../lldo_actions`.
  If the execution is stopped outside the application source, for example by hitting the pause button, the resolution of relative paths won't work.

  The default value for `path` is `lldo_actions`.
  """
  path = args
  if not path:
    path = "lldo_actions"

  if not os.path.isabs(path):
    project_path = source_folder(result)
    if not result.Succeeded():
      result.SetError("Unable to load actions from: {0}.".format(path))
      return
    path = os.path.abspath(os.path.join(project_path, path))

  actions = glob.glob(os.path.join(path, "*.swift"))
  if not actions:
    result.SetError("No actions found in: {0}.".format(path))
    return

  for action_path in actions:
    print("Loading {0}...".format(action_path))
    action_name = os.path.splitext(os.path.basename(action_path))[0]
    alias = "command alias {0} load_swift_file {1}".format(action_name, action_path)
    debugger.HandleCommand(alias)


def load_swift_runtime(debugger, args, ctx, result, _):
  """
  Loads the Swift runtime.

  Since all helpers are written in Swift, the Swift runtime is required to run them.
  However the runtime might not be loaded into LLDB yet, if the application hasn't been stopped in a Swift stack frame.
  Or the runtime will not be loaded at all in pure Objective-C applications.

  This command loads all necessary Swift .dylibs into the current process.
  Already loaded libs will be skipped.

  Attention: Only works in the Simulator!

  To our knowledge it's not possible to transfer a library onto the device and load it from there.
  That means pure Objective-C apps need to add a single unused Swift file, to bundle the Swift runtime into the app.
  It will then be auto loaded during startup.
  """

  # inspired by:
  #   - https://stackoverflow.com/questions/24715891 
  #   - https://stackoverflow.com/questions/51578701

  libs = [
    "libswiftCore.dylib",
    "libswiftDarwin.dylib",
    "libswiftObjectiveC.dylib",
    "libswiftRemoteMirror.dylib",
    "libswiftSwiftOnoneSupport.dylib",
    "libswiftsimd.dylib",
    "libswiftDispatch.dylib",
    "libswiftCoreFoundation.dylib",
    "libswiftCoreGraphics.dylib",
    "libswiftFoundation.dylib",
    "libswiftCoreData.dylib",
    "libswiftAssetsLibrary.dylib",
    "libswiftModelIO.dylib",
    "libswiftos.dylib",
    "libswiftMetal.dylib",
    "libswiftNetwork.dylib",
    "libswiftCoreImage.dylib",
    "libswiftQuartzCore.dylib",
    "libswiftUIKit.dylib"
  ]

  path = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/swift/iphonesimulator/"
  libs_to_load = [path + l for l in libs if l not in loaded_libs()]
  
  for l in libs_to_load:
    error = lldb.SBError()
    ctx.process.LoadImage(lldb.SBFileSpec(l, False), error)
    if not error.Success():
      result.SetError(str(error) + ": " + l)
      return

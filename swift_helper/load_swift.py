import lldb
import os
import re
import textwrap

kNoResult = 0x1001

def __lldb_init_module(debugger, internal_dict):
  commands = [
    load_swift,
    lldo,
    load_swift_runtime
  ]
  for function in commands:
    function.__doc__ = re.sub("([^\n])\n([^\n])", "\g<1> \g<2>", textwrap.dedent(function.__doc__))
    debugger.HandleCommand("command script add -f {0}.{1} {1}".format(__name__, function.__name__))


def rel_path_to(file):
  return os.path.join(os.path.dirname(__file__), file)

def load_swift_file(path, ctx, result):
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


def load_swift(debugger, path, ctx, result, _):
  """
  Loads definitions from a `.swift` file.
  
  Usage: load_swift </path/to/file.swift>
  
  Load the contents of file at the given path and evaluates it in the context of the current debugger context.
  However LLDB expression evaluation is scoped. 
  So definitions from one expression evaluation don't carry over to the next one.
  That means any types or functions defined in your Swift files won't be available to you after you loaded them.
  But there are two ways to work around this.
  First: Everything that's prefixed with `$` will be added to the global scope and be available after the evaluation ended.
  Unfortunately Swift does not allow function or type names to start with a `$` (outside LLDB) and throws many errors which makes working in Xcode rather unpleasant and pretty much pointless.
  Which leaves option two: Put everything into extensions as they also outlive their direct evaluation scope.
  """

  load_swift_file(path, ctx, result)


def lldo(debugger, args, ctx, result, _):
  """
  Loads the LLDO Swift helpers.

  For a detailed description of the available helpers check the documentation at https://github.com/lurado/LLDO/tree/master/docs/
  """

  load_swift_runtime(debugger, args, ctx, result, None)

  files = [
    "NSObject+LLDO.swift",
    "UIViewController+LLDO.swift",
    "UIView+LLDO.swift"
  ]

  for file in files:
    load_swift_file(rel_path_to(file), ctx, result)
    if not result.Succeeded():
      return


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
  That means pure Objective-C apps need to add a single unuses Swift file, to bundle the Swift runtime into the app.
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

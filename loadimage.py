import lldb
import re
import textwrap

def __lldb_init_module(debugger, internal_dict):
  commands = [
    load_image,
    proofimage
  ]
  for function in commands:
    function.__doc__ = re.sub(r"([^\n])\n([^\n])", "\1 \2", textwrap.dedent(function.__doc__))
    debugger.HandleCommand("command script add -f {0}.{1} {1}".format(__name__, function.__name__))


def command_options():
  options = lldb.SBExpressionOptions()
  options.SetLanguage(lldb.eLanguageTypeObjC)
  return options

def transfer_image(path, process, result):
  """
  Transfers an image from the host to the debugged process.

  The image at the given path is read from the host, 
  the data is transferred into the debugged process
  and an `UIImage` is created. 

  Returns the memory address of the created `UIImage`.
  """
  imageBytes = open(path, mode='rb').read()
  imageBytesLength = len(imageBytes)
  if not (imageBytes or imageBytesLength):
    result.SetError("Could not load image.")
    return

  frame = process.GetThreadAtIndex(0).GetSelectedFrame()

  imageBufferStartingAddress = frame.EvaluateExpression("(void *)malloc({0})".format(imageBytesLength), command_options()).value
  
  error = lldb.SBError()
  numberOfWrittenBytes = process.WriteMemory(int(imageBufferStartingAddress, 16), imageBytes, error)
  if not error.Success() or numberOfWrittenBytes != imageBytesLength:
    result.SetError("Transferring image to process memory failed: {0}".format(error))
    return

  imageViewCommand = "(UIImage *)[UIImage imageWithData:(NSData *)[NSData dataWithBytesNoCopy:{0} length:{1} freeWhenDone:YES]]".format(imageBufferStartingAddress, imageBytesLength)
  imageAddress = frame.EvaluateExpression(imageViewCommand, command_options()).value
  return imageAddress


def load_image(debugger, args, ctx, result, _):
  """
  Creates an `UIImage` from a file on the host.

  Usage: load_image </path/to/image.png>

  Loads the image at the given path into the debugged process and creates an `UIImage`.
  This instance is assigned to a LLDB variable (e.g. `$3`) a that can be used freely.
  Unfortunately LLDB variables can't be used in Swift expressions (see https://stackoverflow.com/a/40267006/588314 for details).
  As a workaround the object at the memory address can be casted into an `UIImage` with `UIImage.at(<memory address>)`.
  """
  imagePath = args

  imageAddress = transfer_image(imagePath, ctx.process, result)
  if not result.Succeeded():
    return

  debugger.HandleCommand("expression -l ObjC -- (UIImage *) {0}".format(imageAddress))


def proofimage(debugger, args, ctx, result, _):
  """
  Loads an image and adds it as overlay to the root view.

  Usage: proofimage </path/to/image.png>
  """
  imagePath = args

  imageAddress = transfer_image(imagePath, ctx.process, result)

  if not result.Succeeded():
    return

  frame = ctx.process.GetThreadAtIndex(0).GetSelectedFrame()
  overlayCommand = "(UIImageView *)[(UIView *)[UIView root] overlay:(UIImage *){0}]".format(imageAddress)
  imageViewAddress = frame.EvaluateExpression(overlayCommand, command_options()).value
  result.AppendMessage("(UIImageView *){0}".format(imageViewAddress))

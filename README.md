# TODO
- publish (LLDO - Lurado LLDB helpers)
- Documentation
  - Rework README
- create issue: breakpoints.py
  - https://gist.github.com/kastiglione/d7fc5b3b3ebab1248333b858591e06b0#file-lldbinit
  - https://youtu.be/9Io2_W1iDLQ?t=1250
  - https://github.com/kastiglione/lldb-helpers
  - https://www.dropbox.com/s/9sv67e7f2repbpb/lldb-commands-map.png?dl=0
  -> create bif => breakpoint if/condition (-F -> lldb-helpers)
  -> create baction => breakpoint action (-o -> youtube)
  -> add docu on how to write scripts


# LLDO - LLDB helpers by Lurado

Heavily inspired by [kastiglione](https://gist.github.com/kastiglione/d7fc5b3b3ebab1248333b858591e06b0), you should check out his [talk](https://www.youtube.com/watch?v=9Io2_W1iDLQ).

## Installation

Clone this repo and add 

```
command script import /path/to/LLDO
```

to your `~/.lldbinit`

## Usage

TODO: how to try it out: run example Project (does not really work :-/ -> need to break in a Swift frame)

### ⚠️ Debugging Only!

This purpose of this code is **only** to make debugging and development easier. 
Do **NOT** include it in your releases.

### LLDB Commands

#### Handy Aliases

TODO: transfer list from `__init__.py`

#### Commands

| Command | Description |
|---------|-------------|
| load_image | Loads an image from your local hard drive into the process |
| proofimage | Display an image from your local hard drive as fullscreen overlay |

### Swift Helper

While LLDB commands are nice, helpers in real code are way more powerful, convenient, easier to write, test and maintain.

TODO:
  - Examples
  - How to Extend
    - develop extensions in Xcode, save to a file
    - call `load_swift <path>` to your own file)

#### Usage

While in LLDB type `lldo` to make the helpers available. 
If you find yourself doing it in every session, you can also create a symbolic breakpoint in `UIApplicationMain`, enter `lldo` as 'Debugger Command' and check the 'Automatically Continue' checkbox.
You might even right click that breakpoint and move it to your user so it's available in all your projects.

⚠️ ObjC Only Projects on a Device

To be able to use the Swift helpers in an ObjC only project on a device, you need to bundle the Swift runtime:

  - Add a single Swift file
  - Do **not** create a bridging header
  - make sure you `import UIKit`

TODO: See #??? for details

#### How it Works 

TODO:
  - reference video (https://www.youtube.com/watch?v=9Io2_W1iDLQ)
  - rough rundown

## Development

1. `reload_lldbinit`
1. run command
1. GOTO 1

## Other LLDB Nuggets

- Check out [Chisel](https://github.com/facebook/chisel)
- use `call` instead of `expr[ession]`
- use `j[ump] +N` instead of `thread jump --by N`

## LICENSE

MIT - see LICENSE file

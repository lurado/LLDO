
# 🐲 LLDO - LLDB helpers by Lurado

## Motivation

While LLDB commands are nice, helpers in Swift are _way_ more convenient, easier to write, test and maintain.

This project has been heavily inspired by [@kastiglione](https://twitter.com/kastiglione). You should check out his [talk](https://www.youtube.com/watch?v=9Io2_W1iDLQ).


## Try It

1. Clone this repo
2. Open the `LLDOSwiftHelper.xcodeproj` Xcode project.
4. Run in the Simulator and wait to hit the breakpoint in `AppDelegate.applicationDidBecomeActive`.
5. Start messing around. For example:

```
# Highlights
po UIView.current.highlightLayoutMargins(depth: 2)
po UIView.current.highlightLayoutMargins(false, depth: .max)

# Poking around
po UIButton.first()
po UIView.current.all(UILabel.self)
po UIView.grep("Pass")
po UIView.find(byAccessibilityID: "username_input")
po UIView.current.tree().filter { $0.isHidden }

# Changing stuff
po UITextField.first()?.enterText("mail@company.com")
po UISwitch.first()?.slide()
po UIButton.first()?.tap()

# Automation
load_actions lldb_actions/
login

# For the rest we need additional LLDO's LLDB commands
# Hint: You can use drag and drop the path from Finder 📎
command script import </path/to>/LLDO

# Load a reference design to check for abberations
proofimage </path/to>/LLDO/LLDOSwiftHelper/demo_reference.png
po UIImageView.at(<memory address>).removeFromSuperview()
# OR
po UIView.root.overlay()
```


## Installation

Add the following line to your `~/.lldbinit`:

```
command script import /path/to/LLDO
```

This loads LLDO's LLDB commands by default and makes them available in every project. Whenever you are in LLDB you can type `lldo` to load the Swift helper methods.

If you want to _always_ have them available, create a symbolic breakpoint in `UIApplicationMain`, enter `lldo` as _Debugger Command_ and check the _Automatically continue_ checkbox. You might even right click that breakpoint and move it to your user so it's automatically available in all your projects.


### ⚠️ Objective-C Only Projects on a Device

To be able to use the Swift helpers in an Objective-C only project on a device, you need to bundle the necessary Swift runtime libraries:

1. Add a single Swift file
1. Do **not** create a bridging header
1. make sure you `import UIKit`

See `(lldb) help load_swift_runtime` for details.


## Documentation

### Swift Helpers

The documentation of the Swift helpers lives at [lurado.github.io/LLDO](https://lurado.github.io/LLDO).

### LLDB Commands
#### Aliases

| Alias | Description|
|-------|------------|
| `ps` | Like `po` but always use Swift. _Very_ handy when using the Swift helpers in an Objective-C context. |
| `alias` | Create a LLDB command alias: `alias <name> <command>`. |
| `history` | Shows the LLDB command history. Like the Bash command. |
| `import` | Load a Python script: `import </path/to/script.py>`. |
| `shell` | Execute a shell command, e.g. `shell ls -la`. |
| `reload_lldbinit` | What it says on the tin. Very handy when developing commands. |

#### Commands

| Command | Description |
|---------|-------------|
| `lldo` | Load the Swift helpers. |
| `load_swift` | Load a Swift source code file: `load_swift <path>` |
| `load_swift_runtime` | Load the Swift runtime. Necessary in Objective-C only projects. |
| `load_actions` | Loads LLDB scripts from a folder: `load_actions <path>` |
| `load_image` | Creates a `UIImage` from a file on your local hard drive: `load_image </path/to/image>` |
| `proofimage` | Displays an image from your local hard drive as semi-transparent fullscreen overlay to compare your layout with a reference design: `proofimage </path/to/image>` |
| `psource_folder` | Prints the source folder path of the current breakpoint. |

Use the built in `help` command for further details, e.g. `(lldb) help load_image`.

## Automation

The Swift Helpers and LLDB commands can be combined into little, powerful scripts to automate tasks you do repeatedly.
For example you can create UI automations to, say, log you in or bring your app into a specific state.

To create a script just put a sequence of LLDB commands in a `.lldb` file and call `load_actions <path>` with the folder path containing the file.
`load_actions` will automatically load all `.lldb` files in that folder and create actions base on their filenames: 
A `login.lldb` will result in a `login` action.

The `<path>` parameter for `load_actions` may be relative. 
However, in order for that to work, the breakpoint at which the application is stopped must be in the application source. 
 Just hitting the pause icon and trying to use a relative path won't work.

If you want to share actions with your team _and_ always have them available, you need to create a shared symbolic breakpoint in your application that loads the actions with a relative path:

1. Create a symbolic breakpoint
    - For Swift projects:
        - Symbol: `@objc <module>.<AppDelegate>.init`, e.g. (`@objc LLDO.AppDelegate.init`)
    - For Objective-C projects:
        - Symbol: `main`
        - Module: `<module>`, e.g. (`LLDO`)
1. Add a _Debugger Command_ action: `load_actions <relative/path>`, e.g. `load_actions LLDOSwiftHelper/lldb_actions`
1. Check _Automatically continue_
1. Right click the created breakpoint and select _Share_


## Write Your Own

### Swift Helpers

1. Develop them like any other code in a Xcode project
1. Run an application and pause it to start LLDB
1. Use the [`load_swift` command](#commands) to load the file
1. Call your helpers
1. GOTO 1 (unfortunately loading a files twice in a LLDB session results in duplicate symbols)

### LLDB commands

1. Create a Python script containing the command code
1. Use the [`import` alias](#aliases) in your `.lldbinit` to activate it
1. Run an application and pause it to start LLDB
1. `reload_lldbinit`
1. Run your command
1. Modify as needed
1. GOTO 4 (reloading and re-defining commands in a LLDB session works just fine)


## ⚠️ Debugging Only!

This purpose of this project is **only** to make debugging and development easier. 
Do **NOT** include it in your releases.


## Random LLDB Tidbits

- Check out [Chisel](https://github.com/facebook/chisel)
- use `j[ump] +N` instead of `thread jump --by N`


## LICENSE

MIT - see LICENSE file

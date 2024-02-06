# Update Checker for Blender Add-Ons Published on GitHub

This is a Python code template for implementing scheduled update checks against your GitHub repo hosting your Blender add-on.

You need Blender 3.3 or newer for this code to work.

Help, support, updates and anything else: [https://github.com/gusztavj/Blender-Add-On-GitHub-Update-Checker](https://github.com/gusztavj/Blender-Add-On-GitHub-Update-Checker)

## Legal Stuff

### Copyright

This add-on has been created by [T1nk-R (https://github.com/gusztavj/)](https://github.com/gusztavj/).

#### MIT License

Copyright (c) 2023-2024, T1nk-R (Gusztáv Jánvári)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### Commercial Use

I would highly appreciate to get notified via [janvari.gusztav@imprestige.biz](mailto:janvari.gusztav@imprestige.biz) about any such usage. I would be happy to learn this work is of your interest, and to discuss options for commercial support and other services you may need.

### Disclaimer

This add-on is provided as-is. Use at your own risk. No warranties, no guarantee, no liability, no matter what happens. Still I tried to make sure no weird things happen:

* This module is intended to check a GitHub repository of your choice to get information on the latest published version of whatever is contained in the given repository.
* **CAUTION.** This module requires an access token to the GitHub repository. The token is stored as clean text.
  * Make sure to create a personal token restricted to only access the repos you want everyone to be able to access restricted to access code only restricted to only read code.
  * Note that your personal token expires in a year (or sooner if you decided so). Update check won't work afterwards. To not  disturb your users, such errors are ignored silently. Make sure to change the code and update the token to a newer one before the current expires.
* **CAUTION.** When people use your add-on using this module, they can generate many requests against your repo, and your GitHub rate limit may be exceeded. To overcome this, be sure to set a proper frequency, but don't forget, users will have access to your source code and may change it.
* This template assumes you use [semantic versioning](http://semver.org/) for your add-on. See [Release Tagging Rules](#release-tagging-rules) for more information.

You may learn more about legal matters on page [https://github.com/gusztavj/Blender-Add-On-GitHub-Update-Checker](https://github.com/gusztavj/Blender-Add-On-GitHub-Update-Checker).

## How Does It Work?

Whereas creating a Python package to provide this update checking service in an easily consumable form would sound good, installing Python modules for and by Blender add-ons is a bit cumbersome, and although possible, it requires lot of code and Blender shall be run in Administrator privileges for the operation to succeed.

For that reason I decided to publish this as a code template.

The core of the template is an operator (a subclass of `bpy.types.Operator`) and it's `execute()` function. You'll call this operator from the `execute()` function(s) of your operator(s) to perform the check. In the `draw()` methods of your classes (like `bpy.types.Operator` or `bpy.types.Panel` subclasses) you'll be able to get and display update information.

The add-on saves some data with your add-on in the add-on's preferences (your subclass of `bpy.types.AddOnPreferences`) and will use it as a cache. To not exceed your API rate limit, the add-on will only check your GitHub repo for updates in every couple of days (as specified in `checkFrequencyDays`) and save the information. For subsequent requests it will serve the information cached this way. In addition to saving your repo, this solution also guarantees speed, as checking the repo may take a few moments, making the UI sluggish.

A side effect of this approach is that the first check for updates only happens when the user performs the first action coupled with an `execute()` function calling the update checker operator. Similarly, check for update may only happen when the user performs an operation. The reason for this is that you cannot modify add-on settings, such as the properties of your subclass of `bpy.types.AddOnPreferences`, from the `__init__()`, `invoke()` and `draw()` functions (prohibited by Blender).

## How to Test?

The best way to check if the feature works well with you add-on is to create a dummy but public version of your add-on by creating a release. Be sure to tag it using a [supported tagging format](#release-tagging-rules). Say you create the tag `v2.3.4`. Then you can experiment with what happens if you set the version of your add-on to, say, `(1,0,0)`, `(2,3,4)`, `(2,3,5)`, `(2,4,0)` or `(3,0,0)` in the `version` tuple of the `bl_info` set of your add-on's `__init__.py`. Do not forget to reload the script after each change.

To force update checks, you can just call the update checker operator with the parameter `forceUpdateCheck = True`. If your update checker operator class is named `JohnDoe_OT_MagicMakerUpdateChecker`, call it like this:

```python
JohnDoe_OT_MagicMakerUpdateChecker(forceUpdateCheck = True)
```

With this parameter, the update checker won't care when the update check was performed the last time. To prevent accidental flooding of your GitHub API, the `forceUpdateCheck` property of your operator will be reverted to `False` upon each call. If you don't specify this parameter, it is considered `False`.

## Implementation Guide

Implementation includes making changes to the template's code and you own add-on code. The code template consists of the following files:

* [`updateChecker.py`](/updateChecker.py), a file implementing the functionality, and that you add to your add-on.
* [`Snippets/draw.py`](/Snippets/draw.py), containing the code segment you'll need to add to your `draw()` function(s).
* [`Snippets/execute.py`](/Snippets/execute.py), containing the code segment you'll need to add to your `execute()` function(s).

Implementing the update check involves the following steps:

1. [Copy files](#copy-files) to proper locations.
1. [Replace some tokens in files](#replace-tokens-in-provided-files) to customize it to your name, repo and add-on.
1. Next [insert some code into your add-on files](#modify-your-add-ons-code).
1. Do some [cleanup](#clean-up).

At the end of the day, the code combined with you add-on's code will be able to check in every few days if an update is available.

### Copy Files

Copy all files, `updateChecker.py` and the files from the `Snippets` folder to the folder containing `__init__.py` of your add-on.

### Replace Tokens in Provided Files

Perform the following replacements of placeholders in the code of the files you've just copied. When a placeholder is part of a string, it is enclosed in angle brackets. When it is not, it's just plain uppercase without angle brackets to not mess up Python syntax.

Replace all occurrences of the placeholders in all .py files packaged into this template, including `updateChecker.py`, `Snippets/draw.py` and `Snippets/execute.py`.

1. Replace `<USERSLUG>` with your GitHub username. If your GitHub URL is `https://github.com/johndoe/`, your user name is `johndoe`, so replace `<USERSLUG>` with `johndoe`.

1. Replace `<REPOSLUG>` with your GitHub repo's URL slug. If your repo's full URL is `https://github.com/johndoe/magic-maker`, your repo slug is `magic-maker`, so replace `<REPOSLUG>` with `magic-maker`.

1. Replace `<TOKEN>` with your GitHub token. [More info on token creation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

1. Replace `AUTHORPREFIX` with your common class name prefix. It your main operator is called `JohnDoe_OT_MagicMaker`, your `AUTHORPREFIX` is `JohnDoe`.

1. Replace `ADDONNAME` with the class name of your add-on. It your main operator is called `JohnDoe_OT_MagicMaker`, your `ADDONNAME` is `MagicMaker`.

   Make sure the renamed version of the `AUTHORPREFIX_OT_ADDONNAMEUpdateChecker` class name is unique as you'll need to [register](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html) it in Blender. Also make sure that it conforms to Blender's requirements against operator class names. [This is the latest set of requirements against naming operator classes I'm aware of](https://developer.blender.org/docs/release_notes/2.80/python_api/addons/#Naming).

1. Replace `BLIDNAME` with the properly compiled `bl_idname` of your operator class created right before. If your operator class
   is named `JohnDoe_OT_MagicMakerUpdateChecker`, the `bl_idname` shall be `johndoe.magicmakerupdatechecker`. [This is the latest set of requirements against naming forming bl_idname I'm aware of](https://developer.blender.org/docs/release_notes/2.80/python_api/addons/#Naming).

1. Replace `<ADDON-TITLE>` with the title or name of your add-on, such as `John's Magic Maker`. This will be displayed on the UI so the user knows for what is an update available.

1. Replace `CLASSPREFIX` with the class prefix you use for your classes in this add-on. It your main operator is called `JohnDoe_OT_MagicMaker`, consider renaming `CLASSPREFIXUpdateInfo` to `JohnDoeMagicMakerUpdateInfo`. You'll need to [register](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html) this class and it's your responsibility to make sure the class name is unique. If it's not, it won't work and you may risk healthy operation of other add-ons as well.

### Modify Your Add-On's Code

In this step you'll need to update some of your files.

#### Add Imports

Provided that all your add-on files are located in one folder, add the following import to the beginning of your `__init.py__` to access the `updateChecker` module.

```python
from . import updateChecker
```

If your operator logic is implemented in another file, add it there, too.

#### Register your update info property group and update checker operator

Register the renamed version of `CLASSPREFIXUpdateInfo` and `AUTHORPREFIX_OT_ADDONNAMEUpdateChecker` in the `register()` function of your add-on's `__init__.py` file, in this specific order.

If your classes are named `JohnDoeMagicMakerUpdateInfo` and `JohnDoe_OT_MagicMakerUpdateChecker`, insert the following lines to the said function:

```python
bpy.utils.register_class(JohnDoeMagicMakerUpdateInfo)
bpy.utils.register_class(JohnDoe_OT_MagicMakerUpdateChecker)
```

Note that add-on developers usually list classes to register in a list called `classes` and perform registration in a list enumerator for loop. Feel free to do so:

```python
classes = [
    updateChecker.JohnDoeMagicMakerUpdateInfo,
    updateChecker.JohnDoe_OT_MagicMakerUpdateChecker
    ... # other classes of yours
]

...

def register():
    ... # other stuff to do

    # Register classes
    for c in classes:
        bpy.utils.register_class(c)

    ... # other stuff to do        
```

Don't forget to unregister them in the `unregister()` function in reverse order:

```python
bpy.utils.unregister_class(JohnDoe_OT_MagicMakerUpdateChecker)
bpy.utils.unregister_class(JohnDoeMagicMakerUpdateInfo)
```

Or using the list and loop approach:

```python
def unregister():
    ... # other stuff to do
    
    # Unregister classes (in reverse order)
    for c in reversed(classes):
        try:
            bpy.utils.unregister_class(c)
        except:
            # Don't panic, it was probably not registered
            pass

    ... # other stuff to do        
```

#### Crete or Update Class for Add-On Preferences

If you haven't done yet so, create a subclass of `bpy.types.AddonPreferences` to store add-on level settings. Add a `PointerProperty` with the type you created by subclassing `bpy.types.PropertyGroup` above (the one you registered first in the previous step).

```python
    updateInfo: PointerProperty(type=updateChecker.JohnDoeMagicMakerUpdateInfo)
```

This is gonna be the cache.

#### Insert Code to Display Update Info

You can display update info in Blender's `Preferences` > `Add-Ons` panel or in your own add-on's UI. For both you have to use code like what you can find in `Snippets/draw.py`. The snippet checks if update is available, and if it is, a button is displayed.

* To add it to the add-on's preferences, add the following code to the `draw()` function of your subclass of `bpy.types.AddonPreferences`.

* To add it to your panel, add the following code to the `draw()` function of your operator(s).

```python
def draw(self, context):
    # other stuff to do

    try: # to see if we know anything about updates
        updateInfo = context.preferences.addons[__package__].preferences.updateInfo
        
        # Note that checking update is part of executing the main operator, that is, performing at least
        # one synchronization. Until that no updates will be detected. Updates are not checked each time
        # this dialog is drawn, but as set in `updateInfo.CLASSPREFIXUpdateInfo.checkFrequencyDays`.
        if updateInfo.updateAvailable:
            # Draw update button and tip
            opUpdate = layout.column().row().operator(
                    'wm.url_open',
                    text=f"Update available",
                    icon='URL'
                    )            
            opUpdate.url = updateChecker.RepoInfo.repoReleasesUrl
            self.layout.row().label(text=f"You can update from {updateInfo.currentVersion} to {updateInfo.latestVersion}")
    except:
        # Do nothing, if we could not check updates, probably this is the first time of enabling the add-on
        # and corresponding data structures are not yet available.
        pass

    # other stuff to do
```

Remember, at this point release of updates cannot be checked as the update info class cannot be written to save the timestamp and eventual fresh data. Therefore the results of the last checks will be used. A check can be made in an operator.

#### Insert Code to Check for Updates

Add the code snippet in `Snippets/execute.py` to somewhere, probably near the beginning of one or more of your operators. This is when you can check for updates. If there is an update, the user will be notified when the UI containing the above code in its `draw()` function is redrawn. Note that until an operator with this check is run at least once, no check is made for updates.

```python
def execute(self, context):
    # other stuff to do

    # Call the update checker to check for updates time to time, as specified in 
    # `updateInfo.CLASSPREFIXUpdateInfo.checkFrequencyDays`
    try:
        bpy.ops.BLIDNAME()            
    except:
        # Don't mess up anything if update checking doesn't work, just ignore the error
        pass

    # other stuff to do
```

Mind the placeholder. If your update checker operator class is called `JohnDoe_OT_MagicMakerUpdateChecker` and its `bl_idname` is `johndoe.magicmakerupdatechecker`, the code looks like this:

```python
def execute(self, context):
    # other stuff to do

    # Call the update checker to check for updates time to time, as specified in 
    # `updateInfo.CLASSPREFIXUpdateInfo.checkFrequencyDays`
    try:
        bpy.ops.johndoe.magicmakerupdatechecker()            
    except:
        # Don't mess up anything if update checking doesn't work, just ignore the error
        pass

    # other stuff to do
```

To force update checking to test your code, replace the operator call with this one:

```python
        bpy.ops.johndoe.magicmakerupdatechecker(forceUpdateCheck = True)            
```

### Clean-Up

Once you are done, you are advised to remove files you copied from the `Snippets` folder. They became useless by now.

## Update Info Properties

The update info class contains the following properties available for you to display or otherwise use them:

| Property | Type | Default Value | Description |
| -------- | ---- | ------------- | ----------- |
| `checkFrequencyDays` | `bpy.props.IntProperty` | `3` | Frequency of checking for new updates in days. |
| `updateAvailable` | `bpy.props.BoolProperty` | `False` | Tells whether an update is available (`True`) based on the latest check. |
| `currentVersion` | `bpy.props.StringProperty` | `""` | Version number of the current version of you add-on `x.y.z` format. |
| `latestVersion` | `bpy.props.StringProperty` | `""` | Version number of the latest release (the release tag from the repo) from the last check. |
| `latestVersionName` | `bpy.props.StringProperty` | `""` | The name of the latest release as specified by you in GitHub. |
| `lastCheckedTimestamp` | `bpy.props.StringProperty` | `""` | The date and time of the last successful check for updates in `'%Y-%m-%d %H:%M:%S'` format. This is used to check cache expiry. |

## Release Tagging Rules

For version comparison to work, use semantic versioning [as suggested by GitHub](http://semver.org/). Specifically, make sure your version tags follow any of these patterns:

* `x.y.z`
* `vx.y.z`
* `x.y.z-foo`
* `vx.y.z-foo`

where `x`, `y` and `z` are digits, specifying the major version, the minor version and build number or patch number, `foo` is anything (for example, `beta` for beta versions) and `v` is simply a `v` character. For other patterns, you'll need to edit the version number comparison logic.

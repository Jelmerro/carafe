carafe
======

carafe is a tiny management tool for wine ~~bottles~~ carafes.

## Features

- A tiny command-line script to create bottles/carafes for different programs
- Automatically manages different wine prefixes
- Always uses system wine, but never changes the default .wine configuration
- Configure settings for each carafe separately
- Create shortcuts for installed programs and/or easily start them from the carafe CLI
- All configuration and carafes are neatly stored in a single folder (and are auto-deleted when all carafes are deleted)

(carafe is both the name of the program and for a wine bottle created through this program)

## Note

#### The current command-line interface might be slightly changed, until version 1.0.0 is released

## Simple usage, get going fast

There are two example provided here,
both of which assume you have the setup stored inside the `~/Downloads` folder.

### Example for Steam installer

The following commands will setup a new carafe with steam installed.
```
./carafe steam create
./carafe steam install -e ~/Downloads/SteamSetup.exe
./carafe steam link
```
It can now be started by simply running `./carafe steam start`

The install step can also be called without `-e`,
in that case it will ask for the installer/executable location.

### Example for portable rufus

For portable programs the install step can be skipped.
The installation steps could be something like this:

`./carafe rufus create`

Now copy all the portable program files somewhere to the carafe.
The location for our new rufus carafe is `~/.carafe/rufus/drive_c`.

`cp ~/Downloads/rufus.exe ~/.carafe/rufus/drive_c/`

After copying the files, we can already execute rufus using this command:

`./carafe rufus start -l "C:/rufus.exe"`

Or create a link to the exe just like we did for Steam:

`./carafe rufus link`

So we can run the rufus.exe like so:

`./carafe rufus start`

### Other notes

- To get more clarity about the carafes use the info and list commands
- All info about the Steam carafe: `./carafe steam info`
- A list of all the carafes: `./carafe list`
- Remove the rufus carafe completely with: `./carafe rufus remove`

## Advanced usage

carafe is a single script which can be started from any location.
It will store the configuration and carafes inside `~/.carafe` on all supported systems.
Most testing was done on Linux, but I'm open to pull requests to broaden OS support or to improve other features.

### Wine versions

carafe will need wine as the most important dependency.
Unlike other management tools for wine bottles, carafe does not allow the user to switch between versions.
Instead it uses the system wine for all carafes.
The following advantages are a direct consequence of this decision:

- All carafes will automatically use the latest/greatest version of wine
- It's not required to manually update a hard-coded version for all the carafes (as carafe does not check the wine version)
- There is no need for carafe to manually add new supported wine versions (if there are no breaking CLI changes)

There is one trade-off to all these advantages:

- A regression in a new version of wine can break compatibility until a new wine version is released

### Manage carafe

After running `./carafe` a list of the supported options will shown.
All of them are listed in the output as shown here:

```
usage: carafe {<carafe_name>,list} <sub_command>

Welcome to carafe 0.2.0
carafe is a tiny management tool for wine bottles/carafes.

optional arguments:
  -h, --help            show this help message and exit

sub-commands:
  All the valid sub-commands to manage the carafes

  {create,install,start,remove,info,link,shortcut,winecfg,winetricks}
    create              create a new carafe
    install             install software to the carafe
    start               start an installed program
    remove              remove a carafe
    info                all info about a carafe
    link                link a program to the carafe
    shortcut            generate a desktop shortcut
    winecfg             run winecfg
    winetricks          run winetricks

carafe was made by Jelmer van Arnhem and is MIT licensed
For documentation and other information, see the README.md
```

Most management options can be called without any arguments,
some commands will ask questions to fill required information.
If no user interaction is possible or wanted after running the command,
next time call the command with all arguments which were asked as a question.
In the section below, further details are provided on most options.

#### Create

The first step to using carafe is creating a new carafe to install apps into.
This command only accepts --arch as an optional argument.
By default the system architecture will be used.
You cannot change the arch after creating a carafe (wine limitation),
but you can create a new carafe with a different arch.

```
usage: carafe <carafe_name> create

Use 'create' to make a new carafe, you should start here

optional arguments:
  -h, --help   show this help message and exit
  --arch ARCH  Change the default arch, e.g. to win32
```

As we did in the example for Steam: `./carafe steam create`.

There are a couple of restrictions for choosing a name:

- There are a few of reserved words, like 'wine', 'list' and similar words
- All spaces are removed from the name
- Forward slashes are replaced with dashes

Aside from that you can choose any name you want,
but descriptive names like the name of the main program are recommended.

#### Install

To install software inside the carafe the install option is used.
It can also be used to run other external executables inside the carafe.
If the executable argument is not provided,
carafe will ask the user to enter the location.

```
usage: carafe <carafe_name> install

Use 'install' to run an external exe/msi inside the carafe

optional arguments:
  -h, --help            show this help message and exit
  -e EXECUTABLE, --executable EXECUTABLE
                        Location of the external executable to run inside the
                        carafe
```

#### Start

This option is used to start programs inside a carafe.
For existing carafes, starting the default/linked program should be as straightforward as:

`./carafe <name_of_carafe> start`

For example, the default program of an existing carafe for Steam could be started as:

`./carafe steam start`

To run a different program inside the Steam carafe, add the location argument:

`./carafe steam start -l "Program Files (x86)/Internet Explorer/iexplore.exe"`

For the above command, an absolute path from the root of the carafe's C: disk is assumed.
The location argument is required for carafes with no program linked yet.

```
usage: carafe <carafe_name> start

Use 'start' to start a program inside an existing carafe

optional arguments:
  -h, --help            show this help message and exit
  -l LOCATION, --location LOCATION
                        Location of the executable inside the carafe to start
```

#### Remove

Once you are done with a carafe, this option can completely remove it from disk.

```
usage: carafe <carafe_name> remove

Use 'remove' to delete an existing carafe

optional arguments:
  -h, --help  show this help message and exit
```

If the removal of a carafe results in an empty config file,
the config file will be deleted from disk.
If either the removal of the config or the carafe result in an empty `~/.carafe` folder,
it will be deleted as well, as if carafe had never been used before.
Desktop shortcuts will not be automatically deleted (see 'shortcut' option for creating them).

#### List

To view a list of all the existing carafes, use the list option.

This option will ignore all arguments after it,
and will show a list like this:

`./carafe list`

```
The following carafes are currently configured:
steam
rufus
Run './carafe <carafe_name> info' for more information
```

#### Info

All known information about an existing carafe can be listed with the info option.

```
usage: carafe <carafe_name> info

Use 'info' to print all information about a carafe

optional arguments:
  -h, --help  show this help message and exit
```

For example, after creating a new carafe named 'test',
the command `./carafe test info` will return the following:

```
All information about carafe 'test':
Configured with default system arch
No link is currently configured
When a carafe is linked, you can start the program with './carafe test start'
To modify the link, use './carafe test link'

The current list of executables looks like this:
C:/Program Files (x86)/Internet Explorer/iexplore.exe
C:/Program Files (x86)/Windows NT/Accessories/wordpad.exe
C:/Program Files (x86)/Windows Media Player/wmplayer.exe
C:/Program Files/Internet Explorer/iexplore.exe
C:/Program Files/Windows NT/Accessories/wordpad.exe
C:/Program Files/Windows Media Player/wmplayer.exe
You can add more with './carafe test install'
```

#### Link

An important feature of carafe is the linking system.
It allows the user to pick a default location to execute per carafe.

```
sage: carafe <carafe_name> link

Use 'link' to connect the startup link (recommended)

optional arguments:
  -h, --help            show this help message and exit
  -l LOCATION, --location LOCATION
                        Location of the executable inside the carafe to link
```

After running the 'info' option, a message was displayed regarding the linking.
When running the `./carafe test link` command now, it will ask us to choose an executable like this:

```
0: C:/Program Files (x86)/Internet Explorer/iexplore.exe
1: C:/Program Files (x86)/Windows NT/Accessories/wordpad.exe
2: C:/Program Files (x86)/Windows Media Player/wmplayer.exe
3: C:/Program Files/Internet Explorer/iexplore.exe
4: C:/Program Files/Windows NT/Accessories/wordpad.exe
5: C:/Program Files/Windows Media Player/wmplayer.exe
Choose the number of the new linked application: 3
```

After choosing number 3 as the linked application,
the command `./carafe test info` now displays the following:

```
All information about carafe 'test':
Configured with default system arch
A link for easy startup is configured to the following:
Program Files/Internet Explorer/iexplore.exe
When a carafe is linked, you can start the program with './carafe test start'
To modify the link, use './carafe test link'

The current list of executables looks like this:
C:/Program Files (x86)/Internet Explorer/iexplore.exe
C:/Program Files (x86)/Windows NT/Accessories/wordpad.exe
C:/Program Files (x86)/Windows Media Player/wmplayer.exe
C:/Program Files/Internet Explorer/iexplore.exe
C:/Program Files/Windows NT/Accessories/wordpad.exe
C:/Program Files/Windows Media Player/wmplayer.exe
You can add more with './carafe test install'
```

The list of executables is automatically filled with all exe files inside the carafe.
New programs can be installed with the install option,
and they can be started with `./carafe test start` (See the start option for more details).

#### Shortcut

To create a desktop shortcut, use the shortcut option.
By default, it will place shortcuts on the user desktop.
This can be altered by changing the output folder location.
The executable location can be conveniently set to 'link',
so it will be automatically updated when the linked program is changed.
It will only auto-update for the carafe shortcut type,
but the wine shortcut will continue to work after carafe is (re)moved.

```
usage: carafe <carafe_name> shortcut

Use 'shortcut' to create a .desktop shortcut to a carafe

optional arguments:
  -h, --help            show this help message and exit
  -l LOCATION, --location LOCATION
                        Location of the executable inside the carafe to
                        shortcut. Normally a path, but can be set to 'link' as
                        well.
  -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        Which folder to place the shortcut, default is the
                        user desktop
  -t {carafe,wine}, --type {carafe,wine}
                        The type of shortcut to make
```

Executable location will be asked interactively when not provided as an argument,
in a fairly similar way as is done for the 'link' command.

Shortcuts won't be automatically deleted when a carafe is deleted.

Some programs might create a desktop shortcut during the installation,
these type of shortcuts are made by wine and don't need carafe to work.

#### Winecfg and Winetricks

Both of these commands accept no arguments besides `--help`.

Example usage of winecfg for a Steam carafe looks like this:

`./carafe steam winecfg`

They will directly execute the winecfg or winetricks command respectively.
In the last paragraph, it's explained how these commands are handled,
and how you can run them directly without using the carafe interface.

The carafes are created by running prefixed wine commands.
All features available using wine, winecfg, winetricks or any other tool can be used with carafe.

For example, to open the winecfg for a Steam carafe, the following command could be used:

`WINEPREFIX=~/.carafe/steam winecfg`

This is exactly what carafe will do when asked to invoke winecfg,
but carafe makes sure the arch and wineprefix are automatically correct.

The same shortcut is added for winetricks, other tools can use the original wineprefix command.

In short, carafe is aimed to ease the configuration of wine bottles/carafes,
without introducing any magic or changing the wine prefix system.

### Dependencies

carafe is pure python and only uses native imports, some of them are python 3.5+.

Wine is the only dependency of carafe and it can even do some management tasks without wine installed (such as remove, info and list).
Creating and starting the carafes is done by wine, and won't work without it installed.

By default carafe will look for the commands: wine, wineboot and winecfg.
All of these should automatically be set when installing wine using the package manager.
carafe will show a warning when wine or the other commands are not found,
and offer instructions to resolve the problem.
For other installation methods an alias might be needed,
or you can configure the wine location in the config file.
You can manually edit the `~/.carafe/config.json` to change the default wine command locations.
It might be needed to create the config file, as it normally will only be stored when links or special arch types are used.

### Logging

No wine commands executed by carafe will show any output in the terminal.
The commands will store the log of the latest executed command as `~/.carafe/<carafe_name>/log`.
carafe does not keep a history of all the logs, only the latest one is stored.

## License

carafe itself is made by [Jelmer van Arnhem](https://github.com/jelmerro) and is licensed as MIT, see LICENSE for details.

Dependencies such as wine have no relation to carafe and are be covered by different licenses.

carafe
======

carafe is a tiny management tool for wine ~~bottles~~ carafes.

## Features

- A tiny command-line script to create bottles/carafes for different programs
- Automatically manages different wine prefixes
- Never changes the default .wine configuration
- Configure settings for each carafe separately
- Create shortcuts for installed programs and/or easily start them from the carafe CLI
- All configuration and carafes are neatly stored in a single folder (and are auto-deleted when all carafes are deleted)

(carafe is both the name of the program and for a wine bottle created through this program)

## Simple usage, get going fast

There are two examples provided here,
both of which assume you have the setup stored inside the `~/Downloads` folder.
It's recommended to read both examples before starting,
to get a good idea of the different ways to configure carafe.

To start carafe as `carafe`, you need to install it:

```bash
pip install --user -I git+https://github.com/Jelmerro/carafe
```

Alternatively you can run all carafe commands with python instead: `python3 carafe.py`.
The first option is used in this readme, because it's shorter.
The `carafe.py` script is all you need to manage carafes,
you can download and move it wherever you want.

### Example for Steam installer

The following commands will setup a new carafe with steam installed.
```
carafe steam create
carafe steam install
carafe steam link
```
It can now be started by simply running `carafe steam start`

If you don't like the interactive questions, the same can be achieved like this:

```
carafe steam create
carafe steam install -e ~/Downloads/SteamSetup.exe
carafe steam link -l "Program Files (x86)/Steam/Steam.exe"
carafe steam start
```

It's also possible to skip the link step and start like this: `carafe steam start -l "Program Files (x86)/Steam/Steam.exe"`.
The link option is recommended to make the start command easier to use (and shorter).
Alternatively you could pick a location from a list with this command:

`carafe steam start --ask` or `carafe steam start -a` for short.

### Example for portable rufus

For portable programs the install step can be skipped.
The installation steps could be something like this:

`carafe rufus create`

Now copy all the portable program files somewhere to the carafe.
The location for our new rufus carafe is `~/.carafe/rufus/drive_c`.

`cp ~/Downloads/rufus.exe ~/.carafe/rufus/drive_c/`

After copying the files, we can already execute rufus using this command:

`carafe rufus start -l "C:/rufus.exe"` or `carafe rufus start --ask`.

The command `carafe rufus start --ask` will ask the user to pick a location to start.

To create a link to the exe just like we did for Steam:

`carafe rufus link`

So we can run the rufus.exe like so:

`carafe rufus start`

### Other options

There are many more sub-commands provided by carafe,
the most important ones are listed here:

- All info about the Steam carafe: `carafe steam info`
- A list of all the carafes: `carafe list`
- Remove the rufus carafe completely with: `carafe rufus remove`
- Copy a carafe to a new location (as a backup for example): `carafe steam copy steam-backup`

### Dependencies

carafe is pure python and only uses native imports, some of them are python 3.5+.

Wine is the only dependency of carafe and it can even do some management tasks without wine installed (such as remove, info and list).
Creating and starting the carafes is done by wine, and won't work without it installed.

carafe will show a warning when the 'wine' command is not found,
and offer instructions to resolve the problem.
For some installation methods an alias might be needed,
or you can configure the wine location in the config file.
You can manually edit the `~/.carafe/config.json` to change the default wine command location.
It might be needed to create the config file, as it normally will only be stored when links or special arch types are used.
The config file also accepts a 'winetricks' field for setting the winetricks location/path separately.

## Advanced usage

carafe is a single script which can be started from any location.
It will store the configuration and carafes inside `~/.carafe` on all supported systems.
Most testing was done on Linux, but I'm open to pull requests to broaden OS support or to improve other features.

### Wine versions

carafe will need wine as the most important dependency.
By default, the system wine is used for all carafes.
The following advantages are a direct consequence of this decision:

- All carafes will automatically use the latest/greatest version of wine
- It's not required to manually update a hard-coded version for all the carafes (as carafe does not check the wine version)
- There is no need for carafe to manually add new supported wine versions (if there are no breaking CLI changes)

There is one trade-off to all these advantages:

- A regression in a new version of wine can break compatibility until a new wine version is released

The [wine wiki](https://wiki.winehq.org/FAQ#Which_version_of_Wine_should_I_use.3F) recommends to use a recent or even the latest version of wine,
which is automatically configured by using carafe.

#### Changing a wine version

In the rare cases where you want to use a custom wine version,
you can manually update the carafe config.
A toplevel "wine" key can be used as the global wine location,
while a carafe specific "wine" key can be used to override that per carafe.
The value of the configuration should be an absolute path to the wine executable.

### Manage carafe

After running `carafe` a list of the supported options will shown.
All of them are listed in the output as shown here:

```
usage: carafe {<carafe_name>,list} <sub_command>

Welcome to carafe 1.4.0
carafe is a tiny management tool for wine bottles/carafes.

optional arguments:
  -h, --help            show this help message and exit

sub-commands:
  All the valid sub-commands to manage the carafes

  {create,install,start,rename,copy,remove,info,link,shortcut,regedit,winecfg,winetricks}
    create              create a new carafe
    install             install software to the carafe
    start               start an installed program
    rename              rename an existing carafe
    copy                copy an existing carafe
    remove              remove a carafe
    info                all info about a carafe
    link                link a program to the carafe
    shortcut            generate a desktop shortcut
    log                 show the last command output
    regedit             run regedit
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

As we did in the example for Steam: `carafe steam create`.

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

`carafe <name_of_carafe> start`

For example, the default program of an existing carafe for Steam could be started as:

`carafe steam start`

To run a different program inside the Steam carafe, add the ask argument:

`carafe steam start --ask`

Or use the location argument to start an executable inside the carafe directly:

`carafe steam start -l "Program Files (x86)/Internet Explorer/iexplore.exe"`

For the above command, an absolute path from the root of the carafe's C: disk is assumed.
The location argument is required for carafes with no program linked yet.

```
usage: carafe <carafe_name> start

Use 'start' to start a program inside an existing carafe

optional arguments:
  -h, --help            show this help message and exit
  -k, --keep-log        Keep the wine log (can be multiple GBs and will slow
                        down wine)
  -a, --ask             Instead of starting the link or --location, ask for
                        the path
  -l LOCATION, --location LOCATION
                        Location of the executable inside the carafe to start
```

The start command is the only sub-command which does not save the log by default.
With the keep log argument, the start command can return to the default behavior for all other commands.
If `--keep-log` is provided, the log can be found in `~/.carafe/<carafe_name>/log`.
Keep in mind that this file can be multiple gigabytes after playing for a few hours,
and that it will cause a performance hit on wine to constantly write logs to disk.
You can also show the contents of the log file with the 'log' option.

#### Rename

With the rename option you change the name of an existing carafe.

```
usage: carafe <carafe_name> rename <new_name>

Use 'rename' to change the name of an existing carafe

positional arguments:
  newname     New name of the carafe

optional arguments:
  -h, --help  show this help message and exit
```

For example: `carafe steam rename steam-backup`.

Rename will actually copy the existing carafe and remove the old one.
Running these two options separately will do exactly the same.

#### Copy

With the copy option you can copy an existing carafe to a new location.
This is useful for backups, and it works like this:

```
usage: carafe <carafe_name> copy <new_name>

Use 'copy' to duplicate an existing carafe to a new one

positional arguments:
  newname     Name of the new carafe

optional arguments:
  -h, --help  show this help message and exit
```

For example: `carafe steam copy steam-backup`.

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

`carafe list`

```
The following carafes are currently configured:
steam
rufus
Run 'carafe <carafe_name> info' for more information
```

#### Info

All known information about an existing carafe can be listed with the info option.

```
usage: carafe <carafe_name> info

Use 'info' to print all information about a carafe

optional arguments:
  -h, --help  show this help message and exit
```

For example, to get all info about our steam carafe,
the command `carafe steam info` will return the following:

```
All information about carafe 'steam':
Configured with default system arch
No link is currently configured
When a carafe is linked, you can start the program with 'carafe steam start'
To modify the link, use 'carafe steam link'

The current list of executables looks like this:
C:/Program Files (x86)/Internet Explorer/iexplore.exe
C:/Program Files (x86)/Common Files/Steam/SteamService.exe
C:/Program Files (x86)/Windows NT/Accessories/wordpad.exe
C:/Program Files (x86)/Steam/uninstall.exe
C:/Program Files (x86)/Steam/Steam.exe
C:/Program Files (x86)/Steam/bin/SteamService.exe
C:/Program Files (x86)/Windows Media Player/wmplayer.exe
C:/Program Files/Internet Explorer/iexplore.exe
C:/Program Files/Windows NT/Accessories/wordpad.exe
C:/Program Files/Windows Media Player/wmplayer.exe
You can add more with 'carafe steam install'
```

#### Link

An important feature of carafe is the linking system.
It allows the user to pick a default location to execute per carafe.

```
usage: carafe <carafe_name> link

Use 'link' to connect the startup link (recommended)

optional arguments:
  -h, --help            show this help message and exit
  -l LOCATION, --location LOCATION
                        Location of the executable inside the carafe to link
```

After running the 'info' option, a message was displayed regarding the linking.
When running the `carafe steam link` command now, it will ask us to choose an executable like this:

```
0: C:/Program Files (x86)/Internet Explorer/iexplore.exe
1: C:/Program Files (x86)/Common Files/Steam/SteamService.exe
2: C:/Program Files (x86)/Windows NT/Accessories/wordpad.exe
3: C:/Program Files (x86)/Steam/uninstall.exe
4: C:/Program Files (x86)/Steam/Steam.exe
5: C:/Program Files (x86)/Steam/bin/SteamService.exe
6: C:/Program Files (x86)/Windows Media Player/wmplayer.exe
7: C:/Program Files/Internet Explorer/iexplore.exe
8: C:/Program Files/Windows NT/Accessories/wordpad.exe
9: C:/Program Files/Windows Media Player/wmplayer.exe
Choose the number of the application shortcut: 4
```

After choosing number 4 as the linked application,
the command `carafe steam info` now displays the following:

```
All information about carafe 'steam':
Configured with default system arch
A link for easy startup is configured to the following:
Program Files (x86)/Steam/Steam.exe
When a carafe is linked, you can start the program with 'carafe steam start'
To modify the link, use 'carafe steam link'

The current list of executables looks like this:
C:/Program Files (x86)/Internet Explorer/iexplore.exe
C:/Program Files (x86)/Common Files/Steam/SteamService.exe
C:/Program Files (x86)/Windows NT/Accessories/wordpad.exe
C:/Program Files (x86)/Steam/uninstall.exe
C:/Program Files (x86)/Steam/Steam.exe
C:/Program Files (x86)/Steam/bin/SteamService.exe
C:/Program Files (x86)/Windows Media Player/wmplayer.exe
C:/Program Files/Internet Explorer/iexplore.exe
C:/Program Files/Windows NT/Accessories/wordpad.exe
C:/Program Files/Windows Media Player/wmplayer.exe
You can add more with 'carafe steam install'
```

We can now start steam with `carafe steam start`,
or start a different program inside the carafe: `carafe steam start -l "Program Files/Internet Explorer/iexplore.exe"`.

The list of executables is automatically filled with all exe files inside the carafe.

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
  -n NAME, --name NAME  Name of the new shortcut, default is the name of the
                        carafe
  -t {carafe,wine}, --type {carafe,wine}
                        The type of shortcut to make
```

Executable location will be asked interactively when not provided as an argument,
in a fairly similar way as is done for the 'link' command.

The name of the shortcut will be set to the name of the carafe automatically,
but it can be changed with the optional --name argument like so:

`carafe steam shortcut --name "Steam (Windows version)"`

To achieve the same but with no interactive questions,
the following command could be used to create a carafe shortcut for the linked program:

`carafe steam shortcut --name "Steam (Windows version)" --type carafe --location link`

Some programs might create a desktop shortcut during the installation,
these type of shortcuts are made by wine and don't need carafe to work.

Shortcuts won't be automatically deleted when a carafe is deleted.

#### Log

Example usage of log for a Steam carafe looks like this:

`carafe steam log`

This will show the output of the last wine, winetricks or winecfg command.
It simply reads and prints the file that is stored at `~/.carafe/<carafe_name>/log`.

#### Regedit

Example usage of regedit for a Steam carafe looks like this:

`carafe steam regedit`

To open the regedit for a Steam carafe without using carafe, the following command could be used:

`WINEPREFIX=/home/user/.carafe/steam wine regedit`

This is exactly what carafe will do when asked to invoke regedit,
but carafe makes sure the winearch and wineprefix are automatically correct.

#### Winecfg

Example usage of winecfg for a Steam carafe looks like this:

`carafe steam winecfg`

Running winecfg without carafe works the same as for regedit.

#### Winetricks

Example usage of winetricks for a Steam carafe looks like this:

`carafe steam winetricks`

This will open the winetricks GUI, where a lot of extra components can be installed from.
To install dxvk for the steam carafe with winetricks, run the command:

`carafe steam winetricks dxvk`

The help page describes this behavior as follows:

```
usage: carafe <carafe_name> winetricks <optional_arguments>

Use 'winetricks' to install winetricks components

positional arguments:
  arguments   Any arguments will directly be passed to winetricks

optional arguments:
  -h, --help  show this help message and exit
```

Just like winecfg and regedit, it's also possible to run winetricks commands without carafe:

`WINEPREFIX=/home/user/.carafe/steam winetricks dxvk`

This again means that you need to manually set the wineprefix and winearch to the correct values,
which is something that the carafe command will handle for you.

In short, carafe is aimed to ease the configuration of wine bottles/carafes,
without introducing any magic or changing the wine prefix system.

### Logging

No wine commands executed by carafe will show any output in the terminal.
You can view the latest log using the 'log' option or by reading the 'log' file inside the carafe.
The commands will store the log of the latest executed command as `~/.carafe/<carafe_name>/log`.
carafe does not keep a history of all the logs, only the latest one is stored.
The start command will by default disable all logging,
because these logs can get very large and because it slows down wine.
To restore the default logging, provide the `--keep-log` argument (see the 'start' option for details).

### Wine related files

Wine will create menu shortcuts in `~/.local/share/applications`,
and store the icons for them in `~/.local/share/icons`.
The location `~/.local/share/desktop-directories` will also be used,
along with `~/.config/menus` for menu related files.

These directories are automatically filled with files by wine,
carafe does not create, modify or remove them.

carafe stores all configuration and the prefixes in `~/.carafe`,
which will automatically be deleted when all carafes are removed.

## License

carafe itself is made by [Jelmer van Arnhem](https://github.com/jelmerro) and is licensed as MIT, see LICENSE for details.

Dependencies such as wine have no relation to carafe and are be covered by different licenses.

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

#### The current command-line interface might be changed in future releases

#### The interface might receive breaking changes, until version 1.0.0 is released

## Simple usage, get going fast

There are two example provided here,
both of which assume you have the setup stored inside the `~/Downloads` folder.

### Example for Steam installer

The following commands will setup a new carafe with steam installed.
```
./carafe m add steam
./carafe m install steam -l ~/Downloads/SteamSetup.exe
./carafe m link steam
```
It can now be started by simply running `./carafe steam`

The install step can also be called without `-l`,
in that case it will ask for the installer location.

### Example for portable rufus

For portable programs the install step can be skipped.
The installation steps could be something like this:

`./carafe m add rufus`

Now copy all the portable program files somewhere to the carafe.
The location for our new rufus carafe is `~/.carafe/rufus/drive_c`.

`cp ~/Downloads/rufus.exe ~/.carafe/rufus/drive_c/`

After coping the files, we can already execute rufus using this command:

`./carafe rufus "C:/rufus.exe"`

Or create a link to the exe just like we did for Steam:

`./carafe m link rufus`

So we can run the rufus.exe like so:

`./carafe rufus`

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

All carafe configuration commands start with one of the following arguments:

`./carafe manage <options>` or `./carafe m <options>`

Because of the way the program linking works in carafe, these names are not allowed for any carafe.
See "Start a program" for details on this.

After running `./carafe m` a list of the supported options will shown.
For a quick explanation on all of them, the help output is shown below:

```
usage: carafe m [-h]
                {add,install,remove,list,info,link,shortcut,winecfg,winetricks}
                ...

Welcome to carafe 0.1.0

optional arguments:
  -h, --help            show this help message and exit

sub-commands:
  All the valid sub-commands to manage the carafes

  {add,install,remove,list,info,link,shortcut,winecfg,winetricks}
    add                 add --help
    install             install --help
    remove              remove --help
    list                list --help
    info                info --help
    link                link --help
    shortcut            shortcut --help
    winecfg             winecfg --help
    winetricks          winetricks --help

carafe was made by Jelmer van Arnhem and is MIT licensed
For documentation and other information, see the README.md
```

Most management options can be called without any arguments,
some commands will ask questions to fill required information.
If no user interaction is possible or wanted after running the command,
next time call the command with all arguments which were asked as a question.
In the section below, further details are provided on most options.

### Options details

Almost all arguments for the management options are optional,
but they do explain a lot about their usage and can reduce user interaction.
Most options are explained in detail below.

#### Add

The first step to using carafe is creating a new carafe to install apps into.
This command only accepts --arch as an optional argument.
By default the system architecture will be used.
You cannot change the arch after creating a carafe,
but you can create a new carafe with a different arch.

```
usage: carafe m add [-h] [--arch ARCH] name

Use 'add' to create a new carafe, this is usually step 1

positional arguments:
  name         The name of the new carafe

optional arguments:
  -h, --help   show this help message and exit
  --arch ARCH  Change the default arch, e.g. win32
```

#### Install

To install software inside the carafe the install option is used.
It can also be used to run other external executables inside the carafe.
If the executable argument is not provided,
carafe will ask the user to enter the location.

```
usage: carafe m install [-h] [-e EXECUTABLE] name

Use 'install' to run an external exe/msi inside the carafe

positional arguments:
  name                  The name of an existing carafe

optional arguments:
  -h, --help            show this help message and exit
  -e EXECUTABLE, --executable EXECUTABLE
                        Location of the executable to run inside the carafe
```

#### Remove

Once you are done with a carafe, this option can completely remove it from disk.

```
usage: carafe m remove [-h] name

Use 'remove' to delete an existing carafe

positional arguments:
  name        The name of the existing carafe

optional arguments:
  -h, --help  show this help message and exit
```

If the removal of a carafe results in an empty config file,
the config file will be deleted from disk.
If either the removal of the config or the carafe result in an empty `~/.carafe` folder,
it will be deleted as well, as if carafe had never been used before.
Desktop shortcuts will not be automatically deleted (see 'shortcut' option).

#### List

To view a list of all the existing carafes, use the list option.

```
usage: carafe m list [-h]

Use 'list' to show all existing carafes

optional arguments:
  -h, --help  show this help message and exit
```

#### Info

All known information about an existing carafe can be listed with the info option.

```
usage: carafe m info [-h] name

Use 'info' to print all information about a carafe

positional arguments:
  name        The name of the existing carafe

optional arguments:
  -h, --help  show this help message and exit
```

For example, after creating a new carafe named 'test', the following info will be shown:

```
All information about carafe 'test':
Configured with default system arch
No link is currently configured
When a carafe is linked, you can start the program with './carafe test'
To modify the link, use './carafe m link test'

The current list of executables looks like this:
Program Files (x86)/Internet Explorer/iexplore.exe
Program Files (x86)/Windows NT/Accessories/wordpad.exe
Program Files (x86)/Windows Media Player/wmplayer.exe
Program Files/Internet Explorer/iexplore.exe
Program Files/Windows NT/Accessories/wordpad.exe
Program Files/Windows Media Player/wmplayer.exe
```

#### Link

An important feature of carafe is the linking system.
It allows the user to pick a default location to execute per carafe.

In the previous info output, a message was displayed regarding the linking.
When running the `./carafe m link test` command now, it will ask us to choose an executable like this:

```
0: Program Files (x86)/Internet Explorer/iexplore.exe
1: Program Files (x86)/Windows NT/Accessories/wordpad.exe
2: Program Files (x86)/Windows Media Player/wmplayer.exe
3: Program Files/Internet Explorer/iexplore.exe
4: Program Files/Windows NT/Accessories/wordpad.exe
5: Program Files/Windows Media Player/wmplayer.exe
Choose the number of the new linked application: 3
```

After choosing number 3 as the linked application,
the command `./carafe m info test` now displays the following:

```
All information about carafe 'test':
Configured with default system arch
A link for easy startup is configured to the following:
Program Files/Internet Explorer/iexplore.exe
When a carafe is linked, you can start the program with './carafe test'
To modify the link, use './carafe m link test'

The current list of executables looks like this:
Program Files (x86)/Internet Explorer/iexplore.exe
Program Files (x86)/Windows NT/Accessories/wordpad.exe
Program Files (x86)/Windows Media Player/wmplayer.exe
Program Files/Internet Explorer/iexplore.exe
Program Files/Windows NT/Accessories/wordpad.exe
Program Files/Windows Media Player/wmplayer.exe
```

The list of executables is automatically filled with all exe files inside the carafe.
New programs can be installed with the install option,
and they can be started with `./carafe test` (See "Start a program" for more details).

#### Shortcut

To create a desktop shortcut, use the shortcut option.
By default, it will place shortcuts on the user desktop.
This can be altered by changing the output file location.
The executable location can be conveniently set to 'link',
so it will be automatically updated when the linked program is changed.

```
usage: carafe m shortcut [-h] [-e EXECUTABLE] [-o OUTPUT_FILE] name

Use 'shortcut' to create a .desktop shortcut to a carafe

positional arguments:
  name                  The name of an existing carafe

optional arguments:
  -h, --help            show this help message and exit
  -e EXECUTABLE, --executable EXECUTABLE
                        Location of the executable inside the carafe to
                        shortcut. Normally a path, but can be set to 'link' as
                        well.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Location of the output file, default is the user
                        desktop
```
Executable location will be asked interactively when not provided as an argument,
in a fairly similar way as is done for the 'link' command.

Shortcuts won't be automatically deleted when a carafe is deleted.

#### Winecfg and Winetricks

Both of these commands only accept the carafe name as the first and only argument.
They will directly execute the winecfg or winetricks command respectively.
In the last paragraph, it's explained how these commands are handled,
and how you can run them directly without using the carafe interface.

### Start a program

For existing carafes, starting the default/linked program should be as straightforward as:

`./carafe <name_of_carafe>`

For example, the default program of an existing carafe for Steam could be started as:

`./carafe steam`

To run a different program inside the Steam carafe, append the command with the location:

`./carafe steam "Program Files (x86)/Internet Explorer/iexplore.exe"`

For the above command, an absolute path from the root of the carafe's C: disk is assumed.

### Further customization

The carafes are created by running prefixed wine commands.
All features available using wine, winecfg, winetricks or any other tool can be used with carafe.

For example, to open the winecfg for a Steam carafe, the following command could be used:

`WINEPREFIX=~/.carafe/steam winecfg`

This is exactly what carafe will do when asked to configure wine like so:

`./carafe manage winecfg steam` or `./carafe m winecfg steam`

The same shortcut is added for winetricks, other tools can use the original wineprefix command.

The advantage of using the carafe shortcut is that the arch and prefix are added automatically.

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

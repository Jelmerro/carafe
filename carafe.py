#!/usr/bin/env python3
# Welcome to the (portable) main file of carafe
# A tiny management tool for wine bottles/carafes/containers
# Program configuration is saved in "~/.carafe"
__author__ = "Jelmer van Arnhem"
# See README.md for more details and usage instructions
__license__ = "MIT"
# See LICENSE for more details and exact terms
__version__ = "1.5.0"
# See https://github.com/jelmerro/carafe for repo and updates

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

# MAIN CONFIG FOLDER LOCATION
# If you really want to, you can change the folder location here
CONFIG_FOLDER = os.path.join(os.path.expanduser("~"), ".carafe")

# CONFIG FILE LOCATION
# It's recommended to leave this path as is and only change the folder location
CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")


# UTIL methods for small/common tasks
def read_config():
    if not os.path.isdir(CONFIG_FOLDER):
        return {}
    if not os.path.isfile(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)
    if config == {}:
        try:
            os.remove(CONFIG_FILE)
        except OSError:
            pass
    return config


def remove_config(name):
    config = read_config()
    config.pop(name, None)
    if config == {}:
        try:
            os.remove(CONFIG_FILE)
        except OSError:
            pass
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f)


def modify_config(name, field, value):
    config = read_config()
    if name not in config:
        config[name] = {}
    config[name][field] = value
    os.makedirs(CONFIG_FOLDER, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f)


def list_carafes():
    carafes = []
    if os.path.isdir(CONFIG_FOLDER):
        for item in os.listdir(CONFIG_FOLDER):
            if os.path.isdir(os.path.join(CONFIG_FOLDER, item)):
                carafes.append(item)
    if carafes:
        print("The following carafes are currently configured:")
        for carafe in carafes:
            print(carafe)
        print(f"Run '{sys.argv[0]} <carafe_name> info' for more information")
    else:
        print("There are currently no carafes configured")
        print(f"Use '{sys.argv[0]} <carafe_name> create' to add a new carafe")
    sys.exit(0)


def check_for_tool(name, location):
    if shutil.which(location):
        return
    print(f"\nThe required tool '{name}' could not be found")
    if location == name:
        print("Please install it using your package manager")
        print("(Most required tools will be installed with wine)\n")
        print(f"Or set a custom location in '{CONFIG_FILE}'")
        print("(You might need to create the file manually)")
        print(f"(In the main object set '{name}' to the correct path)\n")
    else:
        print("The path was manually changed in the config file")
        print(f"The location is set to '{location}'")
        print(f"Please remove the custom location from '{CONFIG_FILE}'")
        print(f"Or update the path to the correct '{name}' location\n")


# Wine command locations, optionally loaded from the config file
# It's recommended to change them manually in the config file and not here
conf = read_config()
WINE = conf.get("wine", "wine")
WINETRICKS = conf.get("winetricks", "winetricks")
check_for_tool("wine", WINE)


# Carafe class for managing and starting carafes
class Carafe:

    def __init__(self, name):
        self.name = name
        self.forbidden_names = ["config.json", "wine", "winetricks"]
        if not self.name:
            print("The current name is not allowed because it appears empty")
            sys.exit(1)
        if self.name in self.forbidden_names:
            print("The current name is not allowed because it is reserved")
            sys.exit(1)
        self.prefix = os.path.join(CONFIG_FOLDER, self.name)
        self.arch = self.read_arch()
        self.link_location = self.read_link()
        self.wine = self.read_wine()

    # Linked functions directly called from the parser

    def create(self, args):
        if os.path.isdir(self.prefix):
            print(
                f"{self.name} is already a carafe\n"
                f"Please see the list with '{sys.argv[0]} list'")
            sys.exit(1)
        os.makedirs(self.prefix, exist_ok=True)
        self.arch = args.arch
        remove_config(self.name)
        if self.arch:
            modify_config(self.name, "arch", self.arch)
        self.run_command(f"{self.wine} wineboot --init")

    def install(self, args):
        self.exists()
        executable = args.executable
        if not executable:
            executable = input(
                "To install a program to the carafe, enter the location: ")
        executable = executable.strip()
        for char in ["'", "\""]:
            if executable.startswith(char) and executable.endswith(char):
                executable = executable.replace(char, "", 1)
                executable = executable[::-1].replace(char, "", 1)[::-1]
        executable = executable.strip()
        if not os.path.isfile(executable):
            print("The specified executable could not be found")
            sys.exit(1)
        if executable.endswith(".msi"):
            self.run_command(f"{self.wine} msiexec /i \"{executable}\"")
        else:
            self.run_command(f"{self.wine} \"{executable}\"")

    def start(self, args):
        self.exists()
        if args.ask:
            start = self.ask_for_executable(True)
            if start == "link":
                start = self.link_location
        elif args.location:
            start = self.try_to_sanitize_location(args.location)
        elif not self.link_location:
            print(
                f"{self.name} has no default/linked program path\n"
                f"Please add one with '{sys.argv[0]} {self.name} link'")
            sys.exit(1)
        else:
            start = self.link_location
        self.arch = self.read_arch()
        path = os.path.join(self.prefix, "drive_c", start)
        arg_string = " "
        for arg in args.arguments:
            arg_string += f"{arg} "
        if args.keep_log:
            self.run_command(
                f"{self.wine} \"{path}\" {arg_string}",
                os.path.dirname(path))
        else:
            env = os.environ
            env["WINEPREFIX"] = self.prefix
            if self.arch:
                env["WINEARCH"] = self.arch
            env["WINEDEBUG"] = "-all"
            subprocess.run(
                f"{self.wine} \"{path}\" {arg_string}", shell=True,
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                cwd=os.path.dirname(path), env=env)

    def rename(self, args):
        self.copy(args)
        self.remove(None)

    def copy(self, args):
        self.exists()
        newname = args.newname.replace(" ", "").replace("/", "-")
        if not newname:
            print("The new name is not allowed because it appears empty")
            sys.exit(1)
        additional_reserved = ["-h", "--help", "list"]
        if newname in self.forbidden_names or newname in additional_reserved:
            print("The new name is not allowed because it is reserved")
            sys.exit(1)
        newpath = os.path.join(CONFIG_FOLDER, newname)
        if os.path.isdir(newpath):
            print(
                f"{newname} is already a carafe\n"
                f"Please see the list with '{sys.argv[0]} list'")
            sys.exit(1)
        shutil.copytree(self.prefix, newpath, symlinks=True)
        if self.arch:
            modify_config(newname, "arch", self.arch)
        if self.link_location:
            modify_config(newname, "link", self.link_location)
        try:
            os.remove(os.path.join(newpath, "log"))
        except OSError:
            pass

    def remove(self, _args):
        remove_config(self.name)
        self.exists()
        shutil.rmtree(self.prefix)
        if not os.listdir(CONFIG_FOLDER):
            shutil.rmtree(CONFIG_FOLDER)

    def info(self, _args):
        self.exists()
        executables = self.list_executables()
        print(f"All information about carafe '{self.name}':")
        if self.arch:
            print(f"Configured with custom arch: {self.arch}")
        else:
            print("Configured with default system arch")
        if self.link_location:
            print("A link for easy startup is configured to the following:")
            print(self.link_location)
        else:
            print("No link is currently configured")
        print(
            "When a carafe is linked, you can start the program with "
            f"'{sys.argv[0]} {self.name} start'")
        print(f"To modify the link, use '{sys.argv[0]} {self.name} link'")
        if executables:
            print("\nThe current list of executables looks like this:")
            for exe in executables:
                print(f"C:/{exe}")
            print(
                f"You can add more with '{sys.argv[0]} {self.name} install'")
        else:
            print("\nThere are currently no executables found for this carafe")
            print(
                f"Please add them with '{sys.argv[0]} {self.name} install'")

    def link(self, args):
        self.exists()
        if args.location:
            loc = self.try_to_sanitize_location(args.location)
        else:
            loc = self.ask_for_executable(False)
        modify_config(self.name, "link", loc)

    def shortcut(self, args):
        self.exists()
        if not os.path.isdir(args.output_folder):
            print("The output folder does not seem to exist")
            sys.exit(1)
        loc = args.location
        if not loc:
            loc = self.ask_for_executable(True)
        elif loc != "link":
            loc = self.try_to_sanitize_location(args.location)
        if args.type:
            shortcut_type = args.type
        else:
            shortcut_type = ""
            print("carafe can make two types of shortcut")
            print("One type needs carafe, but it can auto-update the link")
            print("The other type is a pure wine shortcut, but is static")
            while shortcut_type not in ["carafe", "wine"]:
                shortcut_type = input("Choose the type of shortcut to make: ")
        if shortcut_type == "carafe":
            shortcut_contents = self.carafe_shortcut(loc)
        else:
            shortcut_contents = self.wine_shortcut(loc)
        if args.name:
            file_name = f"{args.name}.desktop"
        else:
            file_name = f"{self.name}.desktop"
        output_file = os.path.join(args.output_folder, file_name)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(shortcut_contents)

    def log(self, _args):
        self.exists()
        log_file = os.path.join(self.prefix, "log")
        if os.path.isfile(log_file):
            with open(log_file, encoding="utf-8") as f:
                print(f.read())
        else:
            print(f"No logs for '{self.name}' carafe yet")

    def regedit(self, _args):
        self.exists()
        self.run_command(f"{self.wine} regedit")

    def winecfg(self, _args):
        self.exists()
        self.run_command(f"{self.wine} winecfg")

    def winetricks(self, args):
        self.exists()
        check_for_tool("winetricks", WINETRICKS)
        arg_string = " ".join(args.arguments)
        self.run_command(f"{WINETRICKS} {arg_string}")

    # Class helper functions

    def exists(self):
        if not os.path.isdir(self.prefix):
            print(
                f"{self.name} is not a known carafe\n"
                f"For a list of all carafes: '{sys.argv[0]} list'\n"
                f"Or add a new one with '{sys.argv[0]} {self.name} create'")
            sys.exit(1)

    def read_link(self):
        config = read_config()
        if self.name in config:
            if "link" in config[self.name]:
                return config[self.name]["link"]
        return None

    def read_wine(self):
        config = read_config()
        if self.name in config:
            if "wine" in config[self.name]:
                return config[self.name]["wine"]
        return WINE

    def read_arch(self):
        config = read_config()
        if self.name in config:
            if "arch" in config[self.name]:
                return config[self.name]["arch"]
        return None

    def run_command(self, command, cwd=None):
        env = os.environ
        env["WINEPREFIX"] = self.prefix
        if self.arch:
            env["WINEARCH"] = self.arch
        log_file = os.path.join(self.prefix, "log")
        with open(log_file, "wb", encoding="utf-8") as output:
            subprocess.run(
                command, shell=True, stderr=output, stdout=output,
                cwd=cwd, env=env)

    def try_to_sanitize_location(self, loc):
        loc = loc.strip()
        if loc.startswith("C:"):
            loc = loc.replace("C:", "", 1)
        if loc.startswith(os.path.join(self.prefix, "drive_c")):
            loc = loc.replace(os.path.join(self.prefix, "drive_c"), "", 1)
        if loc.startswith("/"):
            loc = loc.replace("/", "", 1)
        loc = loc.strip()
        absolute = os.path.join(self.prefix, "drive_c", loc)
        if not os.path.isfile(absolute):
            print("Location provided could not be found")
            sys.exit(1)
        return loc

    def list_executables(self):
        drive_c = os.path.join(self.prefix, "drive_c")
        windows = os.path.join(drive_c, "windows")
        exe_pattern = os.path.join(drive_c, "**", "*.exe")
        executables = []
        exe_files = sorted(glob.glob(exe_pattern, recursive=True))
        for exe in exe_files:
            if not exe.startswith(windows):
                exe = exe.replace(drive_c, "", 1)
                if exe.startswith("/"):
                    exe = exe.replace("/", "", 1)
                executables.append(exe)
        return executables

    def ask_for_executable(self, include_link):
        executables = self.list_executables()
        if not executables:
            print(
                "There are currently no executables found for this carafe")
            print(
                f"Please add them with '{sys.argv[0]} {self.name} install'")
            sys.exit(1)
        for index, exe in enumerate(executables):
            print(f"{index}: C:/{exe}")
        link_text = ""
        if self.link_location and include_link:
            print(f"link: C:/{self.link_location}")
            link_text = " (or choose 'link')"
        chosen_app = -1
        while chosen_app < 0 or chosen_app >= len(executables):
            chosen_app = input(
                "Choose the number of the application "
                f"location{link_text}: ").strip()
            if chosen_app == "link" and link_text:
                break
            try:
                chosen_app = int(chosen_app)
            except ValueError:
                chosen_app = -1
        if chosen_app == "link":
            return "link"
        return executables[chosen_app]

    def carafe_shortcut(self, loc):
        carafe_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        carafe_exec = os.path.join(carafe_dir, os.path.basename(sys.argv[0]))
        if loc == "link":
            command = f"{carafe_exec} {self.name} start"
        else:
            command = f"{carafe_exec} {self.name} start -l \"{loc}\""
        return "#!/usr/bin/env xdg-open\n" \
            "[Desktop Entry]\n" \
            f"Name={self.name}\n" \
            "Type=Application\n" \
            f"Exec={command}\n"

    def wine_shortcut(self, loc):
        if loc == "link":
            loc = self.link_location
        command = f"env WINEPREFIX=\"{self.prefix}\""
        if self.arch:
            command += " WINEARCH=\"{self.arch}\""
        command += f" {self.wine} \"C:/{loc}\""
        path = os.path.dirname(os.path.join(self.prefix, "drive_c", loc))
        return "#!/usr/bin/env xdg-open\n" \
            "[Desktop Entry]\n" \
            f"Name={self.name}\n" \
            "Type=Application\n" \
            f"Exec={command}\n" \
            f"Path={path}\n"


def main():
    # Prepare the main parser
    description = f"Welcome to carafe {__version__}\n" \
        "carafe is a tiny management tool for wine bottles/carafes.\n"
    usage = "carafe {<carafe_name>,list} <sub_command>"
    parser = argparse.ArgumentParser(
        usage=usage,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description,
        epilog=f"carafe was made by {__author__} and is {__license__} licensed"
               "\nFor documentation and other information, see the README.md")
    # Sub commands parser
    sub = parser.add_subparsers(
        title="sub-commands", dest="sub",
        description="All the valid sub-commands to manage the carafes")
    # Create
    sub_create = sub.add_parser(
        "create", help="create a new carafe",
        usage="carafe <carafe_name> create",
        description="Use 'create' to make a new carafe, you should start here")
    sub_create.add_argument(
        "--arch", help="Change the default arch, e.g. to win32")
    # Install
    sub_install = sub.add_parser(
        "install", help="install software to the carafe",
        usage="carafe <carafe_name> install",
        description="Use 'install' to run an ext"
                    "ernal exe/msi inside the carafe")
    sub_install.add_argument(
        "-e", "--executable",
        help="Location of the external executable to run inside the carafe")
    # Start
    sub_start = sub.add_parser(
        "start", help="start an installed program",
        usage="carafe <carafe_name> start",
        description="Use 'start' to start a program inside an existing carafe")
    sub_start.add_argument(
        "-k", "--keep-log", action="store_true",
        help="Keep the wine log (can be multiple GBs and will slow down wine)")
    sub_start.add_argument(
        "-a", "--ask", action="store_true",
        help="Instead of starting the link or --location, ask for the path")
    sub_start.add_argument(
        "-l", "--location",
        help="Location of the executable inside the carafe to start")
    sub_start.add_argument(
        "arguments", nargs=argparse.REMAINDER,
        help="Any arguments will directly be passed to the started executable")
    # Rename
    sub_rename = sub.add_parser(
        "rename", help="rename an existing carafe",
        usage="carafe <carafe_name> rename <new_name>",
        description="Use 'rename' to change the name of an existing carafe")
    sub_rename.add_argument("newname", help="New name of the carafe")
    # Copy
    sub_copy = sub.add_parser(
        "copy", help="copy an existing carafe",
        usage="carafe <carafe_name> copy <new_name>",
        description="Use 'copy' to duplicate an existing carafe to a new one")
    sub_copy.add_argument("newname", help="Name of the new carafe")
    # Remove
    sub.add_parser(
        "remove", help="remove a carafe",
        usage="carafe <carafe_name> remove",
        description="Use 'remove' to delete an existing carafe")
    # Info
    sub.add_parser(
        "info", help="all info about a carafe",
        usage="carafe <carafe_name> info",
        description="Use 'info' to print all information about a carafe")
    # Link
    sub_link = sub.add_parser(
        "link", help="link a program to the carafe",
        usage="carafe <carafe_name> link",
        description="Use 'link' to connect the startup link (recommended)")
    sub_link.add_argument(
        "-l", "--location",
        help="Location of the executable inside the carafe to link")
    # Shortcut
    sub_shortcut = sub.add_parser(
        "shortcut", help="generate a desktop shortcut",
        usage="carafe <carafe_name> shortcut",
        description="Use 'shortcut' to create a .desktop shortcut to a carafe")
    location_help = "Location of the executable inside the carafe to " \
        "shortcut, normally a path, but can be set to 'link' as well"
    sub_shortcut.add_argument(
        "-l", "--location",
        help=location_help)
    sub_shortcut.add_argument(
        "-o", "--output-folder",
        default=os.path.join(os.path.expanduser("~"), "Desktop"),
        help="Which folder to place the shortcut, default is the user desktop")
    sub_shortcut.add_argument(
        "-n", "--name",
        help="Name of the new shortcut, default is the name of the carafe")
    sub_shortcut.add_argument(
        "-t", "--type", choices=["carafe", "wine"],
        help="The type of shortcut to make")
    # Log
    sub.add_parser(
        "log", help="show the last command output",
        usage="carafe <carafe_name> log <new_name>",
        description="Use 'log' to show the output of the last command")
    # Regedit
    sub.add_parser(
        "regedit", help="run regedit",
        usage="carafe <carafe_name> regedit",
        description="Use 'regedit' to edit the windows registry")
    # Winecfg
    sub.add_parser(
        "winecfg", help="run winecfg",
        usage="carafe <carafe_name> winecfg",
        description="Use 'winecfg' to configure all wine settings")
    # Winetricks
    sub_tricks = sub.add_parser(
        "winetricks", help="run winetricks",
        usage="carafe <carafe_name> winetricks <optional_arguments>",
        description="Use 'winetricks' to install winetricks components")
    sub_tricks.add_argument(
        "arguments", nargs=argparse.REMAINDER,
        help="Any arguments will directly be passed to winetricks")
    # Actually handle all the arguments
    args = sys.argv[1:]
    if not args:
        parser.print_help()
        sys.exit(0)
    carafe_name = args.pop(0).replace(" ", "").replace("/", "-")
    if carafe_name == "list":
        list_carafes()
    subargs = parser.parse_args(args)
    if not subargs.sub or carafe_name in ["-h", "--help"]:
        parser.print_help()
        sys.exit(0)
    # Call the correct subcommand on the Carafe class
    carafe = globals()["Carafe"](carafe_name)
    getattr(carafe, subargs.sub)(subargs)


# Main startup steps
if __name__ == "__main__":
    main()

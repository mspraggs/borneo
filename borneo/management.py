from __future__ import absolute_import
from __future__ import print_function

import importlib
import inspect
import os
import sys


def gather_commands():
    """Gathers command main functions in the commands directory"""
    commands_dir = os.path.join(os.path.dirname(__file__), "commands")
    command_files = os.listdir(commands_dir)

    commands = {}
    for command_file in command_files:
        modname = inspect.getmodulename(command_file)
        # Try to import the module
        try:
            module = importlib.import_module("borneo.commands.{}"
                                             .format(modname))
            commands[modname] = module.main
        except (ImportError, AttributeError) as e:
            pass

    return commands


def display_help(argv, commands):
    """Print help for commands"""
    print("Usage: {} subcommand [options] [args]"
          .format(os.path.basename(argv[0])))
    print("Available subcommands:")
    print()
    print("[borneo]")
    commands.sort()
    for command in commands:
        print("    {}".format(command))


def execute_command(argv=None):
    """Locates the specified command in the commands directory and executes its
    main routine"""
    argv = argv or sys.argv
    commands = gather_commands()
    try:
        command = commands[argv[1]]
    except (KeyError, IndexError):
        display_help(argv, commands.keys())
    else:
        command(argv[2:])
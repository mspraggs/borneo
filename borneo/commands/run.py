from __future__ import absolute_import
from __future__ import print_function

import importlib
import sys


def main(argv):
    """Run the specified main function in module"""
    try:
        mod = importlib.import_module(argv[0])
    except IndexError:
        print("Usage: python {} run <module>".format(sys.argv[0]))
        sys.exit()
    mod.main()
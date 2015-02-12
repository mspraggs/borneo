from __future__ import absolute_import

import importlib


def main(argv):
    """Run the specified main function in module"""
    mod = importlib.import_module(argv[0])
    mod.main()
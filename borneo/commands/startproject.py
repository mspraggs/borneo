from __future__ import absolute_import

import importlib
import os
import shutil
import sys


def main(argv):
    """Set up a new project using the template """
    try:
        project_name = argv[0]
    except IndexError:
        print("Usage: {} startproject <project_name>".format(sys.argv[0]))
        sys.exit()
    try:
        location = argv[1]
    except IndexError:
        location = '.'
    location = os.path.abspath(location)
    # Check that the project doesn't already exist
    try:
        sys.path.insert(0, location)
        importlib.import_module(project_name)
    except ImportError:
        sys.path.pop(0)
        pass
    else:
        print("Path {} already exists"
              .format(os.path.join(location, project_name)))
        return
    # Now iterate through the project template and substitute in the
    # template arguments to each file
    template_path = os.path.join(os.path.dirname(__file__),
                                 '../templates/project')
    project_path = os.path.join(location, project_name)
    shutil.copytree(template_path, project_path)
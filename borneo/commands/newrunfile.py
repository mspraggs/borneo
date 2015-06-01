from __future__ import absolute_import
from __future__ import print_function

import os
import sys

import jinja2

from borneo.paths import get_project_path


def main(argv):
    try:
        module = argv[0]
    except IndexError:
        print("Usage: python {} newrunfile <module>".format(sys.argv[0]))
        sys.exit()

    template_path = os.path.join(os.path.dirname(__file__),
                                 '../templates/runfile.py')
    output_path = os.path.join(get_project_path(),
                               module.replace(".", "/") + ".py")

    with open(template_path) as f:
        template = jinja2.Template(f.read())
    with open(output_path, 'w') as f:
        f.write(template.render())
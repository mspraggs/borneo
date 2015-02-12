from __future__ import absolute_import
from __future__ import print_function

import os

from jinja2 import Template

from borneo.config import load_project_config
from borneo.paths import get_project_path


def main(argv):
    study_name = argv[0]
    template_args = {'study_name': study_name}

    template_path = os.path.join(os.path.dirname(__file__),
                                 '../templates/study')
    project_path = get_project_path()
    config = load_project_config()
    layout = os.path.join(project_path, config.LAYOUT)

    study_directory = os.path.dirname(layout.format(study_name=study_name,
                                                    component="foo"))

    try:
        os.makedirs(study_directory)
    except OSError:
        pass

    for filename in os.listdir(template_path):
        with open(os.path.join(template_path, filename)) as f:
            template = Template(f.read())
        study_filepath = layout.format(study_name=study_name,
                                       component=filename)
        with open(study_filepath, 'w') as f:
            f.write(template.render(**template_args))

    with open(os.path.join(study_directory, "__init__.py"), 'a'):
        pass

    for component in ["results", "reports"]:
        try:
            os.makedirs(layout.format(study_name=study_name,
                                      component=component))
        except OSError:
            pass

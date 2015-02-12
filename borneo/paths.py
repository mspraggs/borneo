from __future__ import absolute_import

import os
import sys


def get_project_path(argv=None):
    """Get the project root folder"""
    argv = argv or sys.argv
    return os.path.dirname(os.path.abspath(argv[0]))


def get_study_path(study_name, project_path=None, config=None):
    """Get the path to a specific study"""
    from borneo.config import load_project_config
    project_path = project_path or get_project_path()
    config = config or load_project_config()
    file_path = os.path.join(project_path,
                             config.LAYOUT.format(study_name=study_name,
                                                  component="dummy"))
    return os.path.dirname(file_path)


def get_results_path(study_name, project_path=None, config=None):
    """Get the results path for a specific study"""
    from borneo.config import load_project_config
    project_path = project_path or get_project_path()
    config = config or load_project_config()
    return os.path.join(project_path,
                        config.LAYOUT.format(study_name=study_name,
                                             component="results"))


def make_results_path(filename, study_name, project_path=None, config=None):
    """Concatenate the specified filename with the study results directory"""
    path = os.path.join(get_results_path(study_name, project_path, config),
                        filename)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass
    return path
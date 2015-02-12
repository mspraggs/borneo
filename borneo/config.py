from __future__ import absolute_import

import imp
import os

from borneo.paths import get_project_path


def load_project_config(project_path=None):
    """Loads the project settings foudn in settings.py and returns a Config
    object"""
    project_path = project_path or get_project_path()
    settings_file = os.path.join(project_path, "settings.py")
    config = Config()
    config.from_pyfile(settings_file)
    return config


class Config(object):

    def from_object(self, obj):
        """Load settings from the supplied object"""

        for name in dir(obj):
            if name.isupper():
                attr = getattr(obj, name)
                setattr(self, name, attr)

    def from_dict(self, d):
        """Load the settings from the supplied dictionary"""

        for key, value in d.items():
            if key.isupper():
                setattr(self, key, value)

    def from_pyfile(self, filename):
        """Loads the settings from the supplied file"""

        mod = imp.new_module('settings')
        mod.__file__ = filename
        execfile(filename, mod.__dict__)

        self.from_object(mod)

    def from_envvar(self, envvar):
        """Loads the settings from the file pointed to by the environment
        variable"""

        self.from_pyfile(os.environ[envvar])
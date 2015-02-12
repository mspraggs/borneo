from __future__ import absolute_import
from __future__ import unicode_literals

import os
import shutil

import pytest


@pytest.fixture(scope="session")
def tmp_dir(request):

    tmp_dir = os.path.join(os.path.dirname(__file__),
                           'tmp')
    try:
        os.makedirs(tmp_dir)
    except OSError:
        pass

    request.addfinalizer(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
    return tmp_dir

from __future__ import absolute_import

import os
import shutil
import sys

import pytest

from borneo.config import Config
from borneo.paths import (get_project_path, get_rawdata_path, get_results_path,
                          get_study_path, make_rawdata_path, make_results_path)


@pytest.fixture
def dummy_config():
    """Config object with LAYOUT"""
    config = Config()
    config.from_dict({'LAYOUT': '{study_name}/{component}',
                      'RAWDATA_DIR': 'rawdata'})
    return config


@pytest.fixture
def dummy_project_path(tmp_dir, request):
    """Project path"""
    path = os.path.join(tmp_dir, 'static/project')
    request.addfinalizer(lambda: shutil.rmtree(path, ignore_errors=True))
    return path


def test_get_project_path(dummy_project_path):
    """Test get_project_path"""
    path = get_project_path([os.path.join(dummy_project_path, "blah.py")])
    assert path == dummy_project_path


def test_get_study_path(dummy_config, dummy_project_path):
    """Test get_study_path"""
    path = get_study_path('some_study', dummy_project_path, dummy_config)
    assert path == os.path.join(dummy_project_path, 'some_study')


def test_get_results_path(dummy_config, dummy_project_path):
    """Test get_results_path"""
    path = get_results_path("some_study", dummy_project_path, dummy_config)
    assert path == os.path.join(dummy_project_path, "some_study/results")


def test_make_results_path(dummy_config, dummy_project_path):
    """Test make_results_path"""
    path = make_results_path("blah.txt", "some_study", dummy_project_path,
                             dummy_config)
    assert os.path.exists(os.path.dirname(path))
    assert path == os.path.join(dummy_project_path,
                                "some_study/results/blah.txt")


def test_get_rawdata_path(dummy_config, dummy_project_path):
    """Test get_rawdata_path"""
    path = get_rawdata_path(dummy_project_path, dummy_config)
    assert path == os.path.join(dummy_project_path, "rawdata")


def test_make_rawdata_path(dummy_config, dummy_project_path):
    """Test make_rawdata_path"""
    path = make_rawdata_path("foo", dummy_project_path, dummy_config)
    assert path == os.path.join(dummy_project_path, "rawdata/foo")
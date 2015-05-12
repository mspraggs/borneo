from __future__ import absolute_import

from borneo.management import gather_commands


def test_gather_commands():
    """Test gather_commands"""
    commands = gather_commands()
    assert set(commands.keys()) == {"run", "shell", "startproject",
                                    "startstudy"}

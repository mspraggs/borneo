from setuptools import setup, find_packages

EXCLUDE_FROM_PACKAGES = ['borneo.templates',
                         'borneo.bin']

setup(
    name="borneo",
    version="0.0.0",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    scripts=['borneo/bin/borneo-admin.py'],
    entry_points={'console_scripts': [
        'borneo-admin = borneo.management:execute_command',
    ]},
)

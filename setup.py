from codecs import open
from os import path
import sys
from setuptools import setup, find_packages
import setuptools.command.build_py
from advancedactionscheduler.version import __version__

def on_windows():
    return sys.platform == "win32"
    
def on_linux():
    return sys.platform == "linux"

try:
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
        readme = readme_file.read()

    with open(path.join(here, 'HISTORY.rst'), encoding='utf-8') as history_file:
        history = history_file.read().replace('.. :changelog:', '')
except FileNotFoundError:
    readme = ""
    history = ""

install_requires = ["apscheduler", "psutil"]

if on_windows():
    extras_requires = ["wxPython", "pypiwin32"]
    install_requires.extend(extras_requires)
    found_packages=find_packages(exclude=['docs', 'resources', 'snap', 'tests*', 'linux'])
elif on_linux():
    extras_requires = ["wxpython-installer"]
    install_requires.extend(extras_requires)
    found_packages=find_packages(exclude=['docs', 'resources', 'snap', 'tests*', 'win'])
else:
    raise Exception("Advanced Action Scheduler does not support your platform: %s" % sys.platform)
    
test_requirements = []

setup(
    name='advanced-action-scheduler',
    version=__version__,
    description="Advanced Action + Task Scheduler",
    long_description=readme + '\n\n' + history,

    # Author details
    author="Simon Wu",
    author_email='swprojects@runbox.com',

    # The project's main homepage.
    url='https://github.com/swprojects/advanced-action-scheduler',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=found_packages,

    # Dependent packages (distributions)
    install_requires=install_requires,
    
    license="GPLv2",
    
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # 'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv2)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
          'gui_scripts': [
              # 'zippyscan = zippyipscanner.zippyipscanner:main'
          ]
      },
    
)
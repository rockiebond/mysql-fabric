#
# Copyright (c) 2013,2014, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#

import ConfigParser
import distutils
import fnmatch
import glob
import os
import sys

from distutils.core import setup, Command
from distutils.util import change_root
from distutils.sysconfig import get_python_lib
from distutils.command.install_data import install_data as _install_data
from distutils.command.build_scripts import build_scripts as _build_scripts
from distutils import log

def fetch_version(module_name):
    """Retrieve information on Fabric version within *module_name*.
    """
    mod = __import__(module_name, globals(), locals(), ['__version__'])
    return mod.__version__

def find_packages(*args, **kwrds):
    """Find all packages and sub-packages and return a list of them.

    The function accept any number of directory names that will be
    searched to find packages. Packages are identified as
    sub-directories containing an __init__.py file.  All duplicates
    will be removed from the list and it will be sorted
    alphabetically.

    Packages can be excluded by pattern using the 'exclude' keyword,
    which accepts a list of patterns.  All packages with names that
    match the beginning of an exclude pattern will be excluded.
    """
    from fnmatch import fnmatch
    excludes = kwrds.get('exclude', [])
    pkgs = {}
    for base_path in args:
        for root, _dirs, files in os.walk(base_path):
            if '__init__.py' in files:
                assert root.startswith(base_path)
                pkg = root[len(base_path)+1:].replace(os.sep, '.')
                pkgs[pkg] = root

    result = pkgs.keys()
    for excl in excludes:
        # We exclude packages that *begin* with an exclude pattern.
        result = [pkg for pkg in result if not fnmatch(pkg, excl + "*")]
    result.sort()
    return result

def check_connector():
    """Check if connector is properly installed.

    It returns a tuple with the following information:
    * Installed - Indicates whether the connector is properly installed
                  or not.
    * Path MySQL - Path to the package *mysql*.
    * Connector Path - Path to the package *mysql.connector*.
    """
    path_connector = None
    path_mysql = None
    try:
        import mysql
        path_mysql = os.path.dirname(mysql.__file__)

        import mysql.connector
        path_connector = os.path.dirname(mysql.connector.__file__)

        return True, path_mysql, path_connector
    except ImportError as error:
        return False, path_mysql, path_connector

def check_sphinx():
    """Check if sphinx is properly installed.

    It returns a tuple with the following information:
    * Installed - Indicates whether sphinx is properly installed
                  or not.
    * Sphinx Path - Path to the package *sphinx*.
    """
    path_sphinx = None
    try:
        import sphinx
        path_sphinx = os.path.dirname(sphinx.__file__)
        return True, path_sphinx
    except ImportError as error:
        return False, path_sphinx

def check_fabric():
    """Check if Fabric is properly built/installed.

    It returns a tuple with the following information:
    * Installed - Indicates whether Fabric is properly installed
                  or not.
    * Path MySQL - Path to the package *mysql*.
    * Fabric Path - Path to the package *mysql.fabric*.
    """
    path_fabric = None
    path_mysql = None
    try:
        import mysql
        path_mysql = os.path.dirname(mysql.__file__)

        import mysql.fabric
        path_fabric = os.path.dirname(mysql.fabric.__file__)
        return True, path_mysql, path_fabric
    except ImportError as error:
        return False, path_mysql, path_fabric

def check_path_for_docs(directory):
    """Set the path to ** when documentation is being generated and
    check whether fabric and connector python are properly installed
    or not.
    """
    fix_path(directory)

    result, path_mysql, path_connector = check_connector()
    if not result:
        sys.stderr.write(
            "Tried to look for mysql.connector at (%s).\n" % \
            (path_mysql, )
            )
        sys.stderr.write(
            "Sphinx was supposed to use (%s).\n" % \
            (sys.path[0])
            )
        exit(1)

    result, path_myql, path_fabric = check_fabric()
    if not result:
        sys.stderr.write(
            "Tried to look for mysql.fabric at (%s).\n" % \
            (path_mysql, )
            )
        sys.stderr.write(
            "Sphinx was supposed to use (%s).\n" % \
            (sys.path[0])
            )
        exit(1)

def fix_path(directory):
    """Fix path by pointing to the appropriate directory.
    """
    sys.path.insert(0, os.path.abspath(directory))

#
# If Sphinx is installed, create a documentation builder based
# on it. Otherwise, create a fake builder just to report something
# when --help-commands are executed so that users may find out
# that it is possible to build the documents provided Sphinx is
# properly installed.
#
result, path_sphinx = check_sphinx()
if result:
    import sphinx.setup_command as _sphinx
    class build_docs(_sphinx.BuildDoc):
        """Create documentation using Sphinx.
        """
        user_options = _sphinx.BuildDoc.user_options + [
            ("code-dir=", None, "Look for code in the directory"),
            ]

        description = "Create documentation using sphinx"

        def initialize_options(self):
            _sphinx.BuildDoc.initialize_options(self)
            self.code_dir = None

        def finalize_options(self):
            _sphinx.BuildDoc.finalize_options(self)
            if not self.code_dir:
                self.use_directory = get_python_lib()
            else:
                self.use_directory = self.code_dir

        def run(self):
            check_path_for_docs(self.use_directory)
            _sphinx.BuildDoc.run(self)
else:
    class build_docs(Command):
        """Create documentation. Please, install sphinx.
        """
        user_options = [
            ('unknown', None, "Sphinx is not installed. Please, install it."),
            ]
        description = "create documentation. Please, install sphinx"

        def initialize_options (self):
            pass

        def finalize_options (self):
            pass

        def run(self):
            sys.stderr.write(
                "Sphinx is not installed. Please, install it.\n"
                )
            exit(1)

# We need to edit the configuration file before installing it
class install_data(_install_data):
    def run(self):
        from itertools import groupby

        # Set up paths to write to config file
        install_dir = self.install_dir
        install_logdir = '/var/log'
        if os.name == 'posix' and install_dir in ('/', '/usr'):
            install_sysconfdir = '/etc'
        else:
            install_sysconfdir = os.path.join(install_dir, 'etc')

        # Go over all entries in data_files and process it if needed
        data_files = []
        for df in self.data_files:
            # Figure out what the entry contain and collect a list of files.
            from_tuple = False
            if isinstance(df, str):
                # This was just a file name, so it will be installed
                # in the install_dir location. This is a copy of the
                # behaviour inside distutils intall_data.
                directory = install_dir
                filenames = [df]
                from_tuple = False
                if self.warn_dir:
                    self.warn("setup script did not provide a directory for "
                              "'%s' -- installing somewhere under '%s' or "
                              "'%s'" % (df, install_dir, install_sysconfdir))
            else:
                directory = df[0]
                filenames = df[1]
                from_tuple = True

            # Process all the files for the entry and build a list of
            # tuples (directory, file)
            for filename in filenames:
                # It was a config file template, add install
                # directories to the config file.
                if fnmatch.fnmatch(filename, 'data/*.cfg.in'):

                    if not os.path.isabs(directory):
                        directory = directory if from_tuple else "mysql"
                        directory = os.path.join(install_sysconfdir, directory)
                    elif self.root:
                        directory = change_root(self.root, directory)

                    config = ConfigParser.RawConfigParser({
                            'prefix': install_dir,
                            'logdir': install_logdir,
                            'sysconfdir': install_sysconfdir,
                            })
                    config.readfp(open(filename))
                    filename = os.path.splitext(filename)[0]
                    config.write(open(filename, "w"))

                data_files.append((directory, filename))

        # Re-construct the data_files entry from what was provided by
        # merging all tuples with same directory and provide a list of
        # files as second item, e.g.:
        #   [('foo', 1), ('bar', 2), ('foo', 3), ('foo', 4), ('bar', 5)]
        #   --> [('bar', [2, 5]), ('foo', [1, 3, 4])]
        data_files.sort()
        data_files = [
            (d, [ f[1] for f in fs ]) for d, fs in groupby(data_files, key=lambda x: x[0])
            ]
        self.data_files = data_files
        _install_data.run(self)

class build_scripts(_build_scripts):
    """Class for providing a customized version of build_scripts.

    When ``run`` is called, this command class will:
    1. Create a copy of all ``.py`` files in the **scripts** option
       that does not have the ``.py`` extension.
    2. Replace the list in the **scripts** attribute with a list
       consisting of the script files with the ``.py`` extension
       removed.
    3. Call run method in `distutils.command.build_scripts`.
    4. Restore the scripts list to the old value, for other commands
       to use.
    """
    def run(self):
        if not self.scripts:
            return

        saved_scripts = self.scripts
        self.scripts = []
        for script in saved_scripts:
            script = distutils.util.convert_path(script)
            script_copy, script_ext = os.path.splitext(script)

            if script_ext != '.py':
                log.debug("Not removing extension from {script} "
                          "since it's not '.py'".format(script=script))
            else:
                log.debug("Copying {orig} -> {dest}".format(
                    orig=script, dest=script_copy))
                self.copy_file(script, script_copy)
                self.scripts.append(script_copy)
        # distutils is compatible with 2.1 so we cannot use super() to
        # call it.
        _build_scripts.run(self)
        self.outfiles = self.scripts
        self.scripts = saved_scripts

    def get_outputs(self):
        """Get installed files"""
        return self.outfiles

META_INFO = {
    'name': "mysql-fabric",
    'license': "GPLv2",
    'description': "Management system for MySQL deployments",
    'packages': find_packages("lib", exclude=["tests"]),
    'package_dir': {
        '': 'lib',
        },
    'requires': [
        'mysql.connector (>=1.2.2)',
        ],
    'scripts': [
        'scripts/mysqlfabric.py',
        ],
    # The install_data version above will recognize everything that
    # matches *.cfg (after template processing) and install the file
    # relative configuration directory instead of the data directory.
    'data_files' : [
        ('mysql', ['data/fabric.cfg.in']),
        ],
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Database Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    'cmdclass': {
        'build_docs' : build_docs,
        'install_data': install_data,
        },
}

if os.name != "nt":
    META_INFO['cmdclass'].update({
        'build_scripts': build_scripts,
        })

#
# When building the documentation that path is fixed based on
# the --code-dir option within the build_docs class.
#
if "build_docs" not in sys.argv:
    fix_path("lib")
    META_INFO ['version'] = fetch_version('mysql.fabric')
setup(**META_INFO)

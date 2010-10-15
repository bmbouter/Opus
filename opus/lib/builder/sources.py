##############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
##############################################################################

"""Contains routines for manipulating applications from various sources

Copy functions
--------------
Each method takes two parameters, a source, and a destination.
The source string is source specific, probably a URL of some sort.
The destination string is a local directory path, where the destination app
should go.

The functions are expected to create dst directory and put the app contents in
it

The functions should not return anything, they should raise a CopyError on
error.

To copy an app, use the install_app() function

Upgrade functions
-----------------
These functions take a source directory, and some parameter specifying the
version to upgrade to. This parameter is source specific. For example, with git
it will be a revision identifier.

To choose the right upgrade function, consult the upgrade_functions mapping

Introspection Functions
-----------------------
Use the introspect_source function to attempt to determine what kind of app it
is.

Version Functions
-----------------
These attempt to retrieve the version information from an app.

Use the version_functions mapping to choose the right version function for the
app type.

"""

import shutil
import subprocess
import os.path
import os

import opus.lib.builder

# Where the repositories are actually cloned into under the project directory
APPDIR = "apprepos"

class CopyError(Exception):
    pass

def fromfilesys(src, dst):
    """Copies an application already on the local filesystem"""
    shutil.copytree(src, dst)

def fromgit(src, dst):
    """src is a git compatible URL to a git repository"""
    if "#" in src:
        src, rev = src.split("#", 1)
    else:
        rev = None
    proc = subprocess.Popen(["git", "clone", "--", src, dst],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
    output = proc.communicate()[0]
    ret = proc.wait()
    if ret:
        raise CopyError("Could not copy. Git returned {0}".format(output))
    if rev:
        upgradegit(dst, rev)

def fromhg(src, dst):
    if src.startswith("-") or dst.startswith("-"):
        raise ValueError("Bad src or dst")
    proc = subprocess.Popen(["hg", "clone", src, dst],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
    output = proc.communicate()[0]
    ret = proc.wait()
    if ret:
        raise CopyError("Could not copy. Mercurial returned {0}".format(output))

def install_app(apppath, appname, apptype, projectdir):
    """Copies the app into the project directory"""
    copy_functions = {
            'file': fromfilesys,
            'git': fromgit,
            'hg': fromhg,
            }
    try:
        cf = copy_functions[apptype]
    except KeyError:
        raise CopyError("App type not supported")

    # Copy the app into the app dir
    dst = os.path.join(projectdir, APPDIR, appname)
    cf(apppath, dst)

    # Detect whether this application is in "bare" form with application data
    # in the top most level of the repository, or in "package" form with the
    # application being one level removed and the top level containing a
    # setup.py, readme, license, etc.
    bare = -1 # unknown
    
    # The existance of a metadatafile in the application is a very good
    # indicator
    if os.path.exists(os.path.join(dst, "metadata.json")):
        bare = True
    if os.path.exists(os.path.join(dst, appname, "metadata.json")):
        bare = False

    if bare == -1:
        # Check for a models file
        if os.path.exists(os.path.join(dst, "models.py")):
            bare = True
        if os.path.exists(os.path.join(dst, appname, "models.py")):
            bare = False
    if bare == -1:
        # Check for a views.py file
        if os.path.exists(os.path.join(dst, "views.py")):
            bare = True
        if os.path.exists(os.path.join(dst, appname, "views.py")):
            bare = False

    if bare == -1:
        raise CopyError("Could not detect repository format. Please make sure your application has one of these files: metadata.json, models.py, or views.py")

    # Now symlink the application into the project itself
    if bare:
        os.symlink(dst, os.path.join(projectdir, appname))
    else:
        os.symlink(os.path.join(dst, appname),
                os.path.join(projectdir, appname))


###################
# Upgrade functions
###################

def upgradefile(path, to):
    raise NotImplementedError()

def upgradegit(path, to):
    proc = subprocess.Popen(["git", "fetch"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            )
    output = proc.communicate()[0]
    ret = proc.wait()
    if ret:
        raise opus.lib.builder.BuildException("git fetch failed. Ret: {0}, Output: {1}"\
                .format(ret, output))

    proc = subprocess.Popen(['git', 'reset', '--hard', to],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            )
    output = proc.communicate()[0]
    ret = proc.wait()
    if ret:
        raise opus.lib.builder.BuildException("git reset failed. Ret: {0}, Output: {1}"\
                .format(ret, output))

upgrade_functions = {
        'file': upgradefile,
        'git': upgradegit,
        'hg': upgradefile, # not implemented yet
        }

#########################
# Introspection functions
#########################

def is_git(apppath):
    return os.path.exists(os.path.join(apppath, ".git"))

def is_hg(apppath):
    return os.path.exists(os.path.join(apppath, ".hg"))

def introspect_source(apppath):
    """Attempts to determine the source of the given application.

    """
    if is_git(apppath):
        return 'git'
    if is_hg(apppath):
        return 'hg'

    return 'file'
    

#######################
# Get Version Functions
#######################

def file_version(apppath):
    return "N/A"

def git_version(apppath):
    proc = subprocess.Popen(["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=apppath,
            )
    output = proc.communicate()[0]
    ret = proc.wait()
    if ret:
        raise opus.lib.builder.BuildException("git rev-parse failed. Ret: {0}, Output: {1}".format(ret, output))
    return output

version_functions = {
        'file': file_version,
        'git': git_version,
        }

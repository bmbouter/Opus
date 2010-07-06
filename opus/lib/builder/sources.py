"""Contains routines for manipulating applications from various sources

Copy functions
--------------
Each method takes two parameters, a source, and a destination.
The source string is source specific, probably a URL of some sort.
The destination string is a local directory path, where the destination app
should go.

The functions are expected to create a dst/appname directory and put the app
contents in it

The functions should not return anything, they should raise a CopyError
on error.

To choose the right copy function, consult the copy_functions mapping

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

import opus.lib.builder

class CopyError(Exception):
    pass

def fromfilesys(src, dst):
    """Copies an application already on the local filesystem"""
    # Get the name:
    srcpath, name = os.path.split(src)
    if srcpath and not name:
        # Trailing slash? Split agian
        srcpath, name = os.path.split(srcpath)
    shutil.copytree(src, os.path.join(dst, name))

def fromgit(src, dst):
    """src is a git compatible URL to a git repository"""
    proc = subprocess.Popen(["git", "clone", src],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=dst)
    output = proc.communicate()[0]
    ret = proc.wait()
    if ret:
        raise CopyError("Could not copy. Git returned {0}".format(output))

copy_functions = {
        'file': fromfilesys,
        'git': fromgit,
        }

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
        }

#########################
# Introspection functions
#########################

def is_git(apppath):
    return os.path.exists(os.path.join(apppath, ".git"))

def introspect_source(apppath):
    """Attempts to determine the source of the given application.

    """
    if is_git(apppath):
        return 'git'

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

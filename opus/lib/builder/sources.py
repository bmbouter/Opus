"""Contains routines for copying applications from various sources

Each method takes three parameters, a source, a destination, and an app name.
The source string is source specific, probably a URL of some sort.
The destination string is a local file path, where the destination app should go.

The functions are expected to create a dst/appname directory and put the app
contents in it

The functions should not return anything, they should raise a CopyError
on error.

"""

import shutil
import subprocess

copy_functions = {
        'file': fromfile,
        'git': fromgit,
        }

class CopyError(Exception):
    pass

def fromfile(src, dst, appname):
    shutil.copytree(src, os.path.join(dst, appname))

def fromgit(src, dst, appname):
    """src is a git compatible URL to a git repository"""
    proc = subprocess.Popen(["git", "clone", src, os.path.join(dst, appname)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.communicate()[0]
    ret = proc.wait()
    if ret:
        raise CopyError("Could not copy. Git returned {0}".format(output))

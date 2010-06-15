"""Contains routines for copying applications from various sources

Each method takes two parameters, a source, and a destination.
The source string is source specific, probably a URL of some sort.
The destination string is a local directory path, where the destination app
should go.

The functions are expected to create a dst/appname directory and put the app
contents in it

The functions should not return anything, they should raise a CopyError
on error.

"""

import shutil
import subprocess
import os.path

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

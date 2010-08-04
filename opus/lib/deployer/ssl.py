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

"""Module contining routines for generating a self-signed ssl certificate for
running servers until a user uploads their own certificate

"""
import subprocess
import os.path

def gen_cert(filename, directory, server="localhost.localdomain"):
    """Generate two files, a cert and a key file.
    The cert and key files will be named `filename`.crt and `filename`.key.
    They will be placed in the given directory.

    If server is given, that will be the CN

    """

    input = """--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
{server}
root@{server}
""".format(server=server)
    keyout = os.path.join(directory, filename+".key")
    certout = os.path.join(directory, filename+".crt")
    
    proc = subprocess.Popen(["/usr/bin/openssl",
        'req',
        '-newkey', 'rsa:1024',
        '-keyout', keyout,
        '-nodes',
        '-x509',
        '-days', '365',
        '-out', certout,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        )

    output = proc.communicate(input)[0]
    ret = proc.wait()
    if ret:
        from opus.lib.deployer import DeploymentException
        raise DeploymentException("openssl returned {0}. Output: {1}".format(ret, output))

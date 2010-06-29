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

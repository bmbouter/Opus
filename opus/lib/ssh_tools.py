import subprocess
import time
import socket
import select

from django.conf import settings

#Provide Logging
import opus.lib.log
log = opus.lib.log.getLogger()

class HostNotConnectableError(Exception):
    pass

class NodeUtil(object):
    """Represents a remote machine."""

    # SSH commands should use -p SSH_PORT
    SSH_PORT = 22

    def __init__(self, ip, key, username = 'root'):
        """Stores the ip address that we use to connect to it.

        """
        self.ip = ip
        self.key = key
        self.username = username

    def ssh_run_command(self, cmd):
        """Runs a command on the remote machine with the given options.

        Returns a string of the command's output.  This is a blocking call.
        cmd is a list of strings, the first is the command to run, and the rest
        are arguments.

        """
        if not self.ssh_avail():
            raise HostNotConnectableError
        command = ["ssh",
                "-l", self.username,
                "-p", str(self.SSH_PORT),
                "-i", self.key,
                "-o", "StrictHostKeyChecking=no",
                "-o","UserKnownHostsFile=/dev/null",
                self.ip,
                ]
        command.extend(cmd)
        log.warning(' '.join(command))
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]

    def ssh_avail(self):
        """Is ssh available?
        
        Attempts to connect to ssh just enough to see if it's running.
        Returns False if it's not running, True if it is.
        Blocks for a maximum of 1 second.

        """
        remote = socket.socket()
        remote.settimeout(1)
        try:
            remote.connect((self.ip, self.SSH_PORT))
            ready = select.select([remote], [], [], 0) # poll
            if not ready:
                # no data
                return False
            data = remote.recv(256)
            if not data.startswith("SSH"):
                # Something else is listening on that port
                return False
            return True

        except socket.error, e:
            return False

        finally:
            remote.close()

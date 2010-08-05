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

import string

from opus.lib.ssh_tools import NodeUtil, HostNotConnectableError
from generic import Generic

from opus.lib import log
log = log.getLogger()


class Linux(Generic):
    def __init__(self, ip, ssh_key):
        self.ip = ip
        self.ssh_key = ssh_key
        self.node = NodeUtil(ip, ssh_key)
        self.check_user_load()

    def add_user(self, username, password):
        try:
            output = self.node.ssh_run_command(["adduser", username])
            output = self.change_user_password(username, password)
            log.debug('THE PASSWORD WAS SET')
            log.debug("Added %s" % username)
            return True, ""
        except HostNotConnectableError:
            return False, ""


    def change_user_password(self, username, password):
        try:
            output = ssh_node.ssh_run_command(["passwd", "--stdin", username, "<<<", password])
            return output
        except HostNotConnectableError:
            return False


    def log_user_off(self, username):
        try:
            output = self.node.ssh_run_command(["pkill", "-KILL", "-u", str(username)])
            log.debug("Logged %s off" % username)
            return output
        except HostNotConnectableError:
            return False


    def add_administrator(self, username):
        try:
            self.node.ssh_run_command(["chmod", "+w", "/etc/sudoers",
                                        "|", "echo", "'%s ALL=(ALL) ALL'" % username, ">>", "/etc/sudoers",
                                        "|", "chmod", "-w", "/etc/sudoers"])
            return True
        except HostNotConnectableError:
            return False


    def check_user_load(self):
        self.sessions = []
        try:
            output = self.node.ssh_run_command(["w"])
            output = output.split('WHAT')[1]
            for line in output.split('\n'):
                fields = line.split()
                if (len(fields) > 1):
                    user = dict()
                    for i,value in enumerate(fields):
                        if(i == 0):
                            user["username"] = string.rstrip(value)
                        if(i == 1):
                            user["sessionid"] = string.rstrip(value)
                        if(i == 4):
                            user["idletime"] = string.rstrip(value)
                        if(i == 3):
                            user["logontime"] = string.rstrip(value)
                    if (len(user) == 4):
                        self.sessions.append(user)
            return self.sessions
        except HostNotConnectableError:
            return False


    def user_cleanup(self, timeout):
        """
        Checks idle time for all sessions on the node.  If any session is disconnected then the user   
        is logged off.  If the idle time exceeds the timeout parameter, the user is logged off. Timeout
        is in MINUTES.
        """
        log.debug(self.sessions)
        for session in self.sessions:
            log.debug("Reported idletime: " + session["idletime"])
            if 's' in session["idletime"]:
                seconds = session["idletime"].split('s')[0]
                idletime = float(seconds) / 60
            elif 'm' in session["idletime"]:
                idletime = session["idletime"].split('m')[0].split(':')
                minutes = idletime[1]
                hours = idletime[0]
                idletime = int(hours) * 60 + int(minutes)
            elif 'days'in session["idletime"]:
                days = session["idletime"].split('days')[0]
                idletime = float(days) * 24 * 60
            else:
                idletime = session["idletime"].split(':')
                minutes = idletime[0]
                seconds = idletime[1]
                idletime = int(minutes) + (int(seconds) / 60)
            log.debug("Calculated idle time: "+str(idletime))
            if(idletime > timeout):
                self.log_user_off(session["username"])
                

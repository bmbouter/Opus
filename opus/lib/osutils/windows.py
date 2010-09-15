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

from re import split
import string

from opus.lib.ssh_tools import NodeUtil, HostNotConnectableError
from generic import Generic

from opus.lib import log
log = log.get_logger("opus.lib.osutils")

class Windows(Generic):
    def __init__(self, ip, ssh_key):
        self.ip = ip
        self.ssh_key = ssh_key
        self.node = NodeUtil(ip, ssh_key)
        self.check_user_load()

    def add_user(self, username, password):
        try:
            output = self.node.ssh_run_command(["NET", "USER", username, password,"/ADD"])
            if output.find("The command completed successfully.") > -1:
                log.debug("User %s has been created" % username)
            elif output.find("The account already exists.") > -1:
                log.debug('User %s already exists, going to try to set the password' % username)
                output = self.change_user_password(username, password)
                if output.find("The command completed successfully.") > -1:
                    log.debug('THE PASSWORD WAS RESET')
                else:
                    error_string = 'An unknown error occured while trying to set the password for user %s on machine %s.  The error from the machine was %s' % (username, self.ip, output)
                    log.error(error_string)
                    return False, error_string
            else:
                error_string = 'An unknown error occured while trying to create user %s on machine %s.  The error from the machine was %s' % (username, self.ip, output)
                log.error(error_string)
                return False, error_string
            return True, ""
        except HostNotConnectableError:
            return False, ""


    def change_user_password(self, username, password):
        try:
            output = self.node.ssh_run_command(["NET", "USER", username, password])
            return output
        except HostNotConnectableError:
            return False

    def enable_rdp_for_user(self, username):
        try:
            self.node.ssh_run_command(["NET", "localgroup", '"Remote Desktop Users"', "/add", username])
            return True
        except HostNotConnectableError:
            return False

    def add_administrator(self, username):
        try:
            self.node.ssh_run_command(["NET", "localgroup", '"Administrators"', "/add", username])
            return True
        except HostNotConnectableError:
            return False


    def log_user_off(self, username):
        try:
            output = self.node.ssh_run_command(["c:\logoff.exe", str(username)])
            return output
        except HostNotConnectableError:
            return False


    def check_user_load(self):
        try:
            self.sessions = []
            output = self.node.ssh_run_command(["Quser"])
            for line in output.split('\n'):
                fields = split("(\S+) +(\d+) +(Disc) +([none]*[\d+\+]*[\. ]*[\d*\:\d* ]*[\d ]*) (\d*/\d*/\d*) +(\d*\:\d* +[AM]*[PM]*)",line)
                if (len(fields) > 1):
                    user = dict()
                    for i,value in enumerate(fields):
                        if(i == 1):
                            user["username"] = string.rstrip(value)
                        if(i == 2):
                            user["sessionid"] = string.rstrip(value)
                        if(i == 3):
                            user["state"] = string.rstrip(value)
                        if(i == 4):
                            user["idletime"] = string.rstrip(value)
                        if(i == 5):
                            user["logondate"] = string.rstrip(value)
                        if(i == 6):
                            user["logontime"] = string.rstrip(value)
                    if (len(user) == 6):
                        self.sessions.append(user)

                else:
                    fields = split("(\S+) +(\S+) +(\d+) +(Active) +([none]*[\d+\+]*[\. ]*[\d*\:\d* ]*[\d ]*) (\d*/\d*/\d*) +(\d*\:\d* +[AM]*[PM]*)",line)
                    user = dict()
                    for i,value in enumerate(fields):
                        if(i == 1):
                            user["username"] = string.rstrip(value)
                        if(i == 2):
                            user["sessionname"] = string.rstrip(value)
                        if(i == 3):
                            user["sessionid"] = string.rstrip(value)
                        if(i == 4):
                            user["state"] = string.rstrip(value)
                        if(i == 5):
                            user["idletime"] = string.rstrip(value)
                        if(i == 6):
                            user["logondate"] = string.rstrip(value)
                        if(i == 7):
                            user["logontime"] = string.rstrip(value)
                    if (len(user) == 7):
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
            log.debug("Reported idletime: "+session["idletime"])
            if(session["state"] == "Disc"):
                self.log_user_off(session["sessionid"])
            elif((session["idletime"] == ".") or (session["idletime"] == "none")):
                continue
            else:
                days = session["idletime"].split("+")
                if(len(days) > 1):
                    idletime = 24*60*int(days[0])
                    for i,digit in enumerate(days[1].split(":")):
                        if(i == 0):
                            idletime += 60*int(digit)
                        else:
                            idletime += int(digit)
                else:
                    idletime = 0
                    hoursandmins = days[0].split(":")
                    if(len(hoursandmins) > 1):
                        idletime += 60*int(hoursandmins[0])
                        idletime += int(hoursandmins[1])
                    else:
                        idletime += int(hoursandmins[0])
                log.debug("Calculated idle time: "+str(idletime))
                if(idletime > timeout):
                    self.log_user_off(session["sessionid"])

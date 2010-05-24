from core.ssh_tools import NodeUtil, HostNotConnectableError
from generic import Generic

from core import log
log = log.getLogger()

class Windows(Generic):
    def __init__(self, ip, ssh_key):
        self.ip = ip
        self.ssh_key = ssh_key
        self.node = NodeUtil(ip, ssh_key)

    def add_user(self, username, password):
        try:
            output = self.node.ssh_run_command(["NET", "USER", username, password,"/ADD"])
            if output.find("The command completed successfully.") > -1:
                log.debug("User %s has been created" % username)
            elif output.find("The account already exists.") > -1:
                log.debug('User %s already exists, going to try to set the password' % username)
                output = change_user_password(username, password)
                if output.find("The command completed successfully.") > -1:
                    log.debug('THE PASSWORD WAS RESET')
                else:
                    error_string = 'An unknown error occured while trying to set the password for user %s on machine %s.  The error from the machine was %s' % (request.session['username'],host.ip,output)
                    log.error(error_string)
                    return False, error_string
            else:
                error_string = 'An unknown error occured while trying to create user %s on machine %s.  The error from the machine was %s' % (request.session['username'],host.ip,output)
                log.error(error_string)
                return False, error_string
            return True
        except HostNotConnectableError:
            return False


    def change_user_password(self, username, password):
        try:
            output = self.node.ssh_run_command(["NET", "USER", username, password])
            return output
        except HostNotConnectableError:
            return False


    def log_user_off(self, username):
        try:
            output = self.node.ssh_run_command(["c:\logoff.exe", str(username)])
            log.debug('$#$#$#  %s'%output)
            if (len(output) == 0):
                log.debug('LOGGED OFF WINDOWS USER')
                return True
            else:
                return False
        except HostNotConnectableError:
            return False


    def check_user_load(self):
        try:
            output = self.node.ssh_run_command(["Quser"])
            return output
        except HostNotConnectableError:
            return False


    def add_administrator(username):
        try:
            self.node.ssh_run_command(["NET", "localgroup",'"Administrators"',"/add",request.session['username']])
            return True
        except HostNotConnectableError:
            return False


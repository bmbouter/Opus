import string

from core.ssh_tools import NodeUtil, HostNotConnectableError
from generic import Generic

from core import log
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
            if output.find("user %s exists" % username) > -1:
                log.debug('User %s already exists, going to try to set the password' % username)
                output = self.change_user_password(username, password)
                log.debug('THE PASSWORD WAS RESET')
            else:
                log.debug("Added %s" % username)
            return True, ""
        except HostNotConnectableError:
            return False, ""


    def change_user_password(self, username, password):
        try:
            output = self.node.ssh_run_command(["echo", "%s:%s" % (username, password), "|", "chpasswd"])
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
                

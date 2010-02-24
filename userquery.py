from subprocess import Popen, PIPE
import re, string



class VMInstance:
    sessions = list()
    ip = "";

    def __init__(self,ip):
        self.ip = ip
        self.check_user_load(self.sessions)

    '''
    Create an SSH pipe to the specified ip and store all sessions information in list. 
    Each session is stored as a dictionary containing username, sessionname, session id, idle time, 
    logon date, logon time. The two possible states are Active and Disc (disconnected).
    '''
    def check_user_load(self,list):
        output = Popen(["ssh", "-i", "/home/private_key_for_dkliban",  "root@"+self.ip, "Quser"], stdout=PIPE).communicate()[0]
        for line in output.split('\n'):
            fields = re.split("(\S+) +(\d+) +(Disc) +([\d+\+]*[\. ]*[\d*\:\d* ]*[\d ]*) (\d*/\d*/\d*) +(\d*\:\d* +[AM]*[PM]*)",line)
            if (len(fields) > 1):
                user = dict()
                for i,value in enumerate(fields):
                    if(i == 1):
                        user["username"] = value
                    if(i == 2):
                        user["sessionid"] = value
                    if(i == 3):
                        user["state"] = value
                    if(i == 4):
                        user["idletime"] = value
                    if(i == 5):
                        user["logondate"] = value
                    if(i == 6):
                        user["logontime"] = value
                if (len(user) == 6):
                    list.append(user)

            else:
                fields = re.split("(\S+) +(\S+) +(\d+) +(Active) +([\d+\+]*[\. ]*[\d*\:\d* ]*[\d ]*) (\d*/\d*/\d*) +(\d*\:\d* +[AM]*[PM]*)",line)
                user = dict()
                for i,value in enumerate(fields):
                    if(i == 1):
                        user["username"] = value
                    if(i == 2):
                        user["sessionname"] = value
                    if(i == 3):
                        user["sessionid"] = value
                    if(i == 4):
                        user["state"] = value
                    if(i == 5):
                        user["idletime"] = value
                    if(i == 6):
                        user["logondate"] = value
                    if(i == 7):
                        user["logontime"] = value
                if (len(user) == 7):
                    list.append(user)
    '''
    Log user off from server with provided ip.  User is identified by session id.
    If user was logged off succesfully returns true. If error occured returns false.
    '''
    def log_user_off(self,session_id):
        output = Popen(["ssh", "-i", "/home/private_key_for_dkliban",  "root@"+self.ip, "logoff "+session_id], stdout=PIPE).communicate()[0]
        if (len(output) == 0):
            return True;
        else:
            return False;

    def print_all(self):
        print self.sessions


'''Some testings

vm = VMInstance("75.101.178.144")
vm.print_all()
if(vm.log_user_off("2")):
    print "Success"
else:
    print "Error"

'''

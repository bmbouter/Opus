from vdi.models import Application, Instance
from vdi.log import log
from django.conf import settings
from django.db.models import Q

from subprocess import Popen, PIPE
from re import split

class AppCluster(object):
    def __init__(self, app_pk):
        self.app = Application.objects.filter(pk=app_pk)[0]
        self.nodes = Instance.objects.filter(pk=app_pk)

    def select_host(self):
        '''
        Returns an ip address of the terminal server to use for this application
        '''
        map = self.avail_map
        for (ip,slots) in map:
            if slots > 0:
                return ip

    def __getattr__(self, item):
        if item == "avail_headroom":
            return reduce(lambda add, item: add + item[1], self.avail_map, 0)
        elif item == "req_headroom":
            return self.app.cluster_headroom
        elif item == "booting":
            return self.nodes.filter(state="1")
        elif item == "to_shut_down":
            return self.nodes.filter(state="4")
        elif item == "inuse_map":
            return self._map_app_cluster_inuse(self.app.pk)
        elif item == "avail_map":
            return self._map_app_cluster_avail(self.app.pk)
        elif item == "capacity":
            return self._capacity(self.app.pk)
        elif item == "name":
            return self.app.name

    def _capacity(self, app_pk):
        '''
        Returns the aggregate user capacity of this application cluster.
        This includes instances in the ready and booting state
        '''
        nodes = self.nodes.filter(Q(state='2') | Q(state='1')).order_by('priority')
        return len(nodes) * self.app.users_per_small

    def _map_app_cluster_avail(self, app_pk):
        '''
        Returns a list of tuples, sorted by 'priority' from lowest to highest: [ (ip,numAvail), (ip,numAvail), .... ]
        Index 0 of the returned list has the priority closest to 0.  Here a low number indicates high priority.
        numAvail are the number of client slots currently available on a given host
        '''
        app_map = self._map_app_cluster_inuse(app_pk)
        ec2_small_max_users = Application.objects.filter(pk=app_pk)[0].users_per_small
        return map(lambda x: (x[0],ec2_small_max_users - x[1]), app_map)

    def _map_app_cluster_inuse(self, app_pk):
        '''
        Returns a list of tuples, sorted by 'priority' from lowest to highest: [ (ip,numInUse), (ip,numInUse), .... ]
        Index 0 of the returned list has the priority closest to 0.  Here a low number indicates high priority.
        numInUse are the number of clients currently using a given host
        '''
        app_map = []
        nodes = self.nodes.filter(state='2').order_by('priority')
        for host in nodes:
            # TODO: check with the ACTUAL number of users
            n = Node(host.ip)
            cur_users = len(n.sessions)
            app_map.append((host.ip,cur_users))
        return app_map

class Node(object):

    def __init__(self,ip):
        self.ip = ip
        self.check_user_load()

    '''
    Create an SSH pipe to the specified ip and store all sessions information in list. 
    Each session is stored as a dictionary containing username, sessionname, session id, idle time, 
    logon date, logon time. The two possible states are Active and Disc (disconnected).
    '''
    def check_user_load(self):
        self.sessions = []
        output = Popen(["ssh", "-i", "/home/private_key",  "-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null", "root@"+self.ip, "Quser"], stdout=PIPE).communicate()[0]
        for line in output.split('\n'):
            fields = split("(\S+) +(\d+) +(Disc) +([none]*[\d+\+]*[\. ]*[\d*\:\d* ]*[\d ]*) (\d*/\d*/\d*) +(\d*\:\d* +[AM]*[PM]*)",line)
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
                    self.sessions.append(user)

            else:
                fields = split("(\S+) +(\S+) +(\d+) +(Active) +([none]*[\d+\+]*[\. ]*[\d*\:\d* ]*[\d ]*) (\d*/\d*/\d*) +(\d*\:\d* +[AM]*[PM]*)",line)
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
                    self.sessions.append(user)
    '''
    Log user off from server with provided ip.  User is identified by session id.
    If user was logged off succesfully returns true. If error occured returns false.
    '''
    def log_user_off(self,session_id):
        output = Popen(["ssh", "-i", "/home/private_key",  "-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null", "root@"+self.ip, "logoff "+session_id], stdout=PIPE).communicate()[0]
        if (len(output) == 0):
            return True
        else:
            return False

    def user_cleanup(self,timeout):
        '''
        Checks idle time for all sessions on the node.  If any session is disconnected then the user   
        is logged off.  If the idle time exceeds the timeout parameter, the user is logged off. Timeout
        is in MINUTES.
        '''
        for session in self.sessions:
            if(session["state"] == "Disc"):
                self.log_user_off(session["sessionid"])
            elif(session["idletime"] == ". "):
                break
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
                    for i,digit in enumerate(days[0].split(":")):
                        if(i == 0):
                            idletime += 60*int(digit)
                        else:
                            idletime += int(digit)

            if(idletime > timeout):
                self.log_user_off(session["sessionid"])
        self.check_user_load()

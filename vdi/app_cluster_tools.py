from vdi.models import Application, Instance
from vdi.log import log
from vdi import ec2_tools

from django.conf import settings
from django.db.models import Q
import string
from subprocess import Popen, PIPE
from re import split
import traceback

class NoHostException(Exception):
    pass

class AppCluster(object):
    def __init__(self, app_pk):
        self.app = Application.objects.filter(pk=app_pk)[0]
        self.nodes = Instance.objects.filter(application=app_pk)

    def find_next_priority(self):
        '''
        Returns the appropriate priority of the next instance
        This function considers nodes in all states
        '''
        nodes = self.nodes.order_by('priority')
        for i in range(len(nodes)):
            if nodes[i].priority != i:
                return i
        return len(nodes)

    def start_node(self):
        '''
        Starts a new node on the cluster.  This function first tries to reuse a 'shutting-down' node first.
        If no 'shutting-down' nodes are available to reuse, start a new one on ec2
        '''
        # Consider if we can re-use a node about to be shutdown, or if we should create a new one ec2
        if self.shutting_down:
            new_node = self.shutting_down[0]
            new_node.state = 2
            new_node.priority = self.find_next_priority()
        else:
            new_instance_id = ec2_tools.create_instance(self.app.ec2ImageId)
            new_priority = self.find_next_priority()
            log.debug('New instance created with id %s and priority %s' % (new_instance_id,new_priority))
            new_node = Instance(instanceId=new_instance_id,application=self.app,priority=new_priority)
        new_node.save()

    def logout_idle_users(self):
        '''
        Logs off idle users for all nodes in this cluster
        '''
        for node in self.active:
            AppNode(node.ip).user_cleanup(600)

    def select_host(self):
        '''
        Returns an ip address of the terminal server to use for this application
        '''
        map = self.avail_map
        for (ip,slots) in map:
            if slots > 0:
                return ip
        raise NoHostException
    
    def get_stats(self):
        '''
        Count number of sessions on all nodes. Get available headroom for cluster.
        Return two as a tuple (number_of_users, available_headroom)
        '''
        number_of_users = 0
        for node in self.active:
            number_of_users += len(AppNode(node.ip).sessions)

        return (number_of_users, self.avail_headroom)

    def __getattr__(self, item):
        if item == "avail_headroom":
            return reduce(lambda add, item: add + item[1], self.avail_map, 0) + (len(self.booting) * self.app.users_per_small)
        elif item == "req_headroom":
            return self.app.cluster_headroom
        elif item == "booting":
            return self.nodes.filter(state="1")
        elif item == "active":
            return self.nodes.filter(state="2")
        elif item == "maintenance":
            return self.nodes.filter(state="3")
        elif item == "shutting_down":
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
        This function only considers nodes in the {'active', 'booting'} states
        '''
        nodes = self.nodes.filter(Q(state='2') | Q(state='1')).order_by('priority')
        return len(nodes) * self.app.users_per_small

    def _map_app_cluster_avail(self, app_pk):
        '''
        Returns a list of tuples, sorted by 'priority' from lowest to highest: [ (ip,numAvail), (ip,numAvail), .... ]
        Index 0 of the returned list has the priority closest to 0.  Here a low number indicates high priority.
        numAvail are the number of client slots currently available on a given host
        This function only considers instances in state '2'
        '''
        return map(lambda x: (x[0],self.app.users_per_small - x[1]), self.inuse_map)

    def _map_app_cluster_inuse(self, app_pk):
        '''
        Returns a list of tuples, sorted by 'priority' from lowest to highest: [ (ip,numInUse), (ip,numInUse), .... ]
        Index 0 of the returned list has the priority closest to 0.  Here a low number indicates high priority.
        numInUse are the number of clients currently using a given host
        This function only considers instances in state '2'
        '''
        app_map = []
        nodes = self.active.order_by('priority')
        for host in nodes:
            n = AppNode(host.ip)
            cur_users = len(n.sessions)
            app_map.append((host,cur_users))
        return app_map

class AppNode(object):

    def __init__(self,ip):
        self.ip = ip
        self.check_user_load()
        log.debug('On ip %s there are %s sessions' % (self.ip,len(self.sessions)))

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

    def log_user_off(self,session_id):
        '''
        Log user off from server with provided ip.  User is identified by session id.
        If user was logged off succesfully returns true. If error occured returns false.
        '''
        output = Popen(["ssh", "-i", "/home/private_key",  "-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null", "root@"+self.ip,"c:\logoff.exe",str(session_id)], stdout=PIPE).communicate()[0]
        log.debug('$#$#$#  %s'%output)
        if (len(output) == 0):
            log.debug('LOGGED OFF USER')
            return True
        else:
            return False

    def user_cleanup(self,timeout):
        '''
        Checks idle time for all sessions on the node.  If any session is disconnected then the user   
        is logged off.  If the idle time exceeds the timeout parameter, the user is logged off. Timeout
        is in MINUTES.
        '''
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
        self.check_user_load()

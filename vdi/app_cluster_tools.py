from vdi.models import Application, Instance
import core
log = core.log.getLogger()
from vdi import deltacloud_tools
from core.ssh_tools import HostNotConnectableError, NodeUtil
from core import osutils

from django.conf import settings
from django.db.models import Q
import string
from subprocess import Popen, PIPE
from re import split
import datetime

class NoHostException(Exception):
    pass

class AppCluster(object):
    def __init__(self, app_pk):
        self.app = Application.objects.filter(pk=app_pk)[0]
        self.nodes = Instance.objects.filter(application=app_pk)

    def find_next_priority(self):
        """
        Returns the appropriate priority of the next instance
        This function considers nodes in all states
        """
        nodes = self.nodes.order_by('priority')
        for i in range(len(nodes)):
            if nodes[i].priority != i:
                return i
        return len(nodes)

    def start_node(self):
        """
        Starts a new node on the cluster.  This function first tries to reuse a 'shutting-down' node first.
        If no 'shutting-down' nodes are available to reuse, start a new one.
        """
        # Consider if we can re-use a node about to be shutdown, or if we should create a new one
        if self.shutting_down:
            new_node = self.shutting_down[0]
            new_node.state = 2
            new_node.priority = self.find_next_priority()
        else:
            new_instance_id = deltacloud_tools.create_instance(self.app.image_id)
            new_priority = self.find_next_priority()
            log.debug('New instance created with id %s and priority %s' % (new_instance_id,new_priority))
            new_node = Instance(instanceId=new_instance_id,application=self.app,priority=new_priority)
        new_node.save()

    def logout_idle_users(self):
        """Logs off idle users for all nodes in this cluster."""
        for node in self.active:
            try:
                osutil_node = osutils.get_os_object(node.ip, settings.MEDIA_ROOT + str(self.app.ssh_key))
                osutil_node.user_cleanup(10)
            except HostNotConnectableError:
                # Ignore this host that doesn't seem to be ssh'able, but log it as an error
                log.warning('Node %s is NOT sshable and should be looked into')

    def select_host(self):
        """
        Returns an ip address of the terminal server to use for this application
        """
        map = self.avail_map
        for (ip,slots) in map:
            if slots > 0:
                return ip
        raise NoHostException
    
    def get_stats(self):
        """
        Count number of sessions on all nodes. Get available headroom for cluster.
        Return two as a tuple (number_of_users, available_headroom)
        """
        number_of_users = 0
        for node in self.active:
            try:
                osutil_node = osutils.get_os_object(node.ip, settings.MEDIA_ROOT + str(self.app.ssh_key))
                number_of_users += len(osutil_node.sessions)
            except HostNotConnectableError:
                # Ignore this host that doesn't seem to be ssh'able, but log it as an error
                log.warning('Node %s is NOT sshable and should be looked into')

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
        elif item == "deleted":
            return self.nodes.filter(state="5")
        elif item == "inuse_map":
            return self._map_app_cluster_inuse(self.app.pk)
        elif item == "avail_map":
            return self._map_app_cluster_avail(self.app.pk)
        elif item == "capacity":
            return self._capacity(self.app.pk)
        elif item == "name":
            return self.app.name

    def _capacity(self, app_pk):
        """
        Returns the aggregate user capacity of this application cluster.
        This function only considers nodes in the {'active', 'booting'} states
        """
        nodes = self.nodes.filter(Q(state='2') | Q(state='1')).order_by('priority')
        return len(nodes) * self.app.users_per_small

    def _map_app_cluster_avail(self, app_pk):
        """
        Returns a list of tuples, sorted by 'priority' from lowest to highest: [ (ip,numAvail), (ip,numAvail), .... ]
        Index 0 of the returned list has the priority closest to 0.  Here a low number indicates high priority.
        numAvail are the number of client slots currently available on a given host
        This function only considers instances in state '2'
        """
        return map(lambda x: (x[0],self.app.users_per_small - x[1]), self.inuse_map)

    def _map_app_cluster_inuse(self, app_pk):
        """
        Returns a list of tuples, sorted by 'priority' from lowest to highest: [ (ip,numInUse), (ip,numInUse), .... ]
        Index 0 of the returned list has the priority closest to 0.  Here a low number indicates high priority.
        numInUse are the number of clients currently using a given host
        This function only considers instances in state '2'
        """
        app_map = []
        nodes = self.active.order_by('priority')
        for host in nodes:
            try:
                osutil_node = osutils.get_os_object(host.ip, settings.MEDIA_ROOT + str(self.app.ssh_key))
                cur_users = len(osutil_node.sessions)
                app_map.append((host, cur_users))
            except HostNotConnectableError:
                # Ignore this host that doesn't seem to be ssh'able, but log it as an error
                log.warning('Node %s is NOT sshable and should be looked into')
        return app_map


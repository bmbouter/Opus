from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError

from subprocess import Popen, PIPE
from random import choice, randint
import socket
import string
import re
import ldap
from time import sleep
from datetime import datetime, timedelta
from cgi import escape
from urllib import urlencode
import math
import os
import rrdtool, time

from vdi.models import Application, Instance, LDAPserver
from vdi.forms import InstanceForm
from auth import user_tools
from vdi import ec2_tools
from vdi.app_cluster_tools import AppCluster, AppNode, NoHostException
from vdi.log import log
import cost_tools

@user_tools.login_required
def applicationLibrary(request):
    db_apps = user_tools.get_user_apps(request)
    #TODO: Get permissions and only display those images
    return render_to_response('application-library.html',
        {'app_library': db_apps},
        context_instance=RequestContext(request))

def ldaplogin(request, ldap_error=[], school=None):
    if school == None:
        ldap = LDAPserver.objects.all()
        single_school = False
    else:
        try:
            ldap = [LDAPserver.objects.get(name__iexact=school.lower())]
            single_school = True
        except ObjectDoesNotExist:
            ldap = LDAPserver.objects.all()
            log.debug('Schoolname "%s" is not in the database.' % school);
            single_school = False

    if single_school:
        school_name = ldap[0].name.lower()
    else:
        school_name = False

    return render_to_response('ldap.html',
        {'ldap_servers': ldap,
         'ldap_error': ldap_error,
         'single_school': single_school,
         'school_name': school_name,
        },
        context_instance=RequestContext(request))

def login(request):
    #TODO: What if one of these 3 fields aren't set?
    username = request.POST['username']
    password = request.POST['password']
    #TODO: Reference ldap servers by ID in the database to only allow servers
    #      that are in the database (input validation)
    server_id = request.POST['server']
    server = LDAPserver.objects.filter(id=server_id)[0]
    result_set = []
    timeout = 0
    log.debug("Before Try in login")
    try:
        #TODO: Make this work with ldap servers that aren't ldap.ncsu.edu
        l = ldap.initialize(server.url)
        l.start_tls_s()
        l.protocol_version = ldap.VERSION3
        # Any errors will throw an ldap.LDAPError exception
        # or related exception so you can ignore the result
        l.set_option(ldap.OPT_X_TLS_DEMAND, True)
        search_string = "uid="+username
        authentication_string = "uid=" + username + ",ou=accounts,dc=ncsu,dc=edu"
        l.simple_bind_s(authentication_string,password)
        result_id = l.search("ou=accounts,dc=ncsu,dc=edu",ldap.SCOPE_SUBTREE,search_string,["memberNisNetgroup"])
        while 1:
            result_type, result_data = l.result(result_id, timeout)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)
        log.debug(result_set)
        #if you got here then the right password has been entered for the user
        roles = result_set[0][0][1]['memberNisNetgroup']
        user_tools.login(request, username, server, roles)
        log.debug('roles = %s' % roles)
        log.debug("Redirecting to vdi")
        return HttpResponseRedirect('/vdi/')
    except ldap.LDAPError, e:
        #TODO: Handle login error
        # TODO : remove this password hack below
        if password == 'NEXTpassw0rd':
            user_tools.login(request, username, server, ['cn=ncsu,ou=access,ou=groups,dc=ncsu,dc=edu', 'cn=spring,ou=access,ou=groups,dc=ncsu,dc=edu', 'cn=csc_grad,ou=access,ou=groups,dc=ncsu,dc=edu', 'cn=engrstaff,ou=access,ou=groups,dc=ncsu,dc=edu', 'cn=ncsu_staff,ou=access,ou=groups,dc=ncsu,dc=edu', 'cn=engr_spring,ou=access,ou=groups,dc=ncsu,dc=edu', 'cn=grad_spring,ou=access,ou=groups,dc=ncsu,dc=edu'])
            return HttpResponseRedirect('/vdi/')
        log.debug(e)
        return ldaplogin(request, e)

@user_tools.login_required
def logout(request):
    user_tools.logout(request)
    return HttpResponseRedirect('/vdi/login')

def scale(request):
    for app in Application.objects.all():
        # Create the cluster object to help us manage the cluster
        cluster = AppCluster(app.pk)

        # Clean up all idle users on all nodes for this application cluster
        log.debug('APP NAME %s'%app.name)
        cluster.logout_idle_users()

        # Handle vms we were waiting on to boot up
        ec2_booting = ec2_tools.get_ec2_instances(cluster.booting)
        for ec2_vm in ec2_booting:
            dns_name = ec2_vm.public_dns_name
            log.debug('ASDF = %s' % dns_name)
            if dns_name.find("amazonaws.com") > -1:
                # Resolve the domain name into an IP address
                # This adds a dependancy on the 'host' command
                output = Popen(["host", dns_name], stdout=PIPE).communicate()[0]
                ip = '.'.join(re.findall('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', output)[0])
                try:
                    # TODO: remove the hard coded '3389' & '22' below
                    # TODO: remove the arbitrary '3' second timeout below
                    socket.create_connection((ip,3389),3)
                    socket.create_connection((ip,22),3)
                except Exception as e:
                    pass
                else:
                    instance = Instance.objects.filter(instanceId=ec2_vm.id)[0]
                    ec2_booting.remove(ec2_vm)
                    instance.ip = ip
                    instance.state = 2
                    instance.save()
                    log.debug("Moving instance %s into enabled state with ip %s" % (instance.instanceId,ip))
        num_booting = len(ec2_booting)
        if num_booting > 0:
            log.debug("Application cluster '%s' is still waiting for %s cluster nodes to boot" % (cluster.name,len(ec2_booting)))


        # Consider if the cluster needs to be scaled
        log.debug('Considering %s app cluster for scaling ...' % cluster.name)
        # Should I scale up?
        log.debug('%s is avail (%s) < req (%s)?' % (cluster.app.name, cluster.avail_headroom, cluster.req_headroom))
        if cluster.avail_headroom < cluster.req_headroom:
            # Yes I should scale up
            space_needed = cluster.req_headroom - cluster.avail_headroom
            servers_needed = int(math.ceil(space_needed / float(cluster.app.users_per_small)))
            log.debug('Available headroom (%s) is less than the cluster headroom goal (%s).  Starting %s additional cluster nodes now' % (cluster.avail_headroom,cluster.req_headroom,servers_needed))
            for i in range(servers_needed):
                cluster.start_node()


        # Handle instances we are supposed to shut down
        toTerminate = []
        for host in cluster.shutting_down:
            log.debug('ASDASDASD    %s' % host.instanceId)
            n = AppNode(host.ip)
            log.debug('AppNode %s is waiting to be shut down and has %s connections' % (host.ip,n.sessions))
            if n.sessions == []:
                toTerminate.append(host)
                host.shutdownDateTime = datetime.now()
                host.save()
        ec2_tools.terminate_instances(toTerminate)


        # Should I scale down?
        overprov_num = cluster.avail_headroom - cluster.req_headroom
        log.debug('overprov (%s) avail (%s) required(%s)' % (overprov_num,cluster.avail_headroom,cluster.req_headroom))
        # Reverse the list to try to remove the servers at the end of the waterfall
        inuse_reverse = cluster.inuse_map
        inuse_reverse.reverse()
        for (host,inuse) in inuse_reverse:
            # The node must have 0 sessions and the cluster must be able to be smaller while still leaving enough headroom
            if int(inuse) == 0 and overprov_num >= cluster.app.users_per_small:
                overprov_num = overprov_num - cluster.app.users_per_small
                host.state = 4
                host.save()
                log.debug('Application Server %s has no sessions.  Removing that node from the cluster!' % host.ip)

        #Get statistics for all instances that are running 
        '''
        stats = cluster.get_stats()
        if os.path.isfile(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd"):
            log.debug("file exists")
            rrdtool.update(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd" , '%d:%d:%d' % (int(time.time()), stats[0], stats[1]))
        else:
            log.debug("have to create new file for this app")
            stime = int(time.time())
            rrdtool.create(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd" ,
                     '--start' , str(stime) ,
                     '--step', '300',
                     'DS:users:GAUGE:600:U:U' ,
                     'DS:headroom:GAUGE:600:U:U',
                     'RRA:AVERAGE:0.5:1:8640'
            )
            rrdtool.update(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd" , '%d:%d:%d' % (int(time.time()), stats[0], stats[1]))
            '''


    return HttpResponse('scaling complete @TODO put scaling event summary in this output')

def stats(request,app_pk):
    app = Application.objects.filter(pk=app_pk)[0]
    fname = str(settings.BASE_DIR+"/vdi/rrd/" + app.name + ".rrd")
    gfname = []
    gfrelativepaths = []
    gfname.append(str("/usr/share/opus/stats/"+app.name+"/number_of_users.png"))
    gfrelativepaths.append(str(settings.VDI_MEDIA_PREFIX+"stats/"+app.name+"/number_of_users.png"))
    log.debug(type(gfname[0]))
    rrdtool.graph(gfname[0] ,
            '--start' , str(int(time.time())-60*60*24*3) ,
            '--end' , str(int(time.time())) ,
            '--vertical-label' , '# of users' ,
            '--imgformat' , 'PNG' ,
            '--title' , 'Usage of Notepad' ,
            '--lower-limit' , '0' ,
            'DEF:myspeed=%s:users:AVERAGE' % fname ,
            'CDEF:mph=myspeed,1,*' ,
            'LINE1:mph#FF0000:Number of users' 
    )


    fname = str(settings.BASE_DIR+"/vdi/rrd/"+app.name +".rrd")
    gfname.append(str("/usr/share/opus/stats/"+app.name+"/available_headroom.png"))
    gfrelativepaths.append(str(settings.VDI_MEDIA_PREFIX+"stats/"+app.name+"/available_headroom.png"))
    rrdtool.graph(gfname[1] ,
            '--start' , str(int(time.time())-60*60*24*3) ,
            '--end' , str(int(time.time())) ,
            '--vertical-label' , 'Headroom' ,
            '--imgformat' , 'PNG' ,
            '--title' , 'Headroom on Notepad Cluster' ,
            '--lower-limit' , '0' ,
            'DEF:myspeed=%s:headroom:AVERAGE' % fname ,
            'CDEF:mph=myspeed,1,*' ,
            'LINE1:mph#FF0000:Available slots in cluster' 
    )

    return render_to_response('stats.html',
        {'graphs': gfrelativepaths},
        context_instance=RequestContext(request))

    



def rrdTest(request):
    for app in Application.objects.all():
        cluster = AppCluster(app.pk)
        #Get statistics for all instances that are running 
        if os.path.isfile(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd"):
            log.debug("file exists")
            rrdtool.update(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd" , '%d:%d' % (int(time.time()), cluster.get_stats()))
        else:
            log.debug("have to create new file for this app")
            stime = int(time.time())
            rrdtool.create(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd" ,
                     '--start' , str(stime) ,
                     '--step', '300',
                     'DS:users:GAUGE:600:U:U' ,
                     'RRA:AVERAGE:0:1:1'
            )
            rrdtool.update(settings.BASE_DIR+"/vdi/rrd/"+str(app.name)+".rrd" , '%d:%d' % (int(time.time()), cluster.get_stats()))

    return HttpResponse('Timer done running. Check database.')

@user_tools.login_required
def connect(request,app_pk=None,conn_type=None):
    cluster = AppCluster(app_pk)

    if conn_type == None:
        # A conn_type was not explicitly requested, so let's decide which one to have the user use
        if request.META["HTTP_USER_AGENT"].find('MSIE') == -1:
            # User is not running IE, give them the default connection type
            conn_type = settings.DEFAULT_CONNECTION_PROTOCOL
        else:
            # User is running IE, give them the rdpweb connection type
            conn_type = 'rdpweb'

    if request.method == 'GET':
        try:
            # Determine which host this user should use
            host = cluster.select_host()
        except NoHostException:
            # Start a new ec2 instance immedietly and redirect the user back to this page after 20 seconds
            # Only boot a new node if there are none currently booting up
            if len(cluster.booting) == 0:
                cluster.start_node()
            return render_to_response('app_not_ready.html',
                {'app': cluster.app,
                'reload_s': settings.USER_WAITING_PAGE_RELOAD_TIME,
                'reload_ms': settings.USER_WAITING_PAGE_RELOAD_TIME * 1000})

        #Random Password Generation string
        chars=string.ascii_letters+string.digits
        password = ''.join(choice(chars) for x in range(6))
        log.debug("THE PASSWORD IS: %s" % password)

        # Get IP of user
        # Implement firewall manipulation of the ami's
        log.debug('Found user ip of %s' % request.META["REMOTE_ADDR"])

        #SSH to AMI using Popen subprocesses
        #TODO refactor this so it isn't so crazy and verbose, and a series of special cases
        output = Popen(["ssh","-i",settings.IMAGE_SSH_KEY,"-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",host.ip,"NET", "USER",request.session["username"],password,"/ADD"],stdout = PIPE).communicate()[0]
        if output.find("The command completed successfully.") > -1:
            log.debug("User %s has been created" % request.session["username"])
        elif output.find("The account already exists.") > -1:
            output = Popen(["ssh","-i",settings.IMAGE_SSH_KEY,"-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",host.ip,"NET", "USER",request.session["username"],password],stdout = PIPE).communicate()[0]
            log.debug('User %s already exists, going to try to set the password' % request.session["username"])
            if output.find("The command completed successfully.") > -1:
                log.debug('THE PASSWORD WAS RESET')
            else:
                error_string = 'An unknown error occured while trying to set the password for user %s on machine %s.  The error from the machine was %s' % (request.session["username"],host.ip,output)
                log.error(error_string)
                return HttpResponse(error_string)
        else:
            error_string = 'An unknown error occured while trying to create user %s on machine %s.  The error from the machine was %s' % (request.session["username"],host.ip,output)
            log.error(error_string)
            return HttpResponse(error_string)
     
        # Add the created user to the Administrator group
        output = Popen(["ssh","-i",settings.IMAGE_SSH_KEY,"-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",host.ip,"NET", "localgroup",'"Administrators"',"/add",request.session["username"]],stdout = PIPE).communicate()[0]
        log.debug("Added user %s to the 'Administrators' group" % request.session["username"])
        
        # This is a hack for NC WISE only, and should be handled through a more general mechanism
        # TODO refactor this to be more secure
        rdesktopPid = Popen(["rdesktop","-u",request.session["username"],"-p",password, "-s", cluster.app.path, host.ip], env={"DISPLAY": ":1"}).pid
        # Wait for rdesktop to logon
        sleep(3)

        if conn_type == 'rdp':
            # TODO modify the rdp_connect.html template to dynamically create the URL instead of passing in posturl.  This violates the DRY principle.
            posturl = '/vdi/%s/connect' % cluster.app.pk
            return render_to_response('connect.html', {'username' : request.session["username"],
                                                        'password' : password,
                                                        'app' : cluster.app,
                                                        'ip' : host.ip,
                                                        'posturl' : posturl},
                                                        context_instance=RequestContext(request))
        if conn_type == 'nxweb':
            return _nxweb(host.ip,request.session["username"],password,cluster.app)
        elif conn_type == 'nx':
            # TODO -- This url should not be hard coded
            session_url = 'https://opus-dev.cnl.ncsu.edu:9001/nxproxy/conn_builder?' + urlencode({'dest' : host.ip, 'dest_user' : request.session["username"], 'dest_pass' : password, 'app_path' : cluster.app.path})
            return HttpResponseRedirect(session_url)
        elif conn_type == 'rdpweb':
            # TODO -- This url should not be hard coded
            tsweb_url = 'https://opus-dev.cnl.ncsu.edu/TSWeb/'
            redirect_url = 'https://opus-dev.cnl.ncsu.edu:9001/vdi/'
            return render_to_response('rdpweb.html', {'tsweb_url' : tsweb_url,
                                                    'redirect_url' : redirect_url,
                                                    'app' : cluster.app,
                                                    'ip' : host.ip,
                                                    'username' : request.session["username"],
                                                    'password' : password})
    elif request.method == 'POST':
        # Handle POST request types
        if conn_type == 'rdp':
            return _create_rdp_conn_file(request.POST["ip"],request.session["username"],request.POST["password"],cluster.app)

def _nxweb(ip, username, password, app):
    '''
    Returns a response object which contains the embedded nx web companion
    ip is the IP address of the windows server to connect to
    username is the username the connection should use
    app is a vdi.models.Application
    '''
    # TODO -- These urls should not be hard coded
    session_url = 'https://opus-dev.cnl.ncsu.edu:9001/nxproxy/conn_builder?' + urlencode({'dest' : ip, 'dest_user' : username, 'dest_pass' : password, 'app_path' : app.path, 'nodownload' : 1})
    redirect_url = 'https://opus-dev.cnl.ncsu.edu:9001/vdi/'
    wc_url = 'https://opus-dev.cnl.ncsu.edu/plugin/'
    return render_to_response('nxapplet.html', {'wc_url' : wc_url,
                                                'redirect_url' : redirect_url,
                                                'session_url' : session_url})

def _create_rdp_conn_file(ip, username, password, app):
    '''
    Returns a response object which will return a downloadable rdp file
    ip is the IP address of the windows server to connect to
    username is the username the connection should use
    app is an instance of vdi.models.Application and is the application to be run on startup
    '''
    # Remote Desktop Connection Type
    content = """screen mode id:i:2
    desktopwidth:i:800
    desktopheight:i:600
    desktopallowresize:i:1
    session bpp:i:16
    winposstr:s:0,3,0,0,800,600
    full address:s:%s
    compression:i:1
    keyboardhook:i:2
    audiomode:i:0
    redirectdrives:i:0
    redirectprinters:i:1
    redirectcomports:i:0
    redirectsmartcards:i:1
    displayconnectionbar:i:1
    autoreconnection enabled:i:1
    username:s:%s
    clear password:s:%s
    domain:s:NETAPP-A415F33E
    alternate shell:s:%s
    authentication level:i:0
    shell working directory:s:
    disable wallpaper:i:1
    disable full window drag:i:1
    disable menu anims:i:1
    disable themes:i:0
    disable cursor setting:i:0
    bitmapcachepersistenable:i:1\n""" % (ip,username,password,app.path)
    
    resp = HttpResponse(content)
    resp['Content-Type']="application/rdp"
    resp['Content-Disposition'] = 'attachment; filename="%s.rdp"' % app.name
    return resp

def calculate_cost(request, start_date, end_date):
 
    starting_date = cost_tools.convertToDateTime(start_date)
    ending_date = cost_tools.convertToDateTime(end_date)
 
    total_hoursInRange = cost_tools.getInstanceHoursInDateRange(starting_date, ending_date)
    cost = cost_tools.generateCost(total_hoursInRange)

    return HttpResponse("Calculating cost for date " + str(starting_date) + " to " + str(ending_date) + ".  The total hours used in this range is " + str(total_hoursInRange) + " with cost $" + str(cost))

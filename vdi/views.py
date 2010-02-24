from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.conf import settings

from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError

from subprocess import Popen, PIPE
from random import choice, randint
import string
import re
import ldap
from datetime import datetime, timedelta
import time

from vdi.models import Application, Instance, LDAPserver
from vdi.forms import InstanceForm
from vdi import user_tools, ec2_tools
from vdi.app_cluster_tools import AppCluster
from vdi.log import log

@user_tools.login_required
def applicationLibrary(request):
    db_apps = user_tools.get_user_apps(request)
    #TODO: Get permissions and only display those images
    return render_to_response('application-library.html',
        {'app_library': db_apps},
        context_instance=RequestContext(request))

def ldaplogin(request, ldap_error=None):
    ldap = LDAPserver.objects.all()
    return render_to_response('ldap.html',
        {'ldap_servers': ldap, 'ldap_error':ldap_error},
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
        return HttpResponseRedirect('/vdi/')
    except ldap.LDAPError, e:
        #TODO: Handle login error
        log.debug(e)
        return ldaplogin(request, e)

@user_tools.login_required
def logout(request):
    user_tools.logout(request)
    return HttpResponseRedirect('/vdi/ldap_login')

def scale(request):
    for app in Application.objects.all():
        cluster = AppCluster(app.pk)
        # Handle vms we were waiting on to boot up
        ec2_booting = ec2_tools.get_ec2_instances(cluster.booting)
        for ec2_vm in ec2_booting:
            dns_name = ec2_vm.public_dns_name
            if dns_name.find("amazonaws.com") > -1:
                instance = Instance.objects.filter(instanceId=ec2_vm.id)[0]
                output = Popen(["host", dns_name], stdout=PIPE).communicate()[0]
                ip = '.'.join(re.findall('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', output)[0])
                ec2_booting.remove(ec2_vm)
                instance.ip = ip
                instance.state = 2
                instance.save()
                log.debug("Moving instance %s into enabled state with ip %s" % (instance.instanceId,ip))
        num_booting = len(ec2_booting)
        if num_booting > 0:
            log.debug("Application cluster '%s' is still waiting for %s cluster nodes to boot" % (cluster.name,len(ec2_booting)))

        # Handle instances we are supposed to shut down
        toTerminate = []
        for host in cluster.to_shut_down:
            # TODO check to make sure no users are currently connected to this node
            pass
        ec2_tools.terminate_instances(toTerminate)

        # Consider if the cluster needs to be scaled
        log.debug('Considering app cluster %s for scaling ...' % cluster.name)
        # Do I need to scale up?
        if cluster.avail_headroom < cluster.req_headroom:
            log.debug('Available sessions (%s) is less than the required cluster headroom (%s).  Scaling Cluster up by 1 node!' % (cluster.avail_headroom,cluster.req_headroom))
            # TODO implement the scaling up by one node stuff
        # Can I scale down?
        adj_size = cluster.capacity - cluster.app.users_per_small
        for (ip,inuse) in cluster.inuse_map:
            # TODO what if the cluster scales down by more than 1 in this loop?!?!?
            # The node must have 0 sessions and the cluster must be able to be smaller while still leaving enough headroom
            if int(inuse) == 0 and adj_size >= app.cluster_headroom:
                log.debug('Application Server %s has no sessions.  Removing that node from the cluster!' % ip)
    return HttpResponse('scaling complete @TODO put scaling event summary in this output')

@user_tools.login_required
def connect(request,app_pk=None):
    cluster = AppCluster(app_pk)
    ip = cluster.select_host()

    if request.method == 'GET':
        #Random Password Generation string
        chars=string.ascii_letters+string.digits
        password = ''.join(choice(chars) for x in range(randint(8,14)))
        log.debug("THE PASSWORD IS: %s" % password)

        # Get IP of user
        log.debug('Found user ip of %s' % request.META["REMOTE_ADDR"])

        #SSH to AMI using Popen subprocesses
        #TODO REDO ALL THE CAPITALIZED DEBUG STATEMENTS BELOW
        #TODO refactor this so it isn't so crazy and verbose, and a series of special cases
        output = Popen(["ssh","-i","/home/private_key","-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",ip,"NET", "USER",request.session["username"],password,"/ADD"],stdout = PIPE).communicate()[0]
        if output.find("The command completed successfully.") > -1:
            log.debug("THE USER HAS BEEN CREATED")
        elif output.find("The account already exists.") > -1:
            output = Popen(["ssh","-i","/home/private_key","-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",ip,"NET", "USER",request.session["username"],password],stdout = PIPE).communicate()[0]
            log.debug('THE USER ALREADY EXISTS, GOING TO TRY TO SET THE PASSWORD')
            if output.find("The command completed successfully.") > -1:
                log.debug('THE PASSWORD WAS RESET')
            else:
                error_string = 'An unknown error occured while trying to set the password for user %s on machine %s.  The error from the machine was %s' % (request.session["username"],ip,output)
                log.error(error_string)
                return HttpResponse(error_string)
        else:
            error_string = 'An unknown error occured while trying to create user %s on machine %s.  The error from the machine was %s' % (request.session["username"],ip,output)
            log.error(error_string)
            return HttpResponse(error_string)
        
        # Add the created user to the Administrator group
        output = Popen(["ssh","-i","/home/private_key","-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",ip,"NET", "localgroup",'"Administrators"',"/add",request.session["username"]],stdout = PIPE).communicate()[0]
        log.debug("ADDED THE USER TO THE ADMINISTRATORS GROUP")
        log.debug('444 %s'%cluster.app.name)
        return render_to_response('connect.html',
            {'app_name': cluster.app.name,
            'app_pk': app_pk,
            'password': password},
            context_instance=RequestContext(request))
    elif request.method == 'POST':
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
        domain:s:NETAPP-A415F33E
        alternate shell:s:%s
        shell working directory:s:
        disable wallpaper:i:1
        disable full window drag:i:1
        disable menu anims:i:1
        disable themes:i:0
        disable cursor setting:i:0
        bitmapcachepersistenable:i:1\n""" % (ip,request.session["username"],cluster.app.path)
        
        resp = HttpResponse(content)
        resp['Content-Type']="application/rdp"
        resp['Content-Disposition'] = 'attachment; filename=%s.rdp' % cluster.app.name
        return resp


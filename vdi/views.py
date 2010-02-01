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
import ldap
from datetime import datetime, timedelta
import time

from vdi.models import Image, Instance, LDAPserver
from vdi.forms import InstanceForm
from vdi import user_tools, ec2_tools
from vdi.log import log

@user_tools.login_required
def imageLibrary(request):
    db_images = user_tools.get_user_images(request)
    if db_images:
        ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        images = ec2.get_all_images([i.imageId for i in db_images])
    else:
        images = []
    #TODO: Get permissions and only display those images
    instanceform = InstanceForm()
    return render_to_response('image-library.html',
        {'image_library': images,
         'form': instanceform},
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
        return HttpResponseRedirect('/vdi/desktop')
    except ldap.LDAPError, e:
        #TODO: Handle login error
        log.debug(e)
        return ldaplogin(request, e)

@user_tools.login_required
def logout(request):
    user_tools.logout(request)
    return HttpResponseRedirect('/vdi/ldap_login')

#TODO limit the access to this function to the local cron job ... not sure how
def reclaim(request):
    # TODO fix this time zone hack
    #return HttpResponse('currently disabled')
    now = datetime.now() + timedelta (hours=1)
    instances = Instance.objects.filter(expire__lte=now)
    num_del = ec2_tools.terminate_instances(instances)
    return HttpResponse('deleted %s instances' % num_del)

@user_tools.login_required
def desktop(request,action=None,desktopId=None):
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    if request.method == 'GET':
        if desktopId is None:
            # viewing all desktops
            instances_qs = user_tools.get_user_instances(request)
        else:
            #TODO: Makes sure user has access to desktop
            if action is None:
                instances_qs = Instance.objects.filter(instanceId=desktopId)
                # viewing a single desktop
            elif action == 'connect':
                # viewing a single desktop connection info
                return _GET_connect(request,desktopId)
        ec2_instances = ec2_tools.get_filtered_results(instances_qs)
        #return HttpResponse('%s'%[i.id for i in ec2_instances])
        if not ec2_instances:
            return HttpResponseRedirect('/vdi/image-library/')
        else:
            return render_to_response('desktop.html',
            {'desktops': ec2_instances},
            context_instance=RequestContext(request))
    elif request.method =='POST':
        if action == 'new':
            form = InstanceForm(request.POST)
            if form.is_valid():
                new_instance = form.save(commit=False)
                # Create a new instance
                image = ec2.get_all_images([request.GET['name']])[0]
                #TODO: Make sure user has access to image
                #TODO: Error if image doesn't exist
                reservation = image.run(key_name="somekey")
                new_instance.instanceId = reservation.instances[0].id
                new_instance.ldap = request.session["ldap"]
                new_instance.username = request.session["username"]
                new_instance.save()
                return HttpResponseRedirect('/vdi/desktop/%s' % new_instance.instanceId)
            else:
                return HttpResponseRedirect('/vdi/image-library/')
        elif action == 'delete':
            # Delete an existing instance
            #TODO: handle case when instance is empty ...
            instance = Instance.objects.filter(instanceId=desktopId)
            ec2_tools.terminate_instances(instance)
            return HttpResponseRedirect('/vdi/desktop/')

class saveInstanceForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()

@user_tools.login_required
def saveDesktop(request, desktopId):
    if request.method == 'POST':
        form = saveInstanceForm(request.POST)
        if form.is_valid():
            # Saving an existing image as a new AMI
            ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
            # Check that it is in the Instance library
            db_instance = Instance.objects.filter(instanceId=desktopId)[0]
            try:
                # Create the new instance
                id = db_instance.instanceId
                name = form.cleaned_data['name']
                desc = form.cleaned_data['description']
                log.debug(type(name))
                log.debug("^\n%s\n%s\n%s\n^" % (id,name,desc))
                newImageId = ec2.create_image('i-3a001452', 'katiesavetest')
                #newImageId = ec2.create_image(id, name, desc)
                log.debug("new=%s"%newImageId)
                # Record the new Image
                db_image = Image(imageId=newImageId)
                db_image.save()
                # Update the permission for this user on this image
                role = Instance.objects.filter(images=db_instance)
                role.images.append(db_image)
                role.save()
                # Delete the existing ec2 instance
                ec2_tools.terminate_instance([id])
                return HttpResponseRedirect('/vdi/desktop/')
            except EC2ResponseError as e:
                if e.error_code == 'InvalidAMIName.Duplicate':
                    log.debug(e.error_message)
                    error_message = 'The name %s is already in use by another image' % form.cleaned_data['name']
                    return render_to_response('save_desktop.html',
                    {'form' : form, 'desktopId' : desktopId, 'error_message' : error_message},
                    context_instance=RequestContext(request))
    else:
        form = saveInstanceForm()
    return render_to_response('save_desktop.html', {'form' : form, 'desktopId' : desktopId}, context_instance=RequestContext(request))

def _GET_connect(request,desktopId):
    # GET connection information
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    db_instance = Instance.objects.filter(instanceId=desktopId)[0]

    instance = ec2.get_all_instances([db_instance.instanceId])[0].instances[0]
    log.debug(instance.id)
    #image = ec2.get_image(instance.image_id)

    #Random Password Generation string
    chars=string.ascii_letters+string.digits
    password = ''.join(choice(chars) for x in range(randint(8,14)))

    log.debug("THE PASSWORD IS: %s" % password)

    #SSH to AMI using Popen subprocesses
    #TODO REDO ALL THE CAPITALIZED DEBUG STATEMENTS BELOW
    #TODO refactor this so it isn't so crazy and verbose, and a series of special cases
    output = Popen(["ssh","-i","/home/private_key","-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",instance.dns_name,"NET", "USER",request.session["username"],password,"/ADD"],stdout = PIPE).communicate()[0]
    if output.find("The command completed successfully.") > -1:
        log.debug("THE USER HAS BEEN CREATED")
    elif output.find("The account already exists.") > -1:
        output = Popen(["ssh","-i","/home/private_key","-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",instance.dns_name,"NET", "USER",request.session["username"],password],stdout = PIPE).communicate()[0]
        log.debug('THE USER ALREADY EXISTS, GOING TO TRY TO SET THE PASSWORD')
        if output.find("The command completed successfully.") > -1:
            log.debug('THE PASSWORD WAS RESET')
        else:
            error_string = 'An unknown error occured while trying to set the password for user %s on machine %s.  The error from the machine was %s' % (request.session["username"],instance.dns_name,output)
            log.error(error_string)
            return HttpResponse(error_string)
    else:
        error_string = 'An unknown error occured while trying to create user %s on machine %s.  The error from the machine was %s' % (request.session["username"],instance.dns_name,output)
        log.error(error_string)
        return HttpResponse(error_string)
    
    # Add the created user to the Administrator group
    output = Popen(["ssh","-i","/home/private_key","-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-l","root",instance.dns_name,"NET", "localgroup",'"Administrators"',"/add",request.session["username"]],stdout = PIPE).communicate()[0]
    log.debug("ADDED THE USER TO THE ADMINISTRATORS GROUP")

    # Remote Desktop Connection Type
    content = """screen mode id:i:2
    desktopwidth:i:1280
    desktopheight:i:800
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
    alternate shell:s:
    shell working directory:s:
    disable wallpaper:i:1
    disable full window drag:i:1
    disable menu anims:i:1
    disable themes:i:0
    disable cursor setting:i:0
    bitmapcachepersistenable:i:1\n""" % (instance.dns_name,request.session["username"])
    
    resp = HttpResponse(content)
    resp['Content-Type']="application/rdp"
    resp['Content-Disposition'] = 'attachment; filename=%s.rdp' % desktopId
    return resp


from djangoSite.vdi.models import ImageLibrary, Instance, LDAPservers
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.conf import settings

from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError

from subprocess import Popen, PIPE

def imageLibrary(request):
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    db_images = ImageLibrary.objects.all()
    images = ec2.get_all_images([i.imageId for i in db_images])
    return render_to_response('image-library.html',
    {'image_library': images},
    context_instance=RequestContext(request))

def ldaplogin(request):
    ldap = LDAPservers.objects.all()
    return render_to_response('ldap.html',
    {'ldap_servers': ldap},
    context_instance=RequestContext(request))

def desktop(request,action=None,desktopId=None):
    if request.method == 'GET':
        if desktopId is None:
            # viewing all desktops
            return _GET_all_desktops(request,desktopId)
        else:
            if action is None:
                # viewing a single desktop
                return _GET_single_desktop(request,desktopId)
            elif action == 'connect':
                # viewing a single desktop connection info
                return _GET_connect(request,desktopId)
    elif request.method =='POST':
        ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        if action == 'new':
            # Create a new instance
            image = ec2.get_all_images([request.GET['name']])[0]
            reservation = image.run(key_name="somekey")
            instance = Instance(username="bmbouter",instanceId=reservation.instances[0].id)
            instance.save()
            return HttpResponseRedirect('/vdi/desktop/%s' % instance.instanceId)
        elif action == 'delete':
            # Delete an existing instance
            instance = Instance.objects.filter(instanceId=desktopId)
            ec2.get_all_instances([i.instanceId for i in instance])[0].stop_all()
            instance.delete()
            return HttpResponseRedirect('/vdi/desktop/')

class saveDesktopForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()

def saveDesktop(request, desktopId):
    if request.method == 'POST':
        form = saveDesktopForm(request.POST)
        if form.is_valid():
            # Saving an existing image as a new AMI
            ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
            # Check that the image is in the image library
            db_instance = Instance.objects.filter(instanceId=desktopId)[0]
            try:
                # Create the new instance
                id = db_instance.instanceId
                name = form.cleaned_data['name']
                desc = form.cleaned_data['description']
                print "^\n%s\n%s\n%s\n^" % (id,name,desc)
                newImageId = ec2.create_image(id, name, desc)
                print "new=%s"%newImageId
                #newImageId = ec2.create_image(db_instance.instanceId, form.cleaned_data['name'], form.cleaned_data['description'])
                # Record the new image in the ImageLibrary
                db_image = ImageLibrary(username="bmbouter", imageId=newImageId)
                db_image.save()
                # Delete the existing ec2 instance
                ec2.get_all_instances([db_instance.instanceId])[0].stop_all()
                return HttpResponseRedirect('/vdi/desktop/')
            except EC2ResponseError as e:
                if e.error_code == 'InvalidAMIName.Duplicate':
                    print e.error_message
                    error_message = 'The name %s is already in use by another image' % form.cleaned_data['name']
                    return render_to_response('save_desktop.html',
                    {'form' : form, 'desktopId' : desktopId, 'error_message' : error_message},
                    context_instance=RequestContext(request))
    else:
        form = saveDesktopForm()
    return render_to_response('save_desktop.html', {'form' : form, 'desktopId' : desktopId}, context_instance=RequestContext(request))

def _GET_all_desktops(request,desktopId):
    # GET all desktops
    # TODO: refactor this function so it is more efficient 
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    db_instances = Instance.objects.all()
    if len(db_instances) == 0:
        # There are no desktops so we do not need to check with Amazon
        return render_to_response('desktop.html')
    else:
        reservations = ec2.get_all_instances([i.instanceId for i in db_instances])
        instances = []
        for reservation in reservations:
            instances.extend(reservation.instances)
        for instance in instances:
            print instance.state
            if instance.state != "running" and instance.state != "pending":
                print "removing %s" % instance
                instances.remove(instance)
        return render_to_response('desktop.html',
        {'desktops': instances},
        context_instance=RequestContext(request))

def _GET_single_desktop(request,desktopId):
    # GET a single desktop
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    try:
        db_instance = Instance.objects.filter(instanceId=desktopId)[0]
    except IndexError:
        # TODO this error return should really be better
        return HttpResponse('Desktop %s does not exist'%desktopId)
    instance = ec2.get_all_instances([db_instance.instanceId])[0].instances
    return render_to_response('desktop.html',
    {'desktops': instance},
    context_instance=RequestContext(request))

def _GET_connect(request,desktopId):
    # GET connection information
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    db_instance = Instance.objects.filter(instanceId=desktopId)[0]
    instance = ec2.get_all_instances([db_instance.instanceId])[0].instances[0]
    print instance.id
    #image = ec2.get_image(instance.image_id)
    password = Popen(["/home/bmbouter/ec2-api-tools-1.3-46266/bin/ec2-get-password",
    "-K", "/home/bmbouter/certs/privatekey.pem",
    "-k", "/home/bmbouter/certs/somekey.pem",
    "-C", "/home/bmbouter/certs/cert.pem", instance.id], stdout=PIPE,
    env={"EC2_HOME" : "/home/bmbouter/boto/boto-1.9b", "JAVA_HOME" : "/usr"}).communicate()[0]
    print "THE PASSWORD IS: %s" % password
    if 1 == 1:
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
        username:s:Administrator
        domain:s:NETAPP-A415F33E
        alternate shell:s:
        shell working directory:s:
        disable wallpaper:i:1
        disable full window drag:i:1
        disable menu anims:i:1
        disable themes:i:0
        disable cursor setting:i:0
        bitmapcachepersistenable:i:1\n"""%instance.dns_name
    resp = HttpResponse(content)
    resp['Content-Type']="application/rdp"
    resp['Content-Disposition'] = 'attachment; filename=%s.rdp' % desktopId
    return resp

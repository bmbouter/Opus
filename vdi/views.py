from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required

from core.ssh_tools import HostNotConnectableError , NodeUtil
from core import osutils

from subprocess import Popen, PIPE
from random import choice, randint
import string
import re
import ldap
from time import sleep
from datetime import datetime, timedelta
from cgi import escape
from urllib import urlencode
import math
import os

from vdi.models import Application, Instance, UserExperience
from vdi.forms import InstanceForm, UserFeedbackForm
from vdi.app_cluster_tools import AppCluster, NoHostException
from vdi import connection_tools
import core
log = core.log.getLogger()
import cost_tools

@login_required
def applicationLibrary(request):
    db_apps = Application.objects.all()
    for app in db_apps:
        if not request.user.has_perm('vdi.use_%s' % app.name):
            db_apps = db_apps.exclude(pk=app.pk)
    return render_to_response('vdi/application-library.html',
        {'app_library': db_apps, },
        context_instance=RequestContext(request))

@login_required
def connect(request, app_pk=None, conn_type=None):
    # Check that the user has permissions to access this
    app = Application.objects.filter(pk=app_pk)[0]
    if not request.user.has_perm('vdi.use_%s' % app.name):
        return HttpResponseRedirect(settings.LOGIN_URL)

    # Get an AppCluster instance
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
        user_experience = UserExperience.objects.create(user=request.user, application=app)
        user_experience.access_date = datetime.today()
        user_experience.save()
        try:
            # Determine which host this user should use
            host = cluster.select_host()
        except NoHostException:
            # Start a new instance immedietly and redirect the user back to this page after 20 seconds
            # Only boot a new node if there are none currently booting up
            if len(cluster.booting) == 0:
                cluster.start_node()
            return render_to_response('vdi/app_not_ready.html',
                {'app': cluster.app,
                'reload_s': settings.USER_WAITING_PAGE_RELOAD_TIME,
                'reload_ms': settings.USER_WAITING_PAGE_RELOAD_TIME * 1000})

        # Random Password Generation string
        chars=string.ascii_letters+string.digits
        password = ''.join(choice(chars) for x in range(6))
        log.debug("THE PASSWORD IS: %s" % password)

        # Get IP of user
        # Implement firewall manipulation of instance
        log.debug('Found user ip of %s' % request.META["REMOTE_ADDR"])

        # Grab the proper osutils object
        log.debug("before osutils get")
        osutil_obj = osutils.get_os_object(host.ip, settings.MEDIA_ROOT + str(cluster.app.ssh_key))
        if osutil_obj:    
            log.warning(request.session)
            status, error_string = osutil_obj.add_user(request.session['username'], password)
            if status == False:
                return HttpResponse(error_string)

            # Add the created user to the Administrator group
            status = osutil_obj.add_administrator(request.session['username'])
            if status == False:
                HttpResponse(error_string)
            else:
                log.debug("Added user %s to the 'Administrators' group" % request.session['username'])
        else:
            return HttpResponse('Your server was not reachable')

        # This is a hack for NC WISE only, and should be handled through a more general mechanism
        # TODO refactor this to be more secure
        rdesktopPid = Popen(["rdesktop","-u",request.session['username'],"-p",password, "-s", cluster.app.path, host.ip], env={"DISPLAY": ":1"}).pid
        # Wait for rdesktop to logon
        sleep(3)

        if conn_type == 'rdp':
            user_experience.file_presented = datetime.today()
            user_experience.save()
            return render_to_response('vdi/connect.html', {'username' : request.session['username'],
                                                        'password' : password,
                                                        'app' : cluster.app,
                                                        'ip' : host.ip},
                                                        context_instance=RequestContext(request))
            '''
            This code is commented out because it really compliments nxproxy.  Originally nxproxy and vdi were developed
            together but nxproxy has not been touched in a while.  I'm leaving this here for now because it is was hard to
            write, and it would be easy to refactor (probably into the nxproxy module) if anyone felt the need to do so.
            NOTE: There is a vestige of this code in the vdi URLconf

            elif conn_type == 'nxweb':
                return _nxweb(host.ip,request.session["username"],password,cluster.app)
            elif conn_type == 'nx':
                # TODO -- This url should not be hard coded
                session_url = 'https://opus-dev.cnl.ncsu.edu:9001/nxproxy/conn_builder?' + urlencode({'dest' : host.ip, 'dest_user' : request.session["username"], 'dest_pass' : password, 'app_path' : cluster.app.path})
                return HttpResponseRedirect(session_url)
            '''
        elif conn_type == 'rdpweb':
            tsweb_url = settings.VDI_MEDIA_PREFIX+'TSWeb/'
            user_experience.file_presented = datetime.today()
            user_experience.save()
            return render_to_response('vdi/rdpweb.html', {'tsweb_url' : tsweb_url,
                                                    'app' : cluster.app,
                                                    'ip' : host.ip,
                                                    'username' : request.session['username'],
                                                    'password' : password})
    elif request.method == 'POST':
        # Handle POST request types
        if conn_type == 'rdp':
            return _create_rdp_conn_file(request.POST["ip"], request.session['username'], request.POST["password"], cluster.app)

    '''
def _nxweb(ip, username, password, app):
    NOTE:
    This function probably belongs in nxproxy, but is being left here until someone cares enough about nxproxy to move it there

    Returns a response object which contains the embedded nx web companion
    ip is the IP address of the windows server to connect to
    username is the username the connection should use
    app is a vdi.models.Application

    # TODO -- These urls should not be hard coded
    session_url = 'https://opus-dev.cnl.ncsu.edu:9001/nxproxy/conn_builder?' + urlencode({'dest' : ip, 'dest_user' : username, 'dest_pass' : password, 'app_path' : app.path, 'nodownload' : 1})
    wc_url = settings.VDI_MEDIA_PREFIX+'nx-plugin/'
    return render_to_response('vdi/nxapplet.html', {'wc_url' : wc_url,
                                                'session_url' : session_url})
    '''

def _create_rdp_conn_file(ip, username, password, app):
    """
    Returns a response object which will return a downloadable rdp file
    ip is the IP address of the windows server to connect to
    username is the username the connection should use
    app is an instance of vdi.models.Application and is the application to be run on startup
    """
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


@login_required
def nx_conn_builder(request, app_pk=None):
    """
    Returns a response object containing an nx session.
    This function selects a node from the cluster.

    """
    resp = render_to_response('nxproxy/nx_single_session.html', {'nx_ip' : node.ip,
                        'nx_username' : username,
                        'nx_password' : connection_tools.encryptNXPass(nx_password),
                        'conn_type' : 'windows',
                        'dest' : request.GET["dest"],
                        'dest_username' : request.GET["dest_user"],
                        'dest_password' : connection_tools.encodePassword(request.GET["dest_pass"]),
                        'app_path' : app_path})

    if "nodownload" in request.GET:
        if int(request.GET["nodownload"]) == 1:
            return resp

    resp['Content-Type']="application/nx"
    # TODO update the hardcoded string 'connection' below to something like app.name  I'm not sure how to get that data here architecturally
    resp['Content-Disposition'] = 'attachment; filename="%s.nxs"' % 'connection'
    return resp


def show_cost(request):
    log.debug('cost = ')
    log.debug('weekday = %s' % datetime.now().weekday())
    log.debug(datetime.now().isocalendar())
    yesterday_midnight = datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
    day = cost_tools.get_instance_hours_in_date_range(yesterday_midnight,datetime.now())
    month_midnight = datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    month = cost_tools.get_instance_hours_in_date_range(month_midnight,datetime.now())
    year_midnight = datetime.today().replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0)
    week_midnight = year_midnight +timedelta(weeks=datetime.today().isocalendar()[1])
    week = cost_tools.get_instance_hours_in_date_range(week_midnight,datetime.now())
    return render_to_response('vdi/cost_display.html',
        {'day' : day, 'week' : week, 'month' : month},
        context_instance=RequestContext(request))

def calculate_cost(request, start_date, end_date):

    starting_date = cost_tools.convert_to_date_time(start_date)
    ending_date = cost_tools.convert_to_date_time(end_date)

    total_hours_in_range = cost_tools.get_instance_hours_in_date_range(starting_date, ending_date)
    cost = cost_tools.generate_cost(total_hours_in_range)

    return HttpResponse("Calculating cost for date " + str(starting_date) + " to " + str(ending_date) + ".  The total hours used in this range is " + str(total_hours_in_range) + " with cost $" + str(cost))

def user_feedback(request):
    form = UserFeedbackForm()
    return render_to_response('vdi/user-feedback.html',
        {'form' : form},
        context_instance=RequestContext(request))

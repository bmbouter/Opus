from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth.decorators import login_required

from nxproxy.models import NXNode
import core
log = core.log.getLogger()
from core.ssh_tools import HostNotConnectableError , NodeUtil

from subprocess import Popen, PIPE
from string import ascii_letters, digits
from random import choice

class NXSession(object):
    def __init__(self, line):
        terms = line.split()
        self.display = terms[0]
        self.username = terms[1]
        self.user_ip = terms[2]
        self.session_id = terms[3]
        self.node = terms[4]

@login_required
def sessions(request):
    if request.method == 'GET':
        return HttpResponse(_get_sessions())
    elif request.method == 'POST':
        return HttpResponse('POST')

def conn_builder(request,app_pk=None):
    '''
    Returns a response object containing an nx session.
    This function selects a node from the cluster.
    '''
    # TODO stop hardcoding the node selected
    node = NXNode.objects.all()[0]

    #Random Password Generation string
    chars = ascii_letters + digits
    nx_password = ''.join([choice(chars) for x in range(14)])
    username = request.session["username"]

    # SSH to the node, create a user, and set the password with the one-time password above
    ssh_node = NodeUtil(node.ip, settings.NX_NODE_PRIVATE_KEY, settings.NX_NODE_USER)
    try:
        output = ssh_node.ssh_run_command(["useradd", username])
        output = ssh_node.ssh_run_command(["passwd", "--stdin", username, "<<<", nx_password])
    except HostNotConnectableError:
        # TODO: recoded how the exception is handled to be useful
        return HttpResponse('UNABLE TO SSH TO NXNODE')

    # Determine the app_path to be run
    if "app_path" in request.GET:
        app_path = request.GET["app_path"]
    else:
        app_path = ''

    resp = render_to_response('nx_single_session.html', {'nx_ip' : node.ip,
                        'nx_username' : username,
                        'nx_password' : encryptNXPass(nx_password),
                        'conn_type' : 'windows',
                        'dest' : request.GET["dest"],
                        'dest_username' : request.GET["dest_user"],
                        'dest_password' : encodePassword(request.GET["dest_pass"]),
                        'app_path' : app_path})

    if "nodownload" in request.GET:
        if int(request.GET["nodownload"]) == 1:
            return resp

    resp['Content-Type']="application/nx"
    # TODO update the hardcoded string 'connection' below to something like app.name  I'm not sure how to get that data here architecturally
    resp['Content-Disposition'] = 'attachment; filename="%s.nxs"' % 'connection'
    return resp

def encryptNXPass(s):
    '''
    Encrypt a password like No Machine does
    '''
    dummyString = '{{{{'
    validCharList = '!#$%&()*+-.0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]_abcdefghijklmnopqrstuvwxyz{|}'
    if not s:
        return
    enc = encodePassword(s)
    sRet = ''
    if len(enc) < 32:
        enc = dummyString
    sRet = enc[::-1]
    if len(sRet) < 32:
        sRet += dummyString
    app = choice(validCharList)
    k = ord(app)
    l = k + len(sRet) - 2
    sRet = app+sRet

    for i in range(1,len(sRet)):
        j = validCharList.find(sRet[i])
        if j == -1:
            return sRet

        car = validCharList[(j + l * (i+1)) % len(validCharList)]
        sRet = ''.join([ sRet[:i], car, sRet[i+1:]])

    c = (ord(choice(validCharList))) + 2
    sRet = sRet + chr(c)
    return sRet

def encodePassword(password):
    '''
    Encode a password like No Machine does
    '''
    if not password:
        return password
    sPass = [':']
    for i in range(len(password)):
        c = password[i]
        sPass.append("%s:" % int(ord(c)+i+1))
    return ''.join(sPass)

def _get_sessions():
    # Get all Nodes
    nodes = NXNode.objects.all()

    all_sessions = []
    for node in nodes:
        ssh_node = NodeUtil(node.ip,settings.NX_NODE_PRIVATE_KEY,settings.NX_NODE_USER)
        try:
            output = ssh_node.ssh_run_command(["nxserver", "--list"])
        except HostNotConnectableError:
            # TODO: recoded how the exception is handled to be useful
            return HttpResponse('Error: Could not connect to NXNode')
        for line in output.split('\n')[4:]:            
            if not line:
                break;
            all_sessions.append(NXSession(line))
    
    return render_to_response('nx_list_sessions.html',
        {'sessions': all_sessions})

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from nxproxy.models import NXNode
from vdi import user_tools

from subprocess import Popen, PIPE

class NXSession(object):
    def __init__(self, line):
        terms = line.split(' ')
        self.display = terms[0]
        self.username = terms[1]
        self.remote_ip = terms[2]
        self.session_id = terms[3]
        self.node = terms[4]

@user_tools.login_required
def sessions(request):
    if request.method == 'GET':
        return HttpResponse(_get_sessions())
    elif request.method == 'POST':
        return HttpResponse('POST')

def _get_sessions():
    # Get all Nodes
    nodes = NXNode.objects.all()

    all_sessions = []
    for node in nodes:
        output = Popen(["ssh", "-i", settings.NX_NODE_PRIVATE_KEY, "-l", settings.NX_NODE_USER, "-o", "StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null", node.ip, "nxserver", "--list"], stdout=PIPE, stdin=PIPE).communicate()[0]
        for line in output.split('\n')[4:]:            
            return HttpResponse(line)
            return HttpResponse(NXSession(line).remote_ip)
            all_sessions.append(NXSession(line))
    
    return HttpResponse(all_session[0].remote_ip)

from django.shortcuts import render_to_response


def nx_conn_builder(ip, username, password, app):
    """
    Returns a response object containing an nx session.
    This function selects a node from the cluster.

    """
    resp = render_to_response('vdi/nx_single_session.html', 
                        {'nx_ip' : ip,
                        'nx_username' : username,
                        'nx_password' : encryptNXPass(password),
                        'conn_type' : 'unix',
                        'app_path' : app.path})

    resp['Content-Type']="application/nx"
    # TODO update the hardcoded string 'connection' below to something like app.name  I'm not sure how to get that data here architecturally
    resp['Content-Disposition'] = 'attachment; filename="%s.nxs"' % app.name
    return resp


def encryptNXPass(s):
    """Encrypt a password like No Machine does."""
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
    """Encode a password like No Machine does."""
    if not password:
        return password
    sPass = [':']
    for i in range(len(password)):
        c = password[i]
        sPass.append("%s:" % int(ord(c)+i+1))
    return ''.join(sPass)

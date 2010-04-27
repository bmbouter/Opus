import ldap
from core import log
log = log.getLogger()

def get_ldap_roles(server, username, password):
    timeout = 0
    result_set = []
    
    try:
        ldap_session = ldap.open(server.url)
        ldap_session.protocol_version = ldap.VERSION3
        
        if server.ssl_option == True:
            ldap_session.start_tls_s()
            ldap_session.set_option(ldap.OPT_X_TLS_DEMAND, True)
        else:
            ldap_session.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        user_dn = "uid=" + username 
        if server.distinguished_name:
            search_string = server.distinguished_name + ',' + server.bind_base
        else:
            search_string = server.bind_base
        authentication_string = user_dn + "," + search_string
        log.debug(authentication_string)

        ldap_session.simple_bind_s(authentication_string, password)
        
        if server.group_retrieval_string != '':
            result_id = ldap_session.search(search_string,ldap.SCOPE_SUBTREE,user_dn,[str(server.group_retrieval_string)])
            while 1:
                result_type, result_data = ldap_session.result(result_id, timeout)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            #log.debug(result_set)
            roles = result_set[0][0][1][str(server.group_retrieval_string)]
            #log.debug("LDAP Roles = " + str(roles))
            return roles
        else:
            return {}
    except ldap.LDAPError, e:
        log.debug("LDAP Error: " + str(e))
        return None
    finally:
        log.debug("Unbinding")
        ldap_session.unbind()


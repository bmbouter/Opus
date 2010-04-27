import ldap
from core import log
log = log.getLogger()

def get_ldap_roles(url, username, password, authentication_identifier, ssl_option, group_retrieval_string):
    timeout = 0
    result_set = []
    
    try:
        ldap_session = ldap.open(url)
        ldap_session.protocol_version = ldap.VERSION3
        
        if ssl_option == True:
            ldap_session.start_tls_s()
            ldap_session.set_option(ldap.OPT_X_TLS_DEMAND, True)
        else:
            ldap_session.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        search_string = "uid=" + username
        authentication_string = search_string + "," +  authentication_identifier
        
        ldap_session.simple_bind_s(authentication_string, password)
        
        if group_retrieval_string != '':
            result_id = ldap_session.search(authentication_identifier,ldap.SCOPE_SUBTREE,search_string,[str(group_retrieval_string)])
            while 1:
                result_type, result_data = ldap_session.result(result_id, timeout)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            log.debug(result_set)
            roles = result_set[0][0][1][str(group_retrieval_string)]
            log.debug("LDAP Roles = " + str(roles))
            return roles
        else:
            return {}
    except ldap.LDAPError, e:
        log.debug("LDAP Error: " + str(e))
        return None
    finally:
        log.debug("Unbinding")
        ldap_session.unbind()


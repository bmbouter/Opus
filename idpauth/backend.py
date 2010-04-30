from django.contrib.auth.models import User, Permission, Group

from idpauth.models import IdentityProvider

from core import log
log = log.getLogger()


class IdpAuthBackend:

    def authenticate(self, username=None, password=None):
        if not username:
            return None
        else:
            if password == None:
                log.debug("Non-local authen")
                user, created = User.objects.get_or_create(username=username)
                return user
            else:
                log.debug("local authen")
                try:
                    user = User.objects.get(username=username)
                    if user.check_password(password):
                        return user
                except User.DoesNotExist:
                    log.debug("User not found in database")
                    return None
    
    def get_group_permissions(self, user_obj):
        institution = user_obj.username.split('++')
        if len(institution) == 1:
            idp = 'local'
        else:
            idp = IdentityProvider.objects.filter(institution=institution[0])

        if idp[0].type == 'ldap':
            perms = []
            user_profile = user_obj.get_profile()
            roles = user_profile.ldap_roles
            groups = Group.objects.filter(identityprovider=idp)
            for arg in groups:
                group_name = str(arg.name)
                if group_name in roles:
                    perms.extend(Permission.objects.filter(group=arg
                    ).values_list('content_type__app_label', 'codename').order_by())       
            user_obj._group_perm_cache = set(["%s.%s" % (ct, name) for ct, name in perms])
        else:
            perms = Permission.objects.filter(group__identityprovider=idp
            ).values_list('content_type__app_label', 'codename').order_by()
            user_obj._group_perm_cache = set(["%s.%s" % (ct, name) for ct, name in perms])
        
        return user_obj._group_perm_cache


    def get_all_permissions(self, user_obj):
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set([u"%s.%s" % (p.content_type.app_label, p.codename) for p in user_obj.user_permissions.select_related()])
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm):
        return perm in self.get_all_permissions(user_obj)

    def has_module_perms(self, user_obj, app_label):
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


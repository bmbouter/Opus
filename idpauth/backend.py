from django.contrib.auth.models import User

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
                if created:
                    user = self.configure_user(user)
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

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def configure_user(user):
        return user
            

class Generic(object):
    def __init__(self, ip, ssh_key):
        raise NotImplementedError()

    def add_user(self, username, password):
        raise NotImplementedError()

    def change_user_password(self, username, password):
        raise NotImplementedError()

    def add_administrator(self, username):
        raise NotImplementedError()

    def log_user_off(self, username):
        raise NotImplementedError()

    def check_user_load(self):
        raise NotImplementedError()

    def user_cleanup(self, timeout):
        raise NotIMplementedError()

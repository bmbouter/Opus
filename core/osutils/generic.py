class Generic(object):
    def __init__(self, ip):
        self.ip = ip

    def add_user(self):
        raise NotImplementedError()

    def change_user_password(self):
        raise NotImplementedError()

    def log_user_off(self):
        raise NotImplementedError()

    def check_user_load(self):
        raise NotImplementedError()

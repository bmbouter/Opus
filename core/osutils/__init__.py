from core.ssh_tools import NodeUtil


def get_os_object(ip, ssh_key):
    name = get_os_type(ip, ssh_key)

    if name == "linux":
        from linux import Linux as m
    elif name == "windows":
        from windows import Windows as m
    else:
        raise ValueError()

    return m(ip, ssh_key)

def get_os_type(ip, ssh_key):
    node = NodeUtil(ip, ssh_key)
    if node.ssh_avail():
        return "Windows"
    else:
        raise "None"

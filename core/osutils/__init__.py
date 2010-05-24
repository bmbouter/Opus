from core.ssh_tools import NodeUtil
from core import log
log = log.getLogger()


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
    log.debug("Checking OS Type")
    output = node.ssh_run_command(["uname"])
    if "Linux" in output:
        log.debug("Found a Linux machine")
        return "linux"
    else:
        log.debug("Found a Windows machine")
        return "windows"
    return "None"

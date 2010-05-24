from core import ssh_tools

def get_os_type(ip, ssh_key):
    node = NodeUtil(ip, ssh_key)
    os_version_command = "systeminfo | findstr \"OS VERSION\""
    node.ssh_run_command(os_version_command)

def get_os_distribution():
    pass

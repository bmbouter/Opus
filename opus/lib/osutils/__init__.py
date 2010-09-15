##############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
##############################################################################

from opus.lib.ssh_tools import NodeUtil
from opus.lib import log
log = log.get_logger("opus.lib.osutils")


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

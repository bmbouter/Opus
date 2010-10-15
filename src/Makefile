# Set this to the path to the apachectl script. On Fedora this is
# /usr/sbin/apachectl, on Ubuntu it's /usr/sbin/apache2ctl
APACHECTL=/usr/sbin/apachectl

# Change this to the group Opus will be running as when it tries to execute
# this. This is probably the apache user (apache on Fedora, www-data on
# Ubuntu), but you may have deployed Opus to run under a different user/group.
OPUSGROUP=apache

secureops: secureops.c
	gcc -Wall -Werror secureops.c -o secureops -D APACHECTL=\"${APACHECTL}\"
	sudo chown root secureops
	sudo chgrp ${OPUSGROUP} secureops
	sudo chmod 4750 secureops

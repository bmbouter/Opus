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

"""
This file holds routines for automatic database configuration

"""

import random
import string

from django.db import connection, transaction

from opus.lib.log import get_logger
log = get_logger()

def setup_postgres(projectname):
    """Sets up a postgres user with a random password, creates a database with
    the same name, and returns (dbname, dbuser, dbpassword, dbhost, dbport)

    """
    cursor = connection.cursor()
    username = "opus" + projectname
    dbname = username
    password = "".join(random.choice(string.ascii_letters + string.digits) \
            for _ in xrange(20))

    # usernames and dbnames are not strings, only the password is parameterized
    cursor.execute("COMMIT")
    cursor.execute("CREATE USER "+username+" PASSWORD %s", [password])
    cursor.execute("CREATE DATABASE %s" % (dbname,))

    return dbname, username, password, "localhost", ""

def delete_postgres(projectname):
    cursor = connection.cursor()
    dbname = username = "opus" + projectname
    log.info("Removing postgres user and database")
    cursor.execute("COMMIT")
    try:
        cursor.execute("DROP DATABASE %s" % (dbname,))
    except Exception, e:
        log.warning("Failed to drop database. %s", e)
    try:
        cursor.execute("DROP USER %s" % (username,))
    except Exception, e:
        log.warning("Failed to drop user. %s", e)

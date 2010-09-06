
=============
    Opus
=============
Welcome to Opus. The Open Source Services Management Platform.

https://fedorahosted.org/opus/

----------
About Opus
----------
In a nutshell, Opus allows the automatic deployment of Django projects in a
secure way. Specifically, it automates the following items in the process of
deploying a project:

* Configures a new Django project given a list of applications
* Creates a new system user specifically for the project
* Sets files with sensitive information (such as settings.py, an sqlite
  database) to be owned by the new user and no world-read permissions.
* Configures and syncs the database
* Generate a (temporary) self-signed certificate for SSL deployments
* Writes out an Apache configuration file
* Writes out a WSGI file
* Restarts Apache (gracefully, of course)

The entire process is fully automated. Additionally, the entire procedure is
reversible to tear down and destroy a project. Applications can also be added,
removed, or updated on a live project.

Applications for installation in a managed project can come either from a local
filesystem path, or from an external Git repository. If Git is chosen, the
repository will automatically be cloned, and can later be reset to a different
version on request.

Opus is configured with a virtual host base, and a port. You configure Apache
as a NameVirtualHost on that port, and Opus generates Apache configuration
files for each project. For example, if the Opus Servername Suffix is set to
".opus.example.com", a deployed project will host from
"projectname.opus.example.com"

And of course, everything is done with security in mind. Each deployed project
has its own Linux user, and mod_wsgi is set to run projects as that user.
Sensitive configuration files are readable only by that user and the Opus
management user.

-----------
Source Tree
-----------
Here's a rundown on what you've just downloaded:

opus/
    Python package containing all of the Opus Python code.

opus/project/
    The Opus Django project, which contains the primary frontend interface to
    the project builder, deployer, and scaler.

opus/lib/
    Contains Opus supporting libraries and code for applications to use.

opus/lib/builder/
    The Django project building code.

opus/lib/deployer/
    The Django project deployment code

opus/lib/conf/
    The code that manipulates settings of Django projects

opus/lib/prov/
    Provisioning related libraries

src/
    The supporting C code used by the deployer to do certain privileged
    operations.

gwt/
    The source to the Google Web Toolkit interface.

gwt/build
    This is the compiled GWT javascript code needed for the GWT interface to
    function. It's provided in the source distribution for convenience.

------------
Requirements
------------
Opus in its current form requires:

* Python 2.6 or greater (not 3.x)
* Django 1.2 or greater
* Apache
* mod_wsgi
* Linux
* A Django compatible database server
* A C compiler to compile the secureops program (see below)
* Celery and Django-celery (djcelery)
* A Celery compatible message broker such as RabbitMQ

To build the Google Web Toolkit component, you need

* Java
* GWT SDK

----------
Installing
----------
The installation procedure for Opus is not simple. There are a lot of
components that work together, and a lot of steps. We have tried to make this
readme as complete and comprehensive as possible. If you find something
incorrect, missing, or even something that's just a bit confusing or unclear,
let us know. We are committed to keeping this readme as a clear and complete
as possible.

Below, there are several references to the "Opus user." This refers to the
Linux user that the Opus application will be running as. Typically, this is
the same user that Apache uses, and is "apache" throughout examples in this
documentation, but since mod_wsgi can be configured to run projects as another
user (with daemon mode), we use the term "Opus user" instead.

Prerequisites
-------------
Before you begin, you must have all the requirements installed. You must
configure the database server with a username, password, and database for Opus
to use. You must configure your message passing broker with a user, password,
and vhost for Opus to use.

Configuring Postgres
````````````````````
If you choose to use Postgres, here's an example on how our setup usually
goes. This may not work for every system (we use Fedora), but should give you
an idea of what's involved.

We recommend the following setup for your Postgres pg_hba.conf for security::

    # Used for the administrator (a human) to connect.  This can only be
    # accessed by user postgres
    local   all         postgres                               ident sameuser

    # Allow any user to connect to a database of the same name from SSL and only
    # from localhost
    hostssl sameuser         all           127.0.0.1/32           md5
    hostssl sameuser         all           ::1/128           md5

Then connect as the postgres user with `sudo -u postgres psql` and run these
commands to create a user for Opus::

    CREATE USER opus WITH PASSWORD 'putpasswordhere' CREATEROLE CREATEDB;
    CREATE DATABASE opus OWNER opus;

You will now need to generate an ssl cert and key, name them `server.crt` and
`server.key` and put them in the Postgres data directory. It's okay if it's
self signed. You can do this by going to `/etc/pki/tls/certs` and using the
provided makefile. Make sure the files have permissions 600 and are owned by
the Postgres user.

Then you need to go into the data directory, and edit the `postgres.conf` file
to enable ssl. Uncomment the ssl line and change it to `on`.

Then later when configuring database options, make sure to put "localhost" for
the database host, instead of leaving it blank. Otherwise, it will attempt to
use local sockets instead of tcp, which will fail. Also, uncomment the
"sslmode" line in settings.py to ensure encrypion is used.

**Important Note:** Since Opus creates Postgres users and databases of the
format "opus<appname>" you should **not** name your user/database something
that starts with "opus". This could cause conflicts, and in a worst case,
cause Opus to de-provision its own database.

Configuring RabbitMQ
````````````````````
Opus requires a message passing broker, both for itself and to provide to
deployed projects. We recommend RabbitMQ, since it's easy to set up and scales
excellently.

Once installed, you will need to create a user and a vhost for Opus. Remember
these parameters, you will enter them later when configuring Opus' settings.py
file.

These commands can be used to create a new user, a new vhost, and set
permissions. You will probably need to run these under sudo::

    $ rabbitmqctl add_user my_opus_user mypassword
    $ rabbitmqctl add_vhost my_opus_vhost
    $ rabbitmqctl set_permissions -p my_opus_vhost my_opus_user "" ".*" ".*"

As far as I have found, putting the password on the command line is the only
way to set a RabbitMQ password. Be mindful of terminal logs, bash history
logs, and sudo logs that all may save the password.

**Important Note:** Since Opus creates RabbitMQ users and vhosts of the format
"opus<appname>" you should **not** name your user/vhost something that starts
with "opus".  This could cause conflicts, and in a worst case, cause Opus to
de-provision its own database.

Installing Opus
---------------
To install opus, use the following command::

    python setup.py install

from within the source distribution to install the Opus python libraries and
supporting files.

Once the libraries are in place, move on to the next step.

Secure Ops
----------
Under the src/ directory in the source is a single C file and a Makefile. Opus
needs to do certian operations that a non-superuser isn't normally allowed to
do. Specifically, it needs to create system users, change ownership of files,
and restart Apache. This is all done with a small simple C program compiled and
set to run with suid root.

This file is not compiled by setup.py. You will need to compile and install it
yourself.

Compile this file and set its suid flag. It should be owned by root, and only
executable by the Opus user (by setting the group appropriately).  A Makefile
is provided for convenience. It will compile the file using gcc and then use
sudo to change the ownership and permissions of the file. If your system is
configured differently, for example with a different Apache user, then you will
need to either modify the Makefile or compile it yourself.

Once the binary is compiled and working, take note of where it's installed to.
It doesn't need to be installed to a system-wide location, but it does need to
be where the opus user can execute it. You will configure the path to the
executable in the next step in the settings.py under the
OPUS_SECUREOPS_COMMAND option.

Settings
--------
The next step is to deploy the Django project, which you can find installed as
opus.project. To do that, first configure it:

* Copy the settings.py.sample to settings.py
* Configure the necessary settings in there. At a minimum, you'll need to set
  these parameters (this isn't an exaustive list of parameters, just the
  minimum you need to set to get a working installation). See the comments in
  the file for what they do.

  * DATABASE parameters
  * Message Broker parameters
  * SECRET_KEY
  * TEMPLATE_DIRS
  * OPUS_BASE_DIR
  * OPUS_APACHE_CONFD
  * OPUS_SECUREOPS_COMMAND
  * LOG_DIR
  * OPUS_APACHE_SERVERNAME_SUFFIX

Don't forget to make the base directory, log directory, and Apache conf
directory writable by the Opus user.

If you're using sqlite, you must create a directory to house the database file
and the directory must be writable by the Opus user. (Sqlite uses temporary
files, and must have write permission to the entire directory containing the
database file). If you haven't already, create a directory, change ownership
to the Opus user, and reset the database parameter in the settings.py file.

Database Sync
-------------
Now you need to sync the database. This needs to be done as the Opus user,
otherwise log files and sqlite (if it's used) will have the wrong owner and
Opus will get permission errors. If the opus user is "apache", then run this
command from the project directory::

    $ sudo -u apache python manage.py syncdb

If you run this command as root (or any user other than the Opus user), the
sqlite database (if any) as well as some log files will get created as that
user, and thus you will get permission denied errors later when Opus is being
run as an unprivileged user. Make sure you go back and set permissions
appropriately for any files in the LOG_DIR directory, and the sqlite file if
using sqlite.

Deployment
----------
At this point, deployment for Opus is mostly like like any other project as
described in the `Django Deployment Guide`_.

For convenience, a sample wsgi file is included in the "wsgi" directory of the
Opus project directory.

It looks like this::

    import os
    import sys

    os.environ['DJANGO_SETTINGS_MODULE'] = 'opus.project.settings'
    os.environ['CELERY_LOADER'] = "django"

    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()

Note the celery line, which is required for celery to work. If you have your
settings module in a different location, you will need to adjust that line.

The Opus package must be on the Python path for the project to run. If Opus
isn't installed to a system location, or if Opus isn't on your Python path some
other way, then you'll need to add a line such as the following::

    sys.path.insert(0, "/opt/opus-repository")

To be clear, this is the path to the directory *containing* the "opus"
directory, which is the Opus package. In the above example, the opus package
would be /opt/opus-repository/opus, and /opt/opus-repository is the repository
containing this README, the opus package, setup.py, and such.

Once your wsgi file looks good, Apache must be configured to run this app.
Again, follow your normal procedure for deploying a Django app with mod_wsgi,
see the `Django Deployment Guide`_ for help.

 .. _Django Deployment Guide: http://docs.djangoproject.com/en/1.2/howto/deployment/modwsgi/

**Note:** Opus *must* be deployed using mod_wsgi's "Daemon Process" option.
This has to do with how Apache reloads itself, and since Opus periodically
must restart Apache, this causes problems if Opus is running in mod_wsgi's
"embedded mode." The below example takes care of this with the
"WSGIDaemonProcess" and "WSGIProcessGroup" options. This is a limitation that
will hopefully go away once Celery is better integrated.

Here is an example of the opus.conf Apache configuration::

    NameVirtualHost *:80
    NameVirtualHost *:443

    WSGIDaemonProcess OPUS

    <VirtualHost *:80>
        Alias /gwt /var/www/opusenv/share/opus/build
        Alias /adminmedia /usr/lib/python2.6/site-packages/django/contrib/admin/media
        WSGIProcessGroup OPUS
        WSGIScriptAlias / /var/lib/opus/project/wsgi/opus.wsgi
    </VirtualHost>
    <VirtualHost *:443>
        Alias /gwt /var/www/opusenv/share/opus/build
        Alias /adminmedia /usr/lib/python2.6/site-packages/django/contrib/admin/media
        WSGIProcessGroup OPUS
        WSGIScriptAlias / /var/lib/opus/project/wsgi/opus.wsgi
        SSLEngine On
        SSLCertificateFile /path/to/cert/file
        SSLCertificateKeyFile /path/to/key/file
    </VirtualHost>

    Include conf.d/opus/*.conf

You will of course need to change paths and such for your own deployment; this
is only an example. See notes in the next section about this example and what
you need to watch out for.

If you don't want or need SSL, remove those lines and set OPUS_HTTPS_PORT to
None in the settings.py file. Note that SSL virtual host support is provided
by the `Server Name Indication`_ protocol. Not all client browsers support
this.

 .. _Server Name Indication: http://en.wikipedia.org/wiki/Server_Name_Indication

Apache Configuration
--------------------
Apache needs to have a few configuration items apart from the standard
Django+mod_wsgi deployment. Somewhre in your Apache config, set the following
items.

* As shown in the above example, A NameVirtualHost line must be present for
  the ports that Opus will be deploying projects to. For example, if you have
  Opus configured to deploy to ports 80 and 443, Apache needs to have these
  lines in its configuration::

    NameVirtualHost *:80
    NameVirtualHost *:443

* If Opus is configured to serve on non-standard ports (besides 80 and 443),
  make sure to add the appropriate "Listen" directives

* As shown in the above example, make sure to add an "Include" directive to
  include `*.conf` in the directory configured by OPUS_BASE_DIR. e.g.::

    Include conf.d/opus/*.conf

* If you want to use the GWT interface (you probably do), you must configure
  a webserver (perhaps the same one, it doesn't matter) to serve the files
  from gwt/build/ in the source distribution (setup.py will install these files
  to <prefix>/share/opus/build). Then configure Opus's OPUS_GWT_MEDIA directive
  to where browsers can find that media. e.g.::

    Alias /gwt /usr/local/share/opus/build

Celery Daemon
-------------
In order for the asynchronous tasks that Opus uses to run, you must start the
Celery daemon. This can be done by running `manage.py celeryd` which is found
in the opus/lib/project directory. This will most likely need to be run as the
Opus user. e.g.::

    sudo -u apache ./manage.py celeryd

See the Celery documentation for how to run this as a system daemon. We
recommend using a package called supervisord, which can be pip-installed since
it's a pure python process manager.

For your convenience, since supervisord doesn't come with an init script,
here's the one we use:
http://github.com/bmbouter/supervisord_init_script/blob/master/supervisord

Misc Notes
----------
Unfortunately, there are a few caveats at the moment.

* django-admin.py must be in the system path. This isn't a problem unless
  Django and Opus are running in a virtualenv. The solution right now is to
  copy django-admin.py into a system path such as /usr/local/bin

* If you get errors of this nature::

    child pid 30465 exit signal Segmentation fault (11)
    mod_wsgi (pid=30466): Unable to determine home directory for uid=-1.

  See this page: http://code.google.com/p/modwsgi/issues/detail?id=40

  To fix it, see the next bullet.

* WSGI's daemon processes if configured by default to run with the same user
  as Apache, will fail since Apache by default has the `Include conf.d/*.conf`
  line before the "User apache" line. The solution is to move the include line
  down below the user line. (This seems like a mod_wsgi problem more than an
  Opus problem)

* As shown in the example in the last section, the `Include
  conf.d/opus/*.conf` line ought to go below the virtualhost declaration for
  Opus, so that it is the default virtual host served by apache.

* If you get errors of this nature::

    Unable to connect to WSGI daemon process 'OPUS' on
    '/etc/httpd/logs/wsgi.30603.0.1.sock' after multiple attempts.

  See
  http://code.google.com/p/modwsgi/wiki/ConfigurationIssues#Location_Of_UNIX_Sockets

  To fix it, add this line to your Apache configuration::

    WSGISocketPrefix run

------------------
After Installation
------------------
Once Opus is installed and everything is running you should be able to log
into the admin interface and the deployment interface.


Admin Interface
---------------
The admin interface is located at `/admin`. From there, you can add new users
to the system. Right now, any user with an account can create deployments. A
user can only see and modify their own deployments, unless the user is a
super-user.

Deploying Projects
------------------
To deploy a new project, go to `/deployments/`. From there, a user can see
their deployments, and create new deployments through the standard no-frills
interface. New projects are created by filling out the new project form.
Existing projects are edited by clicking on them. From there, you can edit
anything about a project except its name.

App Formats
```````````
Projects currently have two mechanisms for importing applications. Opus can
either copy an application from a location on the local filesystem, or use Git
to clone a remote repository. In both cases, the directory or Git repository
must have a layout just like created by `django-admin.py startapp`. That is,
the __init__.py, urls.py, models.py, and such must be in the top level. The app
is copied (or cloned) right into the project directory and expects it to fit
right in place.

More application sources are easily added, we plan to have more in the future.

GWT Interface
-------------
It is our intention to have the web frontend written entirely with the Google
Web Toolkit. We currently include both a hand-written HTML interface, which we
use to test things out, and are developing in parallel a GWT interface that
looks nice and will eventually replace it. But until it's ready, we'll be
including both.

The GWT interface is served from `/` (i.e. the root URL).

In order for the GWT interface to function, the GWT media directory needs to be
set up.  These are static css and javascript files. Set Apache (or any server)
to serve these static files as described above in the `Apache Configuration`_
section.

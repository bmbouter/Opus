
=============
    Opus
=============
Welcome to Opus. The Open Source Services Management Platform.

----------
About Opus
----------
In a nutshell, Opus allows the automatic deployment of Django projects in a
secure way. Specifically, it automates the following items in th process of
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
reversable to tear down and destroy a project. Applications can also be added,
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
* Some kind of database and the Django compatible Python bindings for it
* A C compiler to compile the secureops program (see below)

To build the Google Web Toolkit component, you need

* Java
* GWT SDK

----------
Installing
----------
Below, there are several references to the "Opus user." This refers to the
Linux user that the Opus application will be running as. Typically, this is the
same user that Apache uses, but since mod_wsgi can be configured to run
projects as another user, we use the term "Opus user" instead.

The first step is to install opus. Use

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
  * SECRET_KEY
  * TEMPLATE_DIRS
  * OPUS_BASE_DIR
  * OPUS_APACHE_CONFD
  * OPUS_SECUREOPS_COMMAND
  * LOG_DIR
  * OPUS_APACHE_SERVERNAME_SUFFIX

Don't forget to make the base directory, log directory, and Apache conf
directory writable by the Opus user.

Database Sync
-------------
Now sync the database by calling `python manage.py syncdb`. Standard Django
procedure.

If you're using sqlite, you must create a directory to house the database file
and the directory must be writable by the Opus user, not just the one sqlite
file (since sqlite uses temporary files).

Note that if you run this command as root (or any user other than the Opus
user), the sqlite database (if any) as well as some log files will get created
as that user, and thus you will get permission denied errors later when Opus
is being run as an unprivileged user. Make sure you go back and set
permissions appropriately for any files in the LOG_DIR directory, and the
sqlite file if using sqlite.

Apache Configuration
--------------------
Apache needs to have a few configuration items apart from the standard
Django+mod_wsgi deployment. Somewhre in your Apache config, set the following
items. We recommend putting this in a separate opus.conf inside of conf.d.

* A NameVirtualHost line must be present for the ports that Opus will be
  deploying projects to. For example, if you have Opus configured to deploy to
  ports 80 and 443, Apache needs to have these lines in its configuration::

    NameVirtualHost *:80
    NameVirtualHost *:443

* If Opus is configured to serve on non-standard ports (besides 80 and 443),
  make sure to add the appropriate "Listen" directives

* Make sure to add an "Include" directive to include `*.conf` in the directory
  configured by OPUS_BASE_DIR. e.g.::

    Include conf.d/opus/*.conf

* If you want to use the GWT interface (you probably do), you must configure
  a webserver (perhaps the same one, it doesn't matter) to serve the files
  from gwt/build/ in the source distribution (setup.py will install these files
  to <prefix>/share/opus/media). Then configure Opus's OPUS_GWT_MEDIA directive
  to where browsers can find that media. e.g.::

    Alias /gwt /usr/local/share/opus/media

Deployment
----------
At this point, deploy the Opus project like any other project as described in
the `Django Deployment Guide`_.

For convenience, here is a sample wsgi file that will need to be created::

    import os
    import sys

    os.environ['DJANGO_SETTINGS_MODULE'] = 'opus.project.settings'

    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()

The Opus package must be on the Python path for the project to run. If Opus
isn't installed to a system location, or if Opus isn't on your Python path some
other way, then you'll need to add a line such as the following::

    sys.path.insert(0, "/opt/opus-repository")

To be clear, this is the path to the directory *containing* the "opus"
directory, which is the Opus package. In the above example, the opus package
would be /opt/opus-repository/opus, and /opt/opus-repository is the repository
containing this README, the opus package, setup.py, and such.

Once your wsgi file is in place, Apache must be configured to run this app.
Again, follow your normal procedure for deploying a Django app with mod_wsgi,
see the `Django Deployment Guide`_ for help.

 .. _Django Deployment Guide: http://docs.djangoproject.com/en/1.2/howto/deployment/modwsgi/

**Note:** Opus *must* be deployed using mod_wsgi's "Daemon Process" option.
This has to do with how Apache reloads itself, and since Opus periodically
must restart Apache, this causes problems if Opus is running in mod_wsgi's
"embedded mode." So make sure lines such as these are in the context of the
WSGIScriptAlias directive in the Apache configuration::

    WSGIDaemonProcess OPUS
    WSGIProcessGroup OPUS

Here is an example of the opus.conf Apache configuration::

    NameVirtualHost *:80
    NameVirtualHost *:443

    <VirtualHost *:80>
            Alias /gwt /var/www/opusenv/share/opus/gwtmedia
            WSGIDaemonProcess OPUS
            WSGIProcessGroup OPUS
            WSGIScriptAlias / /var/lib/opus/wsgi/opus.wsgi
    </VirtualHost>

    Include conf.d/opus/*.conf

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

* As shown above, the `Include conf.d/opus/*.conf` line ought to go below the
  virtualhost declaration for Opus, so that it is the default virtual host
  served by apache.

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
Once Opus is installed and deployed you should be able to log into the admin
interface and the deployment interface.


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

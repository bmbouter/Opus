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
Opus configuraiton related functions go in this package.

"""

import json
import os
import os.path
import random

import opus

def load_settings(globals):
    """Loads settings from the configuration file into the caller's locals
    dict. This is intended to be used from within a Django settings.py to load
    dynamic settings like this:
    >>> from opus.lib.conf import load_settings
    >>> load_settings()

    """
    try:
        settings_file = os.environ["OPUS_SETTINGS_FILE"]
        if not settings_file:
            raise KeyError()
    except KeyError:
        raise ImportError("Cannot find Opus settings file, OPUS_SETTINGS_FILE was undefined")
    try:
        with open(settings_file,'r') as f:
            objs = json.load(f)
    except IOError, e:
        print repr(settings_file)
        raise
    # Encode all strings, see docstring explanation in recurse_encode
    objs = recurse_encode(objs)

    for name, value in objs.iteritems():
        globals[name] = value

def recurse_encode(obj):
    """Recursively go through a structure and change unicode strings to byte
    strings encoded with UTF-8
    Needed because Django chokes when some of its settings are unicode objects
    instead of strings, and because the json library was too difficult to
    figure out how to extend right now.

    Returns the encoded object

    """
    if isinstance(obj, unicode):
        return obj.encode("UTF-8")
    elif isinstance(obj, dict):
        newdict = {}
        for key,value in obj.iteritems():
            if isinstance(key, unicode):
                key = key.encode("UTF-8")
            value = recurse_encode(value)
            newdict[key] = value
        return newdict
    elif isinstance(obj, (list, tuple)):
        for i, oldobj in enumerate(obj):
            obj[i] = recurse_encode(oldobj)
        return obj
    else:
        return obj

class OpusConfig(object):
    """A dictionary like object that supports reading, editing, and saving of
    Opus settings files.

    Provides a dictionary like interface to editing settings.

    Call save() to save the settings back to the file

    Careful that nothing else has edited the file before saving, this class has
    no such checks in place.

    """
    def __init__(self, settingsfile, new=False):
        """Creates a new OpusConfig object with the given settings file.  If
        new is True, an existing file will not be read at initialization, and
        instead the settings will be blank. The named file will still be used
        upon save.

        To create new settings from the template, use
        OpusConfig.new_from_template()
        
        """
        if not new:
            with open(settingsfile,'r') as f:
                self._settings = json.load(f)
        else:
            self._settings = {}
        self._filename = settingsfile

    @staticmethod
    def new_from_template(filename):
        """Returns a new OpusConfig object pre-seeded with defaults, and a
        random secret key generated

        """
        import opus
        opus_dir = opus.__path__[0]
        configfile = os.path.join(opus_dir, "lib", "conf", "default_settings.json")
        config = OpusConfig(configfile)
        config._filename = filename
        config["SECRET_KEY"]  = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])
        return config

    def __getitem__(self, key):
        return self._settings[key]

    def get(self, *args, **kwargs):
        return self._settings.get(*args, **kwargs)

    def __setitem__(self, key, value):
        self._settings[key] = value

    def __delitem__(self, key):
        del self._settings[key]

    def __iter__(self):
        return iter(self._settings)
    iterkeys = __iter__
    def iteritems(self):
        return self._settings.iteritems()
    def __contains__(self, item):
        return item in self._settings
    
    def save(self):
        with open(self._filename, 'w') as f:
            json.dump(self._settings, f, indent=4)
    def saveas(self, filename):
        self._filename = filename
        return self.save()

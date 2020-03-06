# http://docs.cython.org/en/latest/src/tutorial/cython_tutorial.html
# http://www.behnel.de/cython200910/talk.html

# Use tools like cx_Freeze and PyInstaller to create frozen/compiled executables for your programs. The advantage to this is that your users will not have to manually install Python themselves in order to use your applications.
# http://cx-freeze.sourceforge.net/
# http://cx-freeze.readthedocs.io/en/latest/index.html

#http://www.pyinstaller.org/  github.com/pyinstaller/pyinstaller.git
# PyInstaller is a program that freezes (packages) Python programs into stand-alone executables, under Windows, Linux, Mac OS X, FreeBSD, Solaris and AIX. Its main advantages over similar tools are that PyInstaller works with Python 2.7 and 3.3—3.5, it builds smaller executables thanks to transparent compression, it is fully multi-platform, and use the OS support to load the dynamic libraries, thus ensuring full compatibility.

# http://hackerboss.com/how-to-distribute-commercial-python-applications/



# https://www.reddit.com/r/learnpython/comments/32grtr/is_it_possible_to_use_remote_import_in_python/
# https://docs.python.org/3/reference/import.html for example, I've written some code (about 50-100 lines or so) which allows you to import code inside a zip file.
#Conceptually, you could write an import hook which looks like this (note the Finder/Loader API is deprecated, but it continues to work in Python 3.4):

https://github.com/robotframework/PythonRemoteServer
https://pypi.python.org/pypi/robotremoteserver
https://pypi.python.org/pypi/urlimport

import sys
import urllib.request
# Make sure we have a way to build the Module type
Module = type(urllib.request)

class GitHubImporter:
  def find_module(self, path):
    parts = path.split('.')
    # The name must be of the form 'github.<user>.<repository>.<etc>'
    if parts[0] != 'github':
      return None
    if len(parts) < 3:
      raise ImportError('github imports must be of the form github.<user>.<repo>')
    return self

  def load_module(self, path):
    parts = path.split('.')
    user = parts[1]
    repo = parts[2]
    rest = parts[3:]

    # Do magic to load module off GitHub via urllib, checking to ensure that the user
    # and repository actually exist.
    url = get_github_url(user, repo, rest)
    with urllib.request.urlopen(url) as stream:
      code = stream.read()

    comiled_code = compile(code, url, 'exec')
    module = Module(parts)
    eval(compiled_code, locals=module.__dict__)
    return module

sys.meta_path.append(GitHubImporter())

# With the import infrastructure in place:
import github.defunkt.pystache as pystache








# http://blog.dowski.com/2008/07/31/customizing-the-python-import-system/

Customizing the Python Import System
July 31, 2008 at 10:39 PM | categories: Python, Software, work, computing, General

So I've been programming with Python since 2001 and I've never had the need to do anything that the standard import system didn't provide - until this week. We are planning on a little code reorganization for a project at work in preparation for collaboration from more developers. I wrote a simple custom importer/loader that let's a developer write

from application.widgets import foobar

instead of the longer

from application.widgets.foobar.widget import foobar

and the class foobar winds up in globals().

It's not groundbreaking functionality but it actually does add a little clarity in our situation. The whole task it was made quite simple by the features introduced in PEP 302 (that document is a great reference). Now, before anyone suggests that we could have just pulled the classes in via a __init__.py in the application/components directory, note that some components might depend on others which have not been imported and thus their imports would fail.

Anyhow, like I said, it isn't groundbreaking, but the very fact that you can customize Python's import system is neat. I got to thinking about what other ways I could hack the import system, and came up with a little web importer. I'll post the code below, only because I think it is a clever trick, not that it is something to use in development of a Real Application.

"""
Stupid Python Trick - import modules over the web.
Author: Christian Wyglendowski
License: MIT (http://dowski.com/mit.txt)
"""

import httplib
import imp
import sys

def register_domain(name):
    WebImporter.registered_domains.add(name)
    parts = reversed(name.split('.'))
    whole = []
    for part in parts:
        whole.append(part)
        WebImporter.domain_modules.add(".".join(whole))

class WebImporter(object):
    domain_modules = set()
    registered_domains = set()

    def find_module(self, fullname, path=None):
        if fullname in self.domain_modules:
            return self
        if fullname.rsplit('.')[0] not in self.domain_modules:
            return None
        try:
            r = self._do_request(fullname, method="HEAD")
        except ValueError:
            return None
        else:
            r.close()
            if r.status == 200:
                return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = imp.new_module(fullname)
        mod.__loader__ = self
        sys.modules[fullname] = mod
        if fullname not in self.domain_modules:
            url = "http://%s%s" % self._get_host_and_path(fullname)
            mod.__file__ = url
            r = self._do_request(fullname)
            code = r.read()
            assert r.status == 200
            exec code in mod.__dict__
        else:
            mod.__file__ = "[fake module %r]" % fullname
            mod.__path__ = []
        return mod

    def _do_request(self, fullname, method="GET"):
        host, path = self._get_host_and_path(fullname)
        c = httplib.HTTPConnection(host)
        c.request(method, path)
        return c.getresponse()

    def _get_host_and_path(self, fullname):
        tld, domain, rest = fullname.split('.', 2)
        path = "/%s.py" % rest.replace('.', '/')
        return ".".join([domain, tld]), path

sys.meta_path = [WebImporter()]

You can use it like so:

import webimport
webimport.register_domain('dowski.com')
from com.dowski import test

That would fetch and import http://dowski.com/test.py.

There may be other Python libraries out there that do this better - I couldn't find any with a quick Google search. I can think of a number of features would be needed for a serious implementation of something like this (caching, HTTP-AUTH, signatures, remote package support, etc). For now though I'm just throwing this out there because I think it is neat.

Anyone else doing neat tricks with the import hooks that Python exposes?
















# 2004??? code.activestate.com/recipes/305277-import-modules-from-a-remote-server/
# Storing modules in a central location, which are used by remote, seperate clients has obvious benefits. This recipe describes a method by which modules can be fetched from a remote server and compiled into bytecode modules which are used by the client.
# The recipe has 3 sections (server.py, client.py, test.py) which need to be copied into 3 files.
# 
# This solution is ideal for storing configuration modules, which can be downloaded by client applications, when the client application is run. If a module cannot be retrieved, a cached copy from a previous session is used.
# Modules can be replaced at any time, as long as they maintain the previous module interface.
# This recipe uses XMLRPC for transport, however, it could easily use HTTP. This recipe would also benefit (read, needs) from application or transport level authentication and security.

#server.py
from SimpleXMLRPCServer import SimpleXMLRPCServer

def export(module):
    exec('import %s as m' % module)
    filename = m.__file__[:-1] #make pyc = py
    return open(filename).read()

server = SimpleXMLRPCServer(('localhost',1979))
server.register_function(export)
server.serve_forever()

#client.py
from xmlrpclib import ServerProxy
import sha

def remoteImport(module):
    """
    Import a module from a remote server.
    Returns a module object.
    """
    server = ServerProxy('http://localhost:1979')
    filename = sha.new(module).hexdigest() #create a temporary filename
    try:
        code = server.export(module)
    except: #if anything goes wrong, try and read from a (possibly) cached file.
        try:
            code = open('%s.py' % filename).read()
        except IOError: #if we don't have a cached file, raise ImportError
            raise ImportError, 'Module %s is not available.' % module
    #dump the code to file, import it and return the module
    open(filename+'.py','w').write(code)
    exec('import %s as m' % filename)
    return m

if __name__ == "__main__":
    m = remoteImport('test')
    print m.add(1,3)

#test.py
def add(a,b):
    return a + b


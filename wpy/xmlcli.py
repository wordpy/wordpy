#!/usr/bin/python3
import socket, xmlrpc, sys
from datetime import datetime
#from wordpress_xmlrpc import Client  #use class Client: from below for debug
from wordpress_xmlrpc.methods import posts, taxonomies, options
#from wordpress_xmlrpc.methods.posts   import NewPost, EditPost, GetPosts, GetPost, GetPostFormats, GetPostTypes, GetPostType
# from wordpress_xmlrpc.methods.users import GetUserInfo
from wpy.PPrint import pprint as PPrint
import pyx.url  as xUrl
import wp.conf  as WpC
import wpy.time as wTm
import config.log as cLog; L = cLog.logger
cHL, cHO, xHL, xHR = WpC.cHL, WpC.cHO, WpC.xHL, WpC.xHR

#same=# import importlib
#same=# posts = importlib.import_module('wordpress_xmlrpc.methods.posts')

# python-wordpress-xmlrpc.readthedocs.org/en/latest/examples/taxonomies.html

class Cli:  # Xml Client Class
  ''' XmlCli, Exit, XmlMethods: class vars Set in PostC.InitCls
         and TermC.InitCls, ...
  '''
  WpCli = XmlCli = Exit = None
  #XmlMethods = []

Tries  = 5
XmlCliTimeOut = 600  # 10 min since WpPost might take 1 min
SleepSecBetweenXml = 2

# Move all classmethods to module fuctions, as classmethod has no benifit other than grouping them in a class, but we are already grouping all in this module
# After the change, we must change referring cls methods to globals:
# Orig: @classmethod & cls     needed in getattr(Cli, Method)(**kwargs) below
# New:  @classmethod & cls NOT needed in globals()[Method](**kwargs) below
#@staticmethod
def CliCall(Method, **kwargs):
  '''Method is one of the WpC.WB.Bj.XmlMethods Name in str
  return None if error after Tries # of tries
  '''
  Bj = WpC.WB.Bj
  if not isinstance(Method, str):
    raise ValueError(Method+ " Method must be str")
  if not Method in WpC.WB.Bj.XmlMethods:
    raise ValueError(Method+ " Method must be in WpC.WB.Bj.XmlMethods!!"
                     + str(WpC.WB.Bj.XmlMethods))
  if not Bj.XmlCli:
    raise ValueError("Bj.XmlCli in CliCall must not be empty!")
  L.info('\n{} {}', wTm.NowDashYMDHM(), Method)

  WpPost = kwargs.get('WpPost', None)
  WpTerm = kwargs.get('WpTerm', None)
  for obj in (WpPost, WpTerm):
    if obj is not None:
      #PPrint(vars(obj))      #better than PrintPostDetails( obj )
      PPrint({attr:(getattr(obj, attr, '')) for attr in dir(obj)
              if not attr.startswith(('_','definition','struct',))})
      if 'terms' in obj.struct:
        L.info('{}.terms= {}', str(obj), obj.struct['terms'])

  #BId = XmlCli['blog_id']
  #SId = WpC.GetSIdByBId(BId)
  HoursAheadHkTime = 15 + wTm.NonDstPlusOneHour('US/Pacific'
                     ) if WpC.WB.Bj.WH0.DcNum == cHO.DB0001 else 0
  d = datetime.now()
  if d.hour + HoursAheadHkTime in (3, 27) and d.minute in (13,14,15,16):
    L.info("{} Sleep till 3:17 to avoid apache restart @3:15",str(d.time())[:8])
    wTm.Sleep((4-(d.minute - 13))*60, BizHourSleep=False)

  L.info("\nCliCall Method={}, kwargs={}", Method, kwargs)

  for Try in range(Tries):
    try:
      Bj.WpCli = Client(**Bj.XmlCli)
      L.info("\nCliCall: WpCli={}, XmlCli={}", Bj.WpCli, Bj.XmlCli)
      # [Calling a func of a module with function's name in str]
      # (http://stackoverflow.com/questions/3061/)
      #return getattr(Bj, Method)(**kwargs)
      return  globals()[Method](**kwargs)
      #=call: PostC.NewPost(), PostC.EditPost()... , or TermC.NewTerm
    except ConnectionRefusedError:
      L.exception("ConnectionRefusedError")
    except socket.gaierror as msg:
      L.exception("socket.gaierror {}", msg)
    except xmlrpc.client.Fault:  # Move to wp.term.py
      cLog.PrintError(sys.exc_info(), Try)
      e = sys.exc_info()[1]
      if WpPost is not None:
        if CliFaultWpPost(WpPost, e):
          break
      if WpTerm is not None:
        if CliFaultWpTerm(WpTerm, e):
          break
    except:
      cLog.PrintError(sys.exc_info(), Try)
    else:
      break        # everything is fine
    finally:
      wTm.Sleep(SleepSecBetweenXml + Try*5, BizHourSleep=False)
    L.info('  Retry! Try = {}', Try)
    if Try >= (Tries - 1):
      Cli.Exit("\nCannot {} after {} Tries!\n".format(Method, Tries))
      return None

Err1En = 'already exists in this taxonomy'
Err1Cn = '已存在同名项目'
Error2 = 'Ambiguous term name'

def CliFaultWpPost(WpPost, e):
  if hasattr(WpPost, "terms_names"):
    PostKeys = WpPost.terms_names["post_tag"]
    PostCats = WpPost.terms_names["category"]
    L.info("\n\n CliFault WpPost.terms_names= {}", WpPost.terms_names)
    #Wrong!  if hasattr(sys.exc_info()[1], '500'):  # Handle Dup Term.
    if (e.faultCode == 500 and
        (Err1En in e.faultString or Err1Cn in e.faultString)):
      L.warning("\nThis should happen in wp.term TermC!!\n")
      if len(PostKeys) > 0:
         L.info("Try remove from WpPost.terms_names: {}", PostKeys.pop())
         WpPost.terms_names = {"post_tag":PostKeys, "category":PostCats}
      return True
    elif (e.faultCode == 401 and
        'Ambiguous term name' in e.faultString):
      L.warning("\n This should happen in wp.term TermC!!\n")
      if len(PostCats) > 0:
        L.info("Try remove from WpPost.terms_names: {}", PostCats.pop())
        WpPost.terms_names = {"post_tag": PostKeys, "category":PostCats}
      return True
    return False

def CliFaultWpTerm(WpTerm, e):
  " term with provided name already exists in this Taxonomy "
  " Changed from TermC.Dict to Wj.TermD "
  Wj = WpC.WB.Wj

  if (e.faultCode == 500 and
      (Err1En in e.faultString or Err1Cn in e.faultString)):
    from wp.term import TermC, LoadTermsFromDbToDict
    L.info("\n CliFault Cannot add NewTerm: {} {} Error:",
           WpTerm.taxonomy, WpTerm.name, Err1En)
    L.info("Dup term migth be added to db by others since last load, causing "
           "this conflict.\nNow try to add WpTerm to Wj.TermD.\n" )
          #"Now try to re-LoadTermsFromDbToDict.\n" )
    #call back: LoadTermsFromDbToDict() #Reload Terms into Wj.TermD from db
    # Reload Terms into Wj.TermD from db in case of XmlC CliFaultWpTerm
    # Bad!  = Calling Function()
    #XmlC.Cli.WpTermCliFaultCallbk = LoadTermsFromDbToDict()
    # Good! = Passing Function Name.  No ()
    try:
      L.info("Wj.TermD[{}] = {}", WpTerm.taxonomy, Wj.TermD[WpTerm.taxonomy])
    except:
      L.exception("CliFault Cannot print Wj.TermD")
    try:
      L.info("CliFault bool(WpTerm.name in Wj.TermD[{}]) = {}",
             WpTerm.taxonomy, WpTerm.name in Wj.TermD[WpTerm.taxonomy])
    except:
      L.exception("CliFault Cannot print Wj.TermD")

    try:
      #del Wj.TermD[WpTerm.taxonomy][WpTerm.name]
      Wj.TermD[WpTerm.taxonomy][WpTerm.name] = WpTerm.id, WpTerm.slug
      return True
    except:
      L.exception("\n\nCliFault Tried but couldn't add Wj.TermD[{}][{}] !!"
                  " Skip...\n\n", WpTerm.taxonomy, WpTerm.name)
      return False

    L.info("CliFault Cannot return Wj.TermD")
    return True

    ## Cli.WpTermCliFaultCallbk = LoadTermsFromDbToDict
    ## if Cli.WpTermCliFaultCallbk is not None:
    ##   Cli.WpTermCliFaultCallbk()
    #TermC.BDB.Exec("RESET QUERY CACHE") #empty SELECT result if don't RESET
    #LoadTermsFromDbToDict()

  elif e.faultCode == 401 and Error2 in e.faultString:
    L.info("\nCannot add NewTerm: {} {}. Skip \n", WpTerm.taxonomy, WpTerm.name,
            Error2)

## Start PostC XmlMethods, calling wordpress_xmlrpc/methods/posts.py

def NewPost(WpPost=None):
  Bj = WpC.WB.Bj
  if getattr(WpPost, 'id', None) is None:
    L.info('NewPost: WpPost.id is not set or equals None. Now set to zero.')
    WpPost = 0
  elif WpPost.id != 0:
    raise ValueError('In NewPost: WpPost.id must be zero!')
  WpPost.id = int(Bj.WpCli.call(posts.NewPost( WpPost )))
  L.info("\nNew Post ID= {}", WpPost.id )
  # CreatedPost  = Bj.WpCli.call(posts.GetPost (WpPost.id ))
  # PrintPostDetails( CreatedPost )   # Better PPrint( vars(WpPost))
  return WpPost.id

def EditPost(WpPost=None):
  Bj = WpC.WB.Bj
  if WpPost.id <= 1 or not isinstance(WpPost.id, int):
    raise ValueError('EditPost: WpPost.id must be a positive integer!')
  # PrePost = Bj.WpCli.call(posts.GetPost( WpPost.id ))
  # L.info("\nWpPost.id:{}, Before Edit:", WpPost.id)
  # PrintPostDetails( PrePost )   # Better PPrint( vars( WpPost ))
  EditSuccess = Bj.WpCli.call(posts.EditPost(WpPost.id, WpPost))
  L.info("\nWpPost.id= {}, Edit Success= {}", WpPost.id, EditSuccess)
  # EditedPost  = Bj.WpCli.call(posts.GetPost (WpPost.id ))
  # PrintPostDetails( EditedPost )   # Better PPrint( vars(WpPost))
  return EditSuccess

def GetPosts():
  return Bj.WpCli.call( posts.GetPosts(
                         {'post_status': 'publish', 'number': 100}))

def GetPost(post_id=None, optional_args=None):
  return Bj.WpCli.call( posts.GetPost(post_id))

def GetPostFormats():
  return Bj.WpCli.call( posts.GetPostFormats() )

def WpGetPostTypes():
  return Bj.WpCli.call( posts.GetPostTypes() )

def WpGetPostType(posttype=None):
  return Bj.WpCli.call( posts.GetPostType(posttype) )

## End   PostC XmlMethods
## Start TermC XmlMethods, calling wordpress_xmlrpc/methods/taxonomies.py

def NewTerm(WpTerm=None):
  Bj = WpC.WB.Bj
  L.info("\nNew WpTerm= {} {} {}", WpTerm.name, WpTerm.slug , WpTerm)
  L.info("\nNew WpTerm, WpCli={}, XmlCli={}", Bj.WpCli, Cli.XmlCli)
  WpTerm.id = int(Bj.WpCli.call(taxonomies.NewTerm( WpTerm )))
  L.info("\nNew WpTerm.id= {}", WpTerm.id )
  return WpTerm.id

## End   TermC XmlMethods
## Start OptionC XmlMethods, calling wordpress_xmlrpc/methods/taxonomies.py

def GetOptions():
  return Bj.WpCli.call( options.GetOptions([]) )

## End   OptionC XmlMethods

# /usr/local/lib/python3/dist-packages/wordpress_xmlrpc/base.py
#class AuthenticatedMethod(XmlrpcMethod):
#    def default_args(self, client):
#        return (client.blog_id, client.username, client.password)
#class XmlrpcMethod(object):
#    method_name = None      # XML-RPC method name (eg:'Bj.WpCli.getUserInfo')
#    method_args = tuple()   # Tuple of method-specific required parameters
#    optional_args = tuple() # Tuple of method-specific optional parameters
#    results_class = None    # Python class which will convert an XML-RPC
#                            # response dict into an object





# Problem!! xmlcli Client: <ServerProxy for wordpy.com/xmlrpc.php>
#  type : <class 'socket.timeout'> value: timed out

# [xmlrpc.client.ServerProxy needs timeout param](bugs.python.org/issue14134)
# 2015-01-05 to change the underlying connection. What /should/ be done is:

# transport = xmlrpc.client.Transport()
# con = transport.make_connection([host])
# con.timeout = 2
# proxy = ServerProxy([url], transport=transport)

# As the connection will not be created until an RPC method is called, the timeout value assigned to the connection will be observed on socket creation. Making such modifications to the underlying transport should be documented.

# That said, what is a little less than optimal is that the transport attribute of a ServerProxy object is inaccessible (without hackery) after instantiation, so socket level changes are impossible if not using a custom transport. What would be nice would be to add an accessor for ServerProxy.__transport. Likewise, Transport._connection is marked as part of the private interface. Adding public accessors would allow for something like this:
# proxy = ServerProxy([url])
# # pre-connect timeout
# proxy.transport.connection.timeout = 2
# proxy.system.listMethods()
#   or
# proxy = ServerProxy([url])
# proxy.system.listMethods()
# # socket is available as connection has been established
# proxy.transport.connection.sock.settimeout(2)



# below from: /usr/local/lib/python3/dist-packages/wordpress_xmlrpc/base.py
#from xmlrpc import client as xmlrpc_client  # py3.x
# rename xmlrpc_client to xmlrpc.client instead !!
from wordpress_xmlrpc.exceptions import ServerConnectionError, UnsupportedXmlrpcMethodError, InvalidCredentialsError, XmlrpcDisabledError


class Client(object):
  """ Connection to a WordPress XML-RPC API endpoint.
  To execute XML-RPC methods, pass an instance of an
  `XmlrpcMethod`-derived class to `Client`'s `call` method.
  """
  def __init__(self, url, username, password, blog_id=0, transport=None):
    self.url = url
    self.username = username
    self.password = password
    self.blog_id = blog_id

    #L.debug("xmlcli Client args= {} {} {} {} {}", url, username, password,
    #       blog_id, transport)
    #xmlrpc.client.ServerProxy needs timeout param(bugs.python.org/issue14134)
    transport = transport or xmlrpc.client.Transport()
    con = transport.make_connection( xUrl.TldFQDN(url) )
    con.timeout = XmlCliTimeOut

    try:
      self.server = xmlrpc.client.ServerProxy(url, allow_none=True,
                                                transport=transport)
      #L.debug("xmlcli Client server= {}", self.server)
      #import time; time.sleep(2)
      self.supported_methods = self.server.mt.supportedMethods()
      #L.debug("xmlcli Client supported_methods= {}", self.supported_methods)
    except xmlrpc.client.ProtocolError:
      e = sys.exc_info()[1]
      raise ServerConnectionError(repr(e))

  def call(self, method):
    if method.method_name not in self.supported_methods:
      raise UnsupportedXmlrpcMethodError(method.method_name)

    server_method = getattr(self.server, method.method_name)
    args = method.get_args(self)

    try:
      raw_result = server_method(*args)
    except xmlrpc.client.Fault:
      e = sys.exc_info()[1]
      if e.faultCode == 403:
        raise InvalidCredentialsError(e.faultString)
      elif e.faultCode == 405:
        raise XmlrpcDisabledError(e.faultString)
      else:
        raise
    return method.process_result(raw_result)



# Example of Client Usage

def TestXmlServer():
  " simple test program (from the XML-RPC spec) "
  " [XML-RPC client access](docs.python.org/3/library/xmlrpc.client.html) "
  server = xmlrpc.client.ServerProxy("http://localhost:8000") # local server
  with xmlrpc.client.ServerProxy("http://betty.userland.com") as proxy:
    L.debug(proxy)
    try: L.info(proxy.examples.getStateName(41))
    except xmlrpc.client.Error as v:
      L.exception("ERROR {}", v)

class ProxiedTransport(xmlrpc.client.Transport):
  " custom transport to access an XML-RPC server through a HTTP proxy "
  " [XML-RPC client access](docs.python.org/3/library/xmlrpc.client.html) "
  def set_proxy(self, host, port=None, headers=None):
    self.proxy = host, port
    self.proxy_headers = headers

  def make_connection(self, host):
    import http.client
    connection = http.client.HTTPConnection(*self.proxy)
    connection.set_tunnel(host, headers=self.proxy_headers)
    self._connection = host, connection
    return connection

def TestTransPort():
  transport = ProxiedTransport()
  transport.set_proxy('proxy-server', 8080)
  server = xmlrpc.client.ServerProxy('http://betty.userland.com',
                                     transport=transport)
  L.info(server.examples.getStateName(41))


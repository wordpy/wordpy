import config.host_loc as cHL
' cHL contains os or sys var constanst for host_loc = localhost. '
import config.host     as cHO
' cHO contains os or sys var constants for hosts. '
import pyx.host_loc    as xHL
' xHL contains os or sys functions & vars for host_loc = localhost. '
import pyx.host_rem    as xHR
' xHR contains os or sys functions & vars for host_rem = remote host. '

import sys
import pyx.io   as xIO
import config.log    as cLog; L = cLog.logger

ODict = cHO.ODict

# python -i -c "from wpy.host import *; from pprint import pprint;"

# Use a class method without instantiating: stackoverflow.com/questions/9934134/
# * Simple utility functions that generally act on things like collections, or perform some computation or fetch some resource should be module methods
# * Functions related to a class but that do not require either a class or an instance should be static methods
# * Functions that are related to a class, and will need the class for comparison, or to access class variable should be class methods.
# * Functions that will act on an instance should be instance method.
#
# stackoverflow.com/questions/735975/static-methods-in-python
# julien.danjou.info/blog/2013/guide-python-static-class-abstract-methods

# [Python: Use an import done inside of a class in a function](http://stackoverflow.com/questions/6883319/python-use-an-import-done-inside-of-a-class-in-a-function)
class HostCls(xHR.RemoteHostCls):

  def __init__(self, Host, ConnSsh=False, Exit=sys.exit):
    " param ConnSsh = False by Default: No SSH Connection "
    super().__init__()
    self.ConnSsh, self.Exit = ConnSsh, Exit
    #L.info('HCls init Host= {}', Host)
    Tuple = cHO.HostOD[Host]    # = Values in tuple
    self.Host = Host
    self.SshPort = 22  if Tuple[0] is None else Tuple[0]
    #self.FQDN= Host   if Tuple[1] is None else Tuple[1] #FQDN=hostname --fqdn
    self.SshHost= Host if Tuple[1] is None else Tuple[1] #Old: self.FQDN
    self.User = 'ubt' if Tuple[2] is None else Tuple[2]
    self.Type = 'dev'  if Tuple[3] is None else Tuple[3]
    #self.Locat= cHO.DC0000 if Tuple[4] is None else Tuple[4] #Location
    self.DcNum = cHO.DC0000 if Tuple[4] is None else Tuple[4] #Data Center Num
    self.IntIp= '172.0.0.1' if Tuple[5] is None else Tuple[5] #Internal IP Address
    self.IntSshPort = 22    if Tuple[6] is None else Tuple[6] #Internal IP SshC Port
    L.info('HostCls {} {} {}', Host, Tuple, ConnSsh)
    self.SshActiveSetFalse()                          #self.SshActive = False
    L.info('HostCls self.IntIp {}', self.IntIp)
    #self.SameSubnet =     True
    #self.SameSubnet = xHL.RemIpLocIpSameSubnet(self.IntIp)
    self.SameSubnet, self.ConnByVPN, self.ConnReqSshTun = \
        cHO.RemIpLocIp_SameSubnet_ConnByVPN(self.IntIp)
    L.info('HostCls '
           'self.SameSubnet={}, self.ConnByVPN={}, self.ConnReqSshTun={}',
            self.SameSubnet   , self.ConnByVPN   , self.ConnReqSshTun)
    #if (hasattr(self, 'Type')):
    self.FsDir    = '/fs/'    + self.Type +'/'+ self.Host +'/'
    self.FsBkpDir = '/fs/bkp/'+ self.Type +'/'+ self.Host +'/'

    self.TunLocHost = '0.0.0.0'  # listen on all interfaces so others can share
    " Tunnel Local Host (TunLocHost) can't be 'localhost' = '127.0.0.1' "
    self.TunRemHost = '127.0.0.1'  #'localhost'  # Tunnel Remote Host
    self.TunRemPort = 3306         # Tunnel Remote Port

    if ConnSsh:
      self.SshConn()



#class AllH:      # All Hosts
#  #def __init__(self, ConnSsh=False): #Default:No SSH Connection
#  #  self.Hs = ODict((h, HostCls(h, False)) for h in cHO.HostOD)

@xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
def AllHsExec(H, Cmd, StartHost=None, CmdId=None, StdOut=True, StdErr=True):
  ''' Cmd += 'DEBIAN_FRONTEND=noninteractive'
  [ssh Unable to initialize frontend](http://askubuntu.com/questions/506158/)
  '''
  # Exec(Cmd):  if Cmd == 'AllCmds': Run AllCmds
  if Cmd.startswith('sudo apt'):
    Cmd = 'DEBIAN_FRONTEND=noninteractive ' + Cmd
  StartNow = True if StartHost is None else False

  # for h, H in self.Hs.items():  #use @xHR.AllHsDecorator instead
  if StartHost is not None and StartHost == h:
    StartNow = True
  if StartNow:
    H.SshConn()
    if Cmd == 'AllCmds':
      for  Id,Tuple in cHO.AllHostsCmds.items():
        if Tuple[0]:   # if Required
          H.Exec(Tuple[1], CmdId=Id, StdOut=StdOut)
    else:
      H.Exec(Cmd, CmdId=None, StdOut=StdOut)
    H.SshClose('AllHsExec H')


def  AllHostsFqdnIps(ExcludeHostTypes = cHO.AllHostsFqdnIps_ExcludeHostTypes):
  FQDNList  = [ Tuple[1] for Tuple in cHO.HostOD.values()
                     if Tuple[3] not in ExcludeHostTypes ]
  #set =unique dict. FQDNList has dups. xIO.GetIpByFqdn get IP of Host
  return ODict([ (FQDN, xIO.GetIpByFqdn(FQDN)) for FQDN in set(FQDNList) ])

def AllHostsWhiteListFqdnIps():
  " Return ODict([ (Host,IP),..]) "
  import pyx.type as xTp
  return xTp.MergeODicts(AllHostsFqdnIps(), cHO.CustomWhiteListIps)

def AllHostsWhiteListIps():
  " Return tuple of IPs only "
  return tuple([ v for v in AllHostsWhiteListFqdnIps().values()])

def AllHostsGetIpByFqdn(Host):
  return xIO.GetIpByFqdn(cHO.HostOD[Host][1])

# To do: Need to include: /fs/usr/bin/update-server-config


'''
class Loc:      # Local Host running this wpy.host.py
Moved all class vars    from here to config/host_loc.py =cHL as module functions.
Moved all class methods from here to pyx/host_loc.pyx  =xHL as var constants.
cHL contains all os or sys var constanst for host_loc = localhost.
xHL contains all os or sys functions     for host_loc = localhost.
'''



# class Fqdn:
AllFqdns = ODict([
 # Blog: AllFqdns
  ('enw', ('en.wordpy.com',)),
])
" Fqdn of all Domains and SubDomains "

def GetAllRegistrarsDomains():
  " return AllFqdns = cHO.GoDaddyDomains + cHO.Registrar1_Domains "
  AllFqdns.update(cHO.GoDaddyDomains)
  AllFqdns.update(cHO.Registrar1_Domains)
  return AllFqdns

def GetAllGoDaddyDomains():
  AllDomains = []
  for Tuple in cHO.GoDaddyDomains.values():
     for Domain in Tuple:
       AllDomains.append(Domain)
  return AllDomains



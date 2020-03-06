'''
This module (cHO) contains os or sys var constants for hosts in the cloud data center(s).

To use: import config.host as cHO
'''
from   collections import OrderedDict as ODict
from   ipaddress   import IPv4Network, IPv4Address, ip_network, ip_address
import config.log  as cLog; L = cLog.logger

try:
  import pyx.io      as xIO
  LocHostname, LocalIpStr = xIO.GetLocHostname(), xIO.GetLocalIpStr()
except:
  LocHostname, LocalIpStr = 'wpy_host', '127.0.0.1'

LocalIPv4Addr  = IPv4Address(LocalIpStr)

DC0000, DC0001 = 0, 1

DC1000 = 1000   #TODO
DC1010 = 1010   #TODO
PriDcNum, PubDcNum = DC1000, DC0000 # Default Private, Public Data Center Num

DcNum_IPv4Network_D = {
# DcNum: IPv4Network,                 ,
  DC0000: IPv4Network( '10.0.0.0/24'),     #TODO
  DC0001: IPv4Network( '10.0.1.0/24'),     #TODO
  DC1000: IPv4Network('192.168.0.0/24'),   #TODO
  DC1010: IPv4Network('192.168.10.0/24'),  #TODO
}
def Get_IPv4Network_from_DcNum(DcNum):
  return DcNum_IPv4Network_D[DcNum]

DcR0, DcR1, DcR2 = 0, 1, 2

RsPubPriDCs = DataCenterRegions = {
 #RegionNum: ((PubDC1, PubDC2,...), (PriDC1, PriDC2,...)),
  DcR0:((DC0000, ), (DC1000, ),),
  DcR1:((DC0001, ), (),),
 #DcR2:((DC0002, ), (),),
}

RsDCs = {Region: [DC for DCs in PubPriDCs for DC in DCs] for
         Region,                PubPriDCs in RsPubPriDCs.items()}
#={DcR0:[DC0000, DC0168, DC1000, ], ...} # Flatten Tuple

# Main Web Server in Public  Data Centers in Region 0, 1, ... "
GDbHs_WpPub = H000003, H000104a = 'db1' , 'db2'   #TODO
WDbHs_WpPub = H000002, H000104  = 'web1', 'web2'  #TODO
WebHs_WpPub = WDbHs_WpPub


# BestDbHostInCluster = xxxDbHs[0]
GDbHsDC0000 = (H000003 ,) #= DcNum_WpGDb_L_D[   DC0000]  #= ('db1' ,)
GDbHsDC0001 = (H000104a,) #= DcNum_WpGDb_L_D[   DC0001]  #= ('db2',)
#GDbHs_WpPub = GDbHsDC0000 + GDbHsDC0001   #= ('db1','db2',)


WDbHsDC0000 = (H000002,)
WDbHsDC0001 = (H000104,)

DcNum_WpGDb_L_D = {
# DcNum: (db1, db1, ...   ),
  DC0000: GDbHsDC0000,   #: ('db1' ,),
  DC0001: GDbHsDC0001,   #: ('db2',),
}
#DcNum_WpWDb_L_D = {
#  DC0000: WDbHsDC0000,   #: ('web1',),
#  DC0001: WDbHsDC0001,   #: ('web2',),
#}

#GDbH0DC0000, GDbH0DC0001 = GDbHsDC0000[0], GDbHsDC0001[0]  #= 'db1', 'db2'
#WDbH0DC0000, WDbH0DC0001 = WDbHsDC0000[0], WDbHsDC0001[0]  #= 'web1' , 'web2'

H100003,  H100004 = 'ubt03', 'ubt04'    #TODO

DbHsDC1000 = (H100003, H100004,)        #TODO

DbHs_AllPub = GDbHs_WpPub + WDbHs_WpPub
DbHs_AllPri = DbHsDC1000
DbHs_All    = DbHs_AllPub + DbHs_AllPri


CustomWhiteListIps = ODict([ ('GoodHost', '8.8.4.5'), ])
AllHostsFqdnIps_ExcludeHostTypes = ('db','my','nfs','ObjStore',)

DcNum_RedisHostsD = {  #TODO
  DC0000: (H000002,),  #= ('web1',),
  DC0001: (H000104,),  #= ('web2',),
  DC1000: (H100003,),
}


#[SSHTunnel Paramiko CLI works, not in script]
#       (stackoverflow.com/questions/39945269/)
#   Need to sleep(1) for SshTunOpen to be fully established!!
SshTunOpenSleep = 2   # sleep for 2 seconds
SshOpenSleep    = 1   # sleep for 1 seconds

TzHk, TzUsP, TzUsE, TzUsC, TzUtc = 'Asia/Hong_Kong', 'US/Pacific', 'US/Eastern', 'US/Central', 'UTC'

DcTimeZones = {
  TzUsP : (      RsDCs[DcR0]    +       RsDCs[DcR0]   ),
  TzHk  : (      RsDCs[DcR1]    +       RsDCs[DcR1]   ), #Locat=('hk','tk')
 #TzUsE : (      RsDCs[DcR2]    +       RsDCs[DcR2]   ),
  TzUtc : (),
}

def Get_DcNum_from_LocalIPv4Address(FallbackDcNum=PriDcNum):
  for DcNum, network in DcNum_IPv4Network_D.items():
    if LocalIPv4Addr in network:
      L.info(f"Get_DcNum_from_LocalIPv4Address found {LocalIPv4Addr} in "
             f"{network}.  Returning DcNum={DcNum}")
      return DcNum
  return FallbackDcNum

LocDcNum = Get_DcNum_from_LocalIPv4Address()

FLASK_ENV = 'production' if 0 <= LocDcNum < 1000 else 'development'



PriVpnDcNums  = ((DC1000, ),) #= ( (DC1000, DC1011), )
PubVpnDcNums  = ((DC1000, DC0000), (DC1000, DC0001),)
AllVpnDcNums  = PriVpnDcNums + PubVpnDcNums
Vpn_IPv4Networks =  [{ DcNum: Get_IPv4Network_from_DcNum(DcNum)
                       for DcNum in Vpn } for Vpn in AllVpnDcNums ]
#  = [ {DC1000: IPv4Network('192.168.10.0/24'),}, ]

def Connected_by_VPNs(Ip1, Ip2):
  for Vpn in Vpn_IPv4Networks:   # in PriVpn_IPv4Networks:
    Ip1Vpn, Ip2Vpn = False, False

    for Id, Network in Vpn.items():
      if Ip1 in Network:
        Ip1Vpn = True
      if Ip2 in Network:
        Ip2Vpn = True
    if Ip1Vpn and Ip2Vpn:
      return True
  return False

def GetIPv4Network(IpStr, Netmask=24):
  ' [Get subnet from IP address](stackoverflow.com/questions/50867435) '
  return IPv4Network((IpStr, Netmask), strict=False)
# iface = ipaddress.ip_interface('192.178.2.55/255.255.255.0')
# iface                         #Out: IPv4Interface('192.178.2.55/24')
# iface.network                 #Out: IPv4Network(  '192.178.2.0/24')
# iface.netmask                 #Out: IPv4Address(  '255.255.255.0')
# iface.ip                      #Out: IPv4Address(  '192.178.2.55')
# iface.network.network_address #Out: IPv4Address(  '192.178.2.0')

def RemIpLocIp_SameSubnet_ConnByVPN(RemoteIpStr): #Local & Remote Ip Same Subnet
  #LocalIPv4Addr = IPv4Address(LocalIpStr)
  SameSubnet, ConnByVPN, ConnReqSshTun = False, False, False
  try:
    RemoteIpAddr = IPv4Address(RemoteIpStr)
  except:
    return SameSubnet, ConnByVPN, ConnReqSshTun
  #if (LocalIPv4Addr  in Pub_IPv4Networks and
  #    RemoteIpAddr in Pub_IPv4Networks    ):
  #  return True   # Same 10.0.0.8/8 Class A Subnet
  if GetIPv4Network(LocalIpStr) == GetIPv4Network(RemoteIpStr):
    SameSubnet = True
  if Connected_by_VPNs(LocalIPv4Addr, RemoteIpAddr):
    ConnByVPN  = True
  if SameSubnet or ConnByVPN or RemoteIpStr == '127.0.0.1':
    ConnReqSshTun = False
  return SameSubnet, ConnByVPN, ConnReqSshTun


# moved from pyx.host_loc
def Is_IPv4Address_in_IPv4Networks(addr, network):
  return addr in network

# moved from pyx.host_loc
def Is_LocalIPv4Address_in_IPv4Networks(network):
  #return Get_Local_IPv4Address() in network
  return  LocalIPv4Addr in network


ubt, root, gp = 'ubt', 'root', 10022  # = Google Cloud Port
Web1Ip, Db1Ip = '1.1.1.2', '1.1.1.3'
PriIp = '128.101.101.101'

# FQDN = Fully Qualified Domain Name. eg: www.wordpy.com

HostOD = ODict([
 #Host,SshPort,FQDN=hostname --fqdn,User,Type ,DcNum,IntIp,IntSshPort=22 Default
  (H000002, (1022, Web1Ip  ,ubt,'web',DC0000,'10.0.0.2', 22,)), #web1  #TODO
  (H000003, (1022, Db1Ip   ,ubt,'db' ,DC0000,'10.0.0.3', 22,)), #db1   #TODO
  (H000104, (1022, Web1Ip  ,ubt,'web',DC0000,'10.1.0.2', 22,)), #web2  #TODO
  (H000104a,(1022, Db1Ip   ,ubt,'db' ,DC0000,'10.1.0.3', 22,)), #db2   #TODO
  (H100003, (2022, PriIp   ,ubt,'nfs',DC1000,'192.168.0.3', 2022,)),   #TODO
])
' Remote Web or Databse Server (Ubuntu) Hosts in Public Cloud Data Centers'
#('wpy-old',(1022,'www.wordpy.com',  ubt,'web'  DC0000,)),


UidUsrMap = {   33 :'www-data',}
GidGrpMap = {   33 :'www-data',}
UidGidWww = (   33 ,  33   )

def UidGidToUsrGrp(UidGid):
  ''' * param: UidGid tuple e.g. (33,33)
      * return 'www-data:www-data' '''
  return  "{}:{}".format( UidUsrMap[UidGid[0]],  GidGrpMap[UidGid[1]])

UsrGrpWww       = UidGidToUsrGrp(UidGidWww)      # =  'www:www'



def  GetDcNumByHostName(Host):
  if Host in HostOD:
    return HostOD[ Host ][4]
  return DC0000

LocHostDcNum = GetDcNumByHostName( LocHostname )

def GetRegionByHostDcNum(HostDcNum):
  ' return integer DataCenter Region Num, or None if not found '
  for Region, DcNums in RsDCs.items():
      if HostDcNum in DcNums:
        return Region
  return None

def GetRegionByHostName(Host):
  return GetRegionByHostDcNum( GetDcNumByHostName(Host) )


glb, _USR, _CRM = 'global', '_USR', '_CRM'

def GetMainGDbInSameRegionByHostName(Host, DbDSet=glb):
  HostDcNum = GetDcNumByHostName(Host)
  if DbDSet == glb:
    if HostDcNum in DcNum_WpGDb_L_D:
      return DcNum_WpGDb_L_D[ HostDcNum ][0]
    Region = GetRegionByHostDcNum(HostDcNum)
    for DcNum, GDbs in DcNum_WpGDb_L_D.items():
      if Region == GetRegionByHostDcNum(DcNum):
        return GDbs[0]
  #elif DbDSet in ('new_custom'):

  raise ValueError(f"GetMainGDbInSameRegionByHostName {Host}, {DbDSet}")



AllHostsCmds = ODict([
  # Id,  Required, Cmd
  (200, (True ,'hostname; hostname -I; free; df'  )),
  (210, (False,'sudo apt-get install fail2ban'    )),
])
''' install fail2ban: By default IP gets a 5 min ban upon 3 failed attempts
[failed SSH log-in attempts](http://askubuntu.com/questions/178016/)
'''


#class A2:                   # Apache2 config
A2_Dir     = '/etc/apache2/'
A2_Conf    = 'apache2.conf'
A2_DirConf = A2_Dir + A2_Conf
A2_SitesAv = A2_Dir +'sites-available/'
# /fs/web2/etc/apache2/apache2.conf
A2_NonWpDir = '''
<Directory /fs/www/NonWp>
	Options -Indexes +FollowSymLinks
	AllowOverride None
	SecRuleEngine On
	Require all granted
	DirectoryIndex index.htm index.php portal.php
	RewriteEngine On
</Directory>'''



GoDaddyDomains = ODict([
 #(Site1, (DomainA, DomainB, )),
  ('wpy', ('wordpy.com',)),
])

''' GoDaddyDomains = ODict([ (Site1, (DomainA, DomainB, )), ... ])
'''

Registrar1_Domains = ODict([
 #(Site2, (DomainX, DomainY, )),
])
''' Registrar1_Domains = ODict([ (Site2, (DomainX, DomainY, )), ... ])
'''


# class Fqdn:
AllFqdns = ODict([
 # Blog: AllFqdns
  ('enw', ('en.wordpy.com',)),
])
" Fqdn of all Domains and SubDomains "

def GetAllRegistrarsDomains():
  " return AllFqdns = GoDaddyDomains + Registrar1_Domains "
  AllFqdns.update(GoDaddyDomains)
  AllFqdns.update(Registrar1_Domains)
  return AllFqdns



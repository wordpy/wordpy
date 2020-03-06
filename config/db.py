'''
This module (cDB) contains database var constants for wpy.db

To use: import config.db as cDB
'''
from collections import OrderedDict as ODict
import os, sys
import config.host as cHO
glb = cHO.glb  #= 'global'

Tries = 1
UserWpy = 'wpdb_user'
PassWpy = 'wpdb_pass'

MyCnf   = '/home/ubt/.my.cnf'

H100004  = Pri0Db  = cHO.H100004  #='pa32'  = DbHost
DbPort, DbPort1, DbPort2, DbPort3 = 3306, 3306, 3306, 3306
DbChar     = 'utf8mb4'   #= charset

GDB_KwArgs = {'ConnSsh' : False, 'Exit' : sys.exit,} # 'GetSqlCli': False,}
AutoCommit = True
Use_WB_GDB = True
UseSqlAlchemy = False
'''
if UseSqlAlchemy:
  import wpy.db_sa_cls as DbSa
  WB.GlobalDbCls, WB.SiteDbCls = DbSa.SaGlobalDbCls, DbSa.SaSiteDbCls
else:
  import wpy.db      as wDB
  WB.GlobalDbCls, WB.SiteDbCls = wDB.GlobalDbCls,   wDB.SiteDbCls
'''

UDbC = 'udb' # = User Db Cluster
PubDbClusters = GDbC_Wp, WDbC0000, WDbC0001 = 'gdb', 'wdb', 'hdb'
PriDbClusters = Pri0DbC, = 'wdb.pa',


DbCs = DbClusters = {
  #ClusterName: ClusterHosts
  GDbC_Wp     : cHO.GDbHs_WpPub,   #: ('db1','db2',), cHO.GDbHsDC0000=('db1',)
  WDbC0000    : cHO.WDbHsDC0000,   #: ('web1',),
  WDbC0001    : cHO.WDbHsDC0001,   #: ('web2',),
}

#ClusterDefaultNode='1' #Default Galera Node Num:db->db1,wdb->wdb1,hdb->hdb1
def BestDbHostInCluster(ClusterName):
  return DbCs[ClusterName][0]

def GetAllDbHostsInCluster(DbHost):
  for hosts in DbCs.values():
    if DbHost in hosts:
      return hosts
  return (DbHost,)


SIdDbHosts = ODict([
  (1, cHO.GDbHs_WpPub),
  (5, cHO.WDbHsDC0000 ),
  (2, cHO.WDbHsDC0001 ),
])

HostOD = ODict([
  (GDbC_Wp , ()               ),
  (WDbC0000, ()               ),
  (WDbC0001, ()               ),
  (cHO.H000002, (          DbPort, UserWpy, PassWpy,)), # TODO
  (cHO.H000003, (          DbPort, UserWpy, PassWpy,)), # TODO
])

HostOD_DC1000 = ODict([
  (cHO.H100003 , (         DbPort, UserWpy, PassWpy,)),
  (    H100004 , (         DbPort2,UserWpy, PassWpy,)), # H100004= 'ubt04'
])

HostOD.update(HostOD_DC1000)

DbHostPortL_DC1000 = [f"{host}:{HV[0]}" for host,HV in HostOD_DC1000.items()]


# Each site has a unique SPfx in wp-config.php !!
# Blog db settings here override above WpC.SiteOD db settings
#
WpBlogOD = ODict([   # =BDb.
  #      Default DbDSet= SName = Site Name
  # BId, SId, DbHost  ,DbDSet, DbUser ,DbPass   ,
  (   0, ( 1, WDbC0000 ,None , UserWpy,PassWpy,)), # Default BlogDb
  (   1, ( 1, GDbC_Wp  ,glb  , 'root',)),  # wp1
  (2000, (20, WDbC0000 ,'wpy',)),  # wpy = wordpy.com
])


# Each site has a unique SPfx in wp-config.php !!
# Blog db settings here override above WpC.SiteOD db settings
#
PyBlogOD = ODict([   # =BDb.
  #      Default DbDSet= SName = Site Name
  # BId, SId, DbHost,DbDSet   , DbUser   ,DbPass   ,
 #( 100, ( 1, WDbC0000 ,None, UserWpy,PassWpy,)), # Default BlogDb
 #( 101, ( 1, GDbC_Wp  ,None,)),  # wp1
 #(2000, (20, WDbC0000 ,None,)),  # wpy = wordpy.com
])


# OverrideBIdDbHosts: Override DbHost to {BId: NewDbHost,...}
OverrideBIdDbHosts  = {
    200 : H100004,
  }


def GetBlogOD_Tuple(BId):
  return PyBlogOD.get(BId, WpBlogOD.get(BId))

def Is_BId_in_PyBlogOD(BId):
  return BId in PyBlogOD

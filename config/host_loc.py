'''
This module (cHL) contains os or sys var constants for host_loc = localhost.

To use: import config.host_loc as cHL
'''

# Uid =  pwd.getpwnam('www').pw_ui  #bash: id -u www; id -u ubt; id wwwd
# Gid =  pwd.getpwnam('www').pw_gid #bash: id -g www; id -g ubt; id ubt
#class UG:                 # Linux Owner=User, Group Class
#Change from class methods to module function
UidUsrMap = { 1000: 'ubt',}
GidGrpMap = { 1000: 'ubt',}
AdmUidGid = ( 1000, 1000   )

def UidGidToUsrGrp(UidGid):
  ''' * param: UidGid tuple e.g. (1000,1000)
      * return 'AdmUsr:AdmGrp' '''
  return  "{}:{}".format( UidUsrMap[UidGid[0]],  GidGrpMap[UidGid[1]])

UsrGrpLocAdm    = UidGidToUsrGrp(AdmUidGid)   # = 'ubt:ubt'

#AdmUidUsrGidGrp = ( (1000, 'ubt',), (1000,'ubt',), )
#AdmUidGid = AdmUidUsrGidGrp[0][0], AdmUidUsrGidGrp[1][0]
#AdmUsrGrp = AdmUidUsrGidGrp[0][1], AdmUidUsrGidGrp[1][1]


WebDir = '/fs/py/web/'       #Local Web dir
WebHDir= '/fs/py/web/host/'  #Local Web Host dir
WpPDir = '/fs/web/p/'        #Local Wp plugins dir
WpTDir = '/fs/web/t/'        #Local Wp themes dir
WpLDir = '/fs/web/l/'        #Local Wp languages dir
WpLPDir= '/fs/web/l/p/'      #Local Wp languages plugins dir
WpLTDir= '/fs/web/l/t/'      #Local Wp languages themes  dir
WpDDir = '/fs/web/doc/'      #Local Wp doc=upload dir
WpDImg = '/fs/web/doc/img/'  #Local Wp doc img dir (contains Logos)
BkpDir = '/fs/bkp/'



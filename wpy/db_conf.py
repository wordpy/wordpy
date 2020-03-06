import config.host  as cHO
import config.db    as cDB
import wpy.db       as wDB
import wp.conf      as WpC
from pyx.php import array, static_vars
ODict = cDB.ODict
glb = cHO.glb  #= 'global'

WDbWrit, WDbRead, WDbTOut = 1, 1, 0.2
RWsLocal  = (10, 10, 0.2,)
RWsNear   = (30, 30, 0.3,)
RWsRemote = (50, 50, 0.6,)

@static_vars(seq = -1)
def GetRWs(DbHost, DbCliHost): # def GetRWs(DbCliHost, DbHost):
  "self.DbCliLocat = 'pa' or cHO.DC0000; for Web servers = H.WH.DcNum"
  "return RWs = GDbWrit, GDbRead, GDbTOut"
  GetRWs.seq += 1
  if wDB.Is_DbCliHost_DbHost_InSame_DcNum( DbHost, DbCliHost):
    return RWsLocal[0]+ GetRWs.seq, RWsLocal[1] + GetRWs.seq, RWsLocal[2]
  if wDB.Is_DbCliHost_DbHost_InSame_Region(DbHost, DbCliHost):
    return RWsNear[0] + GetRWs.seq, RWsNear[1]  + GetRWs.seq, RWsNear[2]
  return RWsRemote[0] + GetRWs.seq, RWsRemote[1]+ GetRWs.seq, RWsRemote[2]


def WpDbConfigPy(self):
  ''' Dbj = wDB.BlogDbCls or wDB.SiteDbCls or wDB.GlobalDbCls
  #db-config template class
  This func and the following 3 funcs are called from wp.db_config.db_config
  '''
  AddGDbsPy(self)
  if self.BId != 1:
    self.wpdb.add_callback( DbCallbackPy )
    AddWDbsPy(self)


# DcNum = Web server Data Center Number
#@static_vars(seq = -1)
def AddGDbsPy(self, DbCliPyHost=cHO.LocHostname):
  ''' DbCliPyHost here      !=          DbCliPhpHost in WpDbConfigPhpCls
      DbCliPyHost = cHO.LocHostname, DbCliPhpHost = H.WH.Host
  '''
  #AddGDbsPy.seq += 1
  GDB = self.GDB
  #for h in cDB.HostOD[cDB.GDbC_Wp][0]:  # = ('db1','db2',)
  for  h in cHO.GDbHs_WpPub:
    GDbWrit, GDbRead, GDbTOut = GetRWs(h, DbCliPyHost)
    #else: raise ValueError("Web server DcNum unknown!")
    #if h == cHO.H000002:
    self.wpdb.add_database( array(
      ('host'   , h         ), ('name'    , GDB.DbName),
      ('user'   , GDB.DbUser), ('password', GDB.DbPass),
      ('write'  , GDbWrit   ), ('read'    , GDbRead   ),
      ('dataset', GDB.DbDSet), ('timeout' , GDbTOut   ),
    ) )


def AddWDbsPy(self):
  BDB = self.BDB
  Arr = array(                   ('name'    , BDB.DbName),
      ('user'   , BDB.DbUser  ), ('password', BDB.DbPass),
      ('write'  , WDbWrit     ), ('read'    , WDbRead   ),
      ('dataset', BDB.DbDSet  ), ('timeout' , WDbTOut   ),
    )
  #BDB.DbName = BDB.SPfx + BDB.DbDSet     # !=self.H.WDB.DbName= static

  def AddClusterWDbs(hosts):
    for seq, h in enumerate(hosts):
      #self.wpdb.add_database({ 'host' : h, **Arr })
      #Need to copy or Arr is mutable and add_database will del arr['dataset']
      ArrCopy = Arr.copy()
      ArrCopy['host'] = h
      ArrCopy['write'] += seq
      ArrCopy['read']  += seq
      self.wpdb.add_database( ArrCopy )

  if   BDB.DbHost in (cDB.WDbC0000, *cHO.WDbHsDC0000):
    AddClusterWDbs(cHO.WDbHsDC0000)
  elif BDB.DbHost in (cDB.WDbC0001, *cHO.WDbHsDC0001):
    AddClusterWDbs(cHO.WDbHsDC0001)
  elif BDB.DbHost in (cDB.Pri0DbC, *cHO.DbHsDC1000):
    # DbHsDC1000 = ('pa31','pa32','pa32a','pa32b')
    AddClusterWDbs(cDB.DbHostPortL_DC1000)
    # DbHostPortL_DC1000 = ['pa31:3306','pa32:53302','pa32a:3306','pa32b:53302']
  else:
    print("Unknown server DcNum for BDB.DbHost=", BDB.DbHost)
    #self.wpdb.add_database({ 'host' : BDB.DbHost, **Arr })
    ArrCopy = Arr.copy()
    ArrCopy['host'] = BDB.DbHost
    self.wpdb.add_database( ArrCopy )


def DbCallbackPy(query, wpdb):
  ''' in wp.p.ludicrousdb.LudicrousDBCls.run_callbacks
    args = [ args, self ]    # ??? &self = self in py since self is an obj
    for func in self.LDbCallbacks[ group ]:
      result = Php.call_user_func_array( func, args )
  '''
  #print('\n  DbCallbackPy wpdb.table={}, query={}'.format(wpdb.table, query))
  #from pprint import pprint; pprint(wpdb)
  #if ( preg_match("/^wp_(?:bp_|users$|usermeta$)/i", $wpdb->table))
  if wpdb.table is False:
    #print("  wpdb.table is False! DbCallbackPy return BDB.DbDSet=",
    #         wpdb.BDB.DbDSet)
    return wpdb.BDB.DbDSet    #= self.BDB.DbDSet
  if '.' in wpdb.table:
    #print('DbCallbackPy wpdb.table', wpdb.table)
    try: db, table = wpdb.table.split('.')[:2]
    except: raise ValueError('DbCallbackPy wpdb.table', wpdb.table)
    if db == wpdb.GDB.DbName:
       return wDB.GDB_DSET       #= self.GDB.DbDSet
    return wpdb.BDB.DbDSet       #= self.BDB.DbDSet
  if   wpdb.table in wpdb.BDB.Tbs.TbsFed.values():
    return wDB.GDB_DSET       #= self.GDB.DbDSet
  #if (substr(wpdb.table, 0, 6) === 'wp_7_')
  if wpdb.table is False or wpdb.table.startswith(wpdb.BDB.Tbs.TbPfx):
    return wpdb.BDB.DbDSet    #= self.BDB.DbDSet
  print("\n\n Warning!! DbCallbackPy: wpdb.table = {} not in GDB or BDB!!"
        "wpdb.table should startswith = {}\n\n"
        .format(wpdb.table, wpdb.BDB.Tbs.TbPfx))
  return wpdb.BDB.DbDSet    #= self.BDB.DbDSet
  #assert self.BDB.Tbs.TbPfx == self.BDB.SPfx + str(BId) +'_'  #if BId > 1



# Moved from config.db
UserWpy = cDB.UserWpy
PassWpy = cDB.PassWpy
GDbC_Wp, WDbC0000, WDbC0001 = cDB.GDbC_Wp, cDB.WDbC0000, cDB.WDbC0001

# Moved from config.db
DbSiteOD = ODict([
  #    Default DbDSet= SName = Site Name
  #SId,DbHost,DbDSet , DbUser   ,DbPass   ,
  ( 0, (WDbC0000     ,None    , UserWpy,PassWpy,)), #Default SiteDb
])


# Moved from pyx.db
def SiteDbDSetInSId(self, SId=None): #AllDbDSet =SiteDbDSet +BlogDbDSetInSId
  SId = self.SId if SId is None else SId
  SiteDbVal = cDB.DbSiteOD[SId]
  DbHost = SiteDbVal[0]
  try:    DbDSet = SiteDbVal[1]
  except: DbDSet = WpC.GetSNameBySId(SId)  # = SName = Site Name, by default
  #return { DbDSet: {DbHost:[-SId,]}, } # negative Id ==> SId, not BId
  return  ODict([ (DbDSet, ODict([ (DbHost, [-SId,]) ]), ) ])

def BlogDbDSetInSId(self, SId=None, BDbDSet=ODict()):  #Orig: ={}
  SId = self.SId if SId is None else SId
  #L.info('Add to BDbDSet: {} {}', BDbDSet, type(BDbDSet))
  for BId, BV in cDB.WpBlogOD.items():
    if BV[0] == SId:
      try:
        DbHost    = BV[1]
        DbDSet    = BV[2]
        if DbDSet in BDbDSet:
          BDbDSetVal = BDbDSet[DbDSet]
          if DbHost in BDbDSetVal:
            BDbDSetVal[DbHost].append(BId)
          else:
            BDbDSetVal[DbHost] = [BId,]
          #try:
          #  BDbDSet[DbDSet][DbHost].append(BId)
          #except:
          #  BDbDSet[DbDSet][DbHost] = [BId,]
        else:
          #BDbDSet[DbDSet] = {DbHost: [BId,]}
          BDbDSet[DbDSet] = ODict([ (DbHost, [BId,]) ])
      except:
        L.exception('  Error append DSet to BDbDSet for BId= {}', BId)
    #L.debug(BId, BDbDSet)
  return BDbDSet

def AllDbDSetInSId(self, SId=None): # AllDbDSet =SiteDbDSet +BlogDbDSetInSId
  ''' return AllDbDSetInSId(1) =
  {'global': {'db' : [1]},
   'wordpy': {cDB.WDbC0000: [-1, 2, 3, 5, 8]}}   # negative Id ==> SId,not BId
  '''
  SId = self.SId if SId is None else SId
  #return self.BlogDbDSetInSId(      SId, self.SiteDbDSetInSId(      SId))
  return       BlogDbDSetInSId(self, SId,      SiteDbDSetInSId(self, SId))



class WpDbConfigPhpCls:
  ''' db-config template class.  add_database Template
      DbCliPyHost in AddGDbsPy !=        DbCliPhpHost here
      DbCliPyHost = cHO.LocHostname,  DbCliPhpHost = H.WH.Host
  '''
  AddDbTp = '''$wpdb->add_database( array(
  'host'    => {Host:8s}, 'name'     => {Name:8s},
  'user'    => {User:8s}, 'password' => {Pass:8s},
  'write'   => {Writ:8d}, 'read'     => {Read:8d},
  'dataset' => {DSet:8s}, 'timeout'  => {TOut:6.2f},
) );'''

  GDB_USER, GDB_PASS = 'GDB_USER', 'GDB_PASS'
  GDB_NAME, GDB_DSET = 'GDB_NAME', 'GDB_DSET'
  WDB_USER, WDB_PASS, WDB_NAME = 'WDB_USER', 'WDB_PASS', 'WDB_NAME'

  #def __init__(self, DbCliLocat, Dbj):
  def __init__( self, DbCliPhpHost, BDB):
    ''' Dbj = wDB.BlogDbCls or wDB.SiteDbCls or wDB.GlobalDbCls
    Old: Bj = Web.BlogCls   or Web.DeploySiteCls(Web.SiteCls)
    DbCliPhpHost = H.WH.Host
    '''
    self.BDB = BDB
    self.SId = BDB.SId
    self.BId = BDB.BId
    self.DbCliPhpHost   = DbCliPhpHost
    self.GDbPhp = ''       # add_database php code for Global database
    self.WDbPhp = ''       # add_database php code for Web    databases
    self.CBkPhp = '' if self.BId == 1 else (    # add_callback php code
      '\tif ( preg_match("/^wp_(?:bp_|users$|usermeta$)/i", $wpdb->table))'
      '\n\t\treturn GDB_DSET;')
    '''
    TbsSuffix = BDB.Tbs.TbsUsrWp + BDB.Tbs.TbsMSWp
    self.CBkPhp = (    # add_callback php code
      '\tif ( preg_match("/^wp_(?:bp_|{}$)/i", $wpdb->table))'
      '\n\t\treturn GDB_DSET;'.format('$|'.join(TbsSuffix)))
    '''

    self.AddGDbsPhp(self.GDB_NAME, self.GDB_DSET)

    #for DbDSet, Dict in BDB.AllDbDSetInSId(     self.SId).items():
    for  DbDSet, Dict in     AllDbDSetInSId(BDB, self.SId).items():
      if DbDSet is None:
        continue
      for WDbHost, BIds in Dict.items():
        if DbDSet==glb and WDbHost==cDB.GDbC_Wp:
          continue
        self.CallBackPhp(DbDSet, WDbHost, BIds)
        self.AddWDbsPhp(DbDSet, WDbHost)

    self.CBkPhp += '\n\telse\n\t\treturn {};'.format(
                   'GDB_DSET' if self.SId == 1 else 'WDB_DSET')

  # function startsWith($haystack, $needle)
  #   return (substr($haystack, 0, strlen($needle)) === $needle);
  # $wpdb->add_callback( function ($query, $wpdb) {
  #   self.CBkPhp
  # } );
  def CallBackPhp(self, DbDSet, WDbHost, BIds):
    for BId in BIds:
      if BId <= 1:     # skip SiteDbDSet if BId=-SId for SiteDbDSetInSId
        continue       # as it's defaulted to: else return WDB_DSET;
      TbPfx = self.BDB.Tbs.TbPfx                 # if BId=1: TbPfx = wp_
      try: assert TbPfx == self.BDB.SPfx + str(BId) +'_'
      except: AssertionError("wpy.db_conf.CallBackPhp", BIds, BId, TbPfx, self.BDB.SPfx)
      self.CBkPhp += ( "\n\t{}if (substr($wpdb->table, 0, {}) === '{}')"
        "\n\t\treturn '{}';" ).format('' if self.CBkPhp =='' else 'else',
                                      len(TbPfx), TbPfx, DbDSet)
      '''  Cmt = ''
      if DbDSet == self.BDB.DbDSet: #Comment Out if  DbDSet == BDB.DbDSet
        Cmt = '#'      # as it's defaulted to: else return WDB_DSET;
      self.CBkPhp += (
        "\n{C}\telseif (substr($wpdb->table, 0, {L}) === '{P}')"
        "\n{C}\t\treturn '{D}';").format(C=Cmt, L=len(TbPfx),P=TbPfx,D=DbDSet)
      '''

  # DcNum = Web server Data Center Number
  def AddGDbsPhp(self, DbName, DbDSet):
    #for h in cDB.HostOD[cDB.GDbC_Wp][0]:  # = ('db1','db2',)
    for  h in cHO.GDbHs_WpPub:
      GDbWrit, GDbRead, GDbTOut = GetRWs(h, self.DbCliPhpHost)
      #else: raise ValueError("Web server DcNum unknown!")
      self.GDbPhp += self.AddDbTp.format(Host=repr(h), User=self.GDB_USER,
                     Pass=self.GDB_PASS, Name=DbName, Writ=GDbWrit,
                     Read=GDbRead, DSet=DbDSet, TOut=GDbTOut) +'\n'

  def AddWDbsPhp(self, DbDSet, WDbHost):
    QuotedName = "'"+ self.BDB.SPfx + DbDSet +"'" # !=self.BDB.DbName=static
    QuotedDSet = "'"+ DbDSet +"'"                # since DbDSet loops= dynamic
    Dict = {                    'Name' : QuotedName,
        'User' : self.WDB_USER, 'Pass' : self.WDB_PASS,
        'Writ' : WDbWrit      , 'Read' : WDbRead,
        'DSet' : QuotedDSet   , 'TOut' : WDbTOut       }
    if   self.BDB.DbHost in (cDB.WDbC0000,)+ cHO.WDbHsDC0000:
      for h in cHO.WDbHsDC0000:
        self.WDbPhp += self.AddDbTp.format(Host=repr(h), **Dict) +'\n'
    elif self.BDB.DbHost in (cDB.WDbC0001,)+ cHO.WDbHsDC0001:
      for h in cHO.WDbHsDC0001:
        self.WDbPhp += self.AddDbTp.format(Host=repr(h), **Dict) +'\n'
    elif WDbHost in (cDB.GDbC_Wp,)+ cDB.DC0000_GDbHs:
      self.AddGDbsPhp(QuotedName, QuotedDSet)
    else:
      self.WDbPhp += self.AddDbTp.format(Host=repr(WDbHost), User=self.WDB_USER,
               Pass=self.WDB_PASS, Name=QuotedName, Writ=WDbWrit,
               Read=WDbRead, DSet=QuotedDSet, TOut=WDbTOut) +'\n'
    self.WDbPhp += '\n'


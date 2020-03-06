import sys, os, pymysql
import config.db as cDB
import pyx.db    as xDB
import pyx.type  as xTp
import wpy.host  as wHo
import wp.conf   as WpC
import config.log as cLog; L = cLog.logger

cHL, cHO = wHo.cHL, wHo.cHO
glb = cHO.glb  #= 'global'
ODict = cDB.ODict

#python -i -c "from wpy.db import *; SDb = SiteDbCls(1);"
#
# #Bad!# from wpy.web import SiteCls  # Cross import bad
#[Circular (or cyclic) imports in Python](http://stackoverflow.com/questions/744373/)
#If you do import foo inside bar and import bar inside foo, it will work fine. By the time anything actually runs, both modules will be fully loaded and will have references to each other.
#The problem is when instead you do from foo import abc and from bar import xyz. Because now each module requires the other module to already be imported (so that the name we are importing exists) before it can be imported.

#https://mariadb.com/kb/en/mariadb/mariadb-error-codes/#shared-mariadbmysql-error-codes
# dev.mysql.com/doc/refman/5.7/en/gone-away.html
# dev.mysql.com/doc/refman/5.7/en/error-messages-client.html


UserWpy = cDB.UserWpy
PassWpy = cDB.PassWpy
#mysql -u 'wp_dbuser' -P 61207 -p'' -h 0.0.0.0   #Via SshTun
#mysql -u 'wp_dbuser' -P 61207 -p'' -h 127.0.0.1 #Via SshTun #Bad: -h localhost

Tries = 3


class DbCls(xDB.xDbCls):
  '''DbC ='Site'  : ==> web.SiteCls.Hs based on Db.SiteDbCls   by default
         ='Blog'  : ==> web.SiteCls.Hs based on Db.BlogDbCls   by default
         ='Global': ==> web.SiteCls.Hs based on Db.GlobalDbCls by default
  Remove DbC for below:
    self.DbHost in cDB.DbCs[cDB.GDbC_Wp]               ==> DbC=='Global'
    hasattr(self, 'Sj') or isinstance(Sj, Web.SiteCls) ==> DbC=='Site'
    hasattr(self, 'Bj') or isinstance(Bj, Web.BlogCls) ==> DbC=='Blog'

  AutoCommit by default is set in DbCls.__init__(AutoCommit=True) or False,
    but ConnectDb() or Exec() can override it by passing True or False.
  '''

  def __init__(self, DbHost, ConnSsh=False, AutoCommit=True, Exit=sys.exit,
               IniConf=True, SshTunClose_AfterExec = False):
    self.AutoCommit = AutoCommit
    self.Exit   = Exit    # Exit can be print, sys.exit, or ShutdownExit
    #self.SshTunActive = False  # moved into DbH
    self.SshTunClose_AfterExec = SshTunClose_AfterExec
    self.UseDb  = True
    if not hasattr(self, 'IsGDB'):
      self.IsGDB  = False

    # Whether db queries are ready to start executing.
    self.DbReady = False          # similar to wpdb.ready
    self.conn    = None           # Old: self.DbConnected = False
    " if self.conn is None, db is not connected. similar to wpdb.has_connected "

    #if DbC is not None:
    #if getattr(self, 'SId', None) and getattr(self, 'SId', None):
    if IniConf:
      self.InitConf(DbHost, ConnSsh)


  def InitBId(self, BId, Bj):
    if Bj is None:
      if BId is None:
        raise ValueError("Both Bj and BId are None!")
      else:
        if BId is not None and BId not in WpC.BlogOD:
          raise ValueError("Bad BId ={} !".format(BId))
        self.BId  = BId
        #Need to comment out to prevent recursive define Bj->BlogDb->Bj
        #self.Bj = Web.BlogCls(BId)
    else:
      import wpy.web as Web
      if not isinstance(Bj, Web.BlogCls):
        raise ValueError("Bad Bj={} !".format(Bj))
      self.Bj = Bj
      self.BId  = Bj.BId

      if BId is not None and BId != Bj.BId:
        raise ValueError("BId != Bj.BId! ")


  def InitSId(self, SId, Sj):
    if Sj is None:
      if SId is None:
        raise ValueError("Both Sj and SId are None!")
      else:
        if SId is not None and SId not in WpC.SiteOD:
          raise ValueError("Bad SId ={} !".format(SId))
        self.SId  = SId
        #Need to comment out to prevent recursive define Sj->BlogDb->Sj
        #self.Sj = Web.SiteCls(SId)
    else:
      import wpy.web as Web
      if not isinstance(Sj, Web.SiteCls):
        raise ValueError("Bad Sj={} !".format(Sj))
      self.Sj = Sj
      self.SId  = Sj.SId
      if SId is not None and SId != Sj.SId:
        raise ValueError("SId != Sj.SId! ")


  def InitConf(self, DbHost, ConnSsh=True):
    ''' set self.DbHost
    '''
    WV          = WpC.SiteOD[self.SId or 1]
    self.SName   = WV[0]
    self.SPfx   = WV[3] if len(WV) > 3 else WpC.WPfx #Site Prefix
    #L.debug("InitConf self.SName={}; self.SPfx={}", self.SName, self.SPfx)

    # OverrideBIdDbHosts: Override DbHost to {BId: NewDbHost,...}
    if getattr(self, 'BId', None) in cDB.OverrideBIdDbHosts:
      self.DbHost  = cDB.OverrideBIdDbHosts[ self.BId ]
      L.info("self.BId={} in cDB.OverrideBIdDbHosts; set self.DbHost to: {}",
             self.BId , self.DbHost)
    elif self.IsGDB: # Set TbG for GDB, so py run from USA will be faster to db1
      #self.DbHost = cHO.H000003 if Is_DbCliHost_DbHost_In_Region0( DbHost
      #                           ) else cHO.H000104a
      self.DbHost  = cHO.GetMainGDbInSameRegionByHostName( DbHost )
    else:
      if DbHost is None:
        #if DbC == 'Blog' and self.BId in cDB.WpBlogOD:
        if hasattr(self, 'Bj'):
          self.BId    = self.Bj.BId
        #if getattr(self, 'BId', None) in cDB.WpBlogOD:
        #  self.DbHost = cDB.WpBlogOD[self.BId][1]  #= gdb, wdb, or hdb
        #else: #if not hasattr(self, 'BId'): # Get Blog Id BId of Main Sj SId
        #  #if BId not in WpC.BlogOD: BId=SId*100
        #  self.BId= WpC.SiteBlogId(self.SId)
        #  self.DbHost = cDB.DbSiteOD[self.SId][0]  #= gdb, wdb, or hdb
        #self.DbHost = cDB.WpBlogOD[self.BId][1]  #= self.BId must be ok by now
        self.DbHost  = cDB.GetBlogOD_Tuple(self.BId)[1]
        L.info("SaCls self.BId ={}; self.DbHost={}", self.BId , self.DbHost)
      else:
        if getattr(self, 'BId', None) not in cDB.WpBlogOD or \
           getattr(self, 'BId', None) not in cDB.SaBlogOD:
          self.BId= WpC.SiteBlogId(self.SId)
        self.DbHost = DbHost   # Dup set self.DbHost to make sure
        L.info("DbHost not None! self.DbHost DbHost={}", self.DbHost)

      #if self.DbHost in (cDB.GDbC_Wp, cDB.WDbC0000, cDB.WDbC0001):
      if  self.DbHost in cDB.PubDbClusters:
        self.DbHost = cDB.BestDbHostInCluster(self.DbHost)

    #if self.DbHost in cHO.DbHs_AllPub:
    #  #self.ClusterType  = 'galera'
    #  #ClusterName= self.DbHost.rstrip('1234567890') #Strip last digit from str
    #  #self.ClusterHosts=cDB.HostOD[ClusterName][0] # (db1,db2,..) or (wdb1,..)
    #  for Name, Hosts in cDB.DbCs.items():   # cDB.DbCs = cDB.DbClusters:
    #    if self.DbHost in Hosts:
    #      self.ClusterHosts = Hosts
    #      #self.ClusterName = Name
    #      break

    if self.DbHost not in cHO.DbHs_All:
      raise Exception('Error: self.DbHost={} not in cHO.DbHs_All!'
                      .format(self.DbHost))

    HV = cDB.HostOD[self.DbHost]              #= Values in tuple
    #self.DbPort = HV[1] if len(HV)>1 and HV[1] is not None else cDB.DbPort
    #self.DbUser = HV[2] if len(HV)>2 and HV[2] is not None else UserWpy
    #self.DbPass = HV[3] if len(HV)>3 and HV[3] is not None else PassWpy
    self.DbPort  = HV[0] if len(HV)>0 and HV[0] is not None else cDB.DbPort
    self.DbUser  = HV[1] if len(HV)>1 and HV[1] is not None else UserWpy
    self.DbPass  = HV[2] if len(HV)>2 and HV[2] is not None else PassWpy

    self.DbH = wHo.HostCls(self.DbHost, ConnSsh)
    L.debug("InitConf self.DbUser={}; self.DbPass={}", self.DbUser, self.DbPass)

    if self.IsGDB:    # self.IsGDB(): #Set TbG for GDB
      self.Tbs = TbC(SPfx = self.SPfx)
      self.TbG = xTp.BaseCls(Warn=False, **self.Tbs.TbsGlobal)  #Global Tables
      self.DbDSet = glb              #ALWAYS#=Global Db DataSet =glb
      self.DbName = WpC.WPfx+ self.DbDSet #ALWAYS#=Global DbName ='wp_global'
      # BAD to set GDB_NAME: self.DbName = self.SPfx +glb = sh1p_global
      self.DbUser = UserWpy
      self.DbPass = PassWpy
    else:   # DbC in ('Site', 'Blog',):
      SV = cDB.GetBlogOD_Tuple(self.BId)
      self.DbDSet = SV[2] if len(SV)>2 and SV[2] is not None else self.SName
      if len(SV)>3 and SV[3] is not None:    #else inherit from DbCls
        self.DbUser = SV[3]
        L.debug("InitConf not IsGDB len(SV)>2 self.DbUser={}", self.DbUser)
      if len(SV)>4 and SV[4] is not None:    #else inherit from DbCls
        self.DbPass = SV[4]

      if self.SId <= -900:   #  SId = -999 = Discuz bbs
        self.DbName = self.DbDSet
      else:
        self.DbName = self.SPfx + self.DbDSet
        self.Tbs = TbC(SPfx = self.SPfx,
                       SId  = self.SId, BId = getattr(self, 'BId', None))
        if getattr(self, 'BId', 0) > 0:
          self.TbB = xTp.BaseCls(Warn=False, **self.Tbs.TbsBlog)  #Blog Tables
        self.TbM = xTp.BaseCls(Warn=False, **self.Tbs.TbsMS) #Multisite Tables
        #if DbC == 'Blog' and self.BId in cDB.WpBlogOD:
        if hasattr(self, 'Bj') or hasattr(self, 'BId'):
          if   hasattr(self, 'Bj'):
            self.BId = self.Bj.BId
          #BV = cDB.WpBlogOD[getattr(self, 'BId', 1)]  #= tuple
          BV  = cDB.GetBlogOD_Tuple(self.BId)
          if len(BV)>2 and BV[2] is not None:  #else inherit from SiteDbCls
            self.DbDSet = BV[2]                #DataSet
            self.DbName = self.SPfx + self.DbDSet
          if len(BV)>3 and BV[3] is not None:  #else inherit from SiteDbCls
            self.DbUser = BV[3]
            L.debug("InitConf not IsGDB len(BV)>3 self.DbUser={}", self.DbUser)
          if len(BV)>4 and BV[4] is not None:  #else inherit from SiteDbCls
            self.DbPass = BV[4]

    L.info("DbCls.InitConf IsGDB={}, self.DbUser={}", self.IsGDB , self.DbUser)

    # DbHostDotName =wdb3.wp_wpy for Blog or Site, =db3.wp_global for Global
    self.DbHostDotName = self.DbHost +'.'+ self.DbName
    #L.debug('DbHostDotName= {}, DbHost= {}', self.DbHostDotName, self.DbHost)
    self.ConfigDbConn()

  def ConfigDbConn(self, DbCur = xDB.OrderedDictCursor):
    '''  DbCur  = xDB.OrderedDictCursor (custom), or
                = SqlCur.DictCursor = pymysql.cursors.DictCursor '''
    self.DbPort = getattr(self, 'DbPort', cDB.DbPort)
    self.DbChar = cDB.DbChar
    self.DbCur  = DbCur       #= cursorclass

    self.DbConn = {                # pymysql/connections.py
      'host'       : self.DbHost if self.DbH.ConnReqSshTun else self.DbH.IntIp,
      'database'   : self.DbName,  #= self.SPfx + self.DbDSet
      'port'       : self.DbPort,
      'charset'    : self.DbChar,
      'cursorclass': self.DbCur ,
    }
    # Error if [use wp_wpy] before wp_wpy is created!
    if not self.UseDb:             #do not: use database;
      del self.DbConn['database']  #default DbConn['database']=self.DbName
    #def UseDbOn(self):
    #  if hasattr(self, 'DbConn') and hasattr(self, 'DbName'):
    #    self.DbConn['database'] = self.DbName   #= self.SPfx + self.DbDSet
    #  self.UseDb = True
    #def UseDbOff(self):
    #  if hasattr(self, 'DbConn') and 'database' in self.DbConn:
    #    del self.DbConn['database']    # do not:use db;
    #  self.UseDb = False

    # Xref with sa.sa_cls read_default_file:
    if os.path.isfile(cDB.MyCnf):
      # pymysql/connections.py: read_default_file    = '/etc/my.cnf'
      self.DbConn['read_default_file'] = cDB.MyCnf # = '/home/ubt/.my.cnf'
      #if 'user'     in self.DbConn: del self.DbConn['user']
      #if 'password' in self.DbConn: del self.DbConn['password']
      #L.debug('DbConnViaSshTun isfile(cDB.MyCnf) = {}', cDB.MyCnf)
      # Add to MyCnf: #http://dba.stackexchange.com/questions/2820/
      #   [clientm1]      #[clientm1] above default [client]
      #   user=root
      #   password='....'
      #   [client]        #[clientm1] above default [client]
      '''
      if self.DbHost == 'm1': # pymysql/connections.py: read_default_group
        #L.debug('DbHost=m1. try to read_default_group from MyCnf={}',cDB.MyCnf)
        self.DbConn['read_default_group'] = 'clientm1'
      '''
    else: # use current
      self.DbConn['user']     = self.DbUser  #= db username
      self.DbConn['password'] = self.DbPass
    #[configparser](https://docs.python.org/3.5/library/configparser.html)
    # import configparser
    # SqlIniFileParser = configparser.RawConfigParser()
    # SqlIniFileParser.read(cDB.MyCnf)
    # self.DbConn['user']     = SqlIniFileParser.get('client', 'user')
    # self.DbConn['password'] = SqlIniFileParser.get('client', 'password')


  def SelectDb(self, DbName, Tries=3):
    "Php.mysql_select_db(DbName, dbh): "
    "  Returns TRUE on success or FALSE on failure"
    if self.IsValidDbConn(DbName):
      for Try in range(Tries):
        try:
          self.conn.select_db(DbName)
          return True
        except:
          L.exception("db.SelectDb Failed to conn.select_db({})", repr(DbName))
    return False

  def ConnCommit(self, DbName=''):
    if self.IsValidDbConn(DbName):
      try:
        self.conn.commit()
        return True
      except:
        L.exception("db.ConnCommit Failed to conn.commit() {}", DbName)
        return False
    return False



  def ShowDbs(self):
    return self.Exec('SHOW DATABASES', Tries=2)
    #L.debug(self.Exec('SHOW DATABASES', None, 'fetchall'))

  def ShowTbs(self, DbName=None):     # SHOW TABLES IN DbName
    return self.Exec('SHOW TABLES'+('' if DbName is None else ' IN '+ DbName),
                     Tries=2)

  def DropTb(self, Table):
    try:   self.Exec("DROP TABLE "+ Table, Tries=2) #Don't quote TbName repr()
    except: L.exception("\nCan't DROP TABLE = {}", Table)

  def Desc(self, TbName):
    "DESCRIBE [TbName] is shortcut for SHOW COLUMNS"
    return self.Exec('DESC '+ TbName, Tries=2)
  def ShowTbCols(self, TbName, Like=None):
    Sql = "SHOW COLUMNS FROM "+ TbName
    return self.Exec(Sql) if Like is None else self.Exec(
                     Sql + " LIKE '%s'", ( '%' + Like + '%' ), Tries=2)

  def SelectTbCols(self, TbName, Like=None):
    Sql =("SELECT COLUMN_NAME FROM information_schema.columns WHERE "
          " TABLE_SCHEMA='{}' AND TABLE_NAME='{}'".format(self.DbName,TbName))
    return self.Exec(Sql) if Like is None else self.Exec( Sql +
                    " AND COLUMN_NAME LIKE '%s'", ('%' + Like + '%'), Tries=2)

#End DbCls


try:
  import wpy.db_plugin as DbP
except:
  DbP = None

# TbsUsr = Users Tables.  table names = SPfx + TbsUsrWp
TbsUsrPy = ('User',  'UserMeta',)     #.Tbs.TbG.User  = 'wp_users'
TbsUsrWp = ('users', 'usermeta',) #.Tbs.TbG.UserMeta = 'wp_usermeta'

# TbsMS = MultiSite Tables.  table names = SPfx + TbsMSWp
TbsMSPy = ('BlogV'        , 'Blog' , 'RegLog'          , 'SignUp' ,
           'Site', 'SiteMeta'   ,)
TbsMSWp = ('blog_versions', 'blogs', 'registration_log', 'signups',
           'site', 'sitemeta',)    # 'sitecategories'

# TbsBlog = Blog Tables.  table names = TbPfx + TbsBlogWp #TbPfx, NOT SPfx
TbsBlogPy = ('CommentMeta', 'Comment', 'Link'    , 'Option', 'PostMeta', 'Post',
             'TermRel'    , 'TermTax', 'TermMeta', 'Term',)
TbsBlogWp = (     #TbsBlogPy: Db  = table name
  'commentmeta',       #'CommentMeta' : {P} = wp_4_commentmeta
  'comments',          #'Comment'  : {P} = wp_4_comments
  'links',             #'Link'   : {P} = wp_4_links
  'options',           #'Option' : {P} = wp_4_options   = .Tbs.TbB.Options
  'postmeta',          #'PostMeta'  : {PM}= wp_4_postmeta
  'posts',             #'Post'   : {P} = wp_4_posts
  'term_relationships',#'TermRel': {TR}= wp_4_term_relationships
  'term_taxonomy',     #'TermTax': {TT}= wp_4_term_taxonomy
  'termmeta',          #'TermMeta'  : {T} = wp_4_termmeta
  'terms',             #'Term'   : {T} = wp_4_terms
)                # TbPfx, NOT SPfx

#class TbC(xDB.xTbC):
class  TbC:
  'Datbase Table Class for SDB, BDB or GDB'
  #Database Unique Keys in SPfx_user table
  UsrKeys  = ('ID', 'user_login', 'user_nicename', 'user_email')
  TbsUsrPy    , TbsUsrWp, TbsMSPy, TbsMSWp, TbsBlogPy, TbsBlogWp = \
      TbsUsrPy, TbsUsrWp, TbsMSPy, TbsMSWp, TbsBlogPy, TbsBlogWp

  if DbP is not None:
    #DbP.InitPluginTbsCls(TbC)  # Can't pass TbC itself before it's initialized
    TbsBpPy = DbP.TbsBpPy
    TbsBpWp = DbP.TbsBpWp

  def __init__(self, SPfx=WpC.WPfx, SId=1, BId=None):
    if SId <= -900: # bypass if SId = -999 = Discuz bbs
      return
    self.TbPfx = TbPfx = self.SPfx = SPfx
    #import sa.wp_cls as SWp
    #SWp.TbPfx     = SWp.SPfx = SPfx
    if SId < -900:  # exclude -999 = bbs
      return
    self.SPfx, self.SId = SPfx, SId

    #self.TbsUsr = { 'User'  : SPfx +'users', 'UserMeta' : SPfx +'usermeta', }
    #self.TbsUsr = { i: SPfx + j for i,j in zip(TbsUsrPy, TbsUsrWp) }
    self.TbsUsr  = ODict([ (i, SPfx + j)
                           for i,j in zip(TbsUsrPy, TbsUsrWp) ])

    #super().__init__()
    if DbP is not None:
      DbP.InitPluginTbsObj(self)
    if not hasattr(self, 'TbsGlobal'):
      self.TbsGlobal = self.TbsUsr.copy()  # {**Obj.TbsUsr,} #dict.copy()
    self.TbsGDB = self.TbsGlobal

    if BId is not None and BId > 1:             #BId=1: db table prefix wp_
      self.TbPfx =TbPfx = TbPfx + str(BId) +'_' #BId>1: db table prefix wp_4_
      #import sa.wp_cls as SWp
      #SWp.TbPfx = self.TbPfx
    #self.TbsMS = {i: SPfx +j for i,j in zip(TbsMSPy  , TbsMSWp  )}
    self.TbsMS  = ODict([ (i, SPfx + j)
                           for i,j in zip(TbsMSPy  , TbsMSWp  ) ])
    #self.TbsBlog={i: TbPfx+j for i,j in zip(TbsBlogPy, TbsBlogWp)}
    self.TbsBlog= ODict([ (i, TbPfx+j)
                           for i,j in zip(TbsBlogPy, TbsBlogWp) ])
    self.TbsBDB = xTp.MergeODicts(self.TbsBlog, self.TbsMS)

  def IsTbInGDB(self, PyName):
    return PyName in self.TbsGDB
  def IsTbInBDB(self, PyName):
    return PyName in self.TbsBDB


class GlobalDbCls(DbCls):       #DbHost is differen from DbHost
  " self.DbHost in cDB.DbCs[cDB.GDbC_Wp] ==> DbC='Global', except SId/BId=1 "
  #def __init__(self, DbHost=cHO.H000003, ConnSsh=False, AutoCommit=True,
  #                   Exit=sys.exit):
  def __init__(self, DbHost=cHO.H000003, **kwargs):
    self.SId = self.BId = None
    self.IsGDB = True
    #DbCls.__init__(self, DbHost, ConnSsh, AutoCommit, Exit)
    DbCls.__init__( self, DbHost, **kwargs)



class SiteDbCls(DbCls, xDB.xSiteDbCls):
  " isinstance(Sj, Web.SiteCls)  ==>  DbC='Site' "
  #def __init__(self, SId, Sj=None, DbHost=None, ConnSsh=False, AutoCommit=True,
  #                   Exit=sys.exit):
  def __init__(self, SId, Sj=None, DbHost=None, **kwargs):
    self.InitSId(SId, Sj)
    #DbCls.__init__(self, DbHost, ConnSsh, AutoCommit, Exit)
    DbCls.__init__( self, DbHost, **kwargs)



#[No need now]: Need to change BId from position arg to kw arg since BlogDbCls & SiteDbCls are passed into HostSiteConfCls, and HostSiteConfCls would have no idea if 1st position arg is BId or SId !!
#[No need now]: Py3 params after “*” or “*identifier” are keyword-only params and may only be passed used keyword args.  stackoverflow.com/questions/2965271
# def __init__(self, *, BId=BId, DbHost=None, ConnSsh=False,
class BlogDbCls(SiteDbCls):
  " isinstance(Bj, Web.BlogCls)  ==>  DbC='Blog' "
  #def __init__(self, BId=None, Bj=None, DbHost=None, ConnSsh=False,
  #             AutoCommit=True, Exit=sys.exit):
  def __init__(self, BId=None, Bj=None, **kwargs):
    # set self.BId BEFORE SiteDbCls.init as it needs it!!
    #L.debug("BlogDbCls 0 {}", BId)
    self.InitBId(BId, Bj)
    self.SId  = WpC.GetSIdByBId(self.BId)   # = WpC.BlogOD[BId][0]
    #L.debug("BlogDbCls 1 {} {}", self.SId, self.BId)
    #DbCls in SiteDbCls may: self.DbHost=cDB.BestClusterHost(self.DbHost) #above
    # Following update self.DbHost
    #SiteDbCls.__init__(self, self.SId, getattr(self, 'Sj', None), DbHost,
    #                         ConnSsh, AutoCommit, Exit)
    SiteDbCls.__init__( self, self.SId, getattr(self, 'Sj', None), **kwargs)



GDB_DSET  = glb


#def DbCliHostLoc(DbCliHost=cHO.LocHostname):
#  return cHO.GetDcNumByHostName(DbCliHost)
#def DbHostLoc(DbHost):
#  return cHO.GetDcNumByHostName(DbHost   )

def Is_DbCliHost_DbHost_InSame_DcNum( DbHost, DbCliHost=cHO.LocHostname):
  " return if same DcNum "
  return ( cHO.GetDcNumByHostName( DbCliHost) ==
           cHO.GetDcNumByHostName( DbHost   )   )
def Is_DbCliHost_DbHost_InSame_Region(DbHost, DbCliHost=cHO.LocHostname):
  return ( cHO.GetRegionByHostName(DbCliHost) ==
           cHO.GetRegionByHostName(DbHost   )   )

def IsTableInGDB(Tb, Pfx=WpC.WPfx):
  'Check if table in Global Database GDB'
  return Tb.startswith(Pfx) and Tb[len(Pfx):] in (TbsUsrWp +
                                                  getattr(DbP, 'TbsBpWp', ()))

def IsTableInSDB(Tb, Pfx=WpC.WPfx):
  'Check if table in Global Database SDB'
  return Tb.startswith(Pfx) and Tb[len(Pfx):] in (TbsMSWp+ TbsBlogWp)

def IsTableInBDB(Tb, Pfx=WpC.WPfx):
  'Check if table in Global Database BDB'
  return Tb.startswith(Pfx) and Tb[len(Pfx):] in TbsBlogWp

def GetDB(Obj, table):
  # if meta_type.startswith('user'): #other non-GDB data can startswith user
  # set to GDB if table - prefix in ('users', 'usermeta')
  if IsTableInGDB(table):
    return Obj.GDB
  if IsTableInBDB(table) and hasattr(Obj, 'BDB'):
    return Obj.BDB
  return Obj.SDB


def GetMainGDbInSameRegionAsSDB(SDB, GDB):
  NewGDB_DbHost = cHO.GetMainGDbInSameRegionByHostName(SDB.DbHost)
  if NewGDB_DbHost == GDB.DbHost:
    return GDB
  L.info("NewGDB_DbHost={} != GDB.DbHost={}. GDB might be set to closest to "
         "DbCliHost, so need to reset to close to SDB: GDB = GlobalDbCls({})",
         NewGDB_DbHost, GDB.DbHost, NewGDB_DbHost)
  return GlobalDbCls(NewGDB_DbHost)


# SELECT * FROM wp_users u LEFT JOIN wp_usermeta um ON (u.ID = um.user_id) WHERE u.ID=1006;
# SELECT umeta_id, user_id, meta_key, LEFT(meta_value,20) FROM wp_usermeta um WHERE um.user_id=1006;
# SELECT * FROM wp_usermeta WHERE user_id=1006 AND meta_key = 'nickname'; #umeta_id= 223414;
# UPDATE wp_usermeta SET meta_value='WordPy AI' WHERE user_id=1006 AND meta_key = 'nickname'; #and umeta_id= 223414;
# |   223414 |    1006 | nickname | WordPy AI |


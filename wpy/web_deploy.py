import pyx.host_loc as xHL
import wpy.ctx_mgr  as Ctx
import pyx.db       as xDB
import wpy.exe      as Exe
import wpy.host     as HO

import config.host_loc as cHL
import config.host     as cHO
import pyx.host_loc    as xHL
import pyx.host_rem    as xHR
import config.log as cLog; L = cLog.logger
ODict = cHO.ODict

import wpy.time     as wTm
import wpy.web      as Web
import wp.conf      as WpC

'''
ipython -i --c="import wpy.web_deploy as WD
DBlog = WD.DeployBlogCls(1)"

python -i -c "import wpy.web_deploy as WD;"
DSite = WD.DeploySiteCls(1, cHO.H100003)
DSite.DownloadWp(); DSite.SetupWDoc(); DSite.InstallAllThemes(); DSite.InstallAllPlugins()
DSite.WrapUpWDeploy(); DSite.DomainMapping()


ubt@web1:/fs/www$ ln -sfn /fs/web/t/Avada-Child-Theme/header-wpy.php  wpy/wp-content/themes/Avada-Child-Theme/header.php
'''

H000002, H000104 = cHO.H000002, cHO.H000104

Ctx.LogFilePfx = 'web_deploy/' #  + 'SiteName.' = self.SName
WrToLogFile = True

LocWhTEMwDir = cHL.WebHDir +'TEM/www/'   #=/fs/py/web/host/+TEM/www/

def GetTemplateFiles(self, H):
  TemLocRemDirTuple = LocWhTEMwDir, H.WC.LocSiteDir, H.WC.SDir
  return  ODict([   #  TemplateDir , LocDir= Local, RemDir=Remote
    ('fb-2008'      , (*TemLocRemDirTuple, {
    },)),
    ('db-config.php', (*TemLocRemDirTuple, {
      'GDB_USER' : self.GDB.DbUser,
      'GDB_PASS' : self.GDB.DbPass,
      'GDB_DSET' : self.GDB.DbDSet, #='global',
      'GDB_NAME' : self.GDB.DbName, #='wp_global', ALWAYS!!  Below BAD!
      #BAD to set GDB_NAME: H.GDB.DbName = self.SPfx +'global' = sh1p_global
      'WDB_USER' : self.SDB.DbUser,
      'WDB_PASS' : self.SDB.DbPass,
      'WDB_DSET' : self.SDB.DbDSet,
      'WDB_NAME' : self.SDB.DbName,  # = self.SPfx + self.SDB.DbDSet,
     #'AddCBk'   : self.DbConf.CBkPhp,
     #'AddGDb'   : self.DbConf.GDbPhp,
     #'AddWDb'   : self.DbConf.WDbPhp,
    },)),
    ('index-redis.php', (*TemLocRemDirTuple, {
      'DocRoot'    : H.WC.SDir,  #= /fs/web/wpy
      'NoCacheIps' : "', '".join(HO.AllHostsWhiteListIps()),
      'RedisServer': self.RedisServerIp,
    },)),
    ('robots.txt'     , (*TemLocRemDirTuple, {
      'Disallow' : 'Disallow: /wordpy/doc/\nDisallow: /wordpy/gData/' \
                   if self.SId == 1 else '',
    },)),
    ('wp-config.php'  , (*TemLocRemDirTuple, {
      'WDB_HOST' : self.SDB.DbHost,
      'WDB_NAME' : self.SDB.DbName,
      'WDB_USER' : self.SDB.DbUser,
      'WDB_PASS' : self.SDB.DbPass,
      'WDbChar'  : self.SDB.DbChar,
      'WpConfigSalts': WpC.ConfigGenSalts(),
      'SPfx'     : self.SPfx,
      'RedisServer': self.RedisServerIp,
      'WhiteListIps' : "', '".join(HO.AllHostsWhiteListIps()),
      'SId'      : self.SId,
      'BId'      : self.BId,
      'SUrl'     : self.SUrl,
      'MSiteOff' : '' if self.MultiSiteOn else '#MSiteOff#',
      # Error if enable SUNRISE before InstallMultiSite!! Enable afterwards
      #'SUNRISE' : ''          if 'merc' in H.WC.Plugins else '#',
      'SUNRISE'  : '#SUNRISE#' if 'merc' in H.WC.Plugins else '#',
      #Comment out define('SUNRISE','on') for domain mapping. Activate later!
    },)),

      #            /fs/py/web/host/+TEM+/etc/apache2
    (cHO.A2_Conf       , (cHL.WebHDir +'TEM'+ cHO.A2_Dir,
                    H.WC.LocDir.rstrip('/') + cHO.A2_Dir,       cHO.A2_Dir, {
      'A2Dir'   : cHO.A2_Dir,           #=/fs/py/web/host/web1/+ cHO.A2_Dir
      'ServerName' : WpC.Servers(self.SId)[0][2],
      # = [(1,'wpy','wordpy.com'), ...][0][2]
      'WhiteListFqdnIps' : HO.AllHostsWhiteListFqdnIps(),
      'WhiteListIps'     : ' '.join(HO.AllHostsWhiteListIps()),
      'WwwD'     : H.WC.WwwD,
      'WpDirectory' : '|'.join(WpC.AllSitesInWDir(Path=H.WC.WwwD,
                               ListDir=H.WH.Sftp.listdir)),
      'Word Python: '' if H.WH.Host == H000002 else '#', #self.Host0 => H.WH.Host
      'NonWpDir'  : '' if H.WH.Host != H000104 else cHO.A2_NonWpDir,
    },)),
      #            /fs/py/web/host/+TEM+/etc/apache2/sites-available/
    ('www.conf'       , (cHL.WebHDir +'TEM'+ cHO.A2_SitesAv,
                    H.WC.LocDir.rstrip('/') + cHO.A2_SitesAv, cHO.A2_SitesAv, {
      'FQDN'     : self.SFQDN,  #= wordpy.com
      'ServerAlias': ' '.join([d +' *.'+d for d in
                         WpC.BlogFQDNsInSId(self.SId)]),  #, self.Fqdns
                         #same as#  WpC.AllFQDNsInSId(self.SId)]),
      'DocRoot'  : H.WC.SDir,  #= /fs/web/wpy
      'Site'     : self.SName,   #= wpy
    },)),
  ])


def GetSaConfC(DB):
  import config.sa_conf as cSC

  class ConfC(cSC.BaseConfC):
    DB_CHAR    = 'utf8mb4'
    DB_COLLATE = DB_CHAR + '_unicode_ci'
    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    DB_DIALECT = 'mysql'
    DB_DRIVER  = 'pymysql'
    QUERY_DICT = {'charset' : DB_CHAR,}
    DEBUG    = True
    SQL_ECHO = True
    SQL_POOL_SIZE      = SQLALCHEMY_POOL_SIZE 	 = 10
    DB_HOST, DB_PORT, DB_NAME = DB.DbHost, DB.DbPort, DB.DbName
    DB_USER, DB_PASS  = DB.DbUser, DB.DbPass

  return ConfC


''' Instead of decorating each & every class methods with:
  @Ctx.RedirectOutputDctr(RedirectOn=WrToLogFile)
  def CreateDb_GrantUser(self):
use @DecorateAllClassMethods to apply same decorator to every class method
'''
@Ctx.DecorateAllClassMethods( Ctx.RedirectOutputDctr(NewFilePerEntry=True),
                              UseDecorator=WrToLogFile)
class DeployBlogCls(Web.BlogCls):
  'ipython -i --c="import wpy.web_deploy as WD; DBlog = WD.DeployBlogCls(1)"'
  DeployBlog    = True       # Set to False in DeploySiteCls

  def __init__(self, BId, SId=None, Hosts=None, ConnSsh=False):
    Web.BlogCls.__init__(self, BId, SId, Hosts, ConnSsh=ConnSsh, WebConf=True)
    Ctx.LogFilePfx = 'web_deploy/{}.'.format(self.SName)
    self.MultiSiteOn = True  # Tell if wp MultiSite is installed in db yet
    #WpC.WB.InitBlog(BId, ConnSsh=ConnSsh)


  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def SetupBDoc(self, H):       #Include: ChownWww
    H.WH.MkDir(H.WC.WDSBId)     #/fs/web/doc/sites/1/
    # ln -s /fs/web/doc/img/    /fs/web/doc/sites/1/img/
    H.WH.SftpSymLink(H.WC.WDImg, H.WC.WDSBIdImg)
    #ln -s /fs/web/doc/avatars/ /fs/web/doc/sites/1/avatars
    H.WH.SftpSymLink(H.WC.WDAvt, H.WC.WDSBIdAvt)
    #ln -s /fs/web/doc/group-avatars/ /fs/web/doc/sites/1/group-avatars
    H.WH.SftpSymLink(H.WC.WDGrAvt, H.WC.WDSBIdGrA)
    H.WH.MkDir(H.WC.WDSBIdBpA)        #/fs/web/doc/sites/1/bp-attachments/
    # Cannot link or replicate bp-attachments to /fs/web/doc,
    #   since bp-attachments uses wp_BId_posts: ID=post_id
    #   post_id is unique to the Blog. Different Blog will have same post_id.

  #################################################################
  # create the initial blog or global database:
  #    ipython -i -c "import wpy.web_deploy as WD"
  #    > DBlog = WD.DeployBlogCls(1, ConnSsh=False)
  #################################################################

  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use BDB in 1st Hs to Exec
  #@Ctx.RedirectOutputDctr(RedirectOn=WrToLogFile)
  def CreateDb_GrantUser(self):
    #self.MultiSiteOn = False   # If db isn't installed yet, MultiSiteOn=F
    self.BDB.CreateDb_GrantUser(self.BDB.DbName)

  #################################################################
  # There are 4 ways to create the initial blog or global database tables:
  # 1) Do it in WordPress
  # 2) self.CreateBlog()  # uses: self.WH0.Exec("wp wpy-site create --path=...")
  # 3) self.BDB.Exec(<SQL from wp-admin/includes/schema.php>)
  # 4) self.CreateBlogSa() below using SqlAlchemy
  #    ipython -i -c "import wpy.web_deploy as WD"
  #    > DBlog = WD.DeployBlogCls(1, ConnSsh=False)
  #    > DBlog.CreateBlogSa()   # or:  WpModels, Db = DBlog.CreateBlogSa()
  #################################################################

  def CreateBlogSa(self, ClsSuffix=''):
    import pyx.wp_cls     as SWp
    import pyx.sa_cls     as Sa
    from   config.sa_conf   import Config
    from sqlalchemy.ext.declarative import declarative_base
    WpModels = SWp.DynamicWpModels(self.BId, self.BDB.DbName,
                                ClsSuffix=ClsSuffix, DyBase=declarative_base())
    ConfC = GetSaConfC(self.BDB)
    import config.sa_conf as cSC
    config = cSC.Config(ConfC)
    Db    = Sa.SqlAlchemyCls(config=config)
    BlogTb = WpModels.MsBDB['Blog']
    Db.CreateEngine()
    BlogTb.metadata.create_all(Db.Engine)    
    return WpModels, Db
    #for PyName, WpModel in WpModels.MsBDB.items():
    #  pass

  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use WH0 and WC0 in 1st Hs to Exec
  def CreateBlog(self):
    #wp-cli.org/config/#global-parameters : use Command Line args: --arg=xyz
    #  instead of using options in wp-cli.yml. Can't require 2 php in 1 yml!?!
    Cmd=("wp wpy-site create --path={} --url={} --slug={}"
         " --title='{}' --email='{}' --network_id={} --blog_id={}"
        #" --private  " #If set, the new site will be non-public (not indexed)
        #" --porcelain" #If set, only the site id will be output on success
         " --require={} --color=true --debug=true").format(
         self.WC0.SDir, self.SFQDN, self.BName, self.WC0.BTitle,self.SU.UEmail,
         self.SId, self.BId, self.WC0.WebD +'wp-cli/wpy-site.php')
    # /fs/web, /fs/web/wpy, wordpy.com, /, Word Python, wordpy_info,
    # Password, info@wordpy.com, 2, 200
    self.WH0.Exec(Cmd, Tries=1)
    #self.WH0.Exec(Exe.RestartPhp)

  def DeleteBlog(self):
    ''' Be careful!! don't know why but might rm -rf web/doc/img !!
    wp --path=/fs/www/wpy --url=wordpy.com site delete 12 '''
    self.WH0.Exec("wp --path={} --url={} -yes site delete {}"
                  .format(self.WC0.SDir, self.SFQDN, self.BId), Tries=1)


  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use self.Hs[self.Host0]
  def BlogActivatePlugin(self, Slug='bp'):
    " Param: Slug (str) can be Plugin (Abbr name) or PSlug "
    for Plugin, V in self.WC0.Plugins.items():
      PluginsV= WpC.PluginOD[Plugin]
      PSlug   = PluginsV[3]  #= PluginSlug
      if Plugin == Slug or PSlug == Slug:
        self.BlogsActivatePlugin((self.BId, ), PSlug)

  def BlogActivateTheme(self, Slug=None):
    " Param: Slug (str) can be TSlug "
    if Slug is not None:
      return self.BlogsActivateTheme( (self.BId,), Slug)
    for Theme, V in self.WC0.Themes.items():
      ThemesV = WpC.ThemeOD[Theme]
      TSlug   = ThemesV[3]  #= ThemeSlug
      Activate= V[1] #Activate: True=>Network, tuple(BId,..)=>BId,..
      if (Activate is True or ( isinstance(Activate, (list,tuple)) and
          (Activate ==(0,) or self.BId in Activate) )): #Activate=tuple(BId,..)
        self.BlogsActivateTheme( (self.BId,), TSlug)

  def UpdateBlogDesc(self):
    import wp.i.option as WpO
    #WpO.OptionC.InitCls(self)
    WpO.update_option('blogdescription', self.WC0.BDesc)
    # copy options from 'wp_user_roles' to 'wp_6000_user_roles'
    BDB, GDB = self.BDB, self.GDB   # BDB = WpO.OptionC.BDB
    Sql= ("INSERT INTO {}.{} (`option_name`,`option_value`,`autoload`) "
          "SELECT {},`option_value`,`autoload` FROM {} WHERE `option_name`= %s"
          .format(BDB.DbName,BDB.TbB.Option, repr(BDB.Tbs.TbPfx +'user_roles'),
                  BDB.TbB.Option) )             # BDB.Tbs.TbPfx = 'wp_6000_'
    L.info(BDB.Exec(Sql, (BDB.SPfx +'user_roles',), 'insert', Tries=1))
    #BDB.SPfx='wp_'
    Sql= ("INSERT INTO {}.{} (`umeta_id`,`user_id`,`meta_key`,`meta_value`) "
          "VALUES (NULL, %s, %s, %s)").format(GDB.DbName, GDB.TbG.UserMeta)
    L.info(GDB.Exec(Sql, (1001, BDB.Tbs.TbPfx +'_capabilities',
           'a:2:{s:13:"administrator";b:1;s:13:"bbp_keymaster";b:1;}'),
           'insert', Tries=1))


  def AddBpCoverPageOptions(self, Enabled="1",
      ProfilePic= "2015/12/skiing-banner-1070x360.jpg",
      GroupPic  = "2015/12/beach_shade.jpg"              ):
    import wp.i.option as WpO
    #WpO.OptionC.InitCls(self)
    WpO.update_option('bpcp-enabled'        , Enabled                      )
    WpO.update_option('bpcp-profile-default', self.BUrl +'doc/'+ ProfilePic)
    WpO.update_option('bpcp-group-default'  , self.BUrl +'doc/'+ GroupPic  )
  '''To disable the cover image completely,
  #  disables profile cover image and disables group cover image, respectively:
  add_filter( 'bp_is_profile_cover_image_active', '__return_false' );
  add_filter( 'bp_is_groups_cover_image_active', '__return_false' );
  #can also disable it from BuddyPress->Settings without using above code.
  '''

  def AddBlogBpPages(self):
    self.AddBpPages()



''' Instead of decorating each & every class methods with:
  @Ctx.RedirectOutputDctr(RedirectOn=WrToLogFile)
  def CreateDb_GrantUser(self):
use @DecorateAllClassMethods to apply same decorator to every class method
'''
@Ctx.DecorateAllClassMethods( Ctx.RedirectOutputDctr(NewFilePerEntry=True),
                              UseDecorator=WrToLogFile )
class DeploySiteCls(Web.SiteCls):
  'ipython -i --c="import wpy.web_deploy as WD; DS = WD.DeploySiteCls(85)"'
  DeployBlog    = False      # Set to True in DeployBlogCls
  SiteYearStart = 2010
  SiteYearEnd   = 2031  #range(2010,2031) => 2010, 2011,..., 2029, End on 2030

  def __init__(self, SId, Hosts=None, ConnSsh=True):
    Web.SiteCls.__init__(self, SId, Hosts, ConnSsh=ConnSsh, WebConf=True)
    Ctx.LogFilePfx = 'web_deploy/{}.'.format(self.SName)
    self.MultiSiteOn = True  # Tell if wp MultiSite is installed in db yet
    self.NewInstall  = False

  @xHR.AllHostsDecorator
  def PrintHosts(self, Host):
    L.info('Host= {}',Host)

  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def PrintHs(self, H):
    L.info('{} Hs= {}\n {} {}', H.Host, H, H.WH, H.WC)

  # self.SshOpenAll(self)
  # self.SshCloseAll(self)

  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use SDB in 1st Hs to Exec
  def CreateSiteDb(self):
    self.MultiSiteOn = False   # If db isn't installed yet, MultiSiteOn=F
    self.NewInstall  = True
    self.SDB.CreateDb_GrantUser(self.SDB.DbName)

  def CreateAllBlogDbsInSId(self):
    " Skip this if only creating SiteDb "
    self.MultiSiteOn = False   # If db isn't installed yet, MultiSiteOn=F
    self.SDB.CreateAllBlogDbsInSId()

  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def DownloadWp(self, H):
    #if self.SName not in ('wpy',):  # 'wpy','wdp',):
    #  return
    for Id,V in Exe.SvrCmds(0, self, H).items():
      if V[0]:   # if Required
        H.WH.Exec(V[1], CmdId=Id)

    SDir, SCDir = H.WC.SDir, H.WC.SCDir  # = /wp-content/
    #SymLink wp core doesn't work!
    #svn checkout or upgrade latest wp ver  #ChownWww=False so can still write
    H.WH.Svn(SDir, Url=WpC.LatestUrl(), Op='co',Depth='immediates',StdOut=False)
    self.UpdateWpSvn(H, SwitchToLatestWpUrl=False, Refresh=True, ChownWww=False)

    #H.WH.Exec('rm -f '+ SDir +'readme.html '+ SDir +'wp-config-sample.php')
    H.WH.SftpSymLink(H.WC.LogDebug, SCDir +'debug.log')

  # WrapUpWDeploy SvrCmds: sudo chown -R cHO.UsrGrpWww ChownDirs (has H.WC.SDir)

  #Goal: svn co only ./plugins/index.php & hello.php and ./themes/index.php
  #  Exclude: plugins/akismet. So p,t can be symlinked to /fs/web/p,t & update
  #  Exclude: twentyten,eleven,twelve,thirteen,fourteen,fifteen.
  #core.trac.wordpress.org/ticket/34306: themes/twentysixteen not in SVN, so
  # so it needs to be svn co separately
  #
  #1) Best Solution:  svnbook.red-bean.com/en/1.6/svn.advanced.sparsedirs.html
  #svn --depth immediates co  https://core.svn.wordpress.org/tags/4.5.3 wp.svn
  #svn info wp.svn | grep "^Depth:"
  #  Depth: immediates
  #svn update --set-depth infinity wp.svn/wp-admin wp.svn/wp-includes
  #svn update --set-depth exclude  wp.svn/license.txt wp.svn/readme.html wp.svn/wp-config-sample.php
  #svn update --set-depth immediates wp.svn/wp-content/
  #svn update --set-depth files wp.svn/wp-content/plugins/ wp.svn/wp-content/themes/
  #
  #2) Bad Solution: Needs to download everything first!
  #svn co  https://core.svn.wordpress.org/tags/4.5.3 wp.svn
  #svn up --set-depth exclude wp.svn/wp-content/themes/
  #  D    wp.svn/wp-content/themes
  #svn info wp.svn/wp-content/themes | grep "^Depth:"
  #  Depth: exclude


  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def SetupWDoc(self, H):       #Include: ChownWww
    H.WH.MkDir(H.WC.SDDir)      #/fs/www/wpy/doc/
    H.WH.MkDir(H.WC.WDSBId)     #/fs/web/doc/sites/1/

    H.WH.MkDir(H.WC.WDImg)      #/fs/web/doc/img/,     include mkdir doc
    # ln -s /fs/web/doc/img/    /fs/www/wpy/doc/img/
    H.WH.SftpSymLink(H.WC.WDImg, H.WC.SDImg)
    # ln -s /fs/web/doc/img/    /fs/web/doc/sites/1/img/
    H.WH.SftpSymLink(H.WC.WDImg, H.WC.WDSBIdImg)

    H.WH.MkDir(H.WC.WDAvt)
    H.WH.MkDir(H.WC.WDGrAvt)

    #ln -s /fs/web/doc/avatars/ /fs/www/wpy/doc/avatars
    H.WH.SftpSymLink(H.WC.WDAvt, H.WC.SDAvt)
    #ln -s /fs/web/doc/avatars/ /fs/web/doc/sites/1/avatars
    H.WH.SftpSymLink(H.WC.WDAvt, H.WC.WDSBIdAvt)

    #ln -s /fs/web/doc/group-avatars/ /fs/www/wpy/doc/group-avatars
    H.WH.SftpSymLink(H.WC.WDGrAvt, H.WC.SDGrAvt)
    #ln -s /fs/web/doc/group-avatars/ /fs/web/doc/sites/1/group-avatars
    H.WH.SftpSymLink(H.WC.WDGrAvt, H.WC.WDSBIdGrA)


    H.WH.MkDir(H.WC.WDBp)
    # ln -s /fs/web/doc/buddypress/ /fs/www/wpy/doc/buddypress/
    H.WH.SftpSymLink(H.WC.WDBp, H.WC.SDBp)

    H.WH.MkDir(H.WC.WDSite)
    # ln -s /fs/web/doc/sites/ /fs/www/wpy/doc/sites/
    H.WH.SftpSymLink(H.WC.WDSite, H.WC.SDSite)

    H.WH.MkDir(H.WC.WDSBIdBpA)
    #ln -s /fs/web/doc/sites/1/bp-attachments/ /fs/www/wpy/doc/bp-attachments
    H.WH.SftpSymLink(H.WC.WDSBIdBpA, H.WC.SDBpAtt)

    # Cannot link or replicate bp-attachments to /fs/web/doc,
    #   since bp-attachments uses wp_BId_posts: ID=post_id
    #   post_id is unique to the Blog. Different Blog will have same post_id.
    for Y in range(DeploySiteCls.SiteYearStart, DeploySiteCls.SiteYearEnd):
      #      From:  2010 to 2029
      YDir = str(Y) +'/'
      WDSBId_YDir = H.WC.WDSBId + YDir  #/fs/web/doc/sites/1/2016/
      SDDir_YDir  = H.WC.SDDir  + YDir  #/fs/www/wpy/doc/2016/
      H.WH.MkDir(WDSBId_YDir)
      H.WH.SftpSymLink(WDSBId_YDir, SDDir_YDir)


  # DeployFiles: str or (tuple, list)
  # if DeployFiles not None, skip files that are not listed in DeployFiles
  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def DeployApacheWpConf(self, H, DeployFiles=None):
    import re, string, os
    #from wpy.db_conf import WpDbConfigPhpCls
    ##self.DbConf= WpDbConfigPhpCls(H.WH.DcNum, self.SDB)
    #self.DbConf = WpDbConfigPhpCls(H.WH.Host , self.SDB)
    self.MultiSiteOn = False   # Since MultiSite isn't installed yet

    # [py string module – Text Template](https://pymotw.com/2/string/)
    # create new template using {{var}} as the variable syntax
    class WpyTemplate(string.Template):
      delimiter = '{['   # flask.py use {{ }}
      pattern = r'''
      \{\[(?:
      (?P<escaped>\{\[)|
      (?P<named>[_a-z][_a-z0-9]*)\]\}|
      (?P<braced>[_a-z][_a-z0-9]*)\]\}|
      (?P<invalid>)
      )
      '''

    if H.WH.Host in (H000002, H000104):  #self.Host0 => H.WH.Host
      self.RedisServerIp = '127.0.0.1'
    elif H.WH.DcNum == cHO.DB0001:
      self.RedisServerIp = cHO.HostOD[H000104][5]
    else:
      self.RedisServerIp = cHO.HostOD[H000002][5]

    #os.makedirs(H.WC.LocSiteDir, mode=0o775, exist_ok=True)
    xHL.MkDir(H.WC.LocSiteDir)
    H.WH.MkDir(H.WC.SDir) #repeat DownloadWp():Exe.SvrCmds:mkdir
    TemplateFiles = GetTemplateFiles(self, H)

    for FName,V in TemplateFiles.items():
      if (DeployFiles is not None and (  # DeployFiles: str or (tuple, list)
          isinstance(DeployFiles,(list,tuple)) and FName not in DeployFiles
          or isinstance(DeployFiles, str) and FName != DeployFiles )):
        continue   # skip files that are not listed in DeployFiles

      TemplateDir = V[0]
      LocDir  = V[1]  # Local  dir
      RemDir  = V[2]  # Remote dir
      SubVals = V[3]
      FbDir   = 'fb-2008'
      if FName == FbDir:          #FbDir: No trailing slash to copy entire dir
        H.WH.Rsync(LocWhTEMwDir + FbDir, H.WC.WWwDir)
        H.WH.SftpSymLink(H.WC.WWwDir +FbDir , H.WC.SDir +FbDir)
        continue

      # good practice to use the with keyword when dealing with file objects.
      # This has the advantage that the file is properly closed after its
      # suite finishes, even if an exception is raised on the way.
      with open(TemplateDir + FName, 'r') as FIn:
        FInData = FIn.read()
      # FIn.close() #No need to close since FIn.closed()= True
      if FName == 'www.conf':
        FName = self.SName +'.conf'
      LocalFile = LocDir + FName   #Local copy of RemoteFile
      L.info('\n  DeployApacheWpConf to LocalFile: {}', LocalFile)
      t = WpyTemplate(FInData)
      FOutData = t.substitute(SubVals)
      xHL.BkpFile(LocalFile)
      with open(LocalFile, 'w') as FOut:
        FOut.write(FOutData)

      # Since wp-config will be patched later to enable MULTISITE, need to:
      if FName == 'wp-config.php':
        xHL.Exec("mv {} {}".format(LocalFile, LocalFile + wTm.DotNowYMDHM()))

      RemoteFile = RemDir + FName
      L.info('  DeployApacheWpConf to RemoteFile: {}', RemoteFile)
      H.WH.BkpFile(RemoteFile)
      with H.WH.Sftp.open(RemoteFile, 'w') as F_Sftp:
        F_Sftp.write(FOutData)
    '''
    H.WH.MkDir(SDir + 'fb-2008/') #Need trailing slash
    #LocWhTEMwDir = cHL.WebHDir + 'TEM/www/'  #= /fs/py/web/host/ + TEM/www/
    L.info('WH.Sftp.put {} fb-2008/fbml {} fb-2008/fbml', LocWhTEMwDir, SDir)
    H.WH.Sftp.put(   LocWhTEMwDir +'fb-2008/fbml', SDir +'fb-2008/fbml')
    '''
    if self.SId == 1:
      H.WH.SftpSymLink('/fs/sec.gov/Archives', H.WC.SDir +'Archives')
      H.WH.SftpSymLink('/fs/wordpy'          , H.WC.SDir +'wordpy')
      #ln -s  /fs/web/doc/img/wpy/wordpy-16x16.png favicon.ico
      H.WH.SftpSymLink(H.WC.WDImg +'wpy/wordpy-16x16.png',
                       H.WC.SDir  +'favicon.ico')
    elif self.SId == 20:
      H.WH.SftpSymLink(H.WC.WDImg +'wpy/css'    , H.WC.SDir +'css'    )
      H.WH.SftpSymLink(H.WC.WDImg +'wpy/greybox', H.WC.SDir +'greybox')
      H.WH.SftpSymLink(H.WC.WDImg +'wpy/js'     , H.WC.SDir +'js'     )
      H.WH.SftpSymLink(H.WC.WDImg +'wpy/wordpy-16x16.png',
                       H.WC.SDir  +'favicon.ico')


  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def PrepareWpCli(self, H):
    # To copy dir, not files in dir, no trailing slash wp-cli
    #RSyncToRemote(cHL.WebDir +'wp-cli', H.WC.WebD, **H.WH.SshArgs)
    H.WH.Rsync(cHL.WebDir +'wp-cli', H.WC.WebD)

    L.info("InstallWp uses customized wp-cli. "
      " Add blog_id to populate_network() in wp-admin/includes/schema.php\n"
      " Add WP_INSTALLING to get_blog_prefix() in wp-db.php")
    Exe.PatchFiles(H, 'wp', H.WC.SDir)

    self.MultiSiteOn = True  #MSite installed by wp wpy-core multisite_install


  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use WH0 and WC0 in 1st Hs to Exec
  def InstallMultiSite(self):
    Exe.RestartPhpCmd(self.Hs0)  # self.Hs0.WH is self.WH0  #Out: True
    #wp-cli.org/config/#global-parameters : use Command Line args: --arg=xyz
    #  instead of using options in wp-cli.yml. Can't require 2 php in 1 yml!?!
    Cmd=("wp wpy-core multisite_install --path={} --url={} --base={}"
         " --subdomains --title='{}' --admin_user='{}' --admin_password='{}'"
         " --admin_email='{}' --skip-email --site_id={} --blog_id={}"
         " --require={} --color=true --debug=true").format(self.WC0.SDir,
       self.SFQDN, self.SPath, self.WC0.BTitle, self.SU.ULogin, self.SU.UPass,
       self.SU.UEmail,self.SId,self.BId, self.WC0.WebD +'wp-cli/wpy-core.php')
    # /fs/web, /fs/web/wpy, wordpy.com, /, Word Python Info, wordpy_info,
    # Password, info@wordpy.com, 2, 200
    #Cmd= "cd "+ H.WC.WebD +"wp-cli/ && wp wpy-core multisite_install  --path='/fs/web/wpy'  --url='wordpy.com'  --base='/'  --subdomains --title='Word Python Info' --admin_user='wordpy_info' --admin_password='wordpy_password' --admin_email='info@wordpy.com' --skip-email  --site_id=81  --blog_id=8100"

    self.WH0.Exec(Cmd)
    #Exe.RestartPhpCmd(self.Hs0)


  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use GDB in 1st Hs to Exec
  def Disabled_UpdateAdminUserId(self):
    # self.GDB.DbConnViaSshTun() #SshTun Already above
    import wp.i.user as WpU
    import wpy.user  as WU
    Login = self.SU.ULogin
    OldId = WpU.get_user_by('user_login', Login)
    NewId = WU.GetAdminUserIdByLogin(Login)
    #for Id,V in WU.AdminUserD:
    #  if V[0] == Login:
    #     NewId = Id
    L.info(WpU.UpdateUserId(OldId, NewId))


  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def InstallAllThemes(self, H, Skip='Avada'):
    for Theme, V in H.WC.Themes.items():
      ThemesV = WpC.ThemeOD[Theme]
      TSrc    = ThemesV[2]  #= Theme Source: svn, git, loc=local, cbx=cbox
      TSlug   = ThemesV[3]  #= ThemeSlug
      TSrcPath= ThemesV[4] if len(ThemesV) > 4 else None
      Download_WTheme = V[0]
      if Download_WTheme:
        L.info("\n InstallAllThemes {} {} {} {}", Theme, TSrc, TSlug, TSrcPath)
        self.DownloadTheme(Theme, TSrc, TSlug, TSrcPath, Skip, H=H)


  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def InstallAllPlugins(self, H, OnlyInstall=()):
    "DS = WD.DeploySiteCls(1); DS.SshOpenAll();      "
    "DS.InstallAllPlugins(OnlyInstall=('opns',))"
    for Plugin, V in H.WC.Plugins.items():
      if len(OnlyInstall) > 0 and Plugin not in OnlyInstall:
        continue
      #PluginsV = WpC.PluginOD[Plugin]
      #PSrc     = PluginsV[2]  #= Plugin Source: svn, git, loc=local, cbx=cbox
      #PSlug    = PluginsV[3]  #= PluginSlug
      #PSrcPath = PluginsV[4] if len(PluginsV) > 4 else None
      Download_WPlugin = V[0]
      if Download_WPlugin:
        self.DownloadPlugin(Plugin, H)   # , PSrc, PSlug, PSrcPath)


  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def WrapUpWDeploy(self, H):     #Include: ChownWww
    "run this to enable multisite in wp-config before ActivateAllWPlugins"
    self.MultiSiteOn = True       # by now, MultiSite is installed in db
    Exe.PatchFiles(H, 'MSiteOn', H.WC.SDir)

    for Id,V in Exe.SvrCmds(1, self, H).items():
      if V[0]:   # if Required
        H.WH.Exec(V[1], CmdId=Id)
    #SvrCmds includes: 'sudo chown -R '+ cHO.UsrGrpWww+' '+ ChownDirs =H.WC.SDir


  def Run_DbCreate_Federated_Servers(self):
    ''' Need to run it to create SDB.DbHostDotName in mysql.servers,
        so SDB.wp_option can be linked to SDB.DbHostDotName.wp_id_option below.
    '''
    DbCreate_Federated_Servers(self.SDB, self.GDB)

  def DbDrop_Federated_BpUsersTables(self, NewInstall=None):
    if NewInstall is None:
      NewInstall = self.NewInstall
    if NewInstall:
      DbDrop_NewInstall_WpUserTables(self.GDB, self.SDB)
    # drops Fed options table that following drop skip
    DbDrop_Federated_BpTables(self.SDB)


  # RUN LinkTo_GDb_Tbs AFTER Exec wp wpy, or error:
  # WordPress database error Storage engine FEDERATED of the table `wp_wpy`.`wp_bp_notifications_meta` doesn't have this option for query ALTER TABLE wp_bp_notifications_meta ADD KEY meta_key (meta_key(191)) made by include('phar:///usr/local/bin/wp/php/boot-phar.php'), include('phar:///usr/local/bin/wp/php/wp-cli.php'), WP_CLI\Runner->start, WP_CLI\Runner->_run_command, WP_CLI\Runner->run_command, WP_CLI\Dispatcher\Subcommand->invoke, call_user_func, WP_CLI\Dispatcher\CommandFactory::WP_CLI\Dispatcher\{closure}, call_user_func, WpyBp_Command->add_pages, bp_core_install_notifications, dbDelta

  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  def DbLinkTo_GDb_Tbs(self):
    "To verify: SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = DbName; "
    DbCreate_Federated_BpUsersTables(self.SDB, self.GDB)


  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use self.Hs[self.Host0]
  def ActivateAllThemes(self):
    for Theme, V in self.WC0.Themes.items():
      ThemesV = WpC.ThemeOD[Theme]
      TSlug   = ThemesV[3]  #= ThemeSlug
      Activate= V[1] #Activate: True=>Network, tuple(BId,..)=>BId,..
      # self.ActivateTheme(self.Hs[self.Host0], Activate, TSlug)
      if isinstance(Activate, (list,tuple)): # Activate=tuple(BId,..)
        if Activate == (0,):
          Activate = WpC.AllBIdsInSId( self.SId )
        self.BlogsActivateTheme(Activate, TSlug)
      elif Activate is True:                 # Network Activate
        self.SiteEnableTheme(TSlug, Network=True, Activate=True)


  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use self.Hs[self.Host0]
  def ActivateAllWPlugins(self):
    for Plugin, V in self.WC0.Plugins.items():
      PluginsV = WpC.PluginOD[Plugin]
      PSlug    = PluginsV[3]  #= PluginSlug
      Activate = V[1] #Activate: True=>Network, tuple(BId,..)=>BId,..
      if isinstance(Activate, (list,tuple)): # Activate=tuple(BId,..)
        if Activate == (0,):
          Activate = WpC.AllBIdsInSId( self.SId )
        self.BlogsActivatePlugin(Activate, PSlug)
      elif Activate is True:                 # Network Activate
        self.SiteActivatePlugin(PSlug)
    #self.ActivatePlugin(Activate=True, PSlug='merc') #Don't need to activate
    # Warning: The 'merc' plugin could not be found


  def UpdateBlogDesc(self):
    ''' Can't run from DeploySiteCls. Must run from DeployBlogCls.
    ipython -i --c="import wpy.web_deploy as WD; DBlog=WD.DeployBlogCls(WD.BId)"
    '''
    self.DBlog = DeployBlogCls(self.BId)
    self.DBlog.UpdateBlogDesc()

  def AddBpCoverPageOptions(self):
    self.DBlog.AddBpCoverPageOptions()

  def AddSiteBpPages(self):
    # May need to wait for backend bp setup process to finish before Exec wp
    # So move this to the end
    self.AddBpPages()

  def UpdateAllGoDaddyDomainDns(self):
    L.info('UpdateAllGoDaddyDomainDns self.SId= {}',  self.SId)
    from crm.GoDaddy  import UpdateAllGoDaddyDomainDnsInSId
    UpdateAllGoDaddyDomainDnsInSId(self.SId)

  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def DomainMapping(self, H):       # github.com/humanmade/Mercator
    SunRiseF = H.WC.SCDir + 'sunrise.php' #=/fs/web/wpy/wp-content/sunrise.php
    FData = "<?php require '{}/mercator/mercator.php';".format(H.WC.SPDir)
    H.WH.BkpFile(SunRiseF)

    with H.WH.Sftp.open(SunRiseF, 'w') as F_Sftp:
      F_Sftp.write(FData)

    Exe.PatchFiles(H, 'SUNRISE', H.WC.SDir)

  #######################################################################

  def SearchReplaceFQDN(self, OldFQDN='wordpy.com', NewFQDN=None,
                        SFQDN=None, ExportF=False):
    ''' DumpFileOrig = self.SDB.DbDump()    #Backup SDB
        DumpFileNew = self.SDB.DbDump(DbName='wp_wpy')   #Backup wpy SDB
    '''
    if ExportF is None:
      ExportF = self.SDB.GetDumpFileName(self.SDB.DbName)   # = ('wp_wpy')
    NewFQDN = NewFQDN or self.SFQDN
    SFQDN   = SFQDN   or self.SFQDN
    self.WpSearchReplaceFQDN(OldFQDN, NewFQDN, SFQDN, ExportF=ExportF)

  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use WH0, WC0, and SDB in 1st Hs to Exec
  def  MigrateSDB(self, OldFQDN='oldwordpy.com', NewFQDN='wordpy.com',
                        NewDbName='wp_wpy'):
    ''' Too Dangerous to DROP DB using variables !!
    # DropDbSql = "DROP DATABASE {}".format(self.SDB.DbName)
    DropDbSql = "DROP DATABASE wp_vic"
    DropDb    = self.SDB.Exec(DropDbSql, None, 'delete')
    self.SDB.CreateDb_GrantUser()       #Start with a clean new SDB
    '''
    ExportF = self.SDB.GetDumpFileName(self.SDB.DbName)   # = ('wp_wpy')
    self.WpSearchReplaceFQDN(OldFQDN, NewFQDN, OldFQDN, ExportF=ExportF)
    NewDbName = NewDbName or self.SDB.DbName
    DbLoadCmd = self.SDB.DbLoadCmd(ExportF, NewDbName, self.SDB.DbHost)
    self.WH0.Exec( DbLoadCmd )
    #self.WH0.Exec("{} && mv {} {} && cp -p {} {}".format( DbLoadCmd,
    #  self.WC0.SDir +'wp-config.php',
    #  self.WC0.SDir +'wp-config.php'+ wTm.DotNowYMDHM(),
    #  self.WC0.WwwD +'wpy/wp-config.php',
    #  self.WC0.SDir +'wp-config.php',
    #))
    #self.LinkTo_GDb_Tbs() #self.DbCreate_Federated_BpUsersTables(self.SDB, self.GDB)

    # in wp-config search replace:
    #    wdp -> wpy
    #    wordpress.org -> wordpy.com
    # add wordpy to sites-avaiable/vic.conf:  ServerName and ServerAlias
    # a2dissite wpy   #Disable old site
    # sudo rm -rf /fs/www/vic/wp-content/themes/Avada-Child-Theme
    # sudo rm -rf /fs/www/vic/doc
    # cp -rp /fs/www/wpy/wp-content/themes/Avada-Child-Theme
    #        /fs/www/vic/wp-content/themes/Avada-Child-Theme
    # cp -rp /fs/www/wpy/doc /fs/www/vic/doc

#End DeploySiteCls(Web.SiteCls)

# To migrate from wp_wpy to wp_wpy:
#drop database wp_wpy;
#$ WebPy 4 DeploySite
#>>> with wpy.context.RedirectOutput(FilePfx = 'deploy-wordpy.CreateSiteDb.'):
#>>>   D.CreateSiteDb()
#$ WebPy 3 DeploySite
#>>> with wpy.context.RedirectOutput(FilePfx = 'deploy-wordpy.MigrateSDB.'):
#>>>   D.MigrateSDB(OldFQDN='oldwordpy.com', NewFQDN='wordpy.com', NewDbName='wp_wpy')
#$ WebPy 4 DeploySite
#>>> D.SDB.DbChangeTablePfx('wp_400_', 'wp_300_', D.GDB)

#wp_wpy]> UPDATE wp_site SET id = 4 WHERE id = 3;
#wp_wpy]> UPDATE wp_blogs SET blog_id = 400, site_id = 4 WHERE site_id = 3;
#wp_wpy]> select * from wp_400_options where option_value like "%wordpy%";
#| option_id | option_name | option_value | autoload |
#|        10 | blogname    | wordpy.com   | yes      |
#wp_wpy]> update wp_400_options set option_value = "wordpy.com" where option_id = 10;
#wp_wpy]> select * from wp_sitemeta where meta_value like "%wordpy%";
#| meta_id | site_id | meta_key  | meta_value       |
#|       2 |       4 | site_name | wordpy.com Sites |
#wp_wpy]> update wp_sitemeta set meta_value= "wordpy.com Sites" where meta_id = 2;
#
# D.Run_DbCreate_Federated_Servers()
# WD.DbCreate_Federated_BpUsersTables(self.SDB, self.GDB, OptionsTbOnly=True)



@xDB.SDB_ClusterDecorator #loop through all SDB servers in cluster
#@Ctx.RedirectOutputDctr(NewFilePerEntry=True, RedirectOn=WrToLogFile)
def DbCreate_Federated_Servers(SDB, GDB):
  ''' This method uses SDB, so needs to be in web.py, not db.py.
  Need @SDB_ClusterDecorator to loop through all db servers in cluster because:
    mariadb.com/kb/en/mariadb/mariadb-galera-cluster-known-limitations/
  Replication works only with the InnoDB storage engine. Any writes to tables
  of other types, including system (mysql.*) tables are not replicated.
  This limitation excludes DDL statements such as CREATE USER, which
  implicitly modify the mysql.* tables — those are replicated).
    show create table mysql.servers; ENGINE=MyISAM <<== NOT replicated!!

  SELECT * from mysql.servers;  # Create GDB & SDB FederatedX servers below:
  |Server_name |Host     |Db        |Username |Pass|Port|Socket|Wrapper|Owner
  |db1_global  |db1      |wp_global|wp_dbuser|    |3306|      |mysql  |root
  |wdb1.wp_wpy|127.0.0.1|wp_wpy   |wp_dbuser|    |3306|      |mysql  |root

  DROP SERVER [ IF EXISTS ] 'wdb1.wp_wpy';
  '''
  SDB.SshTunClose_AfterExec = False
  CreateSvrSql = ("CREATE SERVER '{Svr}' FOREIGN DATA WRAPPER 'mysql' "
    " OPTIONS (HOST '{Host}', DATABASE '{Name}', USER '{User}', "
    " PASSWORD '{Pass}', PORT {Port}, SOCKET '', OWNER 'root')")
  SelectSql = "SELECT * from mysql.servers WHERE Server_name = %(SvrName)s"

  import wpy.db      as wDB
  GDB = wDB.GetMainGDbInSameRegionAsSDB(SDB, GDB)

  for Db in (GDB, SDB):
    SelectDict = {'SvrName':Db.DbHostDotName, }
    if not SDB.Exec(SelectSql, SelectDict, 'fetchone', Tries=1): #is None: # empty set
      L.info('{} does not exists in mysql.servers! Try to CREATE:',
             Db.DbHostDotName)
      CreateSql= CreateSvrSql.format(Svr=Db.DbHostDotName, Host = Db.DbHost,
         Name=Db.DbName, User=Db.DbUser, Pass=Db.DbPass,Port=Db.DbPort)
      try: CreateDb = SDB.Exec(CreateSql, None, 'insert', Tries=1)
      except: import sys; cLog.PrintError(sys.exc_info())
    else:
      L.info('{} already exist in mysql.servers! No need to recreate.',
             Db.DbHostDotName)

  #SelectDict = {'SvrName':SDB.DbHostDotName, }
  #if SDB.Exec(SelectSql, SelectDict, 'fetchone') is None:   # empty set
  #  L.info('{} does not exists in mysql.servers! Try to CREATE:',
  #         SDB.DbHostDotName)
  #  CreateSql= CreateSvrSql.format(Svr=SDB.DbHostDotName, Host='127.0.0.1',
  #     Name=SDB.DbName, User=SDB.DbUser, Pass=SDB.DbPass,Port=SDB.DbPort)
  #  CreateDb = SDB.Exec(CreateSql, None, 'insert')
  #else:
  #  L.info('{} already exist in mysql.servers! No need to recreate.',
  #         SDB.DbHostDotName)

  #SelectDict = {'SvrName':GDB.DbHostDotName, }
  #if SDB.Exec(SelectSql, SelectDict, 'fetchone') is None:   # empty set
  #  L.info('{} does not exists in mysql.servers! Try to CREATE:',
  #         GDB.DbHostDotName)
  #  CreateSql=CreateSvrSql.format(Svr=GDB.DbHostDotName,Host=GDB.DbHost,
  #     Name=GDB.DbName, User=cDB.UserWpy,Pass=cDB.PassWpy,Port=SDB.DbPort)
  #  CreateDb = SDB.Exec(CreateSql, None, 'insert')
  #else:
  #  L.info('{} already exist in mysql.servers! No need to recreate.',
  #         GDB.DbHostDotName)
  SDB.SshTunClose_AfterExec = True


# mariadb.com/kb/en/mariadb/about-federatedx/
# wDB.Exec(..,DbHost='wdb1') for Federated Tables in different Cluster DbHost
#Use DbLinkTo_GDb_Tbs(), Don't need: @SDB_ClusterDecorator
#@Ctx.RedirectOutputDctr(NewFilePerEntry=True, RedirectOn=WrToLogFile)
#@xDB.SDB_ClusterDecorator #TODO Don't need to loop through all Dbs as they are replicated?  system (mysql.*) tables are not replicated.
def  DbCreate_Federated_BpUsersTables(SDB, GDB, OptionsTbOnly=False):
  ''' This method uses SDB and GDB, so needs to be in web.py, not db.py.
  Create Federated tables are NOT replicated !!??
  '''
  from wpy.db_sql import CreateTbs
  #SDB.SshTunClose_AfterExec = False

  # [enable mysql federated engine](stackoverflow.com/questions/5210309/)
  try: SDB.Exec("install plugin federated soname 'ha_federated.so'", Tries=1)
  #except: import sys; cLog.PrintError(sys.exc_info())
  except:
    L.exception("Can't install plugin federated soname ha_federated.so to SDB")
  #SDB.Exec("show engines")
  import wpy.db      as wDB
  GDB = wDB.GetMainGDbInSameRegionAsSDB(SDB, GDB)

  for TbSuffix, CreateSql in CreateTbs.items():
    if OptionsTbOnly and TbSuffix !='options': #Process only options table, skip others
      continue
    Pfx = SDB.SPfx if TbSuffix != 'options' else SDB.Tbs.TbPfx #=wp_4_
    Table = Pfx + TbSuffix
    DbDotTable = SDB.DbName +'.'+ Table
    L.info('\n {} {} {} {}\n', TbSuffix, Pfx, SDB.SPfx, SDB.Tbs.TbPfx)
    DbExistSql = "SHOW TABLES LIKE '{}'".format(Table)#DbDotTable return None
    if SDB.Exec(DbExistSql, None, 'fetchone', Tries=1) is None:   # empty set
      L.info('{} table does not exists! No need to drop.', Table)
    elif TbSuffix == 'options':
      L.info('{} table cannot be dropped! Skip.', TbSuffix)
    elif SDB.SId == 1:
      L.info('SId=1! wpy tables cannot be dropped! Skip.')
    else:
      L.warning("\n\n{} table still exists! DbDrop_Fed above did not drop it!!"
                " Try to drop it if it's a Federated table\n\n", Table)
      #DbDrop_Federated_BpTables(SDB, DbName=SDB.DbName, Tb=Table)
      SDB.DropTb(Table)
      #Above safer! Below Dangerous! Droped non-Fed tales in wp_global !!
      #DropTblSql = "DROP TABLE {}".format(DbDotTable) #safer than drop Table
      #DropTbl = SDB.Exec(DropTblSql, None, 'insert', Tries=1)
      #L.info('{}  DropTbl= {}', DropTblSql, DropTbl)
      ##if DropTbl != 1:
      ##  raise Exception('Cannot '+ DropTblSql)

    TableOptions= ("ENGINE=FEDERATED CONNECTION='{SvrName}' DEFAULT CHARSET="
        "{DbChar} COLLATE={DbChar}_unicode_ci ROW_FORMAT=DYNAMIC").format(
        SvrName = (SDB.DbHostDotName +'/'+ Table) if TbSuffix =='options'
        else GDB.DbHostDotName, DbChar  =  SDB.DbChar)
    # AUTO_INCREMENT=8715
    CreateFedTableSql = CreateSql.format(Pfx=SDB.SPfx, Options=TableOptions)
    # WRONG! Pfx = SDB.SPfx if TbSuffix == 'options' else SDB.Tbs.TbPfx
    try: Create = SDB.Exec(CreateFedTableSql, None, 'insert', Tries=1)
    except: L.exception("\nCan't execute CreateFedTableSql = {}",
                        CreateFedTableSql)
    #L.info('Create Federated Table: {}', Create)


  SDB.SshTunClose_AfterExec = True


#@Ctx.RedirectOutputDctr(NewFilePerEntry=True, RedirectOn=WrToLogFile)
#@xDB.SDB_ClusterDecorator
def  DbDrop_Federated_BpTables(SDB, DbName=None, Tb=None):
  DbName = SDB.DbName    if DbName is None else DbName
  TbsFed = SDB.FederatedTbsInDb_List(DbName, Tb)
  L.info('\nTry to drop the following Federated tables in DbName= {}', DbName)
  #for Dict in TbsFed:  # [{'TABLE_NAME': 'wp_bp_activity'}, {}, {}..]
  #  Table = Dict['TABLE_NAME']
  for Table in TbsFed:  # [{'TABLE_NAME': 'wp_bp_activity'}, {}, {}..]
    #if not Table.endswith('options'):#Process only options table,skip others
    #  continue
    SDB.DropTb(Table)


#@Ctx.RedirectOutputDctr(NewFilePerEntry=True, RedirectOn=WrToLogFile)
def  DbDrop_NewInstall_WpUserTables(GDB, SDB, DbName=None):
  '''Drop newly created wp_users & wp_usermeta ONLY if count(*) < 50.
  prevent from dropping wp_global.wp_users, wp_usermeta w/ count > 50
  Must include SDB.DbName or GBD.DbName might get dropped accidentally!!!
  '''
  User, UserMeta = GDB.TbG.User, GDB.TbG.UserMeta
  DbName = SDB.DbName    if DbName is None else DbName
  CountStar = 'count(*)'
  for Tb in (User, UserMeta,):
    if SDB.IfTbExist(DbName, Tb):
      CountRow = SDB.Exec("SELECT {} FROM {}.{}".format(CountStar, DbName, Tb),
                           None, 'fetchone', Tries=1)
      CountNum = CountRow[CountStar]
      if CountNum:
        L.info('\nTry to drop new {}.{} as {} < 50', DbName, Tb, CountNum)
        SDB.Exec("DROP TABLE {}.{}".format(DbName, Tb), Tries=1)
        #Don't quote TbName repr()
      else:
        L.info('\nDo NOT drop new {}.{} as {} >=50', DbName, Tb, CountNum)
      L.info('\n')



def Site1():
  S = Web.SiteCls(1, H000002)
  S.SshOpenAll()
  #pprint(S.SDB.Exec('desc wp_posts', Tries=1))
  #pprint(S.SDB.TbG.__dict__)
  #pprint(S.SDB.Exec('desc wp_posts', Tries=1))
  return S

'''
===========
TO DO: Sync
===========
From web1:/fs/web/doc/sites/1/ ~12/ # include 1/bp-attachments
  To web2:/fs/web/doc/sites/1/ ~12/ # include 1/bp-attachments

cax# cd /fs/web/doc
ln -s /fs/web/doc/img/wpy/wordpy-16x16.png /fs/www/wpy/favicon.ico

Sync child themes changes.
      self.WH0.Rsync(cHL.WpPDir + TSlug, ThemeDir, ChownWww=False)

========================================
Below Already Implemented in SetupWDoc()
========================================
mkdir /fs/web/doc && cd /fs/web/doc && mkdir -p img avatars group-avatars

cd /fs/www/???/doc/              # ??? = SName
mv sites buddypress /fs/web/doc
\rm img avatars group-avatars bp-attachments
ln -s /fs/web/doc/sites          sites
ln -s /fs/web/doc/buddypress     buddypress
ln -s /fs/web/doc/img            img
ln -s /fs/web/doc/avatars        avatars
ln -s /fs/web/doc/group-avatars  group-avatars
ln -s /fs/web/doc/sites/BId/bp-attachments bp-attachments

for i in $(seq 2010 2030); do echo mkdir -p $Dir$i; echo ln -s $Dir$i $i; done
Dir='/fs/web/doc/sites/1/'
mv 2010 2011 2012 2013 2014 2015 2016 2017  $Dir
for i in $(seq 2010 2030); do mkdir -p $Dir$i; ln -s $Dir$i $i; done

ln -s sites/20/2015 2015  && ln -s sites/20/2016 2016 && ln -s sites/20/2017 2017

cd /fs/www/???/doc/sites/BId/    # ??? = SName
rm -rf img avatars group-avatars bp-attachments
ln -s /fs/web/doc/img            img
ln -s /fs/web/doc/avatars        avatars
ln -s /fs/web/doc/group-avatars  group-avatars
mkdir bp-attachments

'''


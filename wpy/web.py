'''
python -i -c "import wpy.web as Web; import wp.conf as WpC; WB = WpC.WB;
              WB.InitBlog(20); Wj = WB.Wj; Bj = WB.Bj;"
python -i -c "import wpy.web as Web; B = Web.BlogCls(4, WebConf=True);"

import wpy.web as W; S = W.SiteCls(1, cHO.H000002, ConnSsh=True, WebConf=True);
import wpy.web as W; S = W.SiteCls(2, cHO.H000104, ConnSsh=True, WebConf=True);
S.DownloadPlugin('tcsc', S.Hs0)
S.UpdateWpAll()

import sys
for k,v in sys.modules.items():
  if k.startswith('wpy.'): print(k,v)
'''
#import sys, os  #, pathlib # import parent module
#sys.path.append(str(pathlib.Path('.').absolute().parent))
#sys.path.append('.')

import sys, os # Parent_Dir of  Current_Dir of   Current_Py_Script
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))
#sys.path.append('/fs/py/web/')

import pyx.type  as xTp
import pyx.web   as xWB
import wp.conf   as WpC
import config.db as cDB
import wpy.db    as wDB
import wpy.host  as wHo
import wpy.exe   as wEx
import wpy.time  as wTm
import wp.i.load as WiL
import config.log as cLog; L = cLog.logger
#sys.path.pop() #rm parent dir from sys.path, or error importing other modules
ODict = xTp.ODict
cHL, cHO, xHR = wHo.cHL, wHo.cHO, wHo.xHR


# moved from xWB = pyx.web
class HostSiteConfCls:    # Exit can be print, sys.exit, or ShutdownExit
  ''' DbC='Site'  : ==> web.SiteCls.Hs based on SiteDbCls   by default
         ='Blog'  : ==> web.SiteCls.Hs based on BlogDbCls   by default
         ='Global': ==> web.SiteCls.Hs based on GlobalDbCls by default
  '''
  def __init__(self, Sj, Host, ConnSsh, WebConf, Exit=sys.exit): # Bj=None
    L.debug("HostSiteConfCls: {} {} {} {}", Sj, Host, ConnSsh, WebConf)
    self.Host= Host
    self.WH = wHo.HostCls(Host, ConnSsh=ConnSsh, Exit=Exit)
    " WH = Web Server Host object "
    if WebConf:
      self.WC = WpC.SiteConfCls(Sj, self.WH)


class SiteCls(xWB.xSiteCls):       # Web Site Class
  ''' Hosts: tuple(Host, Host,), or if str -> tuple(str,).
      isinstance(Sj, Web.SiteCls) ==> Hs based on WB.SiteDbCls by default
  '''
  def __init__(self, SId, Hosts=None, ConnSsh=False, WebConf=False,
               AutoCommit=True, Exit=sys.exit, LoadSDB=True):
    import wpy.user as WU
    self.SId     = SId
    if not hasattr(self, 'BId'):#Get BId of MainSite SId if not set in BlogCls
      #    BId = SId*100 if BId not in WpC.BlogOD
      self.BId = WpC.SiteBlogId(self.SId)

    self.AutoCommit = AutoCommit
    self.ConnSsh = ConnSsh
    self.WebConf = WebConf
    self.Exit    = Exit
    V            = WpC.SiteOD[self.SId]
    # L.info('SiteCls {} {} {} {}', self.SId, Hosts, self.BId, V)
    self.SName   = V[0]
    self.SPath   = V[1]   # self.S* Site attributes will not be changed by Blog
    self.Hosts   = V[2] if Hosts is None else Hosts
    if isinstance(self.Hosts, str):
      self.Hosts = (self.Hosts,)    # Watch out!!  tuple('web1',)=('c','a','w')
    self.SPfx    = V[3] if len(V) > 3 else WpC.WPfx  #= Site Prefix
    self.SUId    = V[4] if len(V) > 4 else 1001       #= wordpy_info
    self.SDomains= wHo.GetAllRegistrarsDomains()[self.SName]
    self.SFQDN   = self.SDomains[0]  #Site Fully Q Domain Name: wordpy.com
    self.SUrl    = 'http://'+ self.SFQDN +'/' #Site URL=php network_site_url()
    self.SU      = WU.AdminUserCls(self.SUId)      #Site User  # SU vs BU
    self.XmlCli = {
      'url'      : self.SUrl + 'xmlrpc.php',
      'username' : self.SU.ULogin,
      'password' : self.SU.UPass,
      'blog_id'  : self.BId,   # Old self.SID BAD ?!
    }

    # self.Hs   = ODict((h, wHo.HostCls(h, ConnSsh)) for h in self.Hosts)
    self.Hs = ODict()   # WSite Cluster Of WH, WC, WDB
    for Host in self.Hosts:
      L.info('\nSiteCls init Host= {}', Host)
      self.Hs[Host] = HostSiteConfCls(self, Host, ConnSsh,WebConf,Exit=Exit)

    # Default Site Host0 =the First Hosts
    self.Host0 = self.Hosts[0]
    # L.info("{} {} {}", self.Host0, self.Hosts, self.Hosts[0])
    self.Hs0   = self.Hs[self.Host0]
    self.WH0   = self.Hs0.WH    #=1st WH= wHo.HostCls(Host, ConnSsh)
    " WH = Web Server Host object "

    if self.WebConf:
      self.WC0 = self.Hs[self.Host0].WC   #=1st WC= WpC.SiteConfCls(self, WH)
    '''No need to loop thr all Dbs since SDB0/BDB0 repr the same db for all Hs
       Change from WDB to GDB, SDB, or BDB, depending if Global, Site, or Blog
    self.GDB0  = self.Hs0.GDB
    #self.WDB0 = WB.SiteDbCls(SId,DbHost,WH,ConnSsh)  # DbHost = None
    self.WDB0  = self.Hs0.WDB    #=1st WDB= WB.SiteDbCls()
    '''
    self.SDB_KwArgs  = {'ConnSsh':ConnSsh, 'AutoCommit' : True, 'Exit':Exit, }

    #L.info("SiteCls SId= {}, cDB.Use_WB_GDB= {}", self.SId, cDB.Use_WB_GDB)
    if cDB.Use_WB_GDB:
      self.GDB = WB.GDB
    else:
      self.GDB = WB.GlobalDbCls(AutoCommit = self.AutoCommit, **cDB.GDB_KwArgs)
    L.info("SiteCls SId= {}, self.GDB= {}", self.SId, self.GDB)
    if LoadSDB:
      #L.info("SiteCls SId= {}, LoadSDB= {}", self.SId, LoadSDB)
      self.SDB = WB.SiteDbCls(self.SId, Sj=self, **self.SDB_KwArgs)
      L.info("SiteCls SId= {}, self.SDB= {}", self.SId, self.SDB)


  def DownloadPlugin(self, Plugin, H=None,PSrc=None, PSlug=None, PSrcPath=None):
    " WebPy 3 Site None Yes  && S.DownloadPlugin('ircp', S.Hs0) "
    if H is None:
      H = self.Hs0
    PluginsV = WpC.PluginOD[Plugin]
    PSrc     = PluginsV[2] if PSrc  is None else PSrc
    PSlug    = PluginsV[3] if PSlug is None else PSlug
    if len(PluginsV) > 4 and PSrcPath is None:
      PSrcPath = PluginsV[4]
    PluginDir= H.WC.WPDir + PSlug +'/'
    if PSrc == 'svn':
      SvnUrl = (WpC.PluginsSvnUrl.format(PSlug)
                if PSrcPath is None else PSrcPath )
      # svn co http://plugins.svn.wordpress.org/games . --depth immediates
      #ChownWww = False to allow ubt to write. ChownWww later in WrapUpWDeploy
      H.WH.Svn(PluginDir, Url=SvnUrl, Op='co')
    elif PSrc == 'git':
      H.WH.Git(PSrcPath, PluginDir, ChownWww=False)
    elif PSrc == 'zip':
      ZipFile = H.WC.WPDir + PSlug +'.zip'
      # -nc, --no-clobber: skip downloads if files already exist. not overwrite
      Err = H.WH.Wget(PSrcPath, ZipFile, NoClobber=True)
      L.info('DownloadPlugin Unzip {} {}', ZipFile, Err)
      #if Err:
      #  pass   # return False
      #else:
      H.WH.Unzip(ZipFile, H.WC.WPDir, IfPathExistAction=None, ChownWww=True)
    elif PSrc == 'loc':
      #  H.WH.RenameIfPathExist(PluginDir)
      if not H.WH.SftpPathExist(PluginDir):
        #Add trailing slash to TSlug, or will Rsync to TSlug/TSlug
        #RSyncToRemote(cHL.WpPDir+PSlug, RemDir, Option='avz',**H.WH.SshArgs)
        #Add trailing slash, or will Rsync to PSlug/PSlug
        H.WH.Rsync(cHL.WpPDir + PSlug +'/', PluginDir, ChownWww=False)

    SymLink = H.WC.SPDir + PSlug
    H.WH.SftpSymLink(PluginDir, SymLink)
    if   Plugin == 'ldb':
      LdbDropInDir = PluginDir +'ludicrousdb/drop-ins/'
      H.WH.SftpSymLink(LdbDropInDir +'db.php'      , H.WC.SCDir +'db.php')
      H.WH.SftpSymLink(LdbDropInDir +'db-error.php', H.WC.SCDir +'db-error.php')
    elif Plugin == 'reds':
      H.WH.SftpSymLink(PluginDir  +'includes/object-cache.php',
                       H.WC.SCDir +'object-cache.php')
      # ln -s /fs/web/p/redis-cache/includes/object-cache.php  /fs/www/wpy/wp-content/object-cache.php
    elif Plugin == 'bp':
      self.Install_P_or_T_Lang(H, 'plugins', PSlug, 'zh','CN')
    elif Plugin == 'wpy':
      FilesInWpyDir = H.WH.Sftp.listdir(H.WC.WPDir + PSlug)
      BlogClassPhp = [ f[0:3] for f in FilesInWpyDir if f[3:]=='-class.php'
                       and f[0:3] != 'all' ]       # = ['wpy', 'wdp',]
      PhpPfx = self.SName if self.SName in BlogClassPhp else 'wpy'
      H.WH.SftpSymLink(H.WC.WPDir + PSlug +'/'+ PhpPfx +'-class.php',
                       H.WC.SPDir +'wordpy-class.php' )  # Not H.WC.WPDir !!

    wEx.PatchFiles(H, Plugin, PluginDir)


  @xHR.AllHsDecorator     #decorator Loop through all Hs=odict_values
  def UpdateWpAll(self, H):
    '''import wpy.web as W;
       S = W.SiteCls(1, cHO.H000002, ConnSsh=True, WebConf=True);
       S = W.SiteCls(2, cHO.H000104, ConnSsh=True, WebConf=True);
       S.UpdateWpAll()
    '''
    for PorT in ('plugin', 'theme'):
      L.info('UpdateWpAll {} {}', H, PorT)
      self.UpdateWpPluginOrTheme(H, PorT)
    self.UpdateWpSvn(H)

  #@xHR.AllHsDecorator #Don't use! Calling func already looping through all Hs
  def UpdateWpSvn(self, H=None, SwitchToLatestWpUrl=True,
                        Refresh=True, ChownWww=True):
    ''' cd /fs/www/wpy && svn sw https://core.svn.wordpress.org/tags/4.7.4
    svn up wp-admin wp-includes --set-depth='infinity'
    svn sw: codex.wordpress.org/Installing/Updating_WordPress_with_Subversion
    '''
    if H is None:
      H = self.Hs0
    Svn, SDir, SCDir, STDir = H.WH.Svn, H.WC.SDir, H.WC.SCDir, H.WC.STDir
    L.info('\n UpdateWpSvn')
    if SwitchToLatestWpUrl:
      Svn(SDir, Url=WpC.LatestUrl() , Op='sw')
      # Exclude these Dirs:     # STDir = SDir +'wp-content/themes/'
      for T in ('twentyten','twentyeleven','twentytwelve','twentythirteen',
                'twentyfourteen'):
        Svn(STDir, T, Op='up', SetDepth='exclude')

    if Refresh:
      Svn(  SCDir, '' , SetDepth='immediates',Op='up', StdOut=True)
      for Dir  in ('plugins/', 'themes/',):
        Svn(SCDir, Dir, SetDepth='files'   , Op='up', StdOut=True)
      for Dir  in ('twentyfifteen/', 'twentysixteen/', 'twentyseventeen/',):
        Svn(STDir, Dir, SetDepth='infinity', Op='up', StdOut=False)
      for Dir  in ('wp-admin/', 'wp-includes/',):
        Svn(SDir , Dir, SetDepth='infinity', Op='up', StdOut=False)
      for File in ('license.txt', 'wp-config-sample.php', 'readme.html',):
        Svn(SDir, File, SetDepth='exclude' , Op='up', StdOut=True)

    if ChownWww:
      H.WH.SudoChown(SDir)

  @staticmethod
  def UpdateWpPluginOrTheme(H, PorT = 'plugin'):
    #if H is None:
    #  H = self.Hs0
    PorTDir = H.WC.WPDir if PorT == 'plugin' else H.WC.WTDir #/fs/web/p/ or /t/
    for Dir in H.WH.Sftp.listdir(PorTDir):
      L.info('\n')
      Path = PorTDir + Dir                  # = '/fs/web/p/bbpress-cn.zip'
      if not H.WH.IsRemotePathDir(Path):
        L.info('UpdateWpPluginOrTheme: Not a directory: Path= {}! Skip!', Path)
        continue
      Path = PorTDir + Dir +'/'             # = '/fs/web/p/buddypress/'
      ListDir = H.WH.Sftp.listdir(Path)
      L.info('UpdateWpPluginOrTheme ListDir= {}', ListDir)
      if   '.svn' in ListDir:
        #H.WH.Exec('svn up '+ Path)
        H.WH.Svn(Path, Op='up')
        H.WH.SudoChown(Path)
      elif '.git' in ListDir:
        #H.WH.Exec('cd '+ Path +' && git pull')
        H.WH.GitPull(     Path )
      else:
        L.info('UpdateWpPluginOrTheme: Path= {} is not a svn or git repository!'
               ' Skip!', Path)
    #svn sw https://core.svn.wordpress.org/tags/4.5.3/
    #Patch


  # Param: Blog default value can't = None or self.BName to work in other Blogs
  def BlogSiteFQDN(self, BName, SFQDN=None):
    SFQDN = self.SFQDN if SFQDN is None else SFQDN
    return SFQDN if BName is None else BName +'.'+ SFQDN  #=www.wordpy.com

  def BlogsActivatePlugin(self, BlogIds, PSlug):
    for BlogId in BlogIds:
      L.info('{} BlogActivatePlugin {}', BlogId, PSlug)
      BSFQDN = self.BlogSiteFQDN(WpC.BlogOD[BlogId][1], self.SFQDN)
      self.WH0.Exec('wp --path='+ self.WC0.SDir +' --url='+ BSFQDN
                    +'           plugin activate '+ PSlug)
  def SiteActivatePlugin(self, PSlug):   # Network Activate
    L.info('SiteActivatePlugin {}', PSlug)
    self.WH0.Exec(  'wp --path='+ self.WC0.SDir +' --url='+ self.SFQDN
                    +' --network plugin activate '+ PSlug)


  def DownloadTheme(self, Theme, TSrc, TSlug, TSrcPath, Skip=None, H=None):
    ''' svn co http://themes.svn.wordpress.org/twentyfifteen/1.7/
                                    /fs/web/t/twentyfifteen
        svn co http://themes.svn.wordpress.org/twentysixteen/1.3/
                                    /fs/web/t/twentysixteen
    '''
    if H is None:
      H = self.Hs0
    ThemeDir  = H.WC.WTDir + TSlug +'/'

    if TSrc == 'svn':
      if TSrcPath is None:
        SvnUrl = WpC.ThemesSvnUrl + TSlug +'/'
        if   TSlug == 'twentyfifteen':
          SvnUrl += '1.7/'
        elif TSlug == 'twentysixteen':
          SvnUrl += '1.3/'
        elif TSlug == 'twentyseventeen':
          SvnUrl += '1.2/'
      else:
        SvnUrl = TSrcPath
      # svn co http://themes.svn.wordpress.org/games . --depth immediates
      #ChownWww = False to allow ubt to write. ChownWww later in WrapUpWDeploy
      H.WH.Svn(ThemeDir, Url=SvnUrl, Op='co')
    elif TSrc == 'git':
      H.WH.Git(TSrcPath, ThemeDir, ChownWww=False)
    elif TSrc == 'zip':
      ZipFile = H.WC.WTDir + TSlug +'.zip'
      # -nc, --no-clobber: skip downloads if files already exist. not overwrite
      Err = H.WH.Wget(TSrcPath, ZipFile, NoClobber=True)
      L.info('DownloadTheme Unzip {} {}', ZipFile, Err)
      if Err:
        return False
      H.WH.Unzip(ZipFile, H.WC.WPDir, IfPathExistAction=None, ChownWww=True)
      if TSlug == 'cbox-child':
        H.WH.Exec('rm -rf '+ H.WC.WTDir +'__MACOSX')
    elif TSrc == 'loc' and Skip != TSlug:   # Skip Rsync large themes ~ 100MB!
      #  H.WH.RenameIfPathExist(ThemeDir)
      if not H.WH.SftpPathExist(ThemeDir):
        #Add trailing slash to TSlug, or will Rsync to TSlug/TSlug
        H.WH.Rsync(cHL.WpTDir + TSlug +'/', ThemeDir, ChownWww=False)

    SymLink = H.WC.STDir + TSlug
    if 'child' in TSlug.lower() and not H.WH.SftpPathExist(SymLink):
      H.WH.Exec('cp -rp '+ ThemeDir +' '+ SymLink)
    else:
      H.WH.SftpSymLink(ThemeDir, SymLink)
    self.InstallCustomThemeLang(TSlug, H)

  def BlogsActivateTheme(self, BlogIds, TSlug):
    for BlogId in BlogIds:
      L.info('{} BlogActivateTheme {}', BlogId, TSlug)
      BSFQDN = self.BlogSiteFQDN(WpC.BlogOD[BlogId][1], self.SFQDN)
      self.WH0.Exec('wp --path='+ self.WC0.SDir +' --url='+ BSFQDN
                   +' theme activate '+ TSlug)
  # codex.wordpress.org/Child_Themes : may need to re-save your menu (Appearance > Menus, or Appearance > Customize > Menus) and theme options (including background and header images) after activating the child theme.

  # Network=True:  Enable theme for entire network
  # Activate=True: Activate theme for current site. NOT influenced by Network
  #No SiteActivateTheme(self, H, TSlug):   #No Network Activate
  # ' --network theme activate '+ TSlug)   # Just Blog Activate
  def SiteEnableTheme(self, TSlug, Network=True, Activate=True):
    L.info('SiteEnableTheme {} {}', TSlug, 'Network' if Network else '')
    self.WH0.Exec('wp --path='+ self.WC0.SDir +' --url='+ self.SFQDN
                 +(' --network  ' if Network  else ' ')
                 +(' --activate ' if Activate else ' ')
                 +' theme enable '+ TSlug)

  # codex.wordpress.org/Child_Themes
  def InstallChildTheme(self, H=None, TSlug=None):
    if H is None:
      H = self.Hs0
    if TSlug is None:
      return False
    ChildThemeDir = H.WC.WTDir + TSlug +'-child/'
    L.info('InstallChildTheme for parent theme: {}', TSlug)
    H.WH.RenameIfPathExist(ChildThemeDir)
    H.WH.MkDir(ChildThemeDir)

    ChildCss = ChildThemeDir + 'style.css'
    L.info('  InstallChildTheme to ChildCss: {}', ChildCss)
    Css = WpC.ChildThemeCss.format(Theme=TSlug)
    if (TSlug.startswith('twenty') and
        TSlug[len('twenty'):] in WpC.BpTwentyThemes):
      Css += WpC.BpDequeueStyle.format(TSlug=TSlug)
    with H.WH.Sftp.open(ChildCss, 'w') as F_Sftp:
      F_Sftp.write(Css)

    ChildPhp = ChildThemeDir + 'functions.php'
    L.info('  InstallChildTheme to ChildPhp: {}', ChildPhp)
    with H.WH.Sftp.open(ChildPhp, 'w') as F_Sftp:
      F_Sftp.write(WpC.ChildThemePhp)


  # Discuz Translation: github.com/skyzhou/docker-discuz/blob/master/source/language/lang_admincp_msg.php
  #wget https://translate.wordpress.org/projects/wp-plugins/buddypress/stable/zh-cn/default/export-translations?format=mo  -O /fs/web/p/buddypress-zh_CN.mo
  #wget https://translate.wordpress.org/projects/wp-plugins/buddypress/stable/zh-cn/default/export-translations?format=po  -O /fs/web/p/buddypress-zh_CN.po
  # codex.buddypress.org/translations/ bp plugin auto update translation files
  #   at: wp-content/languages/plugins/buddypress-xx_XX.po/mo
  # Manual update bp Lang files. wp-admin upgrade?
  def Install_P_or_T_Lang(self, H=None, P_T='plugins', Slug='buddypress',
                          lang='zh', COUNTRY='CN'):
    if H is None:
      H = self.Hs0
    LangFile = '/'+ Slug +'-'+ lang.lower() +'_'+ COUNTRY.upper() +'.'
    #LangFile=/buddypress-zh_CN , P_T[:1] ==>> plugins -> p, themes -> t
    #          = /fs/web/l/p/buddypress-zh_CN.
    LocLangFile= cHL.WpLDir +P_T[:1]+ LangFile
    WLangFile  = H.WC.WLDir +P_T[:1]+ LangFile #/fs/web/l/p/buddypress-zh_CN.
    SLangFile  = H.WC.SLDir +P_T    + LangFile
    #          = /fs/www/wpy/wp-content/languages/plugins/buddypress-zh_CN.

    #From pyx.web.InstallCustomThemeLang():
    #H.WH.SftpSymLink(H.WC.WLPDir + 'ALL', H.WC.SLPDir.rstrip('/'))
    #H.WH.SftpSymLink(H.WC.WLTDir + AvDir, H.WC.SLTDir.rstrip('/'))
    #
    #Comment out below. See above pyx.web.InstallCustomThemeLang() SymLink
    ##for Dir in (H.WC.WLPDir, H.WC.WLTDir, H.WC.SLPDir, H.WC.SLTDir):
    #for  Dir in (H.WC.WLDir +P_T[:1], H.WC.SLDir +P_T):
    #  Wpy.Hs0.WC.WLDir = '/fs/web/l/'
    #  Wpy.Hs0.WC.SLDir = '/fs/www/wpy/wp-content/languages/'
    for  Dir in (H.WC.WLDir + P_T[:1], H.WC.SLDir +P_T):
      if not H.WH.SftpPathExist(Dir): #H.WC.SLDir +P_T SymLinked above
        L.info("Install_P_or_T_Lang try to H.WH.MkDir Dir= {}", Dir)
        H.WH.MkDir(Dir)
    if not hasattr(self, 'GotBpLangToLoc'):  #Already Got BpLang to Local
      self.GotBpLangToLoc = True
      for Format in ('mo','po',):
        BpLangUrl = WpC.TranslateUrl(P_T, Slug, lang, COUNTRY, Format)
        #-nc,--no-clobber: skip downloads if files already exist. no overwrite
        H.WH.Wget(BpLangUrl, LocLangFile + Format, NoClobber=False)
    for Format in ('mo','po',):
      H.WH.Rsync(LocLangFile + Format, WLangFile + Format)
      #ln -s to wp-content/languages/plugins/
      H.WH.SftpSymLink(WLangFile + Format, SLangFile + Format)


  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use SDB and WC0 in 1st Hs to Exec
  def WpSearchReplaceFQDN(self, OldFQDN=None, NewFQDN=None, SFQDN=None,
                          ExportF=True):
    SFQDN = SFQDN or self.SFQDN
    #OldFQDN = 'wordpress.org'  if OldFQDN is None else OldFQDN
    #NewFQDN = self.SFQDN if NewFQDN is None else NewFQDN # 'NewUrl.com'
    Tbs = self.SPfx + str(self.BId) + '_* '     #wp_6100_* get all blog tables
    Tbs+= " ".join([Tb for Tb in self.SDB.Tbs.TbsMS.values()])
    Path= self.WC0.SDir    # = self.WC0.WwwD + self.SName    # '/fs/www/wpy/'
    self.WpSearchReplace(OldFQDN, NewFQDN, SFQDN, User=None, Path=Path,
                         Tbs=Tbs, ExportF=ExportF)

  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use SDB in 1st Hs to Exec
  def WpSearchReplaceUrl(self, OldUrl=None, NewUrl=None, SFQDN=None,
                         ExportF=True):
    OldUrl = self.SUrl if OldUrl is None else OldUrl #http://wordpress.org/
    NewUrl = 'http://NewUrl.com/' if NewUrl is None else NewUrl
    SFQDN = self.SFQDN if SFQDN is None else SFQDN
    User  = self.SU.ULogin if User is None else User
    Tbs = self.SDB.Tbs.TbPfx +'* '     #wp_6100_* get all blog tables
    Tbs+= " ".join([Tb for Tb in self.SDB.Tbs.TbsMS.values()])
    self.WpSearchReplace(OldUrl, NewUrl, SFQDN, User=User, Path=None,
                         Tbs=Tbs, ExportF=ExportF)

  # wp-cli.org/commands/search-replace/
  # Set default ExportF=True, so won't accidentally change database!!
  # ExportF can be bool or str = Path of ExportF
  #
  # Don't use @AllHsDecorator to loop thro all Hs as all connect to same wp db
  # Good to use WH0, WC0, and SDB in 1st Hs to Exec
  def WpSearchReplace(self, OldStr, NewStr, SFQDN, User=None, Path=None,
                      Tbs=None, ExportF=True):
    Cmd= ("wp search-replace --path='{path}' {url} {user} '{Old}' '{New}' "
          " {Tbs} ").format(path= self.WC0.SDir if Path is None else Path,
          url = '' if SFQDN is None else "--url='{}'".format(SFQDN),
          user= '' if User  is None else "--user='{}'".format(User),
          Old = OldStr, New = NewStr, Tbs = Tbs )

    if ExportF is not None and ExportF is not False:
      if isinstance(ExportF, bool) and ExportF:
        ExportF = self.SDB.GetDumpFileName()
      elif not isinstance(ExportF, str):
        raise ValueError("ExportF must be str or bool")
      Cmd += " --export="+ ExportF
      self.WH0.MkDirForPath(ExportF, UidGid=wHo.UidGidWww)

    self.WH0.Exec(Cmd)


#End class SiteCls:



class BlogCls(SiteCls):
  ''' BlogCls inherit from SiteCls www.python-course.eu/python3_inheritance.php
  isinstance(Sj, Web.SiteCls) ==> Hs based on WB.SiteDbCls by default
  '''

  def __init__(self, BId=None, SId=None, Hosts=None, ConnSsh=False,
                     WebConf=False, AutoCommit=True, Exit=sys.exit):
    import wpy.user as WU
    # self.UId = Wj.CurrentUId = 0   #set in WU.MemberCls.__init__:
    if BId is None:
      if SId is None:
        raise ValueError("Both BId and SId are None!")
      else:
        self.SId = SId
        #Get BId of Main Site SId. if BId not in WpC.BlogOD, BId = SId*100
        self.BId = WpC.SiteBlogId(self.SId)
    else:
      self.BId   = BId
      if SId is None:
        self.SId = WpC.GetSIdByBId(BId)       #= WpC.BlogOD[BId][0]
      else:
        self.SId = SId

    L.info('BlogCls BId,SId,Hosts= {} {} {}', self.BId, self.SId, Hosts)
    if Hosts is None and self.SId == 1 and self.BId != 1:
      Hosts = ( (cHO.H000104,) if cDB.WpBlogOD[ self.BId ][1]==cDB.WDbC0001
                              else (cHO.H000002,) )
      L.info('BlogCls Hosts= {}', Hosts)

    SiteCls.__init__(self, self.SId, Hosts, ConnSsh, WebConf,
                     AutoCommit=AutoCommit, Exit=sys.exit, LoadSDB=False)

    if cDB.UseSqlAlchemy:
      import wpy.db_sa_cls as DbSa
      BlogDbCls = DbSa.SaBlogDbCls
    else:
      BlogDbCls = wDB.BlogDbCls
    self.BDB = BlogDbCls(self.BId, Bj=self, **self.SDB_KwArgs)
    L.info("BlogCls self.BId = {}, self.BDB={}", self.BId, self.BDB)

    if self.BId in WpC.BlogOD:
      V           = WpC.BlogOD[self.BId]
      self.SId    = V[0] if self.SId is None else self.SId
      self.BName  = V[1]  #BName=SubSite=Blog Name ,=None for main site
      self.BMapDoms=V[2]
      self.BUId   = V[3] if len(V) > 3 else self.SUId
      self.BU     = WU.AdminUserCls(self.BUId)      #Blog User  # SU vs BU
      # stackoverflow.com/questions/18072759/python-nested-list-comprehension
      self.BMapDomains= None if self.BMapDoms is None else [
                        D for Dom in self.BMapDoms
                        for D in wHo.GetAllRegistrarsDomains()[Dom] ]
      #BMapDoms= tuple of Doms. Below, Old: BMapDom = 1 Dom, not tuple of Doms
      #self.BMapDomains=None if self.BMapDom is None else (
      #                      wHo.GetAllRegistrarsDomains()[self.BMapDom] )

      #self.BSFQDN= self.SFQDN if (
      #             self.BName is None) else  self.BName+'.'+self.SFQDN
      #self.BSFQDN= BName+SName H.WH.SshHost: www.wordpy.com
      self.BSFQDN = self.BlogSiteFQDN( self.BName )
      self.BSUrl= 'http://'+ self.BSFQDN +'/'    #= http://www.wordpy.com/
      #    BFQDN= Blog H.WH.SshHost: wordpy.com
      self.BFQDN= self.BSFQDN if (self.BMapDoms is None or
                                  self.BName is None ) else self.BMapDomains[0]
      self.BUrl = 'http://'+ self.BFQDN +'/' #Blog URL = php site_url()

    ''' Update Hs for Blog, or DbName will be wrong!!!
    ### Change WBlog.BDb -> WBlog.WDB0 in SecFilings.py NewsGet.py WpPost.py
    ### Don't Keep self.Hs[Host].WDB the same for Site! Blog has diff BDb!
    if self.BId in cDB.WpBlogOD:
      for Host, HConfDb in self.Hs.items():
        L.info('BlogDbCls update H.WDB')
        HConfDb.WDB = BlogDbCls(self.BId, DbHost=None, ConnSsh=ConnSsh)
      self.WDB0  = self.Hs[self.Host0].WDB    #=1st WDB= WB.SiteDbCls()

    if self.BId in cDB.WpBlogOD:
      self.BDb  = BlogDbCls(self.BId, DbHost=None, ConnSsh=ConnSsh)
    #else: default to db config set in WB.SiteDbCls
    '''

    self.XmlCli = {
      'url'        : self.BUrl + 'xmlrpc.php',
      'username'   : self.BU.ULogin,
      'password'   : self.BU.UPass,
      'blog_id'    : self.BId,
    }



class WpCls(WiL.WiLoad):  # = WB.Wj
  ''' class WpCls(WiL.WiLoad(WpC.WpConfCls)):
  Bj = Web.BlogCls() = obj of BName=Blog name. avoid conflict. SName=Site Name
      WpConfCls= BlogConfCls, Blog ==> wp-cli --url=. Site ==> physical setup.
  Each time when a WordPress blog is visited, the following are executed.
  This class virtualizes these steps so multiple instances of the class with
  different BId or SId (blog id or site id = network id) can be instantiated
  during a single runtime. While WordPress have different php runtime for
  different web host, db host, BId or SId.
  All Wj php global vars are translated to self.vars
  '''
  def __init__(self, Bj=None, BId=0, AutoCommit=True):
    if Bj:
      if isinstance(Bj, BlogCls):
        self.Bj = Bj
      else:
        raise AttributeError("Bj NOT instance of BlogCls or SiteCls")
    elif isinstance(BId, int) and BId > 0:
      self.Bj = Bj = BlogCls(BId, AutoCommit=AutoCommit)
    #elif isinstance(getattr(self, 'Bj', None), BlogCls):
    #  Bj = self.Bj
    else:
      raise AttributeError("Bj and BId are both BAD!")

    self.AutoCommit = AutoCommit
    self.BId    = Bj.BId
    self.Exit   = Bj.Exit # can be print, sys.exit,or ShutdownExit
    self.WH0    = Bj.WH0
    self.GDB    = WB.GDB if cDB.Use_WB_GDB else Bj.GDB
    if getattr(  Bj, 'SDB', None):
      self.SDB    = Bj.SDB
      self.SDB.DbConnViaSshTun()
    if getattr(  Bj, 'BDB', None):
      self.BDB  = Bj.BDB
      self.BDB.DbConnViaSshTun()
    if getattr(  Bj, 'WC0', None):
      self.WC0  = Bj.WC0
    #if XCli is not None:
    #  XCli.Bj   = Bj
    #  XCli.XmlCli = Bj.XmlCli
    #  XCli.Exit   = Bj.Exit
    #  if hasattr(self, 'XmlMethods'):
    #    XCli.XmlMethods += self.XmlMethods
    #    # XCli.XmlMethods = list(set(XCli.XmlMethods)) #unique

    #self.Const= xTp.ConstSingletonCls()  #Can't use it or new BId will error
    self.Const = xTp.ConstCls()
    self.Const.WPfx = WpC.WPfx
    self.wp_index()
    " wp_index() loads wp_settings(), ..., self.wp_rewrite = WcR.WP_Rewrite() "
    self.init_wpdb()
    import wp.term       as WpT
    WpT.InitTermGlobals(self)
    self.XmlRpcUser = False
    self.XmlRpcTerm = False
    self.XmlRpcPost = False


  def init_wpdb(self):
    # From /fs/web/p/ludicrousdb/ludicrousdb.php
    # Plugin Name: LudicrousDB
    # Plugin URI:  https://wordpress.org/plugins/ludicrousdb/  <<BAD!!
    # Author:      John James Jacoby
    # Author URI:  https://jjj.blog/
    # License URI: https://www.gnu.org/licenses/gpl-2.0.html
    # Text Domain: ludicrousdb
    # Description: An advanced database interface for WordPress that supports
    #              replication, fail-over, load balancing, and partitioning

    # Bail if database object is already set
    #if isset( $GLOBALS['wpdb'] ):
    if getattr(self, 'wpdb', None):
      return

    import wp.i.wpdb   as WpDb
    WpDb.InitWpdbGlobals(self)

    # Required files
    #import wp.p.ldb.functions          as LDbFunc
    #import wp.p.ldb.class_ludicrousdb  as LDb
    import  plugins.ldb                 as LDb
    #LDb.InitLDbGlobals(self)
    # Set default constants
    #LDbFunc.ldb_default_constants(self)
    self.define( 'DB_CONFIG_FILE', 'db_config' )

    Bj = self.Bj
    # Create database object
    # Moved from wp.i.load.require_wp_db():
    #self.wpdb = WpDb.wpdb_cls( self.DB_USER, self.DB_PASSWORD,
    #                           self.DB_NAME, self.DB_HOST )
    #self.wpdb = WpDb.WpDbSingletonCls(Bj.BDB.DbUser, Bj.BDB.DbPass,
    #           Bj.BDB.DbName, Bj.BDB.DbHost +':'+ str(Bj.BDB.DbPort), Wj=self)
    #self.wpdb= wpdb = LDb.LDbSingletonCls(Bj.BDB.DbUser, Bj.BDB.DbPass,

    self.wpdb = wpdb = LDb.LudicrousDBCls( Bj.BDB.DbUser, Bj.BDB.DbPass,
                Bj.BDB.DbName, Bj.BDB.DbHost +':'+ str(Bj.BDB.DbPort), Wj=self)
    self.wpdb.GDB = self.GDB
    self.wpdb.BDB = self.BDB

    #self.wBDB = self.wpdb

    #self.wGDB = WpDb.WpDbSingletonCls(Bj.GDB.DbUser, Bj.GDB.DbPass,
    #           Bj.GDB.DbName, Bj.GDB.DbHost +':'+ str(Bj.GDB.DbPort), Wj=self)
    #self.wGDB = LDb.LDbSingletonCls(Bj.GDB.DbUser, Bj.GDB.DbPass,
    #           Bj.GDB.DbName, Bj.GDB.DbHost +':'+ str(Bj.GDB.DbPort), Wj=self)

    # Include LudicrousDB config file if found or set
    if self.defined('DB_CONFIG_FILE'): #and file_exists(self.DB_CONFIG_FILE):
      #same as# import wpy.db_conf as DbConf
      #DbConf = __import__( 'wp.'+ self.DB_CONFIG_FILE )  #doesn't work
      import importlib
      DbConf = importlib.import_module('wp.'+ self.DB_CONFIG_FILE)
      DbConf.db_config(self)
      #L.info("\nLDb.add_database self.LDbServers= {}\n", wpdb.LDbServers)


    # /fs/web/wp/wp-includes/ms-settings.php
    wpdb.set_blog_id(Bj.BId, Bj.SId )
    #self.wGDB.set_blog_id(Bj.BId, Bj.SId )
    # /fs/web/wp/wp-includes/load.php: wp_set_wpdb_vars()
    wpdb.set_prefix( Bj.SPfx )
    #self.wGDB.set_prefix( Bj.SPfx )



WpC.WB = WB = xWB.WpBlogCls(AutoCommit = cDB.AutoCommit)
# Bj should access via WpC.WB.Bj, instead of WpC.Bj
# Wj should access via WpC.WB.Wj, instead of WpC.Wj
# init WpC.Bj and WpC.Wj above when xWB.WpBlogCls.InitBlog(BId) is called
#WpC.Bj = Bj = WB.Bj   # cannot, WB.Bj is still = None at this point
#WpC.Wj = Wj = WB.Wj   # cannot, WB.Wj is still = None at this point

''' usage:
from wp.conf import Wj
array = Php.array
import pyx.php      as Php
import wp.conf      as WpC
array, Wj = Php.array, WpC.Wj
'''

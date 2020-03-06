#!/usr/bin/python3
from collections import OrderedDict as ODict
import wpy.host  as HO
cHL, cHO, xHL, xHR = HO.cHL, HO.cHO, HO.xHL, HO.xHR
'''- cHL contains os or sys var constanst for host_loc = localhost.
   - cHO contains os or sys var constants for hosts.
   - xHL contains os or sys functions & vars for host_loc = localhost.
   - xHR contains os or sys functions & vars for host_rem = remote host. '''

H000002, H000104 = cHO.H000002, cHO.H000104
WPfx = 'wp_'   # = wp prefix for ALL WordPy sites
# WPfx can be changed, but Constant C.WPfx cannot be changed


if 'WB' not in globals():
  WB = None
# init Bj and Wj above when Web.WpBlogCls.InitBlog(BId) is called
#if 'Bj' not in globals():  #Disable it
#  Bj = None                #Bj should access via WpC.WB.Bj, instead of WpC.Bj
#if 'Wj' not in globals():  #Disable it
#  Wj = None                #Wj should access via WpC.WB.Wj, instead of WpC.Wj
##In wpy.web:
#WpC.WB = WpBlogCls()
#class WpBlogCls(metaclass=xType.SingletonMetaClass):
#  def __init__(self):


class WpConfCls:
  ''' WpConfCls= BlogConfCls, Blog ==> wp-cli --url=. Site ==> physical setup.
  Each time when a WordPress blog is visited, the following are executed.
  This class virtualizes these steps so multiple instances of the class with
  different BId or SId (blog id or site id = network id) can be instantiated
  during a single runtime. While WordPress have different php runtime for
  different web host, db host, BId or SId.
  All WP php global vars are translated to self.vars
  '''
  # WordPress Database Table prefix.
  # You can have multiple installations in one database if you give each
  # a unique prefix. Only numbers, letters, and underscores please!
  table_prefix = WPfx = WPfx   #= 'wp_' = wp prefix for ALL WordPy sites

  #def __init__(self):
  #  pass #self.wp_index()

  def wp_index(self):
    " wp-index.php "
    self.WP_USE_THEMES = True
    # Loads the WordPress Environment and Template
    #require( dirname( __FILE__ ) . '/wp-blog-header.php' )  #Below
    self.wp_blog_header()

  def wp_blog_header(self):
    " wp-blog-header.php "
    if not hasattr(self, 'wp_did_header'):  # not in globals():
      self.wp_did_header = True
      # Load the WordPress library
      #require_once( dirname(__FILE__) . '/wp-load.php' )  #Below
      self.wp_load()
      # Set up the WordPress query
      "wp()"
      #require_once( ABSPATH . WPINC . '/template-loader.php' )

  def wp_load(self):
    " wp-load.php "
    # Define ABSPATH as this file's directory
    if not self.defined('ABSPATH'):   # not in globals():
    	#define( 'ABSPATH', dirname( __FILE__ ) . '/' );
      #import sys, os # Current_Dir of Current_Py_Script
      #self.ABSPATH = os.path.dirname(os.path.realpath( sys.argv[0] )) + '/'
    	self.define( 'ABSPATH', '/fs/py/web/wp/' )
    #sys.path.append(self.ABSPATH)
    #require_once( ABSPATH . 'wp-config.php' )  #below
    self.wp_config()

  def wp_config(self):
    ''' wp-config.php
    base configuration for WordPress contains the following configurations:
    MySQL settings, Secret keys, db table prefix ABSPATH
    https://codex.wordpress.org/Editing_wp-config.php
    '''
    self.DB_NAME    = 'wpdb_name'     #override by db.php
    self.DB_USER    = 'wpdb_user'     #override by db.php
    self.DB_PASSWORD= 'wpdb_pass'     #override by db.php
    self.DB_HOST    = 'wdb1'          #override by db.php
    self.DB_CHARSET = 'utf8mb4'
    # core.trac.wordpress.org/ticket/32308
    # wordpress.org/support/topic/tables-not-created-error-establishing-a-database-connection
    self.DB_COLLATE = 'utf8mb4_unicode_ci'

    ''' Authentication Unique Keys and Salts.
     * generate these using {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
     * Can change these any time to invalidate all existing cookies and force all users to re-login
    self.AUTH_KEY =
    self.SECURE_AUTH_KEY =
    self.LOGGED_IN_KEY =
    self.NONCE_KEY =
    self.AUTH_SALT =
    self.SECURE_AUTH_SALT =
    self.LOGGED_IN_SALT =
    self.NONCE_SALT =
    '''

    #digitalocean.com/community/tutorials/how-to-configure-redis-caching-to-speed-up-wordpress-on-ubuntu-14-04
    #self.NONCE_SALT =  'put your unique phrase here'
    #github.com/ericmann/Redis-Object-Cache
    #  add a prefix to all cache keys used by the plugin. If running two single instances of WordPress from the same Redis instance, this constant could be used to avoid overlap in cache keys
    #wordpress.org/support/topic/many-wp-installations-on-the-same-server
    #  To use it on many sites where the table prefixes are the same, you can add:
    # self.WP_CACHE_KEY_SALT = 'MG?&DIJ_s5Dr=U+s@v=zu|6$]@%J%(nTY87H9M6o+MhFNnbOe&C-eI>einT1@R'
    # codex.wordpress.org/Class_Reference/WP_Object_Cache + persistent cache redis!
    # wp slow since add_option INSERT INTO wp_options option_name=_transient_..
    # self.WP_CACHE = True

    # blogvault.net/wordpress-security-1-securing-wp-config-php/
    #self.DISALLOW_FILE_EDIT = True
    #self.DISALLOW_FILE_MODS = True

    ''' codex.wordpress.org/Debugging_in_WordPress
    if ('on' == getattr(_COOKIE, 'wpy_debug', None) or
        'www.wordpy.com' == getattr(_SERVER, 'SERVER_NAME'], None)):
    if (_SERVER['REMOTE_ADDR'] in ('24.6.157.181', '40.118.129.113', '40.83.127.15', '40.118.242.112', '73.164.63.139', '66.35.125.175', '173.48.112.24', '104.42.229.71', '1.36.158.178',)):
    	self.WP_DEBUG = True
    	# Enable Debug logging to the /wp-content/debug.log file
    	self.WP_DEBUG_LOG = True
    	# wordpress.stackexchange.com/questions/34482/preferred-method-of-debugging-a-wordpress-sql-calls
    	self.SAVEQUERIES = True

    	# Disable display of errors and warnings
    	self.WP_DEBUG_DISPLAY = True
    	@ini_set('display_errors',0

    	# Use dev ver of core JS & CSS files (needed if modifying core files)
    	#self.SCRIPT_DEBUG = True
    else:
    '''
    self.WP_DEBUG = False

    # wp/plugins/wordpress-mu-domain-mapping/installation/  Do not define COOKIE_DOMAIN in as it conflicts with logins on your mapped domains
    # www.remicorson.com/share-users-database-on-different-wordpress-installs/
    #self.COOKIE_DOMAIN = '.wordpy.com' #same cookies para for all websites
    #self.COOKIEPATH = '/'
    #self.ADMIN_COOKIE_PATH = '/'
    #self.CUSTOM_USER_TABLE = 'wp_users'
    #self.CUSTOM_USERMETA_TABLE = 'wp_usermeta'

    #self.WPLANG = 'zh_CN')
    #self.WP_LANG_DIR = dirname(__FILE__) . '/wp/wp-content/languages'
    # WordPress v4 and above: Change the language in the admin settings screen. Settings > general > Site Language.

    # wordpress.org/support/topic/add-media-button-doesnt-work-1
    #self.CONCATENATE_SCRIPTS = False

    # www.wpbeginner.com/wp-tutorials/fix-wordpress-memory-exhausted-error-increase-php-memory/
    "self.WP_MEMORY_LIMIT = '512M'"

    # wordpress.org/support/topic/problems-with-scheduler
    # self.ALTERNATE_WP_CRON = True
    # www.wprssaggregator.com/docs/cron-intervals/
    # www.remicorson.com/too-many-wc_sessions-in-woocommerce/
    "self.DISABLE_WP_CRON = True"

    # code.tutsplus.com/tutorials/best-practices-for-preventing-buddypress-spam-user-registrations--wp-25026
    self.BP_REGISTER_SLUG = 'new-acct'  #Defined in Page /new-acct

    # Comment out BP_ROOT_BLOG so subtdomain bp page www.wordpy.com/m/ won't
    #    assocciate to root blog page wordpy.com/m/
    # self.BP_ROOT_BLOG = 1

    # buddypress.org/2009/05/customizable-slugs-in-buddypress/
    #BP_ACTIVITY_SLUG = 'streams'
    #BP_BLOGS_SLUG = 'journals'
    self.BP_MEMBERS_SLUG = 'm'        # users
    #BP_FRIENDS_SLUG = 'peeps'
    self.BP_GROUPS_SLUG =  'g'    #gatherings
    #self.BP_MESSAGES_SLUG = 'notes'
    #self.BP_WIRE_SLUG = 'pinboard'
    #self.BP_XPROFILE_SLUG = 'info'
    # Some other non-component slugs
    #self.BP_REGISTER_SLUG = 'signup'
    #self.BP_ACTIVATION_SLUG = 'enable'
    #self.BP_SEARCH_SLUG = 'find'
    #self.BP_HOME_BLOG_SLUG = 'news'

    # codex.wordpress.org/Editing_wp-config.php#Moving_uploads_folder
    self.UPLOADS = 'doc'
    # wordpress.org/support/topic/how-to-stop-auto-save-draft
    "self.WP_POST_REVISIONS = False    # wp-includes/revision.php"
    "self.AUTOSAVE_INTERVAL = 259200   # in sec- pretty much disable autosave"

    # codex.buddypress.org/getting-started/customizing/bp_enable_multiblog/
    # True so bp content will display on any site in wp Multisite network
    self.BP_ENABLE_MULTIBLOG = True

    # wordpress.org/support/topic/domain-redirection-keeps-forwarding-to-signup-page
    #self.NOBLOGREDIRECT = 'http://wordpy.com/'
    # wordpress.org/support/topic/sub-domain-redirecting-to-wp-signupphp
    "self.NOBLOGREDIRECT = ''"

    # wordpress.stackexchange.com/questions/165507/site-redirecting-to-wp-signup-php
    # wpengine.com/support/how-to-change-a-multi-site-primary-domain/
    self.WP_HOME =    'http://wordpy.com/'
    self.WP_SITEURL = 'http://wordpy.com/'

    # jeffsebring.com/2010/fixing-broken-permalinks-when-moving-wordpress/
    # self.RELOCATE',True
    # Log back to admin account, go to Settings > Permalinks. Click save button

    # remove the earlier added WP_ALLOW_MULTISITE = True
    # self.WP_ALLOW_MULTISITE = True
    self.MULTISITE = True
    self.SUBDOMAIN_INSTALL = True
    #wordpress.org/support/topic/multiple-domains-with-multisite-and-root-domain-not-in-wordpress
    self.DOMAIN_CURRENT_SITE = 'wordpy.com'   # _SERVER['HTTP_HOST']
    # wordpress.org/plugins/wp-multi-network/installation/ to comment out:
    #self.DOMAIN_CURRENT_SITE = 'wordpy.com'
    self.PATH_CURRENT_SITE = '/'
    self.SITE_ID_CURRENT_SITE = 1
    self.BLOG_ID_CURRENT_SITE = 1

    '''  Already set above
    # Absolute path to the WordPress directory.
    if not self.defined('ABSPATH'):   # not in globals():
    	#self.define( 'ABSPATH', dirname( __FILE__ ) . '/' );
      #import sys, os # Current_Dir of Current_Py_Script
      #self.ABSPATH = os.path.dirname(os.path.realpath( sys.argv[0] )) + '/'
    	self.define( 'ABSPATH', '/fs/py/web/wp/' )
    '''

    # wordpress.org/plugins/wordpress-mu-domain-mapping/installation/
    self.SUNRISE = 'on'

    # Sets up WordPress vars and included files.
    #import wp.settings    # wp-settings.php
    self.wp_settings()

  def defined(self, Name):
    return hasattr(self, Name)

  def define(self, Name, Value):
    setattr(self, Name, Value)



BlogConfCls = WpConfCls


'''
[Difference between blog id and site id?](http://wordpress.stackexchange.com/questions/5594/what-is-difference-between-blog-id-and-site-id)
*  site_id = the ID of the parent site (the domain, eg. wordpress.com)
*  blog_id = the ID of the parent site's blog(s) (usually sub-domains, eg mary.wordress.com)

In a Multisite install, you can have a several blogs (identified in the database model by blog_id) within one site (identified in the database model by site_id).

Confusing that most of WordPress code and doc use a terminology that differs from the database model. They refer to a blog using the word site, and to a site using the word network.

[Changing The Site URL « WordPress Codex](http://codex.wordpress.org/Changing_The_Site_URL) refers to the Site URL (as defined in the WP_SITEURL constant), which really is the URL of the blog URL in multisite context.
'''

#def SiteOD():
#  #global WPfx
#  #if 'WpObj' in globals() and hasattr(WpObj, 'WPfx'):  #Bj.WpObj => WpConfCls()
#  #  WPfx = WpObj.WPfx
#  return ODict([   #site_id = the network of Sites or BlogOD

# Each site has a unique SPfx=Prefix in wp-config.php !!
#SName must be ??? = 3 chars. apache2.conf uses <Directory /fs/web/???/>
SiteOD = ODict([   #site_id = the network of Sites or BlogOD
  #SId,SName,SPath,Hosts(www),SPfx:Default=wp_,SU.Id,SU.UPass
  ( 1,('wpy','/',(H000002,H000104,),WPfx,1001,)),#wordpy.com
  (20,('wdp','/',(H000002,        ),WPfx,1001,)),#wordpress.com
])


#wp> get_blog_details( array( 'blog_id' => 2 ))

BlogOD = ODict([    # blog_id = the sites (formerly known as blogs)
  # BId, SId, BName=SubSite,BMapDoms,      BU.Id,BU.UPass
  (   1, ( 1, None        , ('enw',),1001,)),#wpy#BTitle='WordPy' =BName
  (   2, ( 1, 'shop'      , None    ,)),  # wpy  #BTitle='Online Shop'
  (2000, (20, None        , None    ,)),  # wdp = wordpress.com
])

CnSites = ()
def IsCnSite(SId):
  return SId in CnSites

CnBlogs = ()
def IsCnBlog(BId):
  return BId in CnBlogs


BlogTitleOD = ODict([
  # BId,BLogoTxt=Logo Txt, BTitle= Title, BDesc= Blog Description
  (   1, ('WordPy'        ,'WordPy - WordPress in Python',
          'Pythonic ObjO way to admin WordPress content without PHP. Auto '
          'manage remote WP Web & MySql clusters in Hybrid Cloud via SSH.',)),
  (2000, ('WP'            ,'WordPress'      ,'WordPress Innovation'       ,)),
])


'''
[Is there a benefit to defining a class inside another class in Python?](http://stackoverflow.com/questions/78799/)
Nested class inside class:
(1) "inner" class is a one-off, which will never be used outside the definition of the outer class.
(2) use the outer class only as a namespace to group a bunch of closely related classes together.
(2a) Better served using module or package, which is designed to be namespaced
'''
# Comment out class Wp to use this file as module instead!
# class Wp:                   # WordPress config

PluginsSvnUrl = 'http://plugins.svn.wordpress.org/{}/trunk/'
TranslatePluginsUrl = ('https://translate.wordpress.org/projects/wp-plugins'
            '/buddypress/stable/zh-cn/default/export-translations?format=mo')
ThemesSvnUrl = 'http://themes.svn.wordpress.org/'


class SiteConfCls:    # WC.SDir= /web/+ self.SName
  " vs BlogConfCls = WpConfCls "

  def __init__(self, obj, WH):
    self.LocDir= cHL.WebHDir + WH.Host +'/' #=/fs/py/web/host/web2/

    #if WH.DcNum in cHO.PubDCs:
    if  WH.Host  in cHO.WebHs_WpPub:
      self.DataCenter= True
      self.FS   = '/fs/'  # Take advantage of free Local SSD Storage
    else:
      self.DataCenter= False
      self.FS   = '/fs/'
    self.LocSiteDir = self.LocDir +'www/'+ obj.SName +'/'
    #               = /fs/py/web/host/web2/www/wpy/
    self.LogD   = self.FS +'log/www/'+ obj.SName+'/'#/fs/log/www/wpy/
    self.LogDebug = self.LogD+'debug.log'         #/fs/log/www/wpy/debug.log
    self.WebD   = self.FS   + 'web/' #Remote web dir #ln -s /fs/web /fs/web
    self.WWwDir = self.WebD + 'www/' #/fs/web/www: store common SDir files
    #self.WWpDir= self.WebD + 'wp/'  #wordpress latest svn trunk. vs WC.SDir
    self.WPDir  = self.WebD + 'p/'   #svn  Plugins   to /fs/web/p/
    self.WTDir  = self.WebD + 't/'   #svn  Themes    to /fs/web/t/
    self.WLDir  = self.WebD + 'l/'   #Rsync languages/ to /fs/web/l/
    self.WLPDir = self.WLDir+ 'p/'   #Rsync languages/plugins/->/fs/web/l/p/
    self.WLTDir = self.WLDir+ 't/'   #Rsync languages/themes/ ->/fs/web/l/t/

    self.WDDir  = self.WebD + 'doc/'  #/fs/web/doc: store common doc files
    self.WDImg  = self.WDDir+ 'img/'           #/fs/web/doc/img/
    self.WDImgS = self.WDImg+ obj.SName    +'/' #/fs/web/doc/img/wpy/
    self.WDImgSB= self.WDImgS+str(obj.BId)+'/' #/fs/web/doc/img/wpy/4/
    self.WDAvt  = self.WDDir+ 'avatars/'       #/fs/web/doc/avatars/
    self.WDGrAvt= self.WDDir+ 'group-avatars/' #/fs/web/doc/group-avatars/
    self.WDBp   = self.WDDir+ 'buddypress/'    #/fs/web/doc/buddypress/
    self.WDSite = self.WDDir+ 'sites/'         #/fs/web/doc/sites/
    self.WDSBId = self.WDSite+str(obj.BId)+'/' #/fs/web/doc/sites/1/
    self.WDSBIdImg=self.WDSBId+'img/'           #./doc/sites/1/img/
    self.WDSBIdAvt=self.WDSBId+'avatars/'       #./doc/sites/1/avatars/
    self.WDSBIdGrA=self.WDSBId+'group-avatars/' #./doc/sites/1/group-avatars/
    self.WDSBIdBpA=self.WDSBId+'bp-attachments/'#./doc/sites/1/bp-attachments/

    self.WwwD   = self.FS   + 'www/'  #Contains all /fs/www/??? Site=DocRoots
    self.SDir   = self.WwwD + obj.SName+'/' #/fs/www/wpy/=DocRoot= Deploy Site
    self.SCDir  = self.SDir + 'wp-content/'#/fs/www/wpy/wp-content/=S Content
    self.SPDir  = self.SCDir+ 'plugins/'   #/fs/www/wpy/wp-content/plugins/
    self.STDir  = self.SCDir+ 'themes/'    #/fs/www/wpy/wp-content/themes/
    self.SLDir  = self.SCDir+ 'languages/' #/fs/www/wpy/wp-content/languages/
    self.SLPDir = self.SLDir+ 'plugins/'   #wp-content/languages/plugins/
    self.SLTDir = self.SLDir+ 'themes/'    #wp-content/languages/themes/

    self.SDDir  = self.SDir + 'doc/'      #/fs/www/wpy/doc/ =upload #Site Doc
    self.SDImg  = self.SDDir+ 'img/'      #/fs/www/wpy/doc/img/
    self.SDAvt  = self.SDDir+ 'avatars/'       #/fs/www/wpy/doc/avatars/
    self.SDGrAvt= self.SDDir+ 'group-avatars/' #/fs/www/wpy/doc/group-avatars/
    self.SDBp   = self.SDDir+ 'buddypress/'    #/fs/www/wpy/doc/buddypress/
    self.SDBpAtt= self.SDDir+ 'bp-attachments/'#/fs/www/wpy/doc/bp-attachments/
    self.SDSite = self.SDDir+ 'sites/'         #/fs/www/wpy/doc/sites/
    #self.SDSBId: Never Used!  #/fs/www/wpy/doc/sites/1/ = /fs/www/wpy/doc/
    #self.SDSBId= self.SDSite+str(obj.BId)+'/' #/fs/www/wpy/doc/sites/1/
    #self.SDSBIdA=self.SDSBIdA+'bp-attachments/'#./doc/sites/1/bp-attachments/

    self.Plugins= SitePluginD[obj.SId]
    self.Themes = SiteThemeD[obj.SId]
    BT           = BlogTitleOD[obj.BId]
    self.BLogoTxt= BT[0]
    self.BTitle  = BT[0] if BT[1] is None else BT[1]
    self.BDesc   = BT[2]

    self.HasBp  = True if 'bp' in SitePluginD[obj.SId].keys() else False
    self.SitesAv= { SId:V[0] for SId,V in SiteOD.items()
                    if WH.Host in V[2] }


# TranslateUrl = 'wget https://translate.wordpress.org/projects/?format=mo'
def TranslateUrl(P_T, Slug, lang, COUNTRY, Format):
  if P_T not in ('plugins', 'themes',):
    print("Error! P_T not in ('plugins', 'themes',)")
    return False
  if lang not in ('zh',) or COUNTRY not in ('CN',):
    print("Error! lang not in ('zh',) or COUNTRY not in ('CN',)")
    return False
  if Format not in ('mo', 'po',):
    print("Error! False not in ('mo', 'po',)")
    return False
  return ('https://translate.wordpress.org/projects/wp-{}/{}/stable/{}-{}/'
          'default/export-translations?format={}').format(
          P_T, Slug, lang.lower(), COUNTRY.lower(), Format)
# https://translate.wordpress.org/projects/wp-themes/twentysixteen

# generate wp-config.php authentication Unique Keys and Salts
def ConfigGenSalts():    # using WordPress.org secret-key service
  import requests
  Url = "https://api.wordpress.org/secret-key/1.1/salt/"
  return requests.get(Url).text
  #import crypt
  #crypt.mksalt(crypt.METHOD_SHA512)


#[Get version number of latest Wordpress release](http://wordpress.stackexchange.com/questions/176870/)
#rawjson = urllib2.urlopen(Url).read()
#version = json.loads(rawjson)
#print(version["offers"][0]["version"])
def LatestVer():  #=4.5.2
  import requests, json
  Url = "https://api.wordpress.org/core/version-check/1.7/"
  r  = requests.get(Url)
  rj = r.json()
  return rj['offers'][0]['version']

def LatestUrl():  #=4.5.2
  return 'https://core.svn.wordpress.org/tags/'+ LatestVer()
# git://github.com/WordPress/WordPress.git
# git://develop.git.wordpress.org/


def AllSites():
  return tuple([V[0] for V in SiteOD.values()])

#   AllSitesInWDir(Path=D.WC0.WebD, ListDir=D.WH0.Sftp.listdir)
def AllSitesInWDir(Path, ListDir=None):
  if ListDir is None:
    import os
    ListDir = os.listdir
  # print([Dir for Dir in D.USftp.listdir(path)])
  return tuple([Dir for Dir in ListDir(path=Path) if Dir in AllSites()])


def GetSNameBySId(SId):
  return SiteOD[SId][0]

def SiteFQDNsInSId(SId):  # AllFQDNs = SiteFQDNs + BlogFQDNsInSId
  SName = GetSNameBySId(SId)
  return HO.GetAllRegistrarsDomains()[SName]

def BlogFQDNsInSId(SId, AddFQDNs=[]):  # [] = empty tuple
  AllBlogFQDNs = list(AddFQDNs) if isinstance(AddFQDNs, (list,tuple)) else []
  # print('Add to AllBlogFQDNs: ', AllBlogFQDNs)
  for BId,V in BlogOD.items():
    if V[0] == SId:
      AllBlogFQDNs += BlogFQDNsInBId(BId, SId)
      # BName, BMapDoms = V[1], V[2]
      # #print(BId, BMapDoms, BName)
      # try:    FirstSiteFQDNsInSId = SiteFQDNsInSId(SId)[0]
      # except: print('  Error getting SiteFQDNsInSId(SId)[0]!  SId=', SId)
      # else:   AllBlogFQDNs.append( ((BName +'.') if BName else '') +
      #                            FirstSiteFQDNsInSId )
      # if BMapDoms is not None:
      #   #try: AllBlogFQDNs += HO.GetAllRegistrarsDomains()[BMapDoms]
      #   try:    BFQDNs = [ D for Dom in BMapDoms for D in FqdnAll[Dom] ]
      #   except: print('  Error adding to BFQDNs!  BMapDoms=', BMapDoms)
      #   else:   AllBlogFQDNs += BFQDNs
  return AllBlogFQDNs  # list of FQDNs


def BlogFQDNsInBId(BId, SId=None):
  if SId is None:
    SId = GetSIdByBId(BId)
  FqdnAll = HO.GetAllRegistrarsDomains()
  V = BlogOD[BId]
  BName, BMapDoms = V[1], V[2]
  BlogFQDNs = []
  #print(BId, BMapDoms, BName)
  try:    FirstSiteFQDNsInSId = SiteFQDNsInSId(SId)[0]
  except: print('  Error getting SiteFQDNsInSId(SId)[0]!  SId=', SId)
  else:   BlogFQDNs.append( ((BName +'.') if BName else '') +
                             FirstSiteFQDNsInSId )
  if BMapDoms is not None:
    #try: BlogFQDNs += HO.GetAllRegistrarsDomains()[BMapDoms]
    try:    BFQDNs = [ D for Dom in BMapDoms for D in FqdnAll[Dom] ]
    except: print('  Error adding to BFQDNs!  BMapDoms=', BMapDoms)
    else:   BlogFQDNs += BFQDNs

  return BlogFQDNs  # list of FQDNs


def GetBIdByFQDN(FQDN):
  for BId in BlogOD:
    if FQDN in BlogFQDNsInBId(BId):
      return BId

def AllFQDNsInSId(SId): # AllFQDNs = SiteFQDNs + BlogFQDNsInSId
  SiteFQDNs = SiteFQDNsInSId(SId)
  return BlogFQDNsInSId(SId, SiteFQDNs)

def AllBIdsInSId(SId):
  return [ BId for BId,V in BlogOD.items() if V[0]==SId ]

def GoDaddyDomainsInSId(SId):
  SName = GetSNameBySId(SId)
  return cHO.GoDaddyDomains[SName]

def AllGoDaddyDomainsInSId(SId):
  GoDaddyDomains = GoDaddyDomainsInSId(SId)
  return BlogFQDNsInSId(SId, GoDaddyDomains)

def AllHostsInSId(SId):
  return SiteOD[SId][2]

def GetSIdByBId(BId):
  " Return Site Id SId of Blog BId "
  return BlogOD[BId][0]  #=SId

def GetSiteByBId(BId):
  " Return Site Id SId of Blog BId "
  return GetSNameBySId( GetSIdByBId(BId) )

def FirstServer(SId):
  ''' Return First=Main WServer=Servers[0] of current Site with Lowest SId Site
      example return:  (1, 'wpy', 'wordpy.com') '''
  SHost = SiteOD[SId][2][0]
  for Id,V in SiteOD.items():
    if Id > 0 and SiteOD[Id][2][0] == SHost:
      return Id, V[0], HO.GetAllRegistrarsDomains()[V[0]][0]

def Servers(SId):
  Servers = []
  for SHost in SiteOD[SId][2]:
    for Id,V in SiteOD.items():
      if Id > 0 and SiteOD[Id][2][0] == SHost:
        Servers.append((Id, V[0], HO.GetAllRegistrarsDomains()[V[0]][0]))
  return Servers #= [(1,'wpy','wordpy.com'), ...)]


def SiteBlogId(SId):
  " Return Blog Id BId of Main Site SId = Lowest BlogId of Site "
  for BId,V in BlogOD.items():
    if BId > 0 and V[0] == SId:
      return BId
  return SId * 100   #If BId not listed in BlogOD, BId = SId * 100


PluginOD = ODict([  #PSrc= Plugin Source: svn, git, loc=local, cbx=cbox
  #Plugin, Depend , Theme Use ,PSrc ,PSlug, PSrcPath
  ('akis', (None  ,(         ),'svn','akismet',)),
  ('bbp' , (None  ,('av','cb'),'svn','bbpress',)),
  ('bbpcn',(None  ,(         ),'zip','bbpress-cn','http://bbpress.me/wp-content/uploads/2017/02/bbpress.2.5.12-zh_CN.zip')),
  ('bpga', ('bp'  ,('cb',    ),'cbx','bp-group-announcements',)), # Inlucded in: commons-in-a-box/includes/bp-group-announcements-1.0.5.zip
  ('bpgh', ('bp'  ,(         ),'git','bp-group-hierarchy', 'https://github.com/r-a-y/BP-Group-Hierarchy')),
  ('bp'  , (None  ,('cb',    ),'svn','buddypress',)), #download to ./src/ dir: 'https://buddypress.svn.wordpress.org/trunk/')), # https://buddypress.trac.wordpress.org/browser/trunk/ # latest nightly ver
  ('bpap', ('bp'  ,(         ),'svn','buddypress-activity-plus',)),
  ('bpcp', ('bp'  ,(         ),'svn','buddypress-cover-photo',)),
  ('bpd' , ('bp'  ,('cb',    ),'svn','buddypress-docs',)),
  ('bpdw', ('bp'  ,('cb',    ),'cbx','buddypress-docs-wiki',)), # Inlucded in: commons-in-a-box/includes/buddypress-docs-wiki-1.0.9.zip
 #[Install causes blank page](https://github.com/Automattic/hyperdb/issues/12)
 #('hpdb', (None  ,(         ),'svn','hyperdb',)),
  ('ldb' , (None  ,(         ),'git','ludicrousdb','https://github.com/stuttter/ludicrousdb')),  # better than: hyperdb or github.com/TimeIncOSS/ludicrousdb
 #github.com/johnjamesjacoby/ludicrousdb redirect-> github/stuttter/ludicrousdb
  ('reds', (None  ,(         ),'svn','redis-cache',)),
  ('revs', (None  ,('av',    ),'loc','revslider',)),
  ('smpp', (None  ,(         ),'zip','swpm-partial-protection','https://simple-membership-plugin.com/wp-content/uploads/addons/swpm-partial-protection.zip',)),
  ('tmce', (None  ,(         ),'svn','tinymce-advanced',)),
 #('wpy' , ('bp'  ,(         ),'loc','wordpy', None, None)),
  ('wpy' , ('bp'  ,(         ),'git','wordpy', '/fs/web/p/wordpy.git')),
  ('dmap', (None  ,(         ),'svn','wordpress-mu-domain-mapping',)),
  ('wooc', (None  ,(         ),'svn','woocommerce',)),
])

# woocommerce:
# ln -s /usr/share/GeoIP/GeoLiteCountry.dat /fs/www/wpy/doc/GeoIP.dat
#
# ==============================================================
# webdevstudios.com/2015/02/11/how-to-set-up-https-on-wordpress/
# ==============================================================
# wp_wpy]> select * from wp_options where option_name = "siteurl";
# | option_id | option_name | option_value       | autoload |
# |         7 | siteurl     | http://wordpy.com  | yes      |
# wp_wpy]> update wp_options set option_value = "https://wordpy.com" where option_name = "siteurl";
# wp_wpy]> select * from wp_options where option_name = "siteurl";
# |         7 | siteurl     | https://wordpy.com | yes      |
#
# wp_wpy]> select * from wp_options where option_name = "home";
# | option_id | option_name | option_value       | autoload |
# |        11 | home        | http://wordpy.com  | yes      |
# wp_wpy]> update wp_options set option_value = "https://wordpy.com" where option_name = "home" and option_id = 11;
# wp_wpy]> select * from wp_options where option_name = "home";
# |        11 | home        | https://wordpy.com | yes      |
# ==============================================================


#wordpy$ cd /fs/web/wordpy/wp-content/plugins
#mv wordpy       /fs/web/p && ln -s /fs/web/p/wordpy     wordpy
#mv fusion-core   /fs/web/p && ln -s /fs/web/p/fusion-core
#mv LayerSlider   /fs/web/p && ln -s /fs/web/p/LayerSlider
#mv revslider     /fs/web/p && ln -s /fs/web/p/revslider
#mv bp-custom.php /fs/web/p && ln -s /fs/web/p/bp-custom.php
# ln -s /fs/web/p/fusion-builder /fs/www/wpy/wp-content/plugins/fusion-builder
#
## After updating at web1, cp -rp to Loc so Loc can Deploy to other servers:
#cp -rp /sshfs/wordpy/fs/web/p/fusion-core  /fs/web/p
#cp -rp /sshfs/wordpy/fs/web/p/LayerSlider  /fs/web/p


# wp --path=/fs/wordpy --url=wordpy.com          plugin list
PsWpy = ODict([
  # Abbr,  Download,NetworkActivate or just activate: tuple(BlogIds,..)
  #                 Activate plugin in each individual blog if BlogId == 0
  ('akis', (True ,True )),  # akismet
  ('bbp' , (True ,True )),  # bbpress
 #('bbpcn',(True ,False)),  # bbpress-cn
  ('bpga', (False,False)),#cbox.zip bp-group-announcements
  ('bpgh', (False,False)),  # bp-group-hierarchy
  ('bp'  , (True ,(0, ))),  # buddypress # Activate in each individual blog
  ('bpap', (True ,True )),  # buddypress-activity-plus
  ('bpcp', (True ,True )),  # buddypress-cover-photo  #Need to activate
  ('bpd' , (True ,False)),#cbox     buddypress-docs
  ('bpdw', (False,False)),#cbox.zip buddypress-docs-wiki
  ('ldb' , (True ,False)),  # hyperdb
  ('reds', (True ,False)),  # redis-cache
 #('revs', (True ,(4, ))),#error if activated! # revslider
  ('revs', (True ,False)),#error if activated! # revslider
  ('tmce', (True ,True )),  # tinymce-advanced
  ('wpy' , (True ,True )),  # wordpy
  ('dmap', (True ,False)),  # wordpress-mu-domain-mapping
  ('wooc', (True ,True )),  # woocommerce
])

#bp-custom.php


PsWdp = ODict()  #PsWdp = cHO.GoDaddyDomains + cHO.Registrar1_Domains
PsWdp.update(PsWpy)
PsWdp['adds'] = (True ,False)  # add-from-server
PsWdp['admz'] = (True ,False)  # adminimize

SitePluginD = {     #Site Plugin Dict
#SId: Plugins, #Site
   0: PsWpy,   #'www' = Default Site
   1: PsWpy,   #'wpy' = wordpy.com
  20: PsWdp,   #'wpy' = wordpy.com
}

# cb=cbox doesn't offer language translations.  better use Avada instead!!
ThemeOD = ODict([
  # Abbr,  Depend ,Plugin Use      ,TSrc ,ThemeSlug   , TSrcPath
  ('av',   (None  ,(              ),'loc','Avada'            ,)),
  ('avch', ('av'  ,(              ),'loc','Avada-Child-Theme',)),
  ('cb',   (None  ,('cbox','bpdw',),'git','cbox-theme','https://github.com/cuny-academic-commons/cbox-theme')),
  ('cbch', ('cb'  ,(              ),'zip','cbox-child','https://www.dropbox.com/s/aaet25aktzme0ez/cbox-child.zip')),  #http://commonsinabox.org/documentation/themes/developer-guide
  ('t010', (None  ,(              ),'svn','twentyten',)),
  ('t011', (None  ,(              ),'svn','twentyeleven',)),
  ('t012', (None  ,(              ),'svn','twentytwelve',)),
  ('t013', (None  ,(              ),'svn','twentythirteen',)),
  ('t014', (None  ,(              ),'svn','twentyfourteen',)),
  ('t015', (None  ,(              ),'svn','twentyfifteen',)),
  ('t016', (None  ,(              ),'svn','twentysixteen',)),
  ('t017', (None  ,(              ),'svn','twentyseventeen',)),
])

TsWPy = ODict([
  # Abbr,  Download,NetworkActivate or just activate: tuple(BlogIds,..)
  ('avch', (True ,True )),  # Avada-Child-Theme
  ('av'  , (True ,False)),  # Avada       # (4, )
  ('cbch', (True ,False)),  # cbox-child  # (1, )
  ('cb'  , (True ,False)),  # cbox-theme
 #('t015', (True ,False)),  # twentyfifteen
  ('t016', (True ,False)),  # twentysixteen
  ('t017', (True ,False)),  # twentyseventeen
])

TsWdp = ODict([
  ('avch', (True ,True )),  # Avada-Child-Theme
  ('av'  , (True ,False)),  # Avada
 #('t015', (True ,False)),  # twentyfifteen
  ('t016', (True ,False)),  # twentysixteen
  ('t017', (True ,False)),  # twentyseventeen
])


SiteThemeD = {     #Site Theme Dict
#SId: Themes,  #Site
   0: TsWPy,   #'www' = Default Site
   1: TsWPy,   #'wpy' = wordpy.com
  20: TsWdp,   #'wdp' = wordpress.com
}

ChildThemeCss = '''/*
 Theme Name:  {Theme} Child Theme
 Theme URI:   https://wordpress.org/themes/{Theme}/
 Description: {Theme} Child Theme auto generated by wpy.py
 Author:      Victor Tong
 Author URI:  http://wordpy.com/
 Template:    {Theme}
 Version:     1.0.0
 Text Domain: {Theme}-child
*/
# Template line corresponds to the directory name (TSlug) of the parent theme
'''

ChildThemePhp = '''<?php
add_action( 'wp_enqueue_scripts', function() {
	wp_enqueue_style('parent-style', get_template_directory_uri().'/style.css');
	wp_enqueue_style('child-style', get_stylesheet_directory_uri().'/style.css',
	                 array('parent-style') );
} );
'''
# wp> get_template_directory_uri()
# "http://www.wordpy.com/wp-content/themes/twentyfifteen"
# wp> get_stylesheet_directory_uri()    #same if Child Theme activated?
# "http://www.wordpy.com/wp-content/themes/twentyfifteen"

# codex.buddypress.org/themes/buddypress-companion-stylesheets/
BpTwentyThemes = ('sixteen','fifteen','fourteen','thirteen','twelve',)
BpDequeueStyle = '''
/* dequeue if conflict with other child theme customizations
add_action( 'bp_enqueue_scripts', function() {
	wp_dequeue_style( 'bp-{TSlug}' );  # bp-twentysixteen
}, 20 );
*/
'''



# https://wordpress.org/plugins/svg-support/

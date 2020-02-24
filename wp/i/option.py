#!/usr/bin/python3.5
from wordpress_xmlrpc.wordpress       import WordPressOption
from wordpress_xmlrpc.methods         import options
from wordpress_xmlrpc.methods.options import GetOptions, SetOptions
import pyx.db      as xDB
import pyx.php     as Php
import wpy.xmlcli  as XmlC       # Xml Client Class
import wp.conf     as WpC
import wp.i.cache  as WiCa
import wp.i.func   as WiFc
import wp.i.plugin as WiPg
array = Php.array

#wpdb set in Web.WpBlogCls
#    for Module in (WpT, WiM, WiU, WiO, WpTx):
#      Module.wpdb = self.Wj.wpdb


#import wp.i.option as WpO; WpO.OptionC.InitCls(BlogCls(1))
#WpO.XmlGetOptions()
#WpO.DeleteTransientInOption()

def wp_installing():
  return False

#class OptionC:  #Post Class variables are shared among class instances
#  "Change from WDB to BDB since option table in TbsBlog ~= TbsBlogWp"
#  Bj = Exit = XmlCli = BDB = None
#  # /usr/local/lib/python3.5/dist-packages/wordpress_xmlrpc/methods/posts.py
def IniXmlMethods():
  WpC.WB.Bj.XmlMethods = ['GetOptions', 'SetOptions',]


# Moved all staticmethods to module fuctions. staticmethod has no benifit other than grouping them in a class, but we're already grouping all in this module

def XmlGetOptions():
  IniXmlMethods()
  # WpOptions = WordPressOption()
  WpOptions = XmlC.CliCall('GetOptions')

  # filter_options = ['value', 'mystile-child-theme']
  # WpOptions = wp.call( options.GetOptions(filter_options) )
  # for option_key, option_value in WpOptions.items:
  print("\n=============================================:\nWpOption:")
  for o in WpOptions:
    print("\ndesc= "   , str(o.description))
    print("name= "     , str(o.name))
    print("read_only= ", str(o.read_only))
    print("value= "    , str(o.value))


## Start BDB Methods       ######################


# result = get_option('bp_restrict_group_creation', None)
def get_option(option, default=None, DbName=None, Db=None):
  ''' converted to py from wp-includes/option.php
  row = wpdb.get_row( wpdb.prepare( "SELECT option_value FROM
                 wpdb.options WHERE option_name = %s LIMIT 1", option ) )
  developer.wordpress.org/reference/functions/get_option/
  All options returns str such as '', or '0'
  '''
  OptionConsts = {
    'blog_charset' : 'UTF-8',
    'category_base': '',
    'db_version'   : '36686',
    'default_category' : '1',
    'default_comment_status' : 'open',
   #'finished_splitting_shared_terms' : '1',
    'home'         : WpC.WB.Bj.BUrl.rstrip('/'),  #= 'http://www.wordpy.com'
    'permalink_structure' : '/%year%/%monthnum%/%postname%/', # '/%postname%/'
    'tag_base'     : '',
    'siteurl'      : WpC.WB.Bj.BUrl,  # 'http://www.wordpy.com/'
  }
  if   option in OptionConsts:
    return OptionConsts[option]
  import wpy.time as wTm
  if   option == 'timezone_string': #Asia/Hong_Kong,US/Pacific
    try:   return wTm.GetTimeZone(WpC.WB.Bj.WH0.DcNum)
    except:return ''  # default = '', can set to ='UTC'
  elif option == 'gmt_offset':
    try:   return wTm.GetUtcOffsetFromTz(wTm.GetTimeZone(WpC.WB.Bj.WH0.DcNum))
    except:return '0'

  if Db is None:
    Db = WpC.WB.Bj.BDB
  DbName = Db.DbName if DbName is None else DbName
  option = option.strip()
  if not option:
    return False
  #Sql=("SELECT option_value FROM {}.{}".format(DbName, Db.TbB.Option) +
  Sql= ("SELECT *            FROM {}.{}".format(DbName, Db.TbB.Option) +
        " WHERE option_name = %s LIMIT 1;")
  print('get_option', Sql)
  row = Db.Exec(Sql, (option,), 'select')
  if not row: # = row not in (None, False, '', (), [],):
    return default
  print('get_option result row', row)
  value =  row[0]['option_value']

  # If home is not set use siteurl.
  if 'home' == option and '' == value:
    return get_option( 'siteurl' )
  
  if option in ('siteurl', 'home', 'category_base', 'tag_base'):
    value = value.rstrip('/')   # = WiF.untrailingslashit( value )

  return WiFc.maybe_serialize( value )
# SELECT * FROM wp_200_options WHERE option_name LIKE "%widget%"
# SELECT * FROM wp_200_options WHERE option_name = 'sidebars_widgets'


def wp_protect_special_option( option ):
  ''' Protect WordPress special option from being modified.
  Will die if option is in protected list. Protected options are 'alloptions'
  and 'notoptions' options.
  @param string option Option name.
  '''
  if 'alloptions' == option or 'notoptions' == option:
    WiFc.wp_die( Php.sprintf( __( '%s is a protected WP option and may not '
                                  'be modified' ), esc_html( option ) ) )


def form_option( option ):
  ''' Print option value after sanitizing for forms.
  @param string option Option name.
  '''
  Php.echo( esc_attr( get_option( option ) ))


def wp_load_alloptions():
  ''' Loads and caches all autoloaded options, if available or all options.
  @global wpdb wpdb WordPress database abstraction object.
  @return array List of all options.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  
  if not wp_installing() or not WpC.WB.Wj.is_multisite():
    alloptions = WiCa.wp_cache_get( 'alloptions', 'options' )
  else:
    alloptions = False
  
  if not alloptions:
    suppress = wpdb.suppress_errors()
    alloptions_db = wpdb.get_results( "SELECT option_name, option_value FROM "
                           "{} WHERE autoload = 'yes'".format(wpdb.options) )
    if not alloptions_db:
      alloptions_db = wpdb.get_results("SELECT option_name, option_value FROM "
                                       + wpdb.options )
    wpdb.suppress_errors(suppress)
    alloptions = array()
    for o in Php.Array( alloptions_db ):
      alloptions[o.option_name] = o.option_value
    if not wp_installing() or not WpC.WB.Wj.is_multisite():
      WiCa.wp_cache_add( 'alloptions', alloptions, 'options' )
  
  return alloptions


def wp_load_core_site_options( site_id = None ):
  ''' Loads and caches certain often requested site options if WpC.WB.Wj.is_multisite() and a persistent cache is not being used.
  @global wpdb wpdb WordPress database abstraction object.
  @param int site_id Optional site ID for which to query the options. Defaults to the current site.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  
  if WpC.WB.Wj.is_multisite() or wp_using_ext_object_cache() or wp_installing():
    return
  
  if Php.empty(locals(), 'site_id'):
    site_id = wpdb.siteid
  
  core_options = array('site_name', 'siteurl', 'active_sitewide_plugins', '_site_transient_timeout_theme_roots', '_site_transient_theme_roots', 'site_admins', 'can_compress_scripts', 'global_terms_enabled', 'ms_files_rewriting' )
  
  core_options_in = "'" + Php.implode("', '", core_options) + "'"
  options = wpdb.get_results( wpdb.prepare("SELECT meta_key, meta_value FROM {} WHERE meta_key IN ({}) AND site_id = %d".format(wpdb.sitemeta, core_options_in), site_id) )
  
  for option in options:
    key = option.meta_key
    cache_key = site_id +":"+ key
    option.meta_value = maybe_unserialize( option.meta_value )
    
    WiCa.wp_cache_set( cache_key, option.meta_value, 'site-options' )



def update_option(option, value, autoload=None, DbName=None, Db=None):
  ''' converted to py from wp-includes/option.php
  result = wpdb.update( wpdb.options, update_args,
                           array( 'option_name' => option ) )
  WpO.update_option('bp-disable-profile-sync', '1')
  '''
  if Db is None:
    Db = WpC.WB.Bj.BDB
  DbName = Db.DbName if DbName is None else DbName
  option = option.strip()
  # /fs/web/wp/wp-includes/formatting.php: function sanitize_option n/a here!
  # value = sanitize_option( option, value )
  old_value = get_option( option )
  # If the new and old values are the same, no need to update.
  if value == old_value:
    return False
  serialized_value = WiFc.maybe_serialize( value )
  Args = {'option':option, 'value':serialized_value, }
  if autoload is not None:
    Args['autoload'] = 'no' if autoload in ('no', False,) else 'yes'

  Sql= ("UPDATE {}.{}".format(DbName, Db.TbB.Option) +
        " SET option_value =%(value)s WHERE option_name =%(option)s;")
  # conn.commit() when Action = 'update'
  result = Db.Exec(Sql, Args, 'update')
  if not result: # = result not in (None, False, '', (), [],):
    return False
  return True


# option_id  : PRIMARY KEY
# option_name: UNIQUE KEY
# option_value
# autoload
# Also in BDB.BlogCls, since DbName wp_wpy_cos != wp_wpy in BDB.SiteDbCls
def add_option(option, value, autoload='yes', DbName=None, Db=None):
  ''' converted to py from wp-includes/option.php  !!ON DUPLICATE KEY UPDATE!!
  function add_option(option, value = '', autoload = 'yes' )
  result = wpdb.query( wpdb.prepare( "INSERT INTO `wpdb.options`
    (`option_name`, `option_value`, `autoload`) VALUES (%s, %s, %s)
     ON DUPLICATE KEY UPDATE `option_name`  = VALUES(`option_name`),
     `option_value` = VALUES(`option_value`),
     `autoload` = VALUES(`autoload`)", option, serialized_value,autoload))
  '''
  if Db is None:
    Db = WpC.WB.Bj.BDB
  DbName = Db.DbName if DbName is None else DbName
  option = option.strip()
  if not value or not isinstance(value, str):
    return False
  # /fs/web/wp/wp-includes/formatting.php: function sanitize_option n/a here!
  # value = sanitize_option( option, value )
  serialized_value = WiFc.maybe_serialize( value )
  #Args = {'option':option, 'value':serialized_value, }
  autoload = 'no' if autoload in ('no', False,) else 'yes'

  Sql= ("INSERT INTO {}.{}".format(DbName, Db.TbB.Option) +
        " (`option_name`, `option_value`, `autoload`) VALUES (%s, %s, %s)"
        " ON DUPLICATE KEY UPDATE"
        " `option_name`  = VALUES(`option_name` ),"
        " `option_value` = VALUES(`option_value`),"
        " `autoload`     = VALUES(`autoload`    );" )
  result = Db.Exec(Sql, (option, serialized_value, autoload,), 'insert')
  #              conn.commit() when Action = 'update'
  if not result: # = result not in (None, False, '', (), [],):
    return False
  return True


def delete_option( option ):
  ''' Removes option by name. Prevents removal of protected WordPress options.
  @global wpdb wpdb WordPress database abstraction object.
  @param string option Name of option to remove. Expected to not be SQL-escaped
  @return bool True, if option is successfully deleted. False on failure.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  
  option = Php.trim( option )
  if Php.empty(locals(), 'option'):
    return False
  
  wp_protect_special_option( option )
  
  # Get the ID, if no ID then return
  row = wpdb.get_row( wpdb.prepare( "SELECT autoload FROM {} WHERE option_name"
                                    " = %s".format(wpdb.options), option ) )
  if Php.is_null( row ):
    return False
  
  # Fires immediately before an option is deleted.
  # @param string option Name of the option to delete.
  WiPg.do_action( 'delete_option', option )
  
  result = wpdb.delete( wpdb.options, array( ('option_name', option) ) )
  if not wp_installing():
    if 'yes' == row.autoload:
      alloptions = wp_load_alloptions()
      if Php.is_array( alloptions ) and Php.isset( alloptions, option ):
        del( alloptions[option] )
        WiCa.wp_cache_set( 'alloptions', alloptions, 'options' )
    else:
      WiCa.wp_cache_delete( option, 'options' )

  if result:
    # Fires after a specific option has been deleted.
    # The dynamic portion of the hook name, `option`, refers to the option name
    # @param string option Name of the deleted option.
    WiPg.do_action( "delete_option_"+ option, option )
    
    # Fires after an option has been deleted.
    # @param string option Name of the deleted option.
    WiPg.do_action( 'deleted_option', option )
    return True

  return False


def get_site_option(option, default=None, DbName=None):
  OptionConsts = {
    'siteurl'      : WpC.WB.Bj.SUrl,  # 'http://www.wordpy.com/'
  }
  if option in OptionConsts:
    return OptionConsts[option]


def IsOptionTbExist(Db):
  Exist =  Db.IfTbExist(Db.DbName, Db.TbB.Option)
  print(Db.DbName, Db.TbB.Option,
        ' exists!' if Exist else ' does not exist!')
  return Exist
  #print('  Db = {}, Db.DbName = {}'.format(Db, Db.DbName))
  #if not Db.IfDbExist(Db.DbName):
  #  print(Db.DbName, ' does not exist! Skip!')


@xDB.AllBlogDbsDecorator
def GetOptionInAllBlogDbs(Db, option, default=None):
  ''' WpO.GetOptionInAllBlogDbs('bp-disable-profile-sync')
      WpO.get_option('bp-disable-profile-sync')
  '''
  if not IsOptionTbExist(Db):
    return False
  print(get_option(option, default=None, Db=Db))
  return True

@xDB.AllBlogDbsDecorator
def AddOptionInAllBlogDbs(Db, option, value, autoload='yes', default=None):
  ''' WpO.AddOptionInAllBlogDbs('bp-disable-profile-sync', '1', autoload='yes')
  IMPORTANT! Need to: add_option('bp-disable-profile-sync', '1'), or else
     xprofile_sync_wp_profile() & xprofile_sync_bp_profile() in bp-xprofile.php
     will override nickname, first_name, last_name, & display_name set by
     wp_profile_sync() in wordpy-class.php!! 
  Instead of update_option, better use add_option w/ ON DUPLICATE KEY UPDATE!!
     # update_option('bp-disable-profile-sync', '1', Db=Db)
  '''
  if not IsOptionTbExist(Db):
    return False
  print(add_option(option, value, autoload, Db=Db))
  return True


def ChangeOptionName(Name, NewName, DbName=None, Db=None):
  if Db is None:
    Db = WpC.WB.Bj.BDB
  DbName = Db.DbName if DbName is None else DbName
  Sql= ("UPDATE {}.{}".format(DbName, Db.TbB.Option) +
        " SET option_name =%(new_name)s WHERE option_name =%(name)s;")
  SqlDict = {'name':Name, 'new_name':NewName, }
  return Db.Exec(Sql, SqlDict, 'update')

def DeleteTransientInOption(DbName=None, Db=None): # clear author avatar cache
  " Delete Transient In Option, also clear author avatar cache "
  if Db is None:
    Db = WpC.WB.Bj.BDB
  DbName = Db.DbName if DbName is None else DbName
  return Db.Exec("DELETE FROM {}.{} WHERE option_name LIKE "
                     "'\_transient\_%'".format(DbName, Db.TbB.Option))

def AddOptions_bp_restrict_group_creation():
  ''' See p/wordpy/lib/bp-restrict-group-creation.php
  '''
  AddOptions = 'bp_restrict_group_creation', '1', 'yes'
  if add_option(*AddOptions):
    print('Success add_option:', AddOptions)
  else:
    print('Failed  add_option:', AddOptions)

# result = get_option('bp_restrict_group_creation', None)
def UpdateOptions_bp_restrict_group_creation(value='0',autoload='yes'):
  ''' See p/wordpy/lib/bp-restrict-group-creation.php
  '''
  UpdateOptions = 'bp_restrict_group_creation', value, autoload
  if update_option(*UpdateOptions):
    print('Success update_option:', UpdateOptions)
  else:
    print('Failed  update_option:', UpdateOptions)

def RmItemFromSidebarWidget(Item='Meta'):
  import phpserialize as ps
  # Dump = b'a:3:{s:19:"wp_inactive_widgets";a:0:{}s:9:"sidebar-1";a:6:{i:0;s:8:"search-2";i:1;s:14:"recent-posts-2";i:2;s:17:"recent-comments-2";i:3;s:10:"archives-2";i:4;s:12:"categories-2";i:5;s:6:"meta-2";}s:13:"array_version";i:3;}'
  Dump = get_option('sidebars_widgets')
  ps.loads(Dump, decode_strings=True)
  Loads = ps.loads(Dump, decode_strings=True)
  # Loads['sidebar-1']
  for k,v in Loads.items():
    if k.startswith('sidebar'):
      for Id, Widget in v.items():
        print(Id, Widget)
        if Widget.startswith('meta'):
          del v[Id]
          print('Deleted: ', Id, Widget)
          break
  # print(Loads)
  update_option('sidebars_widgets', ps.dumps(Loads).decode())


'''
/fs/web/p/BuddyPress/src/bp-groups/bp-groups-template.php
Determine if the current logged in user can create groups.
@return bool True if user can create groups. False otherwise.
function bp_user_can_create_groups() {

http://wordpy.com/wp-admin/admin.php?page=bp-settings
Groups Settings
Group Creation  [x] Enable group creation for all users.  Admins can always
                create groups, regardless of this setting.
That's why:
p> bp_get_option( 'bp_restrict_group_creation', 0 )  #output# string(1) "0"

After Uncheck Enable group and click apply:
Group Creation  [ ] Enable group creation for all users
wp --url=wordpy.com --path=/fs/www/wpy shell #relaunch wp to refresh option
wp> $restricted=(int)bp_get_option('bp_restrict_group_creation', 0); #output# int(1)
'''


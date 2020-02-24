from collections import OrderedDict as ODict
import pyx.php     as Php
#import wp.i.ms_load as WiML
import wp.conf     as WpC
import wp.i.option as WiO
#import wp.i.wpdb   as WpDb
array = Php.array

''' These functions are needed to load WordPress.
@package WordPress
'''

class WiLoad(WpC.WpConfCls):
  ''' replace global var with self.var=WpC.WB.Wj.var
  global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable[],{},ODict
  '''
  import wp.settings as WpS   # wp-settings.php
  wp_settings = WpS.wp_settings

  #def wp_get_server_protocol(self):
  #  ''' Return the HTTP protocol sent by the server.
  #  @return string The HTTP protocol. Default: HTTP/1.0.
  #  '''
  #  protocol = _SERVER['SERVER_PROTOCOL']
  #  if protocol not in ( 'HTTP/1.1', 'HTTP/2', 'HTTP/2.0' ):
  #    protocol = 'HTTP/1.0'
  #  return protocol

  #def wp_unregister_GLOBALS(self):
  #  ''' Turn register globals off.
  #  @access private
  #  '''
  #  GLOBALS = WpC.WB.Wj.__dict__
  #  if not ini_get( 'register_globals' ):
  #    return
  #  if Php.isset( _REQUEST['GLOBALS'] ):
  #    die( 'GLOBALS overwrite attempt detected' )
  #  # Variables that shouldn't be unset
  #  no_unset = ( 'GLOBALS', '_GET', '_POST', '_COOKIE', '_REQUEST', '_SERVER', '_ENV', '_FILES', 'table_prefix' )
  #
  #  Input = Php.array_merge( _GET, _POST, _COOKIE, _SERVER, _ENV, _FILES, isset( _SESSION ) and is_array( _SESSION ) ? _SESSION : array() )
  #  for k, v in Input.items():
  #    if k not in no_unset and Php.isset( GLOBALS, k ):
  #      Php.unset( GLOBALS[k] )

  #def wp_fix_server_vars(self):
  #  ''' Fix `_SERVER` variables for various setups.
  #  @global string PHP_SELF The filename of the currently executing script,
  #                           relative to the document root.
  #  '''
  #  #global PHP_SELF
  #  default_server_values = array(
  #    ('SERVER_SOFTWARE', ''), ('REQUEST_URI', ''), )
  #
  #  _SERVER = Php.array_merge( default_server_values, _SERVER )
  #
  #  # Fix for IIS when running with PHP ISAPI
  #  if empty( _SERVER['REQUEST_URI'] ) or ( PHP_SAPI != 'cgi-fcgi' and preg_match( '/^Microsoft-IIS\#', _SERVER['SERVER_SOFTWARE'] ) ):
  #
  #    # IIS Mod-Rewrite
  #    if isset( _SERVER['HTTP_X_ORIGINAL_URL'] ):
  #      _SERVER['REQUEST_URI'] = _SERVER['HTTP_X_ORIGINAL_URL']
  #    # IIS Isapi_Rewrite
  #    elif isset( _SERVER['HTTP_X_REWRITE_URL'] ):
  #      _SERVER['REQUEST_URI'] = _SERVER['HTTP_X_REWRITE_URL']
  #    else:
  #      # Use ORIG_PATH_INFO if there is no PATH_INFO
  #      if not isset( _SERVER['PATH_INFO'] ) and isset( _SERVER['ORIG_PATH_INFO'] ):
  #        _SERVER['PATH_INFO'] = _SERVER['ORIG_PATH_INFO']
  #
  #      # Some IIS + PHP configurations puts the script-name in the path-info (No need to append it twice)
  #      if isset( _SERVER['PATH_INFO'] ):
  #      if _SERVER['PATH_INFO'] == _SERVER['SCRIPT_NAME']:
  #          _SERVER['REQUEST_URI'] = _SERVER['PATH_INFO']
  #        else:
  #          _SERVER['REQUEST_URI'] = _SERVER['SCRIPT_NAME'] . _SERVER['PATH_INFO']
  #
  #      # Append the query string if it exists and isn't None
  #      if _SERVER['QUERY_STRING']:
  #        _SERVER['REQUEST_URI'] .= '?' . _SERVER['QUERY_STRING']
  #
  #  # Fix for PHP as CGI hosts that set SCRIPT_FILENAME to something ending in php.cgi for all requests
  #  if isset( _SERVER['SCRIPT_FILENAME'] ) and ( strpos( _SERVER['SCRIPT_FILENAME'], 'php.cgi' ) == strlen( _SERVER['SCRIPT_FILENAME'] ) - 7 ):
  #    _SERVER['SCRIPT_FILENAME'] = _SERVER['PATH_TRANSLATED']
  #
  #  # Fix for Dreamhost and other PHP as CGI hosts
  #  if strpos( _SERVER['SCRIPT_NAME'], 'php.cgi' ) != False:
  #    unset( _SERVER['PATH_INFO'] )
  #
  #  # Fix empty PHP_SELF
  #  self.PHP_SELF = _SERVER['PHP_SELF']
  #  if empty( self.PHP_SELF ):
  #    _SERVER['PHP_SELF'] = self.PHP_SELF = preg_replace( '/(\?.*)?$/', '', _SERVER["REQUEST_URI"] )

  #def wp_check_php_mysql_versions(self):
  #  ''' Check for the required PHP version, and the MySQL extension or
  #  a database drop-in.
  #  Dies if requirements are not met.
  #  @global string required_php_version The required PHP version string.
  #  @global string wp_version           The WordPress version string.
  #  '''
  #  #global required_php_version, wp_version
  #  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable[],{},ODict
  #
  #  php_version = phpversion(self)
  #
  #  if version_compare( self.required_php_version, php_version, '>' ):
  #    wp_load_translations_early(self)
  #
  #    protocol = wp_get_server_protocol(self)
  #    header( sprintf( '%s 500 Internal Server Error', protocol ), True, 500 )
  #    header( 'Content-Type: text/html; charset=utf-8' )
  #    # translators: 1: Current PHP version number, 2: WordPress version number
  #    die( sprintf( __( 'Your server is running PHP version %1$s but WordPress %2$s requires at least %3$s.' ), php_version, self.wp_version, self.required_php_version ) )
  #
  #  if not extension_loaded( 'mysql' ) and not extension_loaded( 'mysqli' ) and not extension_loaded( 'mysqlnd' ) and not file_exists( WP_CONTENT_DIR . '/db.php' ):
  #    wp_load_translations_early(self)
  #
  #    protocol = wp_get_server_protocol(self)
  #    header( sprintf( '%s 500 Internal Server Error', protocol ), True, 500 )
  #    header( 'Content-Type: text/html; charset=utf-8' )
  #    die( __( 'Your PHP installation appears to be missing the MySQL extension which is required by WordPress.' ) )

  #def wp_favicon_request(self):
  #  ''' Don't load all of WordPress when handling a favicon.ico request.
  #  Instead, send the headers for a zero-length favicon and bail.
  #  '''
  #  if '/favicon.ico' == _SERVER['REQUEST_URI']:
  #    header('Content-Type: image/vnd.microsoft.icon')
  #    exit

  #def wp_maintenance(self):
  #  ''' Die with a maintenance message when conditions are met.
  #  Checks for a file in the WordPress root directory named ".maintenance".
  #  This file will contain the variable upgrading, set to the time the file
  #  was created. If the file was created less than 10 minutes ago, WordPress
  #  enters maintenance mode and displays a message.
  #  The default message can be replaced by using a drop-in (maintenance.php in
  #  the wp-content directory).
  #  @global int upgrading the unix timestamp marking when upgrading WordPress began.
  #  '''
  #  if not file_exists( ABSPATH . '.maintenance' ) or wp_installing(self):
  #    return
  #
  #  #global upgrading
  #  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable[],{},ODict
  #
  #  include( ABSPATH . '.maintenance' )
  #  # If the upgrading timestamp is older than 10 minutes, don't die.
  #  if ( time() - self.upgrading ) >= 600:
  #    return
  #
  #  # Filters whether to enable maintenance mode.
  #  # This filter runs before it can be used by plugins. It is designed for
  #  # non-web runtimes. If this filter returns True, maintenance mode will be
  #  # active and the request will end. If False, the request will be allowed to
  #  # continue processing even if maintenance mode should be active.
  #  # @param bool enable_checks Whether to enable maintenance mode. Default True.
  #  # @param int  upgrading     The timestamp set in the .maintenance file.
  #  if not WiPg.apply_filters( 'enable_maintenance_mode', True, self.upgrading ):
  #    return
  #
  #  #if file_exists( WP_CONTENT_DIR . '/maintenance.php' ):
  #  #  require_once( WP_CONTENT_DIR . '/maintenance.php' )
  #  #  die(self)
  #
  #  wp_load_translations_early(self)
  #
  #  protocol = wp_get_server_protocol(self)
  #  header( protocol +" 503 Service Unavailable", True, 503 )
  #  header( 'Content-Type: text/html; charset=utf-8' )
  #  header( 'Retry-After: 600' )
  #  print('''
  #  <!DOCTYPE html>
  #  <html xmlns="http:#www.w3.org/1999/xhtml"<?php if ( is_rtl(self) ) echo ' dir="rtl"'; ?>>
  #  <head>
  #  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  #    <title><?php _e( 'Maintenance' ); ?></title>
  #
  #  </head>
  #  <body>
  #    <h1><?php _e( 'Briefly unavailable for scheduled maintenance. Check back in a minute.' ); ?></h1>
  #  </body>
  #  </html>
  #<?php ''')
  #  die(self)

  #def timer_start(self):
  #  ''' Start the WordPress micro-timer.
  #  @global float timestart Unix timestamp set at the beginning of the page load.
  #  @see timer_stop(self)
  #  @return bool Always returns True.
  #  '''
  #  #global timestart
  #  self.timestart = microtime( True )
  #  return True

  #def timer_stop( display = 0, precision = 3 ):
  #  ''' Retrieve or display the time from the page start to when function is called.
  #  @global float   timestart Seconds from when timer_start(self) is called.
  #  @global float   timeend   Seconds from when function is called.
  #  @param int|bool display   Whether to echo or return the results. Accepts 0|False for return,
  #                             1|True for echo. Default 0|False.
  #  @param int      precision The number of digits from the right of the decimal to display.
  #                             Default 3.
  #  @return string The "second.microsecond" finished time calculation. The number is formatted
  #                 for human consumption, both localized and rounded.
  #  '''
  #  #global timestart, timeend
  #  self.timeend = microtime( True )
  #  timetotal = self.timeend - self.timestart
  #  r = ( Php.function_exists( 'number_format_i18n' ) ) ? number_format_i18n( timetotal, precision ) : number_format( timetotal, precision )
  #  if display:
  #    echo r
  #  return r

  #def wp_debug_mode(self):
  #  ''' Set PHP error reporting based on WordPress debug settings.
  #  Uses three constants: `WP_DEBUG`, `WP_DEBUG_DISPLAY`, and `WP_DEBUG_LOG`.
  #  All three can be defined in wp-config.php. By default, `WP_DEBUG` and
  #  `WP_DEBUG_LOG` are set to False, and `WP_DEBUG_DISPLAY` is set to True.
  #  When `WP_DEBUG` is True, all PHP notices are reported. WordPress will also
  #  display internal notices: when a deprecated WordPress function, function
  #  argument, or file is used. Deprecated code may be removed from a later
  #  version.
  #  It is strongly recommended that plugin and theme developers use `WP_DEBUG`
  #  in their development environments.
  #  `WP_DEBUG_DISPLAY` and `WP_DEBUG_LOG` perform no function unless `WP_DEBUG`
  #  is True.
  #  When `WP_DEBUG_DISPLAY` is True, WordPress will force errors to be displayed.
  #  `WP_DEBUG_DISPLAY` defaults to True. Defining it as None prevents WordPress
  #  from changing the global configuration setting. Defining `WP_DEBUG_DISPLAY`
  #  as False will force errors to be hidden.
  #  When `WP_DEBUG_LOG` is True, errors will be logged to debug.log in the content
  #  directory.
  #  Errors are never displayed for XML-RPC, REST, and Ajax requests.
  #  '''
  #  # Filters whether to allow the debug mode check to occur.
  #  # This filter runs before it can be used by plugins. It is designed for
  #  # non-web run-times. Returning False causes the `WP_DEBUG` and related
  #  # constants to not be checked and the default php values for errors
  #  # will be used unless you take care to update them yourself.
  #  # @param bool enable_debug_mode Whether to enable debug mode checks to occur. Default True.
  #  if not WiPg.apply_filters( 'enable_wp_debug_mode_checks', True :
  #    return
  #
  #  if WP_DEBUG:
  #    error_reporting( E_ALL )
  #
  #    if WP_DEBUG_DISPLAY:
  #      ini_set( 'display_errors', 1 )
  #    elif None != WP_DEBUG_DISPLAY:
  #      ini_set( 'display_errors', 0 )
  #
  #    if WP_DEBUG_LOG:
  #      ini_set( 'log_errors', 1 )
  #      ini_set( 'error_log', WP_CONTENT_DIR . '/debug.log' )
  #  else:
  #    error_reporting( E_CORE_ERROR | E_CORE_WARNING | E_COMPILE_ERROR | E_ERROR | E_WARNING | E_PARSE | E_USER_ERROR | E_USER_WARNING | E_RECOVERABLE_ERROR )
  #
  #  if defined( 'XMLRPC_REQUEST' ) or defined( 'REST_REQUEST' ) or ( defined( 'WP_INSTALLING' ) and WP_INSTALLING ) or self.wp_doing_ajax() ):
  #    @ini_set( 'display_errors', 0 )

  #def wp_set_lang_dir(self):
  #  ''' Set the location of the language directory.
  #  To set directory manually, define the `WP_LANG_DIR` constant
  #  in wp-config.php.
  #  If the language directory exists within `WP_CONTENT_DIR`, it
  #  is used. Otherwise the language directory is assumed to live
  #  in `WPINC`.
  #  '''
  #  if not defined( 'WP_LANG_DIR' ):
  #    if file_exists( WP_CONTENT_DIR . '/languages' ) and @is_dir( WP_CONTENT_DIR . '/languages' ) or not @is_dir(ABSPATH . WPINC . '/languages'):
  #      # Server path of the language directory.
  #      # No leading slash, no trailing slash, full path, not relative to ABSPATH
  #      define( 'WP_LANG_DIR', WP_CONTENT_DIR . '/languages' )
  #      if not defined( 'LANGDIR' ):
  #        # Old static relative path maintained for limited backward compatibility - won't work in some cases.
  #        define( 'LANGDIR', 'wp-content/languages' )
  #    else:
  #      # Server path of the language directory.
  #      # No leading slash, no trailing slash, full path, not relative to `ABSPATH`.
  #      define( 'WP_LANG_DIR', ABSPATH . WPINC . '/languages' )
  #      if not defined( 'LANGDIR' ):
  #        # Old relative path maintained for backward compatibility.
  #        define( 'LANGDIR', WPINC . '/languages' )

  def require_wp_db(self):
    ''' Load the database class file and instantiate the `wpdb` global.
    @global wpdb wpdb The WordPress database class.
    '''
    #wpdb = WpC.WB.Wj.wpdb  # global wpdb
    #if file_exists( WP_CONTENT_DIR . '/db.php' ):
    #  require_once( WP_CONTENT_DIR . '/db.php' )

    if hasattr(self, 'wpdb'):
      return
    # Move to Web.BlogCls.InitWp
    #self.wpdb = WpDb.wpdb_cls( self.DB_USER, self.DB_PASSWORD,
    #                           self.DB_NAME, self.DB_HOST )


  def wp_set_wpdb_vars(self):
    ''' Set the database table prefix and the format specifiers for database
    table columns.
    Columns not listed here default to `%s`.
    @global wpdb   wpdb         The WordPress database class.
    @global string table_prefix The database table prefix.
    '''
    #wpdb = WpC.WB.Wj.wpdb  # global wpdb, table_prefix
    #if self.wpdb.error:
    #  dead_db(self)

    # github.com/PyMySQL/PyMySQL/issues/329
    # PyMySQL convert all objects including int to formatted and quoted str
    # You can use only %s or %(name)s as placeholder.
    self.field_types = array( ('post_author','%d'), ('post_parent','%d'),
        ('menu_order','%d'), ('term_id', '%d'), ( 'term_group', '%d'),
        ('term_taxonomy_id', '%d'), ('parent', '%d'), ( 'count', '%d'),
        ('object_id', '%d'), ( 'term_order', '%d'), ('ID', '%d'),
        ('comment_ID', '%d'), ( 'comment_post_ID', '%d'),
        ('comment_parent', '%d'), ( 'user_id', '%d'), ( 'link_id', '%d'),
        ('link_owner', '%d'), ( 'link_rating', '%d'), ( 'option_id', '%d'),
        ('blog_id', '%d'), ( 'meta_id', '%d'), ( 'post_id', '%d'),
        ('user_status', '%d'), ('umeta_id', '%d'), ( 'comment_karma', '%d'),
        ('comment_count', '%d'),
        # multisite:
        ('active', '%d'), ( 'cat_id', '%d'), ( 'deleted', '%d'),
        ('lang_id', '%d'), ('mature', '%d'), ( 'public', '%d'),
        ('site_id', '%d'), ( 'spam', '%d'),
    )

    # Move to Web.BlogCls.InitWp
    #prefix = self.wpdb.set_prefix( self.table_prefix )

    #if is_wp_error( prefix ):
    #  wp_load_translations_early(self)
    #  wp_die(
    #    # translators: 1: table_prefix 2: wp-config.php
    #    sprintf( __( '<strong>ERROR</strong>: %1$s in %2$s can only contain '
    #                 'numbers, letters, and underscores.' ),
    #      '<code>'+ self.table_prefix +'</code>',
    #      '<code>wp-config.php</code>'
    #    )
    #  )

  #def wp_using_ext_object_cache( using = None ):
  #  ''' Toggle `_wp_using_ext_object_cache` on and off without directly
  #  touching global.
  #  @global bool _wp_using_ext_object_cache
  #  @param bool using Whether external object cache is being used.
  #  @return bool The current 'using' setting.
  #  '''
  #  #global _wp_using_ext_object_cache
  #  current_using = self._wp_using_ext_object_cache
  #  if None != using:
  #    self._wp_using_ext_object_cache = using
  #  return current_using

  def wp_start_object_cache(self):
    ''' Start the WordPress object cache.
    If an object-cache.php file exists in the wp-content directory,
    it uses that drop-in as an external object cache.
    '''
    #wp_filter = self.wp_filter  # global wp_filter
    #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable[],{},ODict

    first_init = False
    #if not Php.function_exists( 'wp_cache_init' ):
    #  if file_exists( WP_CONTENT_DIR . '/object-cache.php' ):
    #    require_once ( WP_CONTENT_DIR . '/object-cache.php' )
    #    if Php.function_exists( 'wp_cache_init' ):
    #      wp_using_ext_object_cache( True )
    #    # Re-initialize any hooks added manually by object-cache.php
    #    if self.wp_filter:
    #      self.wp_filter = WP_Hook::build_preinitialized_hooks( self.wp_filter )

    #  first_init = True
    #elif not wp_using_ext_object_cache(self) and file_exists( WP_CONTENT_DIR . '/object-cache.php' ) ):
    #  # Sometimes advanced-cache.php can load object-cache.php before
    #  # it is loaded here. This breaks the Php.function_exists check above
    #  # and can result in `_wp_using_ext_object_cache` being set
    #  # incorrectly. Double check if an external cache exists.
    #  wp_using_ext_object_cache( True )

    #if not wp_using_ext_object_cache(self):
    #  require_once ( ABSPATH . WPINC . '/cache.php' )
    import wp.i.cache  as WiCa

    ## If cache supports reset, reset instead of init if already
    ## initialized. Reset signals to the cache that global IDs
    ## have changed and it may need to update keys and cleanup caches.
    #if not first_init and Php.function_exists( 'wp_cache_switch_to_blog' ):
    #  wp_cache_switch_to_blog( get_current_blog_id() )
    #elif Php.function_exists( 'wp_cache_init' ):
    #  wp_cache_init(self)
    WiCa.wp_cache_init(self)   #self.wp_object_cache = WP_Object_Cache()

    #if Php.function_exists( 'wp_cache_add_global_groups' ):
    WiCa.wp_cache_add_global_groups( array( 'users', 'userlogins', 'usermeta', 'user_meta', 'useremail', 'userslugs', 'site-transient', 'site-options', 'site-lookup', 'blog-lookup', 'blog-details', 'site-details', 'rss', 'global-posts', 'blog-id-cache', 'networks', 'sites' ), Wj=self )
    WiCa.wp_cache_add_non_persistent_groups( array( 'counts', 'plugins' ) )

  #def wp_not_installed(self):
  #  ''' Redirect to the installer if WordPress is not installed.
  #  Dies with an error message when Multisite is enabled.
  #  '''
  #  if self.is_multisite():
  #    if not is_blog_installed(self) and not wp_installing(self) ):
  #      nocache_headers(self)
  #
  #      wp_die( __( 'The site you have requested is not installed properly. Please contact the system administrator.' ) )
  #  elif not is_blog_installed(self) and not wp_installing(self):
  #    nocache_headers(self)
  #
  #    require( ABSPATH . WPINC . '/kses.php' )
  #    require( ABSPATH . WPINC . '/pluggable.php' )
  #    require( ABSPATH . WPINC . '/formatting.php' )
  #
  #    link = wp_guess_url(self) . '/wp-admin/install.php'
  #
  #    wp_redirect( link )
  #    die(self)

  #def wp_get_mu_plugins(self):
  #  ''' Retrieve an array of must-use plugin files.
  #  The default directory is wp-content/mu-plugins. To change the default
  #  directory manually, define `WPMU_PLUGIN_DIR` and `WPMU_PLUGIN_URL`
  #  in wp-config.php.
  #  @return array Files to include.
  #  '''
  #  mu_plugins = array()
  #  if notis_dir( WPMU_PLUGIN_DIR ):
  #    return mu_plugins
  #  if not dh = opendir( WPMU_PLUGIN_DIR ):
  #    return mu_plugins
  #  while ( ( plugin = readdir( dh ) ) != False ) {
  #    if substr( plugin, -4 ) == '.php':
  #      mu_plugins[] = WPMU_PLUGIN_DIR . '/' . plugin
  #  closedir( dh )
  #  sort( mu_plugins )
  #
  #  return mu_plugins

  #def wp_get_active_and_valid_plugins(self):
  #  ''' Retrieve an array of active and valid plugin files.
  #  While upgrading or installing WordPress, no plugins are returned.
  #  The default directory is wp-content/plugins. To change the default
  #  directory manually, define `WP_PLUGIN_DIR` and `WP_PLUGIN_URL`
  #  in wp-config.php.
  #  @return array Files.
  #  '''
  #  plugins = array()
  #  active_plugins = Php.Array( get_option( 'active_plugins', array() ))
  #
  #  # Check for hacks file if the option is enabled
  #  if get_option( 'hack_file' ) and file_exists( ABSPATH . 'my-hacks.php' ):
  #    _deprecated_file( 'my-hacks.php', '1.5.0' )
  #    Php.array_unshift( plugins, ABSPATH . 'my-hacks.php' )
  #
  #  if empty( active_plugins ) or wp_installing(self):
  #    return plugins
  #
  #  network_plugins = WiML.wp_get_active_network_plugins(self) if self.is_multisite() else False
  #
  #  for plugin in active_plugins:
  #    if ( not validate_file( plugin ) # plugin must validate as file
  #      and '.php' == substr( plugin, -4 ) # plugin must end with '.php'
  #      and file_exists( WP_PLUGIN_DIR . '/' . plugin ) # plugin must exist
  #      # not already included as a network plugin
  #      and ( not network_plugins or not Php.in_array( WP_PLUGIN_DIR . '/' . plugin, network_plugins ) )
  #      ):
  #    plugins[None] = WP_PLUGIN_DIR . '/' . plugin
  #  return plugins

  @staticmethod
  def wp_set_internal_encoding():
    ''' Set internal encoding.
    In most cases the default internal encoding is latin1, which is
    of no use, since we want to use the `mb_` functions for `utf-8` strings.
    '''
    #if Php.function_exists( 'mb_internal_encoding' ):
    charset = WiO.get_option( 'blog_charset' )   #VT Always return 'UTF-8'
    if not charset or not Php.mb_internal_encoding( charset ):
      Php.mb_internal_encoding( 'UTF-8' )


  #def wp_magic_quotes(self):
  #  ''' Add magic quotes to `_GET`, `_POST`, `_COOKIE`, and `_SERVER`.
  #  Also forces `_REQUEST` to be `_GET + _POST`. If `_SERVER`,
  #  `_COOKIE`, or `_ENV` are needed, use those superglobals directly.
  #  '''
  #  # If already slashed, strip.
  #  if get_magic_quotes_gpc(self):
  #    _GET    = stripslashes_deep( _GET    )
  #    _POST   = stripslashes_deep( _POST   )
  #    _COOKIE = stripslashes_deep( _COOKIE )
  #
  #  # Escape with wpdb.
  #  _GET    = add_magic_quotes( _GET    )
  #  _POST   = add_magic_quotes( _POST   )
  #  _COOKIE = add_magic_quotes( _COOKIE )
  #  _SERVER = add_magic_quotes( _SERVER )
  #
  #  # Force REQUEST to be GET + POST.
  #  _REQUEST = Php.array_merge( _GET, _POST )

  #def shutdown_action_hook(self):
  #  ''' Runs just before PHP shuts down execution.
  #  '''
  #  # Fires just before PHP shuts down execution.
  #  do_action( 'shutdown' )
  #  wp_cache_close(self)


  def wp_clone( object ):
    ''' Copy an object.
    @param object object The object to clone.
    @return object The cloned object.
    '''
    # Use parens for clone to accommodate PHP 4. See #17880
    return Php.clone( object )


  def is_admin(self):
    ''' Whether the current request is for an administrative interface page.
    Does not check if the user is an administrator; current_user_can(self)
    for checking roles and capabilities.
    @global WP_Screen current_screen
    @return bool True if inside WordPress administration interface, False otherwise.
    '''
    #GLOBALS = WpC.WB.Wj.__dict__
    #if Php.isset( GLOBALS, 'current_screen' ):
    #  return GLOBALS['current_screen'].in_admin(self)
    #elif defined( 'WP_ADMIN' ):
    #  return WP_ADMIN
    if hasattr(self, 'current_screen'):
      return self.current_screen.in_admin(self)
    elif hasattr(self, 'WP_ADMIN'):
      return WP_ADMIN

    return False


  #def is_blog_admin(self):
  #  ''' Whether the current request is for a site's admininstrative interface.
  #  e.g. `/wp-admin/`
  #  Does not check if the user is an administrator; current_user_can(self)
  #  for checking roles and capabilities.
  #  @global WP_Screen current_screen
  #  @return bool True if inside WordPress blog administration pages.
  #  '''
  #  GLOBALS = WpC.WB.Wj.__dict__
  #  if Php.isset( GLOBALS, 'current_screen' ):
  #    return GLOBALS['current_screen'].in_admin( 'site' )
  #  elif defined( 'WP_BLOG_ADMIN' ):
  #    return WP_BLOG_ADMIN
  #
  #  return False
  #
  #
  #def is_network_admin(self):
  #  ''' Whether the current request is for the network administrative interface.
  #  e.g. `/wp-admin/network/`
  #  Does not check if the user is an administrator; current_user_can(self)
  #  for checking roles and capabilities.
  #  @global WP_Screen current_screen
  #  @return bool True if inside WordPress network administration pages.
  #  '''
  #  GLOBALS = WpC.WB.Wj.__dict__
  #  if Php.isset( GLOBALS, 'current_screen' ):
  #    return GLOBALS['current_screen'].in_admin( 'network' )
  #  elif defined( 'WP_NETWORK_ADMIN' ):
  #    return WP_NETWORK_ADMIN
  #
  #  return False
  #
  #
  #def is_user_admin(self):
  #  ''' Whether the current request is for a user admin screen.
  #  e.g. `/wp-admin/user/`
  #  Does not inform on whether the user is an admin! Use capability
  #  checks to tell if the user should be accessing a section or not
  #  current_user_can(self).
  #  @global WP_Screen current_screen
  #  @return bool True if inside WordPress user administration pages.
  #  '''
  #  if isset( GLOBALS['current_screen'] ):
  #    return GLOBALS['current_screen'].in_admin( 'user' )
  #  elif defined( 'WP_USER_ADMIN' ):
  #    return WP_USER_ADMIN
  #
  #  return False

  @staticmethod
  def is_multisite():
    ''' If Multisite is enabled.
    @return bool True if Multisite is enabled, False otherwise.
    '''
    return True
  #  if defined( 'MULTISITE' ):
  #    return MULTISITE
  #  if (defined( 'SUBDOMAIN_INSTALL' ) or defined( 'VHOST' ) or
  #      defined( 'SUNRISE' )):
  #    return True
  #  return False

  def get_current_blog_id(self):
    ''' Retrieve the current site ID.
    @global int blog_id
    @return int Site ID.
    '''
    #global blog_id
    #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable[],{},ODict
    return Php.absint(self.blog_id)


  def get_current_network_id(self):
    ''' Retrieves the current network ID.
    @return int The ID of the current network.
    '''
    return self.Bj.SId

    if not self.is_multisite():
      return 1

    current_network = get_network(self)

    if not Php.isset( current_network, 'id' ):
      return get_main_network_id(self)

    return Php.absint( current_network.id )

  #better change from class method var to instance method var
  #@Php.static_vars( loaded = False )  #can't static_var in cls method var
  def wp_load_translations_early(self):
    ''' Attempt an early load of translations.
    Used for errors encountered during the initial loading process, before
    the locale has been properly detected and loaded.
    Designed for unusual load sequences (like setup-config.php) or for when
    the script will then terminate with an error, otherwise there is a risk
    that a file can be double-included.
    @global WP_Locale wp_locale The WordPress date and time locale object.
    @staticvar bool loaded
    '''
    #global wp_locale

    #better change from class method var to instance method var
    ##static loaded = False   #set @Php.statc_vars above
    #if WiLoad.wp_load_translations_early.loaded:
    #  return
    #WiLoad.wp_load_translations_early.loaded = True
    if not hasattr(self, 'loaded'):
      self.loaded = False
    if self.loaded:
      return
    self.loaded = True

    return
    #if Php.function_exists( 'did_action' ) and did_action( 'init' ):
    #  return

    # We need wp_local_package
    #require ABSPATH . WPINC . '/version.php'

    # Translation and localization
    #require_once ABSPATH . WPINC . '/pomo/mo.php'
    #require_once ABSPATH . WPINC . '/l10n.php'
    'import wp.i.l10n'
    #require_once ABSPATH . WPINC . '/class-wp-locale.php'
    #require_once ABSPATH . WPINC . '/class-wp-locale-switcher.php'

    # General libraries
    #require_once ABSPATH . WPINC . '/plugin.php'

    #locales = locations = array()

    #while ( True ) {
    #  if defined( 'WPLANG' ):
    #    if '' == WPLANG:
    #      break
    #    locales[] = WPLANG

    #  if isset( wp_local_package ):
    #    locales[] = wp_local_package

    #  if not locales:
    #    break

    #  if defined( 'WP_LANG_DIR' ) and @is_dir( WP_LANG_DIR ):
    #    locations[] = WP_LANG_DIR

    #  if defined( 'WP_CONTENT_DIR' ) and @is_dir( WP_CONTENT_DIR . '/languages' ):
    #    locations[] = WP_CONTENT_DIR . '/languages'

    #  if @is_dir( ABSPATH . 'wp-content/languages' ):
    #    locations[] = ABSPATH . 'wp-content/languages'

    #  if @is_dir( ABSPATH . WPINC . '/languages' ):
    #    locations[] = ABSPATH . WPINC . '/languages'

    #  if not locations:
    #    break

    #  locations = Php.array_unique( locations )

    #  for locale in locales:
    #    for location in locations:
    #      if file_exists( location . '/' . locale . '.mo' ):
    #        load_textdomain( 'default', location . '/' . locale . '.mo' )
    #        if defined( 'WP_SETUP_CONFIG' ) and file_exists( location . '/admin-' . locale . '.mo' ):
    #          load_textdomain( 'default', location . '/admin-' . locale . '.mo' )
    #        break 2
    #  break

    #self.wp_locale = new WP_Locale(self)


  #@Php.static_vars( installing = None )  #can't static_var in cls method var
  #def wp_installing( is_installing = None ):
  #  ''' Check or set whether WordPress is in "installation" mode.
  #  If the `WP_INSTALLING` constant is defined during the bootstrap, `wp_installing(self)` will default to `True`.
  #  @staticvar bool installing
  #  @param bool is_installing Optional. True to set WP into Installing mode, False to turn Installing mode off.
  #                             Omit this parameter if you only want to fetch the current status.
  #  @return bool True if WP is installing, otherwise False. When a `is_installing` is passed, the function will
  #               report whether WP was in installing mode prior to the change to `is_installing`.
  #  '''
  #  #static installing = None   #set @Php.statc_vars above
  #  self.installing = None      #set @Php.statc_vars above
  #
  #  # Support for the `WP_INSTALLING` constant, defined before WP is loaded.
  #  if self.installing is None:
  #    self.installing = defined( 'WP_INSTALLING' ) and WP_INSTALLING
  #
  #  if is_installing is not None:
  #    old_installing = self.installing
  #    self.installing = is_installing
  #    return (bool) old_installing
  #
  #  return (bool) self.installing
  
  
  def is_ssl(self):
    ''' Determines if SSL is used.
    @return bool True if SSL, otherwise False.
    '''
    #if isset( _SERVER['HTTPS'] ):
    #  if 'on' == strtolower( _SERVER['HTTPS'] ):
    #    return True
  
    #  if '1' == _SERVER['HTTPS']:
    #    return True
    #elif isset(_SERVER['SERVER_PORT'] ) and ( '443' == _SERVER['SERVER_PORT'] ):
    #  return True
    return False
  
  
  #def wp_convert_hr_to_bytes( value ):
  #  ''' Converts a shorthand byte value to an integer byte value.
  #  php.net/manual/en/function.ini-get.php
  #  php.net/manual/en/faq.using.php#faq.using.shorthandbytes
  #  @param string value A (PHP ini) byte value, either shorthand or ordinary.
  #  @return int An integer byte value.
  #  '''
  #  value = strtolower( trim( value ) )
  #  bytes = (int) value
  #
  #  if False != strpos( value, 'g' ):
  #    bytes *= GB_IN_BYTES
  #  elif False != strpos( value, 'm' ):
  #    bytes *= MB_IN_BYTES
  #  elif False != strpos( value, 'k' ):
  #    bytes *= KB_IN_BYTES
  #
  #  # Deal with large (float) values which run into the maximum integer size.
  #  return min( bytes, PHP_INT_MAX )
  #
  #
  #@Php.static_vars( ini_all = None )  #can't static_var in cls method var
  #def wp_is_ini_value_changeable( setting ):
  #  ''' Determines whether a PHP ini value is changeable at runtime.
  #  @link https://secure.php.net/manual/en/function.ini-get.php
  #  @param string setting The name of the ini setting to check.
  #  @return bool True if the value is changeable at runtime. False otherwise.
  #  '''
  #  #static ini_all   #set @Php.statc_vars above
  #  self.ini_all
  #
  #  if not isset( self.ini_all ):
  #    self.ini_all = False
  #    # Sometimes `ini_get_all(self)` is disabled via the `disable_functions` option for "security purposes".
  #    if Php.function_exists( 'ini_get_all' ):
  #      self.ini_all = ini_get_all(self)
  #
  #  # Bit operator to workaround https://bugs.php.net/bug.php?id=44936 which changes access level to 63 in PHP 5.2.6 - 5.2.17.
  #  if isset( self.ini_all[ setting ]['access'] ) and ( INI_ALL == ( self.ini_all[ setting ]['access'] & 7 ) or INI_USER == ( self.ini_all[ setting ]['access'] & 7 ) ):
  #    return True
  #
  #  # If we were unable to retrieve the details, fail gracefully to assume it's changeable.
  #  if not is_array( self.ini_all ):
  #    return True
  #
  #  return False

  def wp_doing_ajax(self):
    ''' Determines whether the current request is a WordPress Ajax request.
    @return bool True if it's a WordPress Ajax request, false otherwise.
    '''
    import wp.i.plugin as WiPg
    # Filters whether the current request is a WordPress Ajax request.
    # @param bool wp_doing_ajax Whether the current request is a WP Ajax request
    return WiPg.apply_filters( 'wp_doing_ajax',
                              self.defined( 'DOING_AJAX' ) and self.DOING_AJAX )

  @staticmethod
  def is_wp_error(thing):
    ''' Check whether variable is a WordPress Error.
    Returns true if thing is an object of the WP_Error class.
    @param mixed thing Check if unknown variable is a WP_Error object.
    @return bool True, if WP_Error. False, if not WP_Error.
    usage: from wp.conf import Wj; Wj.is_wp_error()
    '''
    import wp.i.cls.error as WcE
    return isinstance(thing, WcE.WP_Error)



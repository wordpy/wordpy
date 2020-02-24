import pyx.php      as Php
import wp.i.option  as WiO

# Defines constants and global variables that can be overridden, generally in wp-config.php.
# @package WordPress
# Defines initial WordPress constants
# @see wp_debug_mode()
# @global int blog_id  # VT change to self.blog_id

def wp_initial_constants(self):
  #global blog_id  # VT change to self.blog_id

  # Constants for expressing human-readable data sizes in their respective number of bytes.
  self.define( 'KB_IN_BYTES', 1024 )
  self.define( 'MB_IN_BYTES', 1024 * self.KB_IN_BYTES )
  self.define( 'GB_IN_BYTES', 1024 * self.MB_IN_BYTES )
  self.define( 'TB_IN_BYTES', 1024 * self.GB_IN_BYTES )

  #current_limit     = @ini_get( 'memory_limit' )
  #current_limit_int = wp_convert_hr_to_bytes( current_limit )

  ## Define memory limits.
  #if not self.defined( 'WP_MEMORY_LIMIT' ):
  #  if False is wp_is_ini_value_changeable( 'memory_limit' ):
  #    self.define( 'WP_MEMORY_LIMIT', current_limit )
  #  elif WB.Wj.is_multisite():
  #    self.define( 'WP_MEMORY_LIMIT', '64M' )
  #  else:
  #    self.define( 'WP_MEMORY_LIMIT', '40M' )

  #if not self.defined( 'WP_MAX_MEMORY_LIMIT' ):
  #  if False is wp_is_ini_value_changeable( 'memory_limit' ):
  #    self.define( 'WP_MAX_MEMORY_LIMIT', current_limit )
  #  elif -1 == current_limit_int or current_limit_int > 268435456:
  #    self.define( 'WP_MAX_MEMORY_LIMIT', current_limit )   #268435456 = 256M
  #  else:
  #    self.define( 'WP_MAX_MEMORY_LIMIT', '256M' )

  ## Set memory limits.
  #wp_limit_int = wp_convert_hr_to_bytes( self.WP_MEMORY_LIMIT )
  #if -1 != current_limit_int and ( -1 == wp_limit_int or wp_limit_int > current_limit_int ):
  #  @ini_set( 'memory_limit', self.WP_MEMORY_LIMIT )

  #if not isset(blog_id):
  if not Php.isset(self, 'blog_id'):
    self.blog_id = 1

  if not self.defined('WP_CONTENT_DIR'):
    self.define( 'WP_CONTENT_DIR', self.ABSPATH + 'wp-content' ); # no trailing slash, full paths only - WP_CONTENT_URL is self.defined further down

  # Add self.define('WP_DEBUG', True); to wp-config.php to enable display of notices during development.
  if not self.defined('WP_DEBUG'):
    self.define( 'WP_DEBUG', False )

  # Add self.define('WP_DEBUG_DISPLAY', null); to wp-config.php use the globally configured setting for
  # display_errors and not force errors to be displayed. Use False to force display_errors off.
  if not self.defined('WP_DEBUG_DISPLAY'):
    self.define( 'WP_DEBUG_DISPLAY', True )

  # Add self.define('WP_DEBUG_LOG', True); to enable error logging to wp-content/debug.log.
  if not self.defined('WP_DEBUG_LOG'):
    self.define('WP_DEBUG_LOG', False)

  if not self.defined('WP_CACHE'):
    self.define('WP_CACHE', False)

  # Add self.define('SCRIPT_DEBUG', True); to wp-config.php to enable loading of non-minified,
  # non-concatenated scripts and stylesheets.
  if not self.defined( 'SCRIPT_DEBUG' ):
    #if not empty( GLOBALS['wp_version'] ):
    if not Php.empty( self, 'wp_version' ):
      #develop_src = False !== strpos( GLOBALS['wp_version'], '-src' )
      develop_src = '-src' in self.wp_version
    else:
      develop_src = False

    self.define( 'SCRIPT_DEBUG', develop_src )

  # Private
  if not self.defined('MEDIA_TRASH'):
    self.define('MEDIA_TRASH', False)

  if not self.defined('SHORTINIT'):
    self.define('SHORTINIT', False)

  # Constants for features added to WP that should short-circuit their plugin implementations
  self.define( 'WP_FEATURE_BETTER_PASSWORDS', True )

  # Constants for expressing human-readable intervals
  # in their respective number of seconds.
  # Please note that these values are approximate and are provided for convenience.
  # For example, MONTH_IN_SECONDS wrongly assumes every month has 30 days and
  # YEAR_IN_SECONDS does not take leap years into account.
  # If you need more accuracy please consider using the DateTime class (https://secure.php.net/manual/en/class.datetime.php).
  self.define( 'MINUTE_IN_SECONDS', 60 )
  self.define( 'HOUR_IN_SECONDS',   60 * self.MINUTE_IN_SECONDS )
  self.define( 'DAY_IN_SECONDS',    24 * self.HOUR_IN_SECONDS   )
  self.define( 'WEEK_IN_SECONDS',    7 * self.DAY_IN_SECONDS    )
  self.define( 'MONTH_IN_SECONDS',  30 * self.DAY_IN_SECONDS    )
  self.define( 'YEAR_IN_SECONDS',  365 * self.DAY_IN_SECONDS    )


def wp_plugin_directory_constants(self):
  ''' Defines plugin directory WordPress constants
  Defines must-use plugin directory constants, which may be overridden in the sunrise.php drop-in
  '''
  if not self.defined('WP_CONTENT_URL'):
    self.define( 'WP_CONTENT_URL', WiO.get_option('siteurl') + '/wp-content'); # full url - WP_CONTENT_DIR is self.defined further up

  # Allows for the plugins directory to be moved from the default location.
  if not self.defined('WP_PLUGIN_DIR'):
    self.define( 'WP_PLUGIN_DIR', self.WP_CONTENT_DIR + '/plugins' ); # full path, no trailing slash

  # Allows for the plugins directory to be moved from the default location.
  if not self.defined('WP_PLUGIN_URL'):
    self.define( 'WP_PLUGIN_URL', self.WP_CONTENT_URL + '/plugins' ); # full url, no trailing slash

  # Allows for the plugins directory to be moved from the default location.
  if not self.defined('PLUGINDIR'):
    self.define( 'PLUGINDIR', 'wp-content/plugins' ); # Relative to ABSPATH+ For back compat.

  # Allows for the mu-plugins directory to be moved from the default location.
  if not self.defined('WPMU_PLUGIN_DIR'):
    self.define( 'WPMU_PLUGIN_DIR', self.WP_CONTENT_DIR + '/mu-plugins' ); # full path, no trailing slash

  # Allows for the mu-plugins directory to be moved from the default location.
  if not self.defined('WPMU_PLUGIN_URL'):
    self.define( 'WPMU_PLUGIN_URL', self.WP_CONTENT_URL + '/mu-plugins' ); # full url, no trailing slash

  # Allows for the mu-plugins directory to be moved from the default location.
  if not self.defined( 'MUPLUGINDIR' ):
    self.define( 'MUPLUGINDIR', 'wp-content/mu-plugins' ); # Relative to ABSPATH+ For back compat.


def wp_cookie_constants(self):
  ''' Defines cookie related WordPress constants
  Defines constants after multisite is loaded.
  '''
  # Used to guarantee unique hash cookies
  if not self.defined( 'COOKIEHASH' ):
    siteurl = WiO.get_site_option( 'siteurl' )
    if siteurl:
      self.define( 'COOKIEHASH', Php.md5( siteurl ) )
    else:
      self.define( 'COOKIEHASH', Php.md5( wp_guess_url() ) )

  if not self.defined('USER_COOKIE'):
    self.define('USER_COOKIE', 'wordpressuser_' + self.COOKIEHASH)

  if not self.defined('PASS_COOKIE'):
    self.define('PASS_COOKIE', 'wordpresspass_' + self.COOKIEHASH)

  if not self.defined('AUTH_COOKIE'):
    self.define('AUTH_COOKIE', 'wordpress_' + self.COOKIEHASH)

  if not self.defined('SECURE_AUTH_COOKIE'):
    self.define('SECURE_AUTH_COOKIE', 'wordpress_sec_' + self.COOKIEHASH)

  if not self.defined('LOGGED_IN_COOKIE'):
    self.define('LOGGED_IN_COOKIE', 'wordpress_logged_in_' + self.COOKIEHASH)

  if not self.defined('TEST_COOKIE'):
    self.define('TEST_COOKIE', 'wordpress_test_cookie')

  if not self.defined('COOKIEPATH'):
    self.define('COOKIEPATH', Php.preg_replace('|https?://[^/]+|i', '', WiO.get_option('home') + '/' ) )

  if not self.defined('SITECOOKIEPATH'):
    self.define('SITECOOKIEPATH', Php.preg_replace('|https?://[^/]+|i', '', WiO.get_option('siteurl') + '/' ) )

  if not self.defined('ADMIN_COOKIE_PATH'):
    self.define( 'ADMIN_COOKIE_PATH', self.SITECOOKIEPATH + 'wp-admin' )

  if not self.defined('PLUGINS_COOKIE_PATH'):
    self.define( 'PLUGINS_COOKIE_PATH', Php.preg_replace('|https?://[^/]+|i', '', self.WP_PLUGIN_URL)  )

  if not self.defined('COOKIE_DOMAIN'):
    self.define('COOKIE_DOMAIN', False)


def wp_ssl_constants(self):
  ''' Defines cookie related WordPress constants
  '''
  pass
  #if not self.defined( 'FORCE_SSL_ADMIN' ) ):
  #  if 'https' == parse_url( WiO.get_option( 'siteurl' ), PHP_URL_SCHEME ):
  #    self.define( 'FORCE_SSL_ADMIN', True )
  #  else:
  #    self.define( 'FORCE_SSL_ADMIN', False )

  #force_ssl_admin( FORCE_SSL_ADMIN )

  #if self.defined( 'FORCE_SSL_LOGIN' ) and FORCE_SSL_LOGIN:
  #  force_ssl_admin( True )


def wp_functionality_constants(self):
  ''' Defines functionality related WordPress constants
  '''
  if not self.defined( 'AUTOSAVE_INTERVAL' ):
    self.define( 'AUTOSAVE_INTERVAL', 60 )

  if not self.defined( 'EMPTY_TRASH_DAYS' ):
    self.define( 'EMPTY_TRASH_DAYS', 30 )

  if not self.defined('WP_POST_REVISIONS'):
    self.define('WP_POST_REVISIONS', True)

  if not self.defined( 'WP_CRON_LOCK_TIMEOUT' ):
    self.define('WP_CRON_LOCK_TIMEOUT', 60);  # In seconds


def wp_templating_constants(self):
  ''' Defines templating related WordPress constants
  '''
  # Filesystem path to the current active template directory
  #self.define('TEMPLATEPATH', get_template_directory())

  # Filesystem path to the current active template stylesheet directory
  #self.define('STYLESHEETPATH', get_stylesheet_directory())

  # Slug of the default theme for this install.
  # Used as the default theme when installing new sites.
  # It will be used as the fallback if the current theme doesn't exist.
  # @see WP_Theme::get_core_default_theme()
  if not self.defined('WP_DEFAULT_THEME'):
    self.define( 'WP_DEFAULT_THEME', 'twentyseventeen' )



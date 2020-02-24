import wp.conf    as WpC
import pyx.php    as Php
array = Php.array

def ms_settings(self):
  ''' Used to set up and fix common variables and include
  the Multisite procedural and class library.
  Allows for some config in wp-config.php (see ms-default-constants.php)
  @package WordPress   @subpackage Multisite
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable[],{},ODict
  #wpdb = WpC.WB.Wj.wpdb

  # need to init cache again after blog_id is set
  self.wp_start_object_cache()     # Moved from below

  self._SERVER = array( ('HTTP_HOST'  , self.Bj.BSFQDN),
                        ('REQUEST_URI', ''            ), )

  return self

  # Objects representing the current network and current site.
  # These may be populated through a custom `sunrise.php`. If not, then this
  # file will attempt to populate them based on the current request.
  # @global WP_Network current_site The current network.
  # @global object     current_blog The current site.
  #global current_site, current_blog
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable[],{},ODict
  self.current_site = self.current_blog = None

  # WP_Network class
  "import wp.i.class.wp_network"      # WPINC . '/class-wp-network.php'

  # WP_Site class
  "import wp.i.class.wp_site"         # WPINC . '/class-wp-site.php'

  # Multisite loader
  "import wp.i.ms_load"               # WPINC . '/ms-load.php'

  # Default Multisite constants
  "import wp.i.ms_default_constants"  # WPINC . '/ms-default-constants.php'

  #if defined( 'SUNRISE' ):
  #if self.defined('SUNRISE'):
  #  import wp.c.sunrise             # WP_CONTENT_DIR . '/sunrise.php'

  # Check for and define SUBDOMAIN_INSTALL and the deprecated VHOST constant.
  "ms_subdomain_constants()"
  
  # This block will process a request if the current network or current site objects
  # have not been populated in the global scope through something like `sunrise.php`.
  if not Php.isset(self,'current_site') or not Php.isset(self,'current_blog'):
  
    domain = Php.stripslashes( self._SERVER['HTTP_HOST'] ).lower()
    if Php.substr( domain, -3 ) == ':80':
      domain = Php.substr( domain, 0, -3 )
      self._SERVER['HTTP_HOST'] = Php.substr(self._SERVER['HTTP_HOST'], 0, -3)
    elif Php.substr( domain, -4 ) == ':443':
      domain = Php.substr( domain, 0, -4 )
      self._SERVER['HTTP_HOST'] = Php.substr(self._SERVER['HTTP_HOST'], 0, -4)
  
    path = Php.stripslashes( self._SERVER['REQUEST_URI'] )
    #if is_admin():
    #  path = preg_replace( '#(.*)/wp-admin/.*#', '1/', path )
    #list( path ) = explode( '?', path )
    path = path.split('?')
  
    bootstrap_result = ms_load_current_site_and_network(
                       domain, path, is_subdomain_install() )
  
    if True == bootstrap_result:
      pass # `self.current_blog` and `self.current_site are now populated.
    elif False == bootstrap_result:
      ms_not_installed( domain, path )
    else:
      #header( 'Location: ' + bootstrap_result )
      import sys
      sys.exit()
    del bootstrap_result
  
    blog_id = self.current_blog.blog_id
    public  = self.current_blog.public
  
    if Php.empty(self.current_blog, 'site_id'):
      # This dates to [MU134] and shouldn't be relevant anymore,
      # but it could be possible for arguments passed to insert_blog() etc.
      self.current_blog.site_id = 1
  
    site_id = self.current_blog.site_id
    wp_load_core_site_options( site_id )
  
  wpdb.set_prefix( table_prefix, False ) # table_prefix can be set in sunrise.php
  wpdb.set_blog_id( self.current_blog.blog_id, self.current_blog.site_id )
  table_prefix = wpdb.get_blog_prefix()
  _wp_switched_stack = array()
  switched = False
  
  # need to init cache again after blog_id is set
  #wp_start_object_cache()  moved to above, should move down here
  
  if not isinstance(self.current_site, WP_Network):
    self.current_site = WP_Network( self.current_site )
  
  if not isinstance(self.current_blog, WP_Site):
    self.current_blog = WP_Site( self.current_blog )
  
  # Define upload directory constants
  ms_upload_constants()
  
  # Fires after the current site and network have been detected and loaded
  # in multisite's bootstrap.
  #do_action( 'ms_loaded' )

  return self

import pyx.php      as Php
array = Php.array
#import wp.i.ms_load as WiML                # done in wp.i.ms_settings as WiMS
#import wp.i.ms_default_constants as WiMD   # done in wp.i.ms_settings as WiMS


def wp_settings(self):
  ''' Used to set up and fix common variables and include
  the WordPress procedural and class library.
  Allows for some configuration in wp-config.php (see default-constants.php)
  @package WordPress
  '''
  
  self.GLOBALS = self.__dict__  # = WB.Wj.__dict__
  ''' Stores location of WP directory of functions, classes, and core content.
  '''
  self.WPINC = 'i'  # 'wp-includes'
  
  # Include files required for initialization.
  "import wp.i.load as WiL"         # WiL imported in wpy.web
  import wp.i.default_constants as WiD   # default-constants.php
  #import wp.i.plugin as WiPg
  #WiPg.InitFilterGlobals(self)
  if not isinstance(getattr(self, 'wp_filter',        None), array):
    self.wp_filter  = array()  # array()
  if not isinstance(getattr(self, 'wp_actions',       None), array):
    self.wp_actions = array()  # array()
  if not isinstance(getattr(self, 'merged_filters',   None), array):
    self.merged_filters = array()  # array()
  if not isinstance(getattr(self, 'wp_current_filter',None), list ):
    self.wp_current_filter = array()
  
  ''' These can't be directly globalized in version.php. When updating,
   we're including version.php from another install and don't want
   these values to be overridden if already set.
  '''
  #self.wp_version = self.wp_db_version = self.tinymce_version = self.required_php_version = self.required_mysql_version = self.wp_local_package = None
  import wp.i.version as WpV  # version.php
  WpV.InitVersions(self)

  
  ''' If not already configured, `blog_id` will default to 1 in a single site
   config. In multisite, it will be overridden by default in ms-settings.php.
   @global int blog_id
  '''
  self.blog_id = getattr(self, 'blog_id', 1)
  
  #Set initial default constants including WP_MEMORY_LIMIT,
  #  WP_MAX_MEMORY_LIMIT, WP_DEBUG, SCRIPT_DEBUG, WP_CONTENT_DIR and WP_CACHE.
  WiD.wp_initial_constants(self)
  
  # Check for the required PHP ver and for the MySQL extension or a db drop-in.
  #self.wp_check_php_mysql_versions()  # in WiL
  
  # Disable magic quotes at runtime. Magic quotes are added using wpdb later
  #   in wp-settings.php.
  #@ini_set( 'magic_quotes_runtime', 0 )
  #@ini_set( 'magic_quotes_sybase',  0 )
  
  # WordPress calculates offsets from UTC.
  Php.date_default_timezone_set( 'UTC' )
  # weston.ruter.net/2013/04/02/do-not-change-the-default-timezone-from-utc-in-wordpress/
  # [Default tz hardcoded as UTC]wordpress.stackexchange.com/questions/30946/
  
  # Turn register_globals off.
  #self.wp_unregister_GLOBALS()  # in WiL
  
  # Standardize _SERVER variables across setups.
  #self.wp_fix_server_vars()  # in WiL
  
  # Check if we have received a request due to missing favicon.ico
  #self.wp_favicon_request()  # in WiL
  
  # Check if we're in maintenance mode.
  #self.wp_maintenance()  # in WiL
  
  # Start loading timer.
  #self.timer_start()  # in WiL
  
  # Check if we're in WP_DEBUG mode.
  #self.wp_debug_mode()  # in WiL
  
  ''' Filters whether to enable loading of the advanced-cache.php drop-in.
  This filter runs before it can be used by plugins. It is designed for non-web
  run-times. If False is returned, advanced-cache.php will never be loaded.
  @param bool enable_advanced_cache Whether to enable loading advanced-cache.php
                                     (if present).  Default True.
  '''
  #if WP_CACHE and apply_filters('enable_loading_advanced_cache_dropin',True):
  ## For an advanced caching plugin to use. Uses a static drop-in because you
  ##    would only want one.
  #  if WP_DEBUG:
  #    import wp.c.advanced-cache.php:
  #  else:
  #    import wp.c.advanced-cache.php #suppress error for 2nd import

  # Define WP_LANG_DIR if not set.
  #self.wp_set_lang_dir()  # in WiL
  
  # Load early WordPress files.
  #import wp.i.compat
  #import wp.i.cls.list_util       # class-wp-list-util.php'
  #import wp.i.func                # functions.php
  #import wp.i.cls.matchesmapregex # class-wp-matchesmapregex.php
  import wp.i.cls.wp  as WcW       # class-wp.php
  import wp.i.cls.error as WcE     # class-wp-error.php
  #import wp.i.pomo.mo
  #import wp.i.cls.phpass          # class-phpass.php
  
  # Include the wpdb class and, if present, a db.php database drop-in.
  #wpdb = WB.Wj.wpdb  # global wpdb
  self.require_wp_db()  # in WiL
  
  # Set the database table prefix and the format specifiers for database table columns.
  #GLOBALS['table_prefix'] = table_prefix
  #table_prefix set in wp.conf.WpConfCls
  #table_prefix = self.table_prefix   #Only use self.global_vars
  self.wp_set_wpdb_vars()  # in WiL
  
  # Start the WordPress object cache, or an external object cache if the drop-in is present.
  #wp_start_object_cache()
  
  # Attach the default filters.
  import wp.i.default_filters as DFilters   # default-filters.php
  DFilters.default_filters(self)
  
  # Initialize multisite if enabled.
  if self.is_multisite():  # in WiL
    self.MULTISITE = True
    # import wp.i.class_wp_site_query       # class-wp-site-query.php
    # import wp.i.class_wp_network_query    # class-wp-network-query.php
    # import wp.i.ms_blogs                  # ms-blogs.php
    import wp.i.ms_settings as WiMS         # ms-settings.php
    self = WiMS.ms_settings(self)
  elif not hasattr(self, 'MULTISITE'):
    self.MULTISITE = False
  
  #register_shutdown_function( 'shutdown_action_hook' )
  
  # Stop most of WordPress from being loaded if we just want the basics.
  #if SHORTINIT:
  #  return False
  
  # Load the L10n library.
  #import wp.i.l10n as WiL1
  #import wp.i.cls.locale                # class-wp-locale.php
  #import wp.i.cls.locale_switcher       # class-wp-locale-switcher.php
  
  # Run the installer if WordPress is not installed.
  #self.wp_not_installed()  # in WiL
  
  # Load most of WordPress.
  #import wp.i.class_wp_walker
  #import wp.i.class_wp_ajax_response
  #import wp.i.formatting
  #import wp.i.capabilities
  #import wp.i.class_wp_roles
  #import wp.i.class_wp_role
  #import wp.i.class_wp_user
  #import wp.i.class_wp_query
  #import wp.i.query
  #import wp.i.date
  "import wp.i.theme           as WiTheme"
  #import wp.i.class_wp_theme
  #import wp.i.template
  #import wp.i.user
  #import wp.i.class_wp_user_query
  #import wp.i.class-wp-session-tokens  # class-wp-session-tokens.php
  #import wp.i.meta
  #import wp.i.class_wp_meta_query
  #import wp.i.class_wp_metadata_lazyloader
  #import wp.i.general_template
  import wp.i.link_template   as WiLT
  #import wp.i.author_template
  import wp.i.post            as WiP
  #import wp.i.class_walker_page
  #import wp.i.class_walker_page_dropdown
  #import wp.i.class_wp_post_type
  #import wp.i.class_wp_post
  #import wp.i.post_template
  #import wp.i.revision
  #import wp.i.post_formats
  #import wp.i.post_thumbnail_template
  #import wp.i.category
  #import wp.i.class_walker_category
  #import wp.i.class_walker_category_dropdown
  #import wp.i.category_template
  #import wp.i.comment
  #import wp.i.class_wp_comment
  #import wp.i.class_wp_comment_query
  #import wp.i.class_walker_comment
  #import wp.i.comment_template
  #import wp.i.rewrite
  import wp.i.cls.rewrite   as WcR
  #import wp.i.feed
  #import wp.i.bookmark
  #import wp.i.bookmark_template
  #import wp.i.kses
  #import wp.i.cron
  #import wp.i.deprecated
  #import wp.i.script_loader
  import wp.i.taxonomy            as WiT
  #import wp.i.class-wp-taxonomy   # class-wp-taxonomy.php
  #import wp.i.class_wp_term
  #import wp.i.class_wp_term_query
  #import wp.i.class_wp_tax_query
  #import wp.i.update
  #import wp.i.canonical
  #import wp.i.shortcodes
  #import wp.i.embed
  #import wp.i.class_wp_embed
  #import wp.i.class_embed
  #import wp.i.class_wp_oembed_controller
  #import wp.i.media
  #import wp.i.http
  #import wp.i.class_http
  #import wp.i.cls.http            as WcH  #import wp.i.class_wp_http_streams
  #import wp.i.class_wp_http_curl
  #import wp.i.class_wp_http_proxy
  #import wp.i.class_wp_http_cookie
  #import wp.i.class_wp_http_encoding
  #import wp.i.class_wp_http_response
  #import wp.i.class_wp_http_requests_response
  #import wp.i.class-wp-http-requests-hooks # class-wp-http-requests-hooks.php
  #import wp.i.widgets
  #import wp.i.class_wp_widget
  #import wp.i.class_wp_widget_factory
  #import wp.i.nav_menu
  #import wp.i.nav_menu_template
  #import wp.i.admin_bar
  #import wp.i.rest_api
  #import wp.i.rest_api.class_wp_rest_server
  #import wp.i.rest_api.class_wp_rest_response
  #import wp.i.rest_api.class_wp_rest_request

  #import wp.i.rest-api/endpoints/class-wp-rest-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-posts-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-attachments-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-post-types-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-post-statuses-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-revisions-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-taxonomies-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-terms-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-users-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-comments-controller.php
  #import wp.i.rest-api/endpoints/class-wp-rest-settings-controller.php
  #import wp.i.rest-api/fields/class-wp-rest-meta-fields.php
  #import wp.i.rest-api/fields/class-wp-rest-comment-meta-fields.php
  #import wp.i.rest-api/fields/class-wp-rest-post-meta-fields.php
  #import wp.i.rest-api/fields/class-wp-rest-term-meta-fields.php
  #import wp.i.rest-api/fields/class-wp-rest-user-meta-fields.php
  #GLOBALS['wp_embed'] = WP_Embed()
  
  # Load multisite_specific files.
  #if self.is_multisite():  # in WiL
  #  import wp.i.ms_functions
  #  import wp.i.ms_default_filters
  #  import wp.i.ms_deprecated
  
  # Define constants that rely on the API to obtain the default value.
  # Define must_use plugin directory constants, which may be overridden in the sunrise.php drop-in.
  WiD.wp_plugin_directory_constants(self)
  
  self.wp_plugin_paths = array() # GLOBALS['wp_plugin_paths'] = array()
  
  # Load must_use plugins.
  #for mu_plugin in self.wp_get_mu_plugins():  # in WiL
  #  importlib.import_module( mu_plugin ) # include_once( mu_plugin )
  #del mu_plugin
  
  # Load network activated plugins.
  #if self.is_multisite():  # in WiL
  #  for network_plugin in WiML.wp_get_active_network_plugins(self):
  #    WiPg.wp_register_plugin_realpath( network_plugin )
  #    importlib.import_module(network_plugin) # include_once(network_plugin)
  #  del network_plugin
  
  ''' Fires once all must_use and network-activated plugins have loaded.
  '''
  #self.do_action( 'muplugins_loaded' )
  
  #if self.is_multisite():  # in WiL
  #  WiMD.ms_cookie_constants(self)
  
  # Define constants after multisite is loaded.
  WiD.wp_cookie_constants(self)
  
  # Define and enforce our SSL constants
  WiD.wp_ssl_constants(self)
  
  # Create common globals.
  #import wp.i.vars
  
  # Make taxonomies and posts available to plugins and themes.
  # @plugin authors: warning: these get registered again on the init hook.
  #move the following to after int: self.wp_rewrite = WcR.WP_Rewrite()
  #WiT.create_initial_taxonomies(self)
  #move the following to after int: self.post_type_meta_caps
  
  # Register the default theme directory root
  #WiTheme.register_theme_directory( get_theme_root(self) )
  
  # Load active plugins.
  #for plugin in wp_get_active_and_valid_plugins(self):
  #  WiPg.wp_register_plugin_realpath( plugin )
  #  importlib.import_module( plugin )     # include_once( plugin )
  #del plugin
  
  # Load pluggable functions.
  #import wp.i.pluggable
  #import wp.i.pluggable_deprecated
  
  # Set internal encoding.
  self.wp_set_internal_encoding()  # in WiL
  
  # Run wp_cache_postload() if object cache is enabled and the func exists.
  #if WP_CACHE and Php.function_exists( 'wp_cache_postload' ):
  #  wp_cache_postload()
  
  ''' Fires once activated plugins have loaded.
  Pluggable functions are also available at this point in the loading order.
  '''
  #self.do_action( 'plugins_loaded' )
  
  # Define constants which affect functionality if not already defined.
  WiD.wp_functionality_constants(self)
  
  # Add magic quotes and set up _REQUEST ( _GET + _POST )
  #self.wp_magic_quotes()  # in WiL
  
  ## Fires when comment cookies are sanitized.
  #self.do_action( 'sanitize_comment_cookies' )
  
  ## WordPress Query object
  #@global WP_Query wp_the_query
  ##GLOBALS['wp_the_query'] = new WP_Query(self)
  self.wp_the_query = None   # should = WP_Query(self) #TODO
  
  ## Holds the reference to @see wp_the_query
  ##Use this global for WordPress queries
  ##@global WP_Query wp_query
  #GLOBALS['wp_query'] = GLOBALS['wp_the_query']
  self.wp_query = self.wp_the_query
  
  ## Holds the WordPress Rewrite object for creating pretty URLs
  ##@global WP_Rewrite wp_rewrite
  ##GLOBALS['wp_rewrite'] = new WP_Rewrite()
  self.wp_rewrite = WcR.WP_Rewrite()    # Wj = self  #TODO Fixup

  ## WordPress Object
  ##@global WP wp
  #GLOBALS['wp'] = new WP(self)
  self.wp = WcW.WP()   # no need to pass self into WP like  WcW.WP(self)

  ###########################################################
  # Since self = WB.Wj, and all global vars = WB.Wj.vars,   #
  #     need to init global vars below                      #
  ###########################################################
  # Run below after int: wp_rewrite,  wp_query & wp_the_query
  #WcW.InitWpGlobals(self)
  # Run below after int: wp_taxonomies, wp, wp_rewrite

  #WiT.InitTaxonomyGlobals(self)
  if not Php.is_array(getattr(self, 'wp_taxonomies', None)):
    self.wp_taxonomies = array()

  #Run below after int: self.wp_rewrite = WcR.WP_Rewrite()
  WiT.create_initial_taxonomies(self)

  # Run after int: post_type_meta_caps, _wp_post_type_features, wp, wp_rewrite
  #WiP.InitPostGlobals(self)
  if not Php.is_array(getattr(self, 'wp_post_types',         None)):
    self.wp_post_types         = array()
  # wp-includes/capabilities.php
  if not Php.is_array(getattr(self, 'post_type_meta_caps',   None)):
    self.post_type_meta_caps   = array()
  if not Php.is_array(getattr(self, '_wp_post_type_features',None)):
    self._wp_post_type_features= array()
  if not Php.is_array(getattr(self, 'wp_post_statuses',      None)):
    self.wp_post_statuses      = array()
  #import wp.i.cls.post_type as WcPT
  #WcPT.InitPostTypesGlobals(self)

  # Run below after int: self.post_type_meta_caps
  #WiP.create_initial_post_types()
  WiP.create_initial_post_types(self)
  #WiLT.InitLinkTemplate(self)
  ###########################################################
  
  ## WordPress Widget Factory Object
  ##@global WP_Widget_Factory wp_widget_factory
  #GLOBALS['wp_widget_factory'] = new WP_Widget_Factory(self)
  self.wp_widget_factory = None  # should = WP_Widget_Factory(self) #TODO
  
  ## WordPress User Roles
  ##@global WP_Roles wp_roles
  #GLOBALS['wp_roles'] = new WP_Roles(self)
  self.wp_roles = None  # should = WP_Roles(self) #TODO
  
  ## Fires before the theme is loaded.
  #self.do_action( 'setup_theme' )
  
  # Define the template related constants.
  WiD.wp_templating_constants(self)
  
  # Load the default text localization domain.
  #WiL1.load_default_textdomain(self)
  
  #locale = get_locale(self)
  #locale_file = WP_LANG_DIR + "/locale.php"
  #if ( 0 == validate_file( locale ) ) and is_readable( locale_file ):
  #  importlib.import_module( locale_file )     # include_once( locale_file )
  #del locale_file
  
  # Pull in locale data after loading text domain.
  #import wp.i.locale
  
  ## WordPress Locale object for loading locale domain date and various strings
  ##@global WP_Locale wp_locale
  #GLOBALS['wp_locale'] = new WP_Locale(self)
  self.wp_locale = None    # should = WP_Locale(self) #TODO

  ##  WordPress Locale Switcher object for switching locales.
  ## @global WP_Locale_Switcher wp_locale_switcher WP locale switcher object.
  ## GLOBALS['wp_locale_switcher'] = WP_Locale_Switcher()
  #self.wp_locale_switcher = WP_Locale_Switcher()
  ## GLOBALS['wp_locale_switcher'].init()
  #self.wp_locale_switcher.init()
  
  ## Load functions for active theme, for parent & child theme if applicable.
  #if not self.wp_installing(self) or 'wp_activate.php' == pagenow:  # in WiL
  #  if TEMPLATEPATH != STYLESHEETPATH and os.path.isfile(
  #                     STYLESHEETPATH + '/functions.py' ):
  #    importlib.import_module( STYLESHEETPATH + '.functions' )
  #  if os.path.isfile( TEMPLATEPATH + '/functions.py' )
  #    importlib.import_module( TEMPLATEPATH + '.functions' )
  
  # Fires after the theme is loaded.
  #self.do_action( 'after_setup_theme' )
  
  # Set up current user.
  #GLOBALS['wp'].init(self)
  "self.wp.init(self)"  #= wp_get_current_user()  #TODO

  
  ## Fires after WordPress has finished loading but before any headers are sent.
  ## Most of WP is loaded at this stage, and the user is authenticated. WP continues
  ## to load on the {@see 'init'} hook that follows (e.g. widgets), and many plugins instantiate
  ## themselves on it for all sorts of reasons (e.g. they need a user, a taxonomy, etc.).
  ## If you wish to plug an action once WP is loaded, use the {@see 'wp_loaded'} hook below.
  #self.do_action( 'init' )
  
  ## Check site status
  #if self.is_multisite():  # in WiL
  #  file = ms_site_check(self):
  #  if True !=  file:
  #    require( file )
  #    importlib.import_module( file )
  #    die(self)
  #  del file
  
  ## This hook is fired once WP, all plugins, and the theme are fully loaded and instantiated.
  ## Ajax requests should use wp-admin/admin-ajax.php. admin-ajax.php can handle requests for
  ## users not logged in.
  ## @link https://codex.wordpress.org/AJAX_in_Plugins
  #self.do_action( 'wp_loaded' )


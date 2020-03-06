# Fixed all &value pass by reference, foreach

# [Rewrote GNU GPL v2 code in another language: can I change a license?](http://softwareengineering.stackexchange.com/questions/151515/)
# Original WordPress written in Php, https://wordpress.org/download/source/
# Copyright 2011-2017 by the contributors
# Python Version, line-by-line translated from wp.4.7.1 by Victor Tong
# Copyright (c) 2020 wordpy <info@wordpy.com>

import re, pymysql
import config.log as cLog; L = cLog.logger
import pyx.php    as Php
import pyx.type   as xTp
import wpy.db     as wDB
import wp.i.func  as WiFc
import wp.i.l10n  as WiTr
import wp.i.plugin as WiPg
import wp.i.cls.error as WcE  # WP_Error
array = Php.array
SqlCur, SqlConn, SqlErr = pymysql.cursors, pymysql.connections, pymysql.err
__, _x, _n_noop = WiTr.__, WiTr._x, WiTr._n_noop

EZSQL_VERSION = 'WP1.25'
OBJECT  = 'OBJECT'    #object = 'OBJECT'   # Back compat.
OBJECT_K= 'OBJECT_K'
ARRAY_A = 'ARRAY_A'
ARRAY_N = 'ARRAY_N'


def InitWpdbGlobals(self):
  #global wp_version,  required_mysql_version, EZSQL_ERROR   # , Wj
  #wp_version             = self.wp_version
  #required_mysql_version = self.required_mysql_version

  if not getattr(self, 'EZSQL_ERROR', None):
    self.EZSQL_ERROR = array()
  #EZSQL_ERROR   = self.EZSQL_ERROR
  #Wj = self


#class wpdb(xTp.SingletonBaseClass):
class wpdb_cls(Php.stdClass):
  ''' replicate from wp-includes/wp-db.php: class wpdb
      WordPress Database Access Abstraction Object
  PHP has static class vars. If not declared static, they are instance vars.
  Py:If only 1 instance, best to make all vars per-instance as it's bit faster
  PyMySQL convert all obj including int to formatted and quoted string.
    use only %s or %(name)s as placeholder.  Don't use %d.
  '''

  #public function __construct( dbuser, dbpassword, dbname, dbhost ) {
  def __init__(self, dbuser=None, dbpassword=None, dbname=None, dbhost=None,
               Wj=None):      # Dbj = None,
    ''' Connects to the database server and selects a database
    PHP5 style constructor for compatibility with PHP5. Does
    the actual setting up of the class properties and connection
    to the database.
    @link https://core.trac.wordpress.org/ticket/3354
    @since 2.0.8
    @global string wp_version
    @param string dbuser     MySQL database user
    @param string dbpassword MySQL database password
    @param string dbname     MySQL database name
    @param string dbhost     MySQL database host
    self.Bj = wpdb.Bj set in wpy.web.WpBlogCls
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    self.Wj   = Wj
    self.Bj   = None if Wj is None else Wj.Bj
    if Wj is None:
      self.Bj   = None
      self.AutoCommit = False
    else:
      self.Bj         = Wj.Bj
      self.AutoCommit = Wj.Bj.AutoCommit

    # Whether to show SQL/DB errors.
    # Default behavior is to show errors if both WP_DEBUG and WP_DEBUG_DISPLAY
    # evaluated to True.
    # @access private   @var bool
    self.show_errors = False

    # Whether to suppress errors during the DB bootstrapping.
    # @access private   @var bool
    self.suppress_errors = False

    # The last error during query.
    # @var string
    last_error = ''

    # Amount of queries made
    # @access public   @var int
    self.num_queries = 0

    # Count of rows returned by previous query
    # @access public   @var int
    self.num_rows = 0

    # Count of affected rows by previous query
    # @access private   @var int
    self.rows_affected = 0

    # The ID generated for an AUTO_INCREMENT column by the previous query (usually INSERT).
    # @access public   @var int
    self.insert_id = 0

    # Last query made
    # @access private   @var array
    #self.last_query = None   # Orig Empty

    # Results of the last query made
    # @access private   @var array|None
    #self.last_result = None   # Orig Empty

    # MySQL result, which is either a resource or boolean.
    # @access protected   @var mixed
    #self.result = None   # Orig Empty

    # Cached column info, for sanity checking data before inserting
    # @access protected   @var array
    self.col_meta = array()    #??  array()

    # Calculated character sets on tables
    # @access protected   @var array
    self.table_charset = array()    #??  array()

    # Whether text fields in the current query need to be sanity checked.
    # @access protected   @var bool
    self.check_current_query = True

     # Flag to ensure we don't run into recursion problems when checking the collation.
    # @access private   @var bool
    # @see self.check_safe_collation()
    self.checking_collation = False

    # Saved info on the table column
    # @access protected   @var array
    #self.col_info = None   # Orig Empty

    # Saved queries that were executed
    # @access private   @var array
    #self.queries = array()

    # The number of times to retry reconnecting before dying.
    # @access protected   @see self.check_connection()
    self.reconnect_retries = 5

    # WordPress table prefix
    # You can set this to have multiple WordPress installations
    # in a single database. The second reason is for possible
    # security precautions.
    # @access public   @var string
    self.prefix = ''

    #wp-settings.php: self.Wj.table_prefix = table_prefix
    #wp-config:table_prefix  = 'wp_'
    self.table_prefix = self.Bj.SPfx  #Orig Empty !!!!  VT Changed.

    # WordPress base table prefix.
    # @access public   @var string
    #base_prefix
    #set in: InitCls: wpdb.set_prefix( table_prefix )
    self.base_prefix = self.Bj.SPfx   #Orig Empty !!!!  VT Changed.

    # Whether the database queries are ready to start executing.
    # @access private   @var bool
    self.ready = False

    # Blog ID.
    # @access public   @var int
    self.blogid = 0

    # Site ID.
    # @access public   @var int
    self.siteid = 0

    # List of WordPress per-blog tables
    # @access private   @var array
    # @see self.tables()
    #self.tables = ( 'posts', 'comments', 'links', 'options', 'postmeta',
    #  'terms', 'term_taxonomy','term_relationships','termmeta','commentmeta')
    self.blog_tables    = array( *wDB.TbC.TbsBlogWp )

    # List of deprecated WordPress tables
    # categories, post2cat, and link2cat were deprecated in 2.3.0,db ver 5539
    #self.old_tables = ( 'categories', 'post2cat', 'link2cat' )

    # List of WordPress global tables
    # @access private   @var array
    # @see self.tables()
    #self.global_tables = array( 'users', 'usermeta' )
    self.global_tables  = array( *wDB.TbC.TbsUsrWp )

    # List of Multisite global tables
    # @access private   @var array
    # @see self.tables()
    #self.ms_global_tables = ( 'blogs', 'signups', 'site', 'sitemeta',
    #                  'sitecategories', 'registration_log', 'blog_versions' )
    self.ms_global_tables = array( *wDB.TbC.TbsMSWp )

    # List of WordPress per-blog tables
    # Comments,     Comment Metadata,  Links,       Options
    #self.comments = self.commentmeta = self.links = self.options = None
    # Post Metadata, Posts,      Terms,       Term Relationships,
    #self.postmeta = self.posts = self.terms = self.term_relationships =  None
    # Term Taxonomy,     Term Meta
    #self.term_taxonomy = self.termmeta  = None
    ## Global and Multisite (MS) Tables
    # User Metadata, Users,      MS Blogs,    MS Blog Versions
    #self.usermeta = self.users = self.blogs = self.blog_versions = None
    # MS Registration Log,  MS Signups,    MS Sites
    #self.registration_log = self.signups = self.site = None
    # MS Sitewide Terms, MS Site Metadata
    #self.sitecategories = self.sitemeta = None

    # Format specifiers for DB columns. Columns not listed here default to %s
    #   Initialized during WP load. wp-includes/load.php: wp_set_wpdb_vars()
    # Keys are column names, values are format types: 'ID' : '%d'
    # @see self.prepare() @see self.insert()
    # @see self.update()  @see self.delete()
    # @see wp_set_wpdb_vars()
    # @access public   @var array
    self.field_types = array() # Set in wp.i.load = WiL

    # Database table columns charset
    # @access public   @var string
    #self.charset = None   # Orig Empty

    # Database table columns collate
    # @access public   @var string
    #self.collate = None   # Orig Empty

    # Database Username
    # @access protected   @var string
    #self.dbuser = None   # Orig Empty

    # Database Password
    # @access protected   @var string
    #self.dbpassword = None   # Orig Empty

    # Database Name
    # @access protected   @var string
    #self.dbname = None   # Orig Empty

    # Database Host
    # @access protected   @var string
    #self.dbhost = None   # Orig Empty

    # Database Handle
    # @access protected   @var string
    #self.dbh = None   # Orig Empty

    # A textual description of the last query/get_row/get_var call
    # @access public   @var string
    #self.func_call = None   # Orig Empty

    # Whether MySQL is used as the database engine.
    # Set in WPDB::db_connect() to True,by default. This is used when checking
    # against the required MySQL version for WordPress. Normally,a replacement
    # database drop-in (db.php) will skip these checks, but setting this to
    # True will force the checks to occur.
    # @access public   @var bool
    self.is_mysql = None

    # A list of incompatible SQL modes.
    # @access protected   @var array
    self.incompatible_modes = array( 'NO_ZERO_DATE', 'ONLY_FULL_GROUP_BY',
      'STRICT_TRANS_TABLES', 'STRICT_ALL_TABLES', 'TRADITIONAL' )

    # Whether to use mysqli over mysql.
    # @access private   @var bool
    #self.use_mysqli = False  #Set to True below

    # Whether we've managed to successfully connect at some point
    # @access private   @var bool
    self.has_connected = False

    # self.db_connect()  #db_connect in  InitCls instead

    #register_shutdown_function( self.__destruct' )

    if getattr(self.Wj, 'WP_DEBUG', None) and getattr(self.Wj, 'WP_DEBUG_DISPLAY',None):
      self.Show_Errors()

    # Use ext/mysqli if it exists and:
    #  - WP_USE_EXT_MYSQL is defined as False, or
    #  - We are a development version of WordPress, or
    #  - We are running PHP 5.5 or greater, or
    #  - ext/mysql is not loaded.

    #if Php.function_exists( 'mysqli_connect' ):  # Always True!
    #  if self.Wj.defined( 'WP_USE_EXT_MYSQL' ):
    #    self.use_mysqli = ! WP_USE_EXT_MYSQL
    #  elif (Php.version_compare( phpversion(), '5.5', '>=' ) or not
    #        Php.function_exists('mysql_connect')): #func exists, Always True!
    #    self.use_mysqli = True
    #  #elif False !== Php.strpos( self.Wj.wp_version, '-' ):
    #  elif '-' in self.Wj.wp_version:
    #    self.use_mysqli = True

    self.use_mysqli = True

    if  self.BDB is None:
      self.dbuser     = dbuser
      self.dbpassword = dbpassword
      self.dbname     = dbname
      self.dbhost     = dbhost
    else:
      self.dbuser     = self.BDB.DbUser
      self.dbpassword = self.BDB.DbPass
      self.dbname     = self.BDB.DbName
      self.dbhost     = self.BDB.DbHost

    # wp-config.php creation will manually connect when ready.
    #if self.Wj.defined( 'WP_SETUP_CONFIG' ):
    #  return
    self.db_connect()

    # Move to Web.BlogCls.InitWp
    ## /fs/web/wp/wp-includes/ms-settings.php
    #self.set_blog_id(self.Bj.BId, self.Bj.SId )
    ## /fs/web/wp/wp-includes/load.php: wp_set_wpdb_vars()
    #self.set_prefix( self.table_prefix )

    #[using super() py3 vs py2](stackoverflow.com/questions/10482953/)
    #In multiple inheritance, super() calls method from the next class in MRO
    #super().__init__()
    #Can't call super() now that added inherit: wpdb_cls(Php.stdClass)


  # calling classmethod needs additional memory than staticmethod or function
  # but since we only have 1 instance, better to use instance method instead
  # but cannot use instance method before instance is created.


  def __destruct(self):
    ''' PHP5 style destructor and will run when database object is destroyed.
    @see wpdb::__construct()
    @since 2.0.8
    @return True
    '''
    return True

  #def __getattr__(self, name): #don't, or can't get self.col_info
  def __get(self, name):
    ''' Makes private properties readable for backward compatibility.
    @param string name The private member to get, and optionally process
    @return mixed The private member
    '''
    if 'col_info' == name:
      self.load_col_info()
    #return getattr(self, name)
    return super().__getattr__(name)

  #def __setattr__(self,name,value): #don't, or can't set self.col_meta,etc
  def __set(self, name, value):
    ''' Makes private properties settable for backward compatibility.
    @param string name  The private member to set
    @param mixed  value The value to set
    '''
    protected_members = array(
      'col_meta',
      'table_charset',
      'check_current_query',
    )
    if Php.in_array(name, protected_members, True):
      return
    #setattr(self, name, value)
    return super().__setattr__(name, value)

  def __isset(self, name ):
    ''' Makes private properties check-able for backward compatibility.
    @param string name  The private member to check
    @return bool If the member is set or not
    '''
    return Php.isset(self, name)

  #def __delattr__(self, name):
  def __unset(self, name ):
    ''' Makes private properties un-settable for backward compatibility.
    @param string name  The private member to unset
    '''
    delattr(self, name)


  def init_charset(self):
    ''' Set self.charset and self.collate
    '''
    charset = ''
    collate = ''

    #if Php.function_exists('is_multisite') and self.Wj.is_multisite():
    #if self.Wj.is_multisite():
    charset = 'utf8'
    #if self.Wj.defined( 'DB_COLLATE' ) and DB_COLLATE:
    #  collate = DB_COLLATE
    #else:
    #  collate = 'utf8_general_ci'
    collate = self.Wj.DB_COLLATE if getattr(self.Wj, 'DB_COLLATE', None) \
              else 'utf8_general_ci'
    #elif hasattr(self.Wj, 'DB_COLLATE'):
    #  collate = self.Wj.DB_COLLATE

    if hasattr(self.Wj, 'DB_CHARSET'):
      charset = self.Wj.DB_CHARSET

    charset_collate = self.determine_charset( charset, collate )

    self.charset = charset_collate['charset']
    self.collate = charset_collate['collate']


  def determine_charset(self, charset, collate ):
    ''' Determines the best charset and collation to use given a charset and collation.
    For example, when able, utf8mb4 should be used instead of utf8.
    @param string charset The character set to check.
    @param string collate The collation to check.
    @return array The most appropriate character set and collation to use.
    '''
    #if (( self.use_mysqli and not isinstance(self.dbh, mysqli)) # wDB.SqlConn
    if self.use_mysqli or Php.empty(self, 'dbh'):
      return Php.compact(locals(), 'charset', 'collate')

    if 'utf8' == charset and self.has_cap( 'utf8mb4' ):
      charset = 'utf8mb4'

    if 'utf8mb4' == charset and not self.has_cap( 'utf8mb4' ):
      charset = 'utf8'
      collate = Php.str_replace( 'utf8mb4_', 'utf8_', collate )

    if 'utf8mb4' == charset:
      # _general_ is outdated, so we can upgrade it to _unicode_, instead.
      if not collate or 'utf8_general_ci' == collate:
        collate = 'utf8mb4_unicode_ci'
      else:
        collate = Php.str_replace( 'utf8_', 'utf8mb4_', collate )

    # _unicode_520_ is a better collation, we should use that when it's available.
    if self.has_cap( 'utf8mb4_520' ) and 'utf8mb4_unicode_ci' == collate:
      collate = 'utf8mb4_unicode_520_ci'

    return Php.compact(locals(), 'charset', 'collate')


  def set_charset(self, dbh, charset = None, collate = None ):
    ''' Sets the connection's character set.
    @param resource dbh     The resource given by mysql_connect
    @param string   charset Optional. The character set. Default None.
    @param string   collate Optional. The collation. Default None.
    '''
    if not Php.isset( locals(), 'charset' ):
      charset = self.charset
    if not Php.isset( locals(), 'collate' ):
      collate = self.collate
    if self.has_cap( 'collation' ) and not Php.empty(locals(), 'charset'):
      set_charset_succeeded = True

      if self.use_mysqli:
        if (Php.function_exists( 'mysqli_set_charset' ) and
            self.has_cap( 'set_charset' )):
          set_charset_succeeded = Php.mysqli_set_charset( dbh, charset )

        if set_charset_succeeded:
          query = self.prepare( 'SET NAMES %s', charset )
          if Php.empty(locals(), 'collate'):
            query += self.prepare( ' COLLATE %s', collate )
          Php.mysqli_query( dbh, query )
      else:
        if (Php.function_exists( 'mysql_set_charset' ) and
            self.has_cap( 'set_charset' )):
          set_charset_succeeded = Php.mysql_set_charset( charset, dbh )
        if set_charset_succeeded:
          query = self.prepare( 'SET NAMES %s', charset )
          if not Php.empty(locals(), 'collate'):
            query += self.prepare( ' COLLATE %s', collate )
          Php.mysql_query( query, dbh )


  def set_sql_mode(self, modes = array() ):
    ''' Change the current SQL mode, and ensure its WordPress compatibility.
    If no modes are passed, it will ensure the current MySQL server
    modes are compatible.
    @param dict  modes Optional. A list of SQL modes to set.
    '''
    if Php.empty( locals(), 'modes' ):
      if self.use_mysqli:
        res = Php.mysqli_query( self.dbh, 'SELECT @@SESSION.sql_mode' )
      else:
        res = Php.mysql_query( 'SELECT @@SESSION.sql_mode', self.dbh )

      if Php.empty( locals(), 'res' ):
        return

      if self.use_mysqli:
        #modes_array = Php.mysqli_fetch_array( res )
        # No need for 'VALUE_LIST' after ODict->array, so array[n]=value
        # mysqli_fetch_array(dbh, result_type='MYSQL_BOTH'), so array[n]=value
        modes_array = Php.mysqli_fetch_array( dbh )
        #if Php.empty( modes_array[0] ):
        # add "if modes_array" in case if modes_array = array()
        if modes_array and Php.empty( modes_array, 0 ):
          return
        modes_str = modes_array[0]
      else:
        # Orig: mysql_result(result, 0), replace with (dbh, 0)
        #modes_str = Php.mysql_result( res, 0 )
        modes_str = Php.mysql_result(  dbh, 0 )

      if Php.empty( locals(), 'modes_str' ):
        return

      modes = modes_str.split( ',' )

    modes = Php.array_change_key_case( modes, 'CASE_UPPER' )

    # Filters the list of incompatible SQL modes to exclude.
    # @since 3.9.0
    # @param array incompatible_modes An array of incompatible modes.
    #incompatible_modes = (array) apply_filters(
    #                     'incompatible_sql_modes', self.incompatible_modes )
    incompatible_modes = Php.Array(WiPg.apply_filters(
                         'incompatible_sql_modes', self.incompatible_modes ))
    #incompatible_modes = list( self.incompatible_modes )

    #for i, mode in enumerate(modes):
    for  i, mode in modes.items():    # now modes is Php.array()
      if Php.in_array(mode, incompatible_modes):
        del modes[ i ]

    modes_str = ','.join( modes )

    if self.use_mysqli:
      Php.mysqli_query(self.dbh,"SET SESSION sql_mode='{}'".format(modes_str))
    else:
      Php.mysql_query("SET SESSION sql_mode='{}'".format(modes_str), self.dbh)


  def set_prefix(self, prefix, set_table_names = True ):
    ''' Sets the table prefix for the WordPress tables.
    @param string prefix          Alphanumeric name for the new prefix.
    @param bool   set_table_names Optional. Whether the table names,
                                  e.g. self.posts, should be updated or not.
    @return string|WP_Error Old prefix or WP_Error on error
    '''
    # re.match() checks for a match only at the beginning of the string, while
    #re.search() checks for a match anywhere in the string.
    #if (Php.preg_match( '|[^a-z0-9_]|i', prefix ) )
    Re = re.compile('[^0-9a-zA-Z\_]')
    if Re.search(prefix):
      return WcE.WP_Error('invalid_db_prefix', 'Invalid database prefix' )
    old_prefix = getattr(self, 'base_prefix', '')
    old_prefix = ''  # self.Wj.is_multisite() ? '' : prefix
    if Php.isset( self, 'base_prefix' ):
      old_prefix = self.base_prefix
    self.base_prefix = prefix

    if set_table_names:
      for table, prefixed_table in self.GetTables( 'global' ).items():
        setattr(self, table, prefixed_table)
      if self.Wj.is_multisite() and Php.empty(self, 'blogid'):
        return old_prefix
      self.prefix = self.get_blog_prefix()

      for table, prefixed_table in self.GetTables( 'blog' ).items():
        setattr(self, table, prefixed_table)
      for table, prefixed_table in self.GetTables( 'old' ).items():
        setattr(self, table, prefixed_table)

    return old_prefix


  def set_blog_id(self, blog_id, site_id = 0 ):
    ''' Sets blog id.
    @param int blog_id
    @param int site_id Optional.
    @return int previous blog id
    '''
    if not Php.empty( locals(), 'site_id' ):
      self.siteid = site_id
    old_blog_id  = self.blogid
    self.blogid = blog_id
    L.info('wpdb set_blog_id self.blogid = {}', self.blogid)
    self.prefix = self.get_blog_prefix()
    for table, prefixed_table in self.GetTables( 'blog' ).items():
      setattr(self, table, prefixed_table)
    for table, prefixed_table in self.GetTables( 'old'  ).items():
      setattr(self, table, prefixed_table)
    return old_blog_id

  def get_blog_prefix(self, blog_id = None ):
    ''' Gets blog prefix.
    @param int blog_id Optional.
    @return string Blog prefix.
    '''
    #if ( self.Wj.is_multisite() ):
    if blog_id is None:
      blog_id = self.blogid
    blog_id = int(blog_id)
    #if self.Wj.defined( 'MULTISITE' ) and blog_id in (0, 1):
    if blog_id in (0, 1, -1):  #VT Added -1
      return self.base_prefix
    else:
      return self.base_prefix + str(abs(blog_id)) +'_'  #VT Added abs
    #else:
    #  return self.base_prefix


  #def tables(  self, scope = 'all', prefix = True, blog_id = 0 ) {
  def GetTables(self, scope = 'all', prefix = True, blog_id = 0 ):
    ''' Returns a dict of WordPress tables.
    Also allows for the CUSTOM_USER_TABLE and CUSTOM_USER_META_TABLE to
    override the WordPress users and usermeta tables that would otherwise
    be determined by the prefix.
    The scope argument can take one of the following:
    'all'     - returns 'all' and 'global' tables. No old tables are returned.
    'blog'    - returns the blog-level tables for the queried blog.
    'global'  - returns the global tables for the installation,
                returning multisite tables only if running multisite.
    'ms_global'-returns the multisite global tables, regardless if current
                installation is multisite.

    @param string scope   Optional. Can be all, global, ms_global, blog, or
                          old tables. Defaults to all.
    @param bool   prefix  Optional. Whether to include table prefixes.
                          Default True. If blog prefix is requested, then the
                          custom users and usermeta tables will be mapped.
    @param int    blog_id Optional. The blog_id to prefix. Defaults to
                          self.blogid. Used only when prefix is requested.
    @return array Table names. When a prefix is requested, the key is the
                               unprefixed table name.
    '''
    if scope == 'all' :
      #tables= self.global_tables + self.blog_tables
      tables = Php.array_merge(self.global_tables, self.blog_tables)
      #if ( self.Wj.is_multisite() )
      #tables= tables + self.ms_global_tables
      tables = Php.array_merge(tables, self.ms_global_tables)
    elif scope == 'blog' :
      tables = self.blog_tables
    elif scope == 'global' :
      tables = self.global_tables
      #if ( self.Wj.is_multisite() )
      #tables+= self.ms_global_tables
      tables  = Php.array_merge(tables, self.ms_global_tables)
    elif scope == 'ms_global' :
      tables = self.ms_global_tables
    #elif scope == 'old' :
    #  tables = self.old_tables
    else:
      return array()

    #VT transform from php array to py dict
    #tables = { t:t for t in tables }

    if prefix:
      if not blog_id:
        blog_id = self.blogid
      blog_prefix = self.get_blog_prefix( blog_id )
      base_prefix = self.base_prefix
      #global_tables= self.global_tables + self.ms_global_tables
      global_tables = Php.array_merge(self.global_tables,
                                      self.ms_global_tables)

      NewTables = array()   # VT Added to avoid err: ODict mutated during iter
      for k, table in tables.items():
        if Php.in_array(table, global_tables):
          #tables[ table ] = base_prefix + table
          NewTables[ table ] = base_prefix + table
        else:
          #tables[ table ] = blog_prefix + table
          NewTables[ table ] = blog_prefix + table
        # comment out php: unset( tables[ k ] ) as in py dict, k is table
        # comment out del tables[ k ]  to avoid err: ODict mutated during iter
        #del tables[ k ]  # RuntimeError: OrderedDict mutated during iteration

      #L.debug("wpdb.GetTables tables= {}"   , tables)
      #L.debug("wpdb.GetTables NewTables= {}", NewTables)
      tables = NewTables   # VT Added to avoid err: ODict mutated during iter

      #if Php.isset(tables, 'users'   ) and self.Wj.defined( 'CUSTOM_USER_TABLE' ):
      #  tables['users']    = CUSTOM_USER_TABLE
      #if Php.isset(tables, 'usermeta') and self.Wj.defined(
      #                                            'CUSTOM_USER_META_TABLE' ):
      #  tables['usermeta'] = CUSTOM_USER_META_TABLE

    return tables


  #def select(self, DbName, dbh = None ):
  #  ''' Selects a database using the current database connection.
  #  The database name will be changed based on the current database
  #  connection. On failure, the execution will bail and display an DB error.
  #  @param string        DbName  MySQL database name
  #  @param resource|None dbh Optional link identifier.
  #  '''
  #  if Php.is_null(dbh):
  #    dbh = self.dbh

  #  #if True is self.use_mysqli:
  #  #  success = mysqli_select_db( dbh, DbName )
  #  #else:
  #  #  success = mysql_select_db( DbName, dbh )
  #  if   DbName == self.GDB.DbName:
  #    success = self.GDB.SelectDb(DbName, Tries=3)
  #  elif DbName == self.BDB.DbName:
  #    success = self.BDB.SelectDb(DbName, Tries=3)
  #  else:
  #    raise ValueError("wpdb.select DbName={} not in ({}, {})"
  #                     .format(DbName,  self.GDB.DbName, self.BDB.DbName))

  #  if not success:
  #    self.ready = False
  #    if not WiPg.did_action( 'template_redirect' ):
  #      self.Wj.wp_load_translations_early()
  #      message = ("wpdb.select:  Can't select database!\n"
  #          "We were able to connect to the database server (which means your"
  #          " username and password is okay) but not able to select", DbName)

  #      #message = '<h1>' + __( 'Can&#8217;t select database' ) + "</h1>\n"

  #      #message += '<p>' + sprintf(
  #      #  # translators: %s: database name
  #      #  __( 'We were able to connect to the database server (which means your username and password is okay) but not able to select the %s database.' ),
  #      #  '<code>' + htmlspecialchars( DbName, ENT_QUOTES ) + '</code>'
  #      #) + "</p>\n"

  #      #message += "<ul>\n"
  #      #message += '<li>' + __( 'Are you sure it exists?' ) + "</li>\n"

  #      #message += '<li>' + sprintf(
  #      #  # translators: 1: database user, 2: database name
  #      #  __( 'Does the user %1$s have permission to use the %2$s database?' ),
  #      #  '<code>' + htmlspecialchars( self.dbuser, ENT_QUOTES )  + '</code>',
  #      #  '<code>' + htmlspecialchars( DbName, ENT_QUOTES ) + '</code>'
  #      #) + "</li>\n"

  #      #message += '<li>' + sprintf(
  #      #  # translators: %s: database name
  #      #  __( 'On some systems the name of your database is prefixed with your username, so it would be like <code>username_%1$s</code>. Could that be the problem?' ),
  #      #  htmlspecialchars( DbName, ENT_QUOTES )
  #      #)+ "</li>\n"

  #      #message += "</ul>\n"

  #      #message += '<p>' + sprintf(
  #      #  # translators: %s: support forums URL
  #      #  __( 'If you don&#8217;t know how to set up a database you should <strong>contact your host</strong>. If all else fails you may find help at the <a href="%s">WordPress Support Forums</a>.' ),
  #      #  __( 'https:#wordpress.org/support/' )
  #      #) + "</p>\n"

  #      self.bail( message, 'db_select_fail' )


  def _weak_escape(self, string ):
    ''' Do not use, deprecated.
    Use esc_sql() or wpdb::prepare() instead.
    @deprecated 3.6.0 Use wpdb::prepare()
    @see wpdb::prepare
    @see esc_sql()
    @param string string
    @return string
    '''
    if ( Php.func_num_args(string) == 1 and
         Php.function_exists( '_deprecated_function' ) ):
      _deprecated_function(__METHOD__, '3.6.0', 'wpdb::prepare() or esc_sql()')
    return addslashes( string )


  def _real_escape(self, string ):
    ''' Real escape, using mysqli_real_escape_string() or mysql_real_escape_string()
    @see mysqli_real_escape_string()
    @see mysql_real_escape_string()
    @param  string string to escape
    @return string escaped
    '''
    if self.dbh:
      #L.debug("wpdb._real_escape= {} {}", self.use_mysqli, self.dbh, string)
      if self.use_mysqli:
        #L.debug('wpdb._real_escape: {} {}', self.dbh, string )
        return Php.mysqli_real_escape_string( self.dbh, string )
      else:
        return Php.mysql_real_escape_string( string, self.dbh )
    #class = get_class( self )
    #if Php.function_exists( '__' ):
    #  # translators: %s: database access abstraction class, usually wpdb or a
    #  #   class extending wpdb
    #  WiFc._doing_it_wrong("wpdb._real_escape", sprintf( __( '%s must set a database connection'
    #                  'for use with escaping.' ), class ), '3.6.0' )
    #else:
    #  WiFc._doing_it_wrong("wpdb._real_escape", sprintf( '%s must set a database connection for'
    #                  'use with escaping.', class ), '3.6.0' )
    L.warning('\n wpdb._real_escape: must set a db connection to escape. {}',
              string)
    return Php.addslashes( string )


  def _escape(self, data ):
    ''' Escape data. Works on arrays.
    @uses wpdb::_real_escape()
    @param  string|dict  data
    @return string|dict  escaped
    '''
    if Php.is_array( data ):
      for k, v in data.items():
        if Php.is_array(v):
          data[k] = self._escape( v )
        else:
          data[k] = self._real_escape( v )
    else:
      data = self._real_escape( data )

    return data


  def escape(self, data ):
    ''' Do not use, deprecated.
    Use esc_sql() or wpdb::prepare() instead.
    @deprecated 3.6.0 Use wpdb::prepare()
    @see wpdb::prepare()
    @see esc_sql()
    @param mixed data
    @return mixed
    '''
    if ( Php.func_num_args(data) == 1 and
         Php.function_exists( '_deprecated_function' ) ):
      _deprecated_function(__METHOD__, '3.6.0', 'wpdb::prepare() or esc_sql()')
    if Php.is_array( data ):
      for k, v in data.items():
        if Php.is_array( v ):
          data[k] = self.escape( v, 'recursive' )
        else:
          data[k] = self._weak_escape( v, 'internal' )
    else:
      data = self._weak_escape( data, 'internal' )

    return data


  #def escape_by_ref( &$string ):
  def  EscapeByRef(self, string ):
    ''' Escapes content by reference for insertion into the db, for security
    @uses wpdb::_real_escape()
    @param string string to escape
    '''
    if not Php.is_float( string ):
      #L.debug("wpdb.EscapeByRef string before _real_escape= {}", string)
      string = self._real_escape( string )
      #L.debug("wpdb.EscapeByRef string after  _real_escape= {}", string)
    #L.warning("EscapeByRef got string passed by ref, so need to return"
    #    "string to be updated by calling fucntion! updated string= {}", string)
    return string


  #def prepare( $query, $args ):
  def prepare(self, query, *args ):
    ''' Prepares a SQL query for safe execution. Uses sprintf()-like syntax.
    PyMySQL convert all obj including int to formatted and quoted string.
      use only %s or %(name)s as placeholder.  Don't use %d.
    The following directives can be used in the query format string:
      %d (integer)  -> %s
      %f (float)    -> %s
      %s (string)
      %% (literal percentage sign - no argument needed)
    All of %d, %f, and %s are to be left unquoted in the query string and they need an argument passed for them.
    Literals (%) as parts of the query must be properly written as %%.
    This function only supports a small subset of the sprintf syntax; it only supports %d (integer), %f (float), and %s (string).
    Does not support sign, padding, alignment, width or precision specifiers.
    Does not support argument numbering/swapping.
    May be called like {@link https://secure.php.net/sprintf sprintf()} or like {@link https://secure.php.net/vsprintf vsprintf()}.
    Both %d and %s should be left unquoted in the query string.
        wpdb::prepare( "SELECT * FROM `table` WHERE `column` = %s AND `field` = %d", 'foo', 1337 )
        wpdb::prepare( "SELECT DATE_FORMAT(`field`, '%%c') FROM `table` WHERE `column` = %s", 'foo' )
    @link https://secure.php.net/sprintf Description of syntax.
    @param string      query    Query statement with sprintf()-like placeholders
    @param array|mixed args     The array of variables to substitute into the query's placeholders if being called like
                                 {@link https://secure.php.net/vsprintf vsprintf()}, or the first variable to substitute into the query's placeholders if
                                 being called like {@link https://secure.php.net/sprintf sprintf()}.
    @param mixed       args,... further variables to substitute into the query's placeholders if being called like
                                 {@link https://secure.php.net/sprintf sprintf()}.
    @return string|void Sanitized query string, if there is a query to prepare.
    '''
    if Php.is_null( query ):
      return
    AllArgs = query, *args

    # This is not meant to be foolproof -- but it will catch obviously incorrect usage.
    #if Php.strpos( query, '%' ) == False:
    if '%' not in query:
      WiFc._doing_it_wrong( 'wpdb::prepare',  __( 'The query argument of {} '
            'must have a placeholder.' ).format('wpdb::prepare()' ), '3.9.0' )

    #args= array( query, *args )   # args = tuple before converting to array
    args = Php.func_get_args( AllArgs )
    Php.array_shift( args )
    # If args were passed as an array (as in vsprintf), move them up
    if Php.isset( args, 0 ) and Php.is_array(args[0]):
      args = args[0]

    # in case someone mistakenly already singlequoted it
    #$query = Php.str_replace( "'%s'", '%s', $query );
    #$query = Php.str_replace( '"%s"', '%s', $query ); # doublequote unquoting
    query = query.replace( "'%s'", '%s' ).replace( '"%s"', '%s' )

    # quote the strings, avoiding escaped strings like %%s
    #$query = Php.preg_replace( '|(?<!%)%s|', "'%s'", $query );
    query = re.sub( '(?<!%)%s', "'%s'", query )

    # Move below %d & %f -> %s after %s->'%s' above, so %d & %f won't -> '%s'
    # Force floats to be locale unaware
    #$query = Php.preg_replace( '|(?<!%)%f|' , '%F', $query );
    #query= re.sub('(?<!%)%f' , '%F', query )
    #query= re.sub('(?<!%)%f' , '%s', query )   #PyMySQL pymysql %f -> %s
    #query= re.sub('(?<!%)%d' , '%s', query )   #PyMySQL pymysql %d -> %s
    #query = re.sub('(?<!%)%[d|f]', '%s', query) #pymysql %d/%f ->%s, not '%s'
    #Comment out above so  %d/%f -> int or float, not '%s'

    #array_walk( $args, array( self, 'EscapeByRef' ) )
    #L.debug('\n\n wpdb prepare query= {}', query)
    #L.debug('wpdb prepare before array_walk args = {}', args)
    # below bad since array_walk returns True or False!!
    #args= Php.array_walk(args, self.EscapeByRef)
    Php.array_walk( args, self.EscapeByRef ) #args= mutable arr passed by ref
    #return @vsprintf( query, args )
    #L.debug('\n wpdb prepare after  array_walk args = {}\n', args)
    #return @vsprintf( query, args )
    return Php.vsprintf(query, args)  #= query % ( *args, )


  def esc_like(self, text ):
    ''' First half of escaping for LIKE special characters % and _ before preparing for MySQL.
    Use this only before wpdb::prepare() or esc_sql().  Reversing the order is very bad for security.
    Example Prepared Statement:
        wild = '%'
        find = 'only 43% of planets'
        like = wild + wpdb.esc_like( find ) + wild
        sql  = wpdb.prepare( "SELECT * FROM {} WHERE post_content LIKE '%s'".format(wpdb.posts), like )
    Example Escape Chain:
        sql  = esc_sql( wpdb.esc_like( input ) )
    @param string text The raw text to be escaped. The input typed by the user should have no
                        extra or deleted slashes.
    @return string Text in the form of a LIKE phrase. The output is not SQL safe. Call wpdb::prepare()
                   or real_escape next.
    '''
    return addcslashes( text, '_%\\' )


  def print_error(self, Str = '' ):
    ''' Print SQL/DB error.
    @global array EZSQL_ERROR Stores error information of query and error string
    @param string Str The error to display
    @return False|void False if the showing of errors is disabled.
    '''
    #global var==>self.Wj.var, except: var=self.Wj.var=same Obj,mutable array
    EZSQL_ERROR = self.Wj.EZSQL_ERROR  # global EZSQL_ERROR

    if not Str:
      if self.use_mysqli:
        Str = self.last_error     # mysqli_error( self.dbh )
      else:
        Str = self.last_error     # mysql_error( self.dbh )
    #EZSQL_ERROR.update( {'query':self.last_query, 'error_str':Str} )
    EZSQL_ERROR[None] = array( ('query',self.last_query), ('error_str',Str) )

    if self.suppress_errors:
      return False

    self.Wj.wp_load_translations_early()

    caller = self.get_caller()
    if caller:
      # translators: 1: Database error message, 2: SQL query, 3: Name of the calling function
      error_str = (__('WordPress database error {} for query {} made by {}')
                   ).format(Str, self.last_query, caller )
    else:
      # translators: 1: Database error message, 2: SQL query
      error_str = (__('WordPress database error {} for query {}')
                   ).format(Str, self.last_query )
    Php.error_log( error_str )

    # Are we showing errors?
    if not self.Show_Errors():
      return False

    # If there is an error then take note of it
    #if self.Wj.is_multisite():
    msg = "{} [{}]\n{}\n".format(
          __('WordPress database error:'), Str, self.last_query)

    if self.Wj.defined( 'ERRORLOGFILE' ):
      Php.error_log( msg, 3, ERRORLOGFILE )
    if self.Wj.defined( 'DIEONDBERROR' ):
      WiFc.wp_die( msg )
    else:
      Str   = Php.htmlspecialchars( Str, ENT_QUOTES )
      query = Php.htmlspecialchars( self.last_query, ENT_QUOTES )
      L.exception( "{} [{}]\n{}\n", __('WordPress database error:'), Str, query)


  def Show_Errors(self, show = True ):
    ''' Enables showing of database errors.
    This function should be used only to enable showing of errors.
    wpdb::hide_errors() should be used instead for hiding of errors. However,
    this function can be used to enable and disable showing of database
    errors.
    @see wpdb::hide_errors()
    @param bool show Whether to show or hide errors
    @return bool Old value for showing errors.
    '''
    errors = self.show_errors
    self.show_errors = show
    return errors


  def hide_errors(self):
    ''' Disables showing of database errors.
    By default database errors are not shown.
    @see wpdb::Show_Srrors()
    @return bool Whether showing of errors was active
    '''
    show = self.show_errors
    self.show_errors = False
    return show


  def suppress_errors(self, suppress = True ):
    ''' Whether to suppress database errors.
    By default database errors are suppressed, with a simple
    call to this function they can be enabled.
    @see wpdb::hide_errors()
    @param bool suppress Optional. New value. Defaults to True.
    @return bool Old value
    '''
    errors = self.suppress_errors
    self.suppress_errors = bool( suppress )
    return errors


  def flush(self):
    ''' Kill cached query results.
    '''
    self.last_result = array()
    self.col_info    = None
    self.last_query  = None
    self.rows_affected = self.num_rows = 0
    self.last_error  = ''
    if self.use_mysqli: # and self.result instanceof mysqli_result:
      # move to below since self.dbh might not be init yet
      #Php.mysqli_free_result( self.result )
      self.result = None

      # Sanity check before using the handle
      if (Php.empty( self, 'dbh' ) or
          not self.IsObjInstanceOfCursor(self.dbh)):
        return
      Php.mysqli_free_result( self.dbh )    # self.result )

      # Clear out any results from a multi-query
      while Php.mysqli_more_results( self.dbh ):
        NextResult = Php.mysqli_next_result( self.dbh )
        if not NextResult:  # VT Added
          break             # VT Added

    #elif is_resource( self.result ):
    #  mysql_free_result( self.result )


  def db_connect(self, allow_bail = True):
    ''' Connect to and select database.
    If allow_bail is False, the lack of database connection will need
    to be handled manually.
    @since 3.9.0 allow_bail parameter added.
    @param bool allow_bail Optional. Allows the function to bail. Default True.
    @return bool True with a successful connection, False on failure.
    '''
    self.is_mysql = True

    # Deprecated in 3.9+ when using MySQLi. No equivalent
    # new_link parameter exists for mysqli_* functions.
    #new_link = self.Wj.defined( 'MYSQL_NEW_LINK' ) ? MYSQL_NEW_LINK : True
    new_link = getattr(self.Wj, 'MYSQL_NEW_LINK', True)
    #client_flags = self.Wj.defined( 'MYSQL_CLIENT_FLAGS' ) ? MYSQL_CLIENT_FLAGS : 0
    client_flags = getattr(self.Wj, 'MYSQL_CLIENT_FLAGS', 0)

    if True is self.use_mysqli:
      #self.dbh = mysqli_init()

      # mysqli_real_connect doesn't support the host param including a port or
      # socket like mysql_connect does. This duplicates how mysql_connect
      # detects a port and/or socket file.
      port = None
      socket = None
      host = self.dbhost
      if getattr(self, 'BDB', None): #VT Add
        port = self.BDB.DbPort       #VT Add
      else:                             #VT Add
        port_or_socket = Php.strstr( host, ':' )
        if port_or_socket:  # if not Php.empty( locals(), 'port_or_socket' ):
          host = Php.substr( host, 0, Php.strpos( host, ':' ) )
          port_or_socket = Php.substr( port_or_socket, 1 )
          #L.debug('wpdb {} {}', host, port_or_socket)
          if 0 != Php.strpos( port_or_socket, '/' ):
            port = Php.intval( port_or_socket )
            maybe_socket = Php.strstr( port_or_socket, ':' )
            if maybe_socket:  # if not Php.empty( locals(), 'maybe_socket' ):
              socket = Php.substr( maybe_socket, 1 )
          else:
            socket = port_or_socket
        L.debug('wpdb {} {} {} {}', host, port_or_socket, port, socket)

      #if getattr(self.Wj, 'WP_DEBUG', None):
      #  mysqli_real_connect( self.dbh, host, self.dbuser, self.dbpassword,
      #                       None, port, socket, client_flags )
      #VT Changed to BDB below:
      if getattr(self, 'BDB', None): #VT Add
        #autocommit: pymysql default=False! mysqli_real_connect: default= True
        self.dbconn = self.BDB.ConnectDb(AutoCommit=self.AutoCommit)
        #self.dbconn.autocommit(True)  #if don't declare autocommit above
      else:
        L.debug('\n\n wpdb.dbconnect BDB or Bj absent! return!\n\n')
        return False
      self.dbh = self.dbconn.cursor()
      #else:
      #  @mysqli_real_connect( self.dbh, host, self.dbuser, self.dbpassword,
      #                        None, port, socket, client_flags )

      #if self.dbh.connect_errno:
      if self.dbh is False:
        self.dbh = None

        #It's possible ext/mysqli is misconfigured. Fall back to ext/mysql if:
        # - We haven't previously connected, and
        # - WP_USE_EXT_MYSQL isn't set to False, and
        # - ext/mysql is loaded.
        attempt_fallback = True

        if self.has_connected:
          attempt_fallback = False
        #elif self.Wj.defined( 'WP_USE_EXT_MYSQL' ) and not WP_USE_EXT_MYSQL:
        elif hasattr(self.Wj, 'WP_USE_EXT_MYSQL') and not self.Wj.WP_USE_EXT_MYSQL:
          attempt_fallback = False
        elif not Php.function_exists( 'mysql_connect' ):
          attempt_fallback = False

        if attempt_fallback:
          self.use_mysqli = False
          return self.db_connect( allow_bail )
    #else:
    #  #if getattr(self.Wj, 'WP_DEBUG', None):
    #  self.dbh = mysql_connect( self.dbhost, self.dbuser, self.dbpassword,
    #                            new_link, client_flags )
    #  #else:
    #  #  self.dbh = @mysql_connect(self.dbhost, self.dbuser, self.dbpassword,
    #  #                            new_link, client_flags )

    #if self.dbh is False and allow_bail:
    if not self.dbh and allow_bail:
      self.Wj.wp_load_translations_early()

      # Load custom DB error template, if present.
      #if file_exists( WP_CONTENT_DIR + '/db-error.php' ):
      #  require_once( WP_CONTENT_DIR + '/db-error.php' )
      #  die()

      message = 'wpdb.db_connect: Error establishing a db connection'
      #message = '<h1>' + __( 'Error establishing a database connection' ) + "</h1>\n"

      #message += '<p>' + sprintf(
      #  # translators: 1: wp-config.php. 2: database host
      #  __( 'This either means that the username and password information in your %1$s file is incorrect or we can&#8217;t contact the database server at %2$s. This could mean your host&#8217;s database server is down.' ),
      #  '<code>wp-config.php</code>',
      #  '<code>' + htmlspecialchars( self.dbhost, ENT_QUOTES ) + '</code>'
      #) + "</p>\n"

      #message += "<ul>\n"
      #message += '<li>' + __( 'Are you sure you have the correct username and password?' ) + "</li>\n"
      #message += '<li>' + __( 'Are you sure that you have typed the correct hostname?' ) + "</li>\n"
      #message += '<li>' + __( 'Are you sure that the database server is running?' ) + "</li>\n"
      #message += "</ul>\n"

      #message += '<p>' + sprintf(
      #  # translators: %s: support forums URL
      #  __( 'If you&#8217;re unsure what these terms mean you should probably contact your host. If you still need help you can always visit the <a href="%s">WordPress Support Forums</a>.' ),
      #  __( 'https://wordpress.org/support/' )
      #) + "</p>\n"

      self.bail( message, 'db_connect_fail' )
      return False

    elif self.dbh:
      if not self.has_connected:
        self.init_charset()

      self.has_connected = True

      self.set_charset( self.dbh )

      self.ready = True
      self.set_sql_mode()
      self.select( self.dbname, self.dbh )

      return True

    return False


  #def check_connection(self, allow_bail = True ):
  #  ''' Checks that the connection to the database is still up. If not, try to reconnect.
  #  If this function is unable to reconnect, it will forcibly die, or if after the
  #  the {@see 'template_redirect'} hook has been fired, return False instead.
  #  If allow_bail is False, the lack of database connection will need
  #  to be handled manually.
  #  @param bool allow_bail Optional. Allows the function to bail. Default True.
  #  @return bool|void True if the connection is up.
  #  '''
  #  if self.use_mysqli:
  #    if not Php.empty(self, 'dbh') and Php.mysqli_ping( self.dbh ):
  #      return True
  #  else:
  #    if not Php.empty(self, 'dbh') and Php.mysql_ping( self.dbh ):
  #      return True

  #  error_reporting = False

  #  # Disable warnings, as we don't want to see a multitude of "unable to connect" messages
  #  if getattr(self.Wj, 'WP_DEBUG', None):
  #    error_reporting = error_reporting()
  #    error_reporting( error_reporting & ~E_WARNING ) #~ bin negation operator

  #  #for ( tries = 1; tries <= self.reconnect_retries; tries++ ) {
  #  for tries in range( self.reconnect_retries ):
  #    # On the last try, re-enable warnings. We want to see a single instance of the
  #    # "unable to connect" message on the bail() screen, if it appears.
  #    if self.reconnect_retries == tries and getattr(self.Wj, 'WP_DEBUG', None):
  #      error_reporting( error_reporting )

  #    if self.db_connect( False ):
  #      if error_reporting:
  #        error_reporting( error_reporting )

  #      return True

  #    sleep( 1 )

  #  # If template_redirect has already happened,
  #  #    it's too late for wp_die()/dead_db().
  #  # Let's just return and hope for the best.
  #  if WiPg.did_action( 'template_redirect' ):
  #    return False

  #  if not allow_bail:
  #    return False

  #  self.Wj.wp_load_translations_early()

  #  message = 'wpdb.check_connection: Error reconnecting to database server '\
  #            + self.dbhost
  #  #message = '<h1>' + __( 'Error reconnecting to the database' ) + "</h1>\n"

  #  #message += '<p>' + sprintf(
  #  #  # translators: %s: database host
  #  #  __( 'This means that we lost contact with the database server at %s. This could mean your host&#8217;s database server is down.' ),
  #  #  '<code>' + htmlspecialchars( self.dbhost, ENT_QUOTES ) + '</code>'
  #  #) + "</p>\n"

  #  #message += "<ul>\n"
  #  #message += '<li>' + __( 'Are you sure that the database server is running?' ) + "</li>\n"
  #  #message += '<li>' + __( 'Are you sure that the database server is not under particularly heavy load?' ) + "</li>\n"
  #  #message += "</ul>\n"

  #  #message += '<p>' + sprintf(
  #  #  # translators: %s: support forums URL
  #  #  __( 'If you&#8217;re unsure what these terms mean you should probably contact your host. If you still need help you can always visit the <a href="%s">WordPress Support Forums</a>.' ),
  #  #  __( 'https://wordpress.org/support/' )
  #  #) + "</p>\n"

  #  # We weren't able to reconnect, so we better bail.
  #  self.bail( message, 'db_connect_fail' )

  #  # Call dead_db() if bail didn't die, because this database is no more. It has ceased to be (at least temporarily).
  #  dead_db()


  def query(self, query ):
    ''' Perform a MySQL database query, using current database connection.
    More information can be found on the codex page.
    @param string query Database query
    @return int|False Number of rows affected/selected or False on error
    '''
    L.info('wpdb query query= {}', query)
    if not self.ready:
      self.check_current_query = True
      return False

    # Filters the database query.
    # Some queries are made before the plugins have been loaded,
    # and thus cannot be filtered with this method.
    # @param string query Database query.
    #query = WiPg.apply_filters( 'query', query )
    self.flush()

    # Log how the function was called
    #self->func_call = "\$db->query(\"$query\")";
    self.func_call = 'db.query("{}")'.format(query)

    # If we're writing to the database, make sure the query will write safely.
    if self.check_current_query and not self.check_ascii( query ):
      stripped_query = self.strip_invalid_text_from_query( query )
      # strip_invalid_text_from_query() can perform queries, so we need
      # to flush again, just to make sure everything is clear.
      self.flush()
      if stripped_query != query:
        self.insert_id = 0
        return False

    self.check_current_query = True

    # Keep track of the last query for debug.
    self.last_query = query

    # php.net/manual/en/mysqli.errno.php
    try:    self._do_query( query )
    #except pymysql.InternalError as Err:
    except  pymysql.MySQLError as Err:
      errno, errmsg = Err.args
      L.exception("wpdb.query errno={}, errmsg={}", *Err.args)
      # MySQL server has gone away, try to reconnect.
    else:
      errno = 0    # Orig: mysql_errno = 0
    # dev.mysql.com/doc/refman/5.7/en/error-messages-client.html
    # dev.mysql.com/doc/refman/5.7/en/gone-away.html

    #above replace below:
    #if self.dbh:
    #  if self.use_mysqli:
    #    #if self.dbh instanceof mysqli:
    #    if self.IsObjInstanceOfCursor(self.dbh):
    #      errno = mysqli_errno( self.dbh )
    #    else:
    #      # dbh is defined, but isn't a real connection.
    #      # Something has gone horribly wrong, let's try a reconnect.
    #      errno = 2006
    #  else:
    #    if is_resource( self.dbh ):
    #      errno = mysql_errno( self.dbh )
    #    else:
    #      errno = 2006

    #if Php.empty( self.dbh ) or 2006 == errno:
    # VT Added  2013 == 'Lost connection to server'
    if Php.empty(self, 'dbh') or errno in (2006, 2013):
      L.debug("wpdb query empty(self, 'dbh') or errno in (2006, 2013) {} {}",
              self.dbh, errno)
      if self.check_connection():
        self._do_query( query )
      else:
        self.insert_id = 0
        return False

    # If there is an error then take note of it.
    if self.use_mysqli:
      L.debug("wpdb query self.use_mysqli {}", self.use_mysqli)
      #if self.dbh instanceof mysqli:
      if self.IsObjInstanceOfCursor(self.dbh):
        self.last_error = errno  # mysqli_error( self.dbh )
      else:
        self.last_error =__('Unable to retrieve the error message from MySQL')
    else:
      #if is_resource( self.dbh ):
      #  self.last_error = errno  # mysql_error( self.dbh )
      #else:
      self.last_error =__('Unable to retrieve the error message from MySQL')

    if self.last_error:
      L.error("wpdb query self.last_error {}", self.last_error)
      # Clear insert_id on a subsequent failed insert.
      if self.insert_id and Php.preg_match('/^\s*(insert|replace)\s/i',query):
        self.insert_id = 0

      self.print_error()
      return False

    if Php.preg_match( '/^\s*(create|alter|truncate|drop)\s/i', query ):
      L.debug("wpdb query preg_match 1")
      return_val = self.result
    elif Php.preg_match( '/^\s*(insert|delete|update|replace)\s/i', query ):
      if self.use_mysqli:
        self.rows_affected = Php.mysqli_affected_rows( self.dbh )
      else:
        self.rows_affected = Php.mysql_affected_rows( self.dbh )
      # Take note of the insert_id
      if Php.preg_match( '/^\s*(insert|replace)\s/i', query ):
        if self.use_mysqli:
          self.insert_id = Php.mysqli_insert_id( self.dbh )
        else:
          self.insert_id = Php.mysql_insert_id( self.dbh )
        L.debug("wpdb query preg_match 2 insert_id = {}", self.insert_id)
      # Return number of rows affected
      return_val = self.rows_affected
      L.debug("wpdb query preg_match 2 rows_affected = {}", self.rows_affected)

    else:
      num_rows = 0
      #if self.use_mysqli and self.result instanceof mysqli_result:
      if True is self.use_mysqli:#and self.IsObjInstanceOfCursor(self.dbh)

        # change mysqli_fetch_object from fetchall to fetchone
        #   to emulate php's getting 1 row at a time
        #self.last_result= Php.mysqli_fetch_object( self.dbh ) # result-->dbh
        #self.last_result = self.dbh._rows
        for row_num, row in enumerate(self.dbh._rows):
          self.last_result[row_num] = Php.mysqli_fetch_object( self.dbh )
        num_rows = self.dbh.rowcount

        ##while row = Php.mysqli_fetch_object( self.result ):
        #while True:
        #  row = Php.mysqli_fetch_object( self.dbh ) # replace result with dbh
        #  if not row:
        #    break
        #  self.last_result[num_rows] = row
        #  num_rows += 1
      #elif is_resource( self.result ):
      #  while ( row = Php.mysql_fetch_object( self.result ) ) {
      #    self.last_result[num_rows] = row
      #    num_rows++

      # Log number of rows the query returned
      # and return number of rows selected
      self.num_rows = num_rows
      return_val    = num_rows

    L.debug("wpdb query return_val= {}", return_val)
    return return_val


  def _do_query(self, query ):
    ''' Internal function to perform the mysql_query() call.
    @see wpdb::query()
    @param string query The query to run.
    '''
    L.debug('wpdb do_query query= {}', query)
    #if self.Wj.defined( 'SAVEQUERIES' ) and SAVEQUERIES:
    if getattr(self.Wj, 'SAVEQUERIES', None):
      self.timer_start()

    if not Php.empty(self, 'dbh') and self.use_mysqli:
      self.result = Php.mysqli_query( self.dbh, query )
    elif not Php.empty(self, 'dbh'):
      self.result = Php.mysql_query( query, self.dbh )
    L.info('wpdb do_query self.result= {}', self.result)
    self.num_queries += 1
    L.debug('wpdb do_query self.num_queries = {}', self.num_queries)

    if getattr(self.Wj, 'SAVEQUERIES', None):
      self.queries[None] = array( query, self.timer_stop(), self.get_caller())


  def insert(self, table, data, Format = None ):
    '''
    Insert a row into a table.
        self.insert( 'table', array( ('column', 'foo'), ('field', 'bar')) )
        self.insert( 'table', array( ('column', 'foo'), ('field', 1337 )),
                               ( '%s', '%s' ) )  # PyMySQL %d->%s
    @see self.prepare()
    @see self.field_types
    @see wp_set_wpdb_vars()
    @param string table Table name
    @param array  data  Data to insert (in column : value pairs).
                        Both data columns and data values should be "raw"
                          (neither should be SQL escaped).
                        Sending a None value will cause the column to be set to
                        None -the corresponding Format is ignored in this case.
    @param array|string Format Optional.   An array of formats to be mapped
                          to each of the value in data.
                        If string, that Format will be used for all of the
                          values in data.
                        A Format is one of '%d', '%f', '%s' (int, float, str).
                                  # PyMySQL %d &  %f  ->%s
                        If omitted, all values in data will be treated as str
                        unless otherwise specified in self.field_types.
    @return int|False   The number of rows inserted, or False on error.
    '''
    return self._insert_replace_helper( table, data, Format, 'INSERT' )


  def replace(self, table, data, Format = None ):
    '''
    Replace a row into a table.
        self.replace( 'table', { 'column' : 'foo', 'field' : 'bar' } )
        self.replace( 'table', { 'column' : 'foo', 'field' : 1337 },
                                ( '%s', '%s' ) )  # PyMySQL %d->%s
    @see self.prepare()
    @see self.field_types
    @see wp_set_wpdb_vars()
    @param string table Table name
    @param array  data  Data to insert (in column : value pairs).
                        Both data columns and data values should be "raw"
                          (neither should be SQL escaped).
                        Sending a None value will cause the column to be set to
                        None -the corresponding Format is ignored in this case.
    @param array|string Format Optional.   An array of formats to be mapped
                          to each of the value in data.
                        If string, that Format will be used for all of the
                          values in data.
                        A Format is one of '%d', '%f', '%s' (integer, float, string).
                        # PyMySQL %d & %f -> %s
                        If omitted, all values in data will be treated as strings unless otherwise specified in self.field_types.
    @return int|False The number of rows affected, or False on error.
    '''
    return self._insert_replace_helper( table, data, Format, 'REPLACE' )


  def _insert_replace_helper(self, table, data, Format = None, Type = 'INSERT' ):
    '''
    PHP passes vars to functions by value, but Python passes by reference.
    Since `data` might be modified in the method here and affect the
    same `data` array in the calling function, so we need to make a
    copy of `data` for processing here.

        :::python
        data = data.copy()

    Helper function for insert and replace.
    Runs an insert or replace query based on Type argument.
    @see self.prepare()
    @see self.field_types
    @see wp_set_wpdb_vars()
    @param string table Table name
    @param array  data  Data to insert (in column : value pairs).
                        Both data columns and data values should be "raw"
                          (neither should be SQL escaped).
                        Sending a None value will cause the column to be set to
                        None -the corresponding Format is ignored in this case.
    @param array|string Format Optional.   An array of formats to be mapped
                          to each of the value in data.
                        If string, that Format will be used for all of the
                          values in data.
                        A Format is one of '%d', '%f', '%s' (int, float, str).
                        # PyMySQL %d & %f -> %s
                        If omitted, all values in data will be treated as str
                        unless otherwise specified in self.field_types.
    @param string Type  Optional. INSERT or REPLACE. Defaults to INSERT.
    @return int|False   The number of rows affected, or False on error.
    '''
    data = data.copy()
    self.insert_id = 0

    if Php.strtoupper( Type ) not in ( 'REPLACE', 'INSERT' ):
      return False

    L.debug('wpdb insert data={}, Format={}', data, Format)
    data = self.process_fields( table, data, Format )
    if not data:
      return False

    L.debug('wpdb insert data = self.process_fields = {}', data)
    # formats = values = array() #BAD!!!# Share the same mutable list!
    formats = array()
    values  = array()
    for value in data:   # same as data.values():
      if value.get('value', None) is None:
        formats[None] = "NULL"
        continue
      formats[None] =value['Format']
      values[None] = value['value' ]
      #L.debug('value= {} {} {}', value, value['Format'], value['value' ])

    #L.debug('formats= {}', formats)
    #L.debug('values= {}', values)
    #fields   = ', '.join( data.keys() )
    fields  = '`' + Php.implode( '`, `', Php.array_keys( data ) ) + '`'
    #formats  = ', '.join( formats )
    formats = Php.implode( ', ', formats )

    #sql= "$Type INTO `$table` ($fields) VALUES ($formats)"
    sql = "{} INTO `{}` ({}) VALUES ({})".format(Type, table, fields, formats)
    #self.check_current_query = False

    #return self.query( self.prepare( sql, values ) )
    Prepare = self.prepare( sql, values )
    L.debug('wpdb insert Prepare = {}', Prepare)
    return  self.query( Prepare )

    #return wDB.GetDB(self, table).Exec(sql, values)


  def update(self, table, data, where, Format = None, where_format = None ):
    '''
    PHP passes vars to functions by value, but Python passes by reference.
    Since `data` might be modified in the method here and affect the
    same `data` array in the calling function, so we need to make a
    copy of `data` for processing here.

        :::python
        data = data.copy()

    Update a row in the table
        self.update( 'table', array( ('column', 'foo'), ('field', 'bar') ),
                      array( ('ID', 1) ) )
        self.update( 'table', array( ('column', 'foo'), ('field', 1337) ),
                    array( ('ID', 1) ), ('%s','%s',), ('%f',)) #PyMySQL %d->%s
    @param string table Table name
    @param array  data  Data to update (in column : value pairs).
                        Both data columns and data values should be "raw"
                          (neither should be SQL escaped).
                       Sending a None value will cause the column to be set to
                       NULL -the corresponding Format is ignored in this case.
    @param array  where A named array of WHERE clauses (in column :value
                        pairs). Multiple clauses will be joined with ANDs.
                        Both where columns and where values should be "raw".
                        Sending a None value will create an IS NULL comparison
                       -the corresponding Format will be ignored in this case.
    @param array|string Format Optional.   An array of formats to be mapped
                          to each of the values in data.
                        If string, that Format will be used for all of the
                          values in data.
                        A Format is one of '%d', '%f', '%s' (int, float, str).
                        # PyMySQL %d & %f -> %s
                        If omitted, all values in data will be treated as str
                        unless otherwise specified in self.field_types.
    @param array|string where_format Optional.An array of formats to be mapped
                          to each of the values in where.
                        If string, that Format will be used for all of the
                        items in where.
                        A Format is one of '%d', '%f', '%s' (int, float, str).
                        # PyMySQL %d & %f -> %s
                       If omitted, all values in where will be treated as str.
    @return int|False   The number of rows updated, or False on error.
    '''
    data = data.copy()

    if not Php.is_array(data) or not Php.is_array(where):
      return False

    data = self.process_fields( table, data, Format )
    if False is data:
      return False
    where = self.process_fields( table, where, where_format )
    if False is where:
      return False

    #fields = conditions= values= array() #BAD!!# Share the same mutable list!
    fields     = array()
    conditions = array()
    values     = array()
    for field, value in data.items():
      if value.get('value', None) is None:
        fields[None] = "`{}` = NULL".format(field)
        continue
      fields[None] = "`{}` = {}".format(field, value['Format'])
      values[None] = value['value']

    #L.debug('\n wpdb update fields= {}', fields)     #VT
    #L.debug(   'wpdb update values= {}', values)     #VT

    for field, value in where.items():
      if value.get('value', None) is None:
        conditions[None] = "`{}` IS NULL".format(field)
        continue
      conditions[None] = "`{}` = {}".format(field, value['Format'])
      values[None] = value['value']

    #L.debug('wpdb update values= {}'    , values)     #VT
    #L.debug('wpdb update conditions= {}', values)     #VT
    #fields    = implode( ', ', fields )
    fields     = ', '.join( fields )
    #conditions= implode( ' AND ', conditions )
    conditions = ' AND '.join( conditions )

    sql = "UPDATE `{}` SET {} WHERE {}".format(table, fields, conditions)
    #self.check_current_query = False

    #return self.query( self.prepare( sql, values ) )
    Prepare = self.prepare( sql, values )
    L.debug('wpdb update Prepare = {}', Prepare)
    return self.query( Prepare )

    #return wDB.GetDB(self, table).Exec(sql, values)


  def delete(self, table, where, where_format = None ):
    ''' Delete a row in the table
        wpdb::delete( 'table', array( ('ID', 1)) )
        wpdb::delete( 'table', array( ('ID', 1)), ( '%s',) )  # PyMySQL %d->%s
    @see wpdb::prepare()
    @see wpdb::field_types
    @see wp_set_wpdb_vars()
    @param str   table Table name
    @param array where A dict of WHERE clauses (in column : value pairs).
                       Multiple clauses will be joined with ANDs.
                       Both where columns and where values should be "raw".
                      Sending a None value will create an IS NULL comparison -
                       the corresponding format will be ignored in this case.
    @param array|str where_format Optional. An array of formats to be mapped
                                  to each of the values in where. If string,
                 that format will be used for all of the items in where.
                 A format is one of '%d', '%f', '%s' (integer, float, string).
                 # PyMySQL %d & %f -> %s
                 If omitted, all values in where will be treated as strings
                 unless otherwise specified in wpdb::field_types.
    @return int|False The number of rows updated, or False on error.
    '''
    if not Php.is_array( where ):
      return False

    where = self.process_fields( table, where, where_format )
    if False is where:
      return False

    #conditions = values = array()   #Bad# Share same mutable array
    conditions  = array()
    values      = array()
    for field, value in where.items():
      if Php.is_null( value['value'] ):
        conditions[None] = "`{}` IS NULL".format(field)
        continue

      conditions[None] = "`{}` = {}".format(field, value['Format'])
      values[None] = value['value']

    #conditions = implode( ' AND ', conditions )
    conditions  = ' AND '.join( conditions )

    sql = "DELETE FROM `{}` WHERE {}".format(table, conditions)

    self.check_current_query = False

    #return self.query( self.prepare( sql, values ) )
    Prepare = self.prepare( sql, values )
    L.debug('wpdb delete Prepare = {}', Prepare)
    return self.query( Prepare )



  def process_fields(self, table, data, Format ):
    '''
    Processes arrays of field/value pairs and field formats.
    This is a helper method for wpdb's CRUD methods, which take field/value
    pairs for inserts, updates, and where clauses. This method first pairs
    each value with a Format. Then it determines the charset of that field,
    using that to determine if any invalid text would be stripped. If text is
    stripped, then field processing is rejected and the query fails.

    @param string table  Table name.
    @param array  data   Field/value pair.
    @param mixed  Format Format for each field.
    @return array|False Returns an array of fields that contain paired values
                       and formats. Returns False for invalid values.
    '''
    data = self.process_field_formats( data, Format )
    if False is data:
      return False

    data = self.process_field_charsets( data, table )
    if False is data:
      return False

    data = self.process_field_lengths( data, table )
    if False is data:
      return False

    converted_data = self.strip_invalid_text( data )
    if data is not converted_data:
      return False
    return data


  def process_field_formats(self, data, Format ):
    '''
    Prepares arrays of value/Format pairs as passed to wpdb CRUD methods.
    @param array data   Array of fields to values.
    @param mixed Format Formats to be mapped to the values in data.
                        ( '%s', '%s', )  # PyMySQL %d->%s
    @return array Array, keyed by field names with values being an array
                  of 'value' and 'Format' keys.
    '''
    #formats = original_formats = Php.Array(Format) #bad!! Same mutable array
    formats          = Php.Array( Format )  #split into 2 lines to avoid
    original_formats = Php.Array( Format )  #   same mutable array

    for field, value in data.items():
      value = array( ('value', value), ('Format', '%s'), )
      if Format:   # if not Php.empty( locals(), 'Format' ):
        #value['Format'] = formats.pop(0)
        value['Format']  = Php.array_shift( formats )
        if not value['Format']:
          value['Format'] =original_formats[0] #=php: reset(original_formats)
      elif Php.isset(self.field_types, field):
        value['Format'] = self.field_types[ field ]
      data[ field ] = value
    #L.debug('process_field_formats: data= {}', data)
    #{'meta_key': {'Format': '%s', 'value': 'first_name'},
    #     'user_id': {'Format': '%s', 'value': 10054}}
    return data


  def process_field_charsets(self, data, table ):
    ''' Adds field charsets to field/value/format arrays generated by
    the wpdb::process_field_formats() method.
    @param array  data  As it comes from the wpdb::process_field_formats() method.
    @param string table Table name.
    @return array|False The same array as data with additional 'charset' keys.
    '''
    for field, value in data.items():    # PyMySQL %d & %f -> %s
      if '%d' == value['Format'] or '%f' == value['Format']:
        # We can skip this field if we know it isn't a string.
        # This checks %d/%f versus ! %s because its sprintf() could take more.
        value['charset'] = False
      else:
        value['charset'] = self.get_col_charset( table, field )
        if self.Wj.is_wp_error( value['charset'] ):
          return False

      data[ field ] = value

    return data


  def process_field_lengths(self, data, table ):
    ''' For string fields, record the maximum string length that field can safely save.
    @param array  data  As it comes from the wpdb::process_field_charsets() method.
    @param string table Table name.
    @return array|False The same array as data with additional 'length' keys, or False if
                        any of the values were too long for their corresponding field.
    '''
    for field, value in data.items():
      if '%d' == value['Format'] or '%f' == value['Format']:
        # We can skip this field if we know it isn't a string.
        # This checks %d/%f versus ! %s because its sprintf() could take more.
        value['length'] = False
      else:
        value['length'] = self.get_col_length( table, field )
        if self.Wj.is_wp_error( value['length'] ):
          return False

      data[ field ] = value

    return data


  def get_var(self, query = None, x = 0, y = 0 ):
    ''' Retrieve one variable from the database.
    Executes a SQL query and returns the value from the SQL result.
    If the SQL result contains more than one column and/or more than one row, this function returns the value in the column and row specified.
    If query is None, this function returns the value in the specified column and row from the previous SQL result.
    @param string|None query Optional. SQL query. Defaults to None, use the result from the previous query.
    @param int         x     Optional. Column of value to return. Indexed from 0.
    @param int         y     Optional. Row of value to return. Indexed from 0.
    @return string|None Database query result (as string), or None on failure
    '''
    #self->func_call = "\$db->get_var(\"$query\", $x, $y)";
    self.func_call = 'db.get_var("{}", {}, {})'.format(query, x, y)
    #L.debug("wpdb.get_var: self.func_call = {} {}",
    #        self.func_call, self.last_result)

    if self.check_current_query and self.check_safe_collation( query ):
      self.check_current_query = False

    if query:
      self.query( query )

    # Extract var out of cached results based x,y vals
    #if self.last_result[y]:  # IndexError: list index out of range
    if not Php.empty(self.last_result, y):
      values = Php.array_values( Php.get_object_vars( self.last_result[y] ) )
      #L.debug("wpdb.get_var: values= {}", values)

    # If there is a value return it else return None
    #return ( isset( values[x] ) and values[x] != '' ) ? values[x] : None
    #L.debug("wpdb.get_var: values[x]= {}", values[x],
    #      ( Php.isset(locals(), 'values') and values[x] != ''))
    return values[x] if ( Php.isset(locals(), 'values') and values[x] != ''
                        ) else None


  def get_row(self, query = None, output = OBJECT, y = 0 ):
    ''' Retrieve one row from the database.
    Executes a SQL query and returns the row from the SQL result.
    @param str|None query  SQL query.
    @param str      output Optional. The required return type. One of OBJECT,
                          ARRAY_A, or ARRAY_N, which correspond to an stdClass
                          object, an associative array, or a numeric array,
                          respectively. Default OBJECT.
    @param int         y      Optional. Row to return. Indexed from 0.
    @return array|object|None|void Database query result in format specified by output or None on failure
    '''
    #self->func_call = "\$db->get_row(\"$query\",$output,$y)";
    self.func_call = 'db.get_row("{}", {}, {})'.format(query, output, y)

    if self.check_current_query and self.check_safe_collation( query ):
      self.check_current_query = False

    if query:
      self.query( query )
    else:
      return None

    #if y not in self.last_result:  # self.last_result is a list in py, so:
    #if y >= len(self.last_result) or y < 0:   # [1,2,3][2] = 3
    if  not Php.isset(self.last_result, y):
      return None

    if output == OBJECT:
      return self.last_result[y] if self.last_result[y] else None
    elif output == ARRAY_A:
      return Php.get_object_vars( self.last_result[y]
                             ) if self.last_result[y] else None
    elif output == ARRAY_N:
      return Php.array_values( Php.get_object_vars( self.last_result[y] ) ) if self.last_result[y] else None
    elif Php.strtoupper( output ) == OBJECT:
      # Back compat for OBJECT being previously case insensitive.
      return self.last_result[y] if self.last_result[y] else None
    else:
      self.print_error( " db.get_row(string query, output type, int offset) "
                    "-- Output type must be one of: OBJECT, ARRAY_A, ARRAY_N")


  def get_col(self, query = None , x = 0 ):
    ''' Retrieve one column from the database.
    Executes a SQL query and returns the column from the SQL result.
    If the SQL result contains more than one column, this function returns the column specified.
    If query is None, this function returns the specified column from the previous SQL result.
    @param string|None query Optional. SQL query. Defaults to previous query.
    @param int         x     Optional. Column to return. Indexed from 0.
    @return array Database query result. Array indexed from 0 by SQL result row number.
    '''
    #if self.check_current_query and self.check_safe_collation( query ):
    #  self.check_current_query = False

    if query:
      self.query( query )

    new_array = array()
    # Extract the column values
    #for ( i = 0, j = count( self.last_result ); i < j; i++ ) {
    i = 0
    while i < len( self.last_result ):
      new_array[i] = self.get_var( None, x, i )
      i += 1
    return new_array


  def get_results(self, query = None, output = OBJECT ):
    ''' Retrieve an entire SQL result set from the database (i.e., many rows)
    Executes a SQL query and returns the entire SQL result.
    @param string query  SQL query.
    @param string output Optional. Any of ARRAY_A | ARRAY_N | OBJECT | OBJECT_K constants.
                          With one of the first three, return an array of rows indexed from 0 by SQL result row number.
                          Each row is an associative array (column : value, ...), a numerically indexed array (0 : value, ...), or an object. ( ->column = value ), respectively.
                          With OBJECT_K, return an associative array of row objects keyed by the value of each row's first column's value.
                          Duplicate keys are discarded.
    @return array|object|None Database query results

    [get_results() vs query()](wordpress.stackexchange.com/questions/166260/)
    query() method is the general method to do queries with $wpdb
    get_results() method uses the query() method to retrieve specific results
      and does some work on the output.
    the work of the query is done by query(). Eveything after that is just
    "casting" the results to the data type specified by the $output argument.
    '''
    #self.func_call = '\$db->get_results("$query", $output)'
    self.func_call = 'db.get_results("{}", {})'.format(query, output)

    if self.check_current_query and self.check_safe_collation( query ):
      self.check_current_query = False

    if query:
      self.query( query )
    else:
      return None

    new_array = array()

    if output == OBJECT:
      # Return an integer-keyed array of row objects
      return self.last_result

    elif output == OBJECT_K:
      # Return an array of row objects with keys from column 1
      # (Duplicates are discarded)
      for row in self.last_result:               # row = BaseCls obj
        var_by_ref = Php.get_object_vars( row )  # = BaseCls.__dict__
        #key = list(var_by_ref.values())[0]
        key = Php.array_shift( var_by_ref )
        #if key not in new_array:
        if not Php.isset(new_array, key):
          new_array[ key ] = row
      return new_array

    elif output == ARRAY_A or output == ARRAY_N:
      # Return an integer-keyed array of...
      if self.last_result:
        for row in Php.Array( self.last_result ):
          if output == ARRAY_N:
            # ...integer-keyed row arrays  #TODO: Verify order or values()!!
            new_array[None] = Php.array_values( Php.get_object_vars( row ))
          else:
            # ...column name-keyed row arrays
            new_array[None] = Php.get_object_vars( row )
      return new_array

    elif Php.strtoupper( output ) == OBJECT:
      # Back compat for OBJECT being previously case insensitive.
      return self.last_result

    return None


  def get_table_charset(self, table ):
    ''' Retrieves the character set for the given table.
    @param string table Table name.
    @return string|WP_Error Table character set, WP_Error object if it couldn't be found.
    >>> res = self.get_results('SHOW FULL COLUMNS FROM `wp_terms`')
    >>> pprint(self.col_meta['wp_terms']['slug']._obj )
    OrderedDict([('Field', 'slug'), ('Type', 'varchar(200)'),
                 ('Collation', 'utf8mb4_unicode_ci'),
                 ('Privileges', 'select,insert,update,references'),...
                 ('Comment', '')])
    >>> self.col_meta['wp_terms']['slug'].Collation   #= 'utf8mb4_unicode_ci'
    '''
    tablekey = Php.strtolower( table )

    # Filters the table charset value before the DB is checked.
    # Passing a non-None value to the filter will effectively short-circuit
    # checking the DB for the charset, returning that value instead.
    # @param string charset The character set to use. Default None.
    # @param string table   The name of the table being checked.
    charset = WiPg.apply_filters( 'pre_get_table_charset', None, table )
    if None != charset:
      return charset

    if Php.isset(self.table_charset, tablekey):
      return self.table_charset[ tablekey ]

    #charsets = columns = array()   #bad.  same mutable array() or {}
    charsets = array()
    columns  = array()

    table_parts = table.split( '.' )
    #table = '`' + implode( '`.`', table_parts ) + '`'
    table  = '`' + '`.`'.join( table_parts ) + '`'
    results = self.get_results( "SHOW FULL COLUMNS FROM "+ table )
    if not results:
      return WcE.WP_Error( 'wpdb_get_table_charset_failure' )

    for column in results:
      columns[ Php.strtolower( column.Field ) ] = column

    self.col_meta[ tablekey ] = columns

    for column in columns:   # same as columns.values():
      if not Php.empty(column, 'Collation'):
        #list( charset ) = column.Collation.split( '_' )
        charset = column.Collation.split( '_' )[0]

        # If the current connection can't support utf8mb4 characters, let's only send 3-byte utf8 characters.
        if 'utf8mb4' == charset and not self.has_cap( 'utf8mb4' ):
          charset = 'utf8'

        charsets[ Php.strtolower( charset ) ] = True

      #list( Type ) = column.Type.split( '(' )
      Type = column.Type.split( '(' )[0]

      # A binary/blob means the whole query gets treated like this.
      if Php.strtoupper( Type ) in ( 'BINARY', 'VARBINARY', 'TINYBLOB', 'MEDIUMBLOB', 'BLOB', 'LONGBLOB' ):
        self.table_charset[ tablekey ] = 'binary'
        return 'binary'

    # utf8mb3 is an alias for utf8.
    if Php.isset(charsets, 'utf8mb3'):
      charsets['utf8'] = True
      del charsets['utf8mb3']

    # Check if we have more than one charset in play.
    count = len( charsets )
    if 1 == count:
      charset = Php.key( charsets )
    elif 0 == count:
      # No charsets, assume this table can store whatever.
      charset = False
    else:
      # More than one charset. Remove latin1 if present and recalculate.
      del charsets['latin1']
      count = len( charsets )
      if 1 == count:
        # Only one charset (besides latin1).
        charset = Php.key( charsets )
      elif (2 == count and Php.isset(charsets , 'utf8') and
                           Php.isset(charsets , 'utf8mb4')):
        # Two charsets, but they're utf8 and utf8mb4, use utf8.
        charset = 'utf8'
      else:
        # Two mixed character sets. ascii.
        charset = 'ascii'

    self.table_charset[ tablekey ] = charset
    return charset


  def get_col_charset(self, table, column ):
    ''' Retrieves the character set for the given column.
    @param string table  Table name.
    @param string column Column name.
    @return string|False|WP_Error Column character set as a string. False if the column has no
                                  character set. WP_Error object if there was an error.
    '''
    tablekey = Php.strtolower( table )
    columnkey = Php.strtolower( column )

    # Filters the column charset value before the DB is checked.
    # Passing a non-None value to the filter will short-circuit
    # checking the DB for the charset, returning that value instead.
    # @param string charset The character set to use. Default None.
    # @param string table   The name of the table being checked.
    # @param string column  The name of the column being checked.
    charset = WiPg.apply_filters( 'pre_get_col_charset', None, table, column )
    if None != charset:
      return charset

    # Skip this entirely if this isn't a MySQL database.
    if Php.empty( self, 'is_mysql' ):
      return False

    if Php.empty( self.table_charset, 'tablekey' ):
      # This primes column information for us.
      table_charset = self.get_table_charset( table )
      if self.Wj.is_wp_error( table_charset ):
        return table_charset

    # If still no column information, return the table charset.
    if Php.empty( self.col_meta, ' tablekey' ):
      return self.table_charset[ tablekey ]

    # If this column doesn't exist, return the table charset.
    if Php.empty( self.col_meta[ tablekey ], 'columnkey' ):
      return self.table_charset[ tablekey ]

    # Return False when it's not a string column.
    if Php.empty( self.col_meta[ tablekey ][ columnkey ], 'Collation' ):
      return False

    #list( $charset ) = explode( '_', $this->col_meta[ $tablekey ][ $columnkey ]->Collation );
    #charset= self.col_meta[ tablekey ][ columnkey ].Collation.split( '_' )[0]
    charset = Php.explode( '_',
                          self.col_meta[ tablekey ][ columnkey ].Collation)[0]
    return charset


  def get_col_length(self, table, column ):
    ''' Retrieve the maximum string length allowed in a given column.
    The length may either be specified as a byte length or a character length.
    @param string table  Table name.
    @param string column Column name.
    @return array|False|WP_Error { 'length' : (int), 'type' : 'byte' | 'char' }
                                 False if the column has no length (for example, numeric column)
                                 WP_Error object if there was an error.
    '''
    tablekey = Php.strtolower( table )
    columnkey = Php.strtolower( column )

    # Skip this entirely if this isn't a MySQL database.
    if Php.empty( self, 'is_mysql' ):
      return False

    if Php.empty( self.col_meta, tablekey ):
      # This primes column information for us.
      table_charset = self.get_table_charset( table )
      if self.Wj.is_wp_error( table_charset ):
        return table_charset

    if Php.empty( self.col_meta[ tablekey ], columnkey ):
      return False

    #typeinfo= self.col_meta[ tablekey ][ columnkey ].Type.split( '(' )
    typeinfo = Php.explode( '(', self.col_meta[ tablekey ][ columnkey ].Type )

    Type = Php.strtolower( typeinfo[0] )
    if not Php.empty(typeinfo, 1):
      length = Php.trim( typeinfo[1], ')' )
    else:
      length = False

    if Type in ( 'char', 'varchar'):
      return array(
        ('type'  , 'char'),
        ('length', int( length )),
      )
    elif Type in ('binary', 'varbinary'):
      return array(
        ('type'  , 'byte'),
        ('length', int( length )),
      )
    elif Type in ('tinyblob', 'tinytext'):
      return array(
        ('type'  , 'byte'),
        ('length', 255),        # 2^8 - 1
      )
    elif Type in ('blob', 'text'):
      return array(
        ('type'  , 'byte'),
        ('length', 65535),      # 2^16 - 1
      )
    elif Type in ('mediumblob', 'mediumtext'):
      return array(
        ('type'  , 'byte'),
        ('length', 16777215),   # 2^24 - 1
      )
    elif Type in ('longblob', 'longtext'):
      return array(
        ('type'  , 'byte'),
        ('length', 4294967295), # 2^32 - 1
      )
    else:
      return False


  def check_ascii(self, string ):
    ''' Check if a string is ASCII.
    The negative regex is faster for non-ASCII strings, as it allows
    the search to finish as soon as it encounters a non-ASCII character.
    @param string string String to check.
    @return bool True if ASCII, False if not.
    '''
    if Php.function_exists( 'mb_check_encoding' ): #from pyx.unicode.IsAscii
      if Php.mb_check_encoding( string, 'ASCII' ):
        return True
    #elif  not Php.preg_match( '/[^0x00-0x7F]/', string ):
    elif not Php.preg_match( '/[^\\x00-\\x7F]/', string ):
      return True

    return False


  def check_safe_collation(self, query ):
    ''' Check if the query is accessing a collation considered safe on the current version of MySQL.
    @param string query The query to check.
    @return bool True if the collation is safe, False if it isn't.
    '''
    if self.checking_collation:
      return True

    # We don't need to check the collation for queries that don't read data.
    query = Php.ltrim( query, "\r\n\t (" )
    if Php.preg_match( '/^(?:SHOW|DESCRIBE|DESC|EXPLAIN|CREATE)\s/i', query ):
      return True

    # All-ASCII queries don't need extra checking.
    if self.check_ascii( query ):
      return True

    table = self.get_table_from_query( query )
    if not table:
      return False

    self.checking_collation = True
    collation = self.get_table_charset( table )
    self.checking_collation = False

    # Tables with no collation, or latin1 only, don't need extra checking.
    if False is collation or 'latin1' == collation:
      return True

    table = Php.strtolower( table )
    if Php.empty( self.col_meta, table ):
      return False

    #L.debug("\nwpdb check_safe_collation col_meta[table] {}",
    #        self.col_meta[table])
    # If any of the columns don't have one of these collations, it needs more sanity checking.
    for col in self.col_meta[ table ]:   # same as .values():
      #L.debug("\nwpdb check_safe_collation col= {}", col); L.debug(col)
      if Php.empty( col, 'Collation' ):
        continue

      if col.Collation not in ( 'utf8_general_ci', 'utf8_bin',
                                'utf8mb4_general_ci', 'utf8mb4_bin' ):
        return False

    return True


  def strip_invalid_text(self, data ):
    ''' Strips any invalid characters based on value/charset pairs.
    @param array data Array of value arrays. Each value array has the keys
                       'value' and 'charset'. An optional 'ascii' key can be
                       set to False to avoid redundant ASCII checks.
    @return array|WP_Error The data parameter, with invalid characters removed from
                           each value. This works as a passthrough: any additional keys
                           such as 'field' are retained in each value array. If we cannot
                           remove invalid characters, a WP_Error object is returned.
    '''
    db_check_string = False
    #pprint(data)  # TypeError: unhashable type: 'instancemethod'
    # userdata is array, inspect.ismethod(A.__repr__) is True
    #L.debug('wpdb.strip_invalid_text {}', data)

    #Orig: foreach ( data as &value ) {   # &value is reference
    #Old: To simulate ref, &value = data[i], which can be assigned to new val
    #Old: for i, value in enumerate(data):      # data was ODict or dict
    #New: below, since data is now Php.array(), can mutate data[k] to NewValue
    #New: change data[i] to data[k] since &value = data[k]
    for k, value in data.items():
      charset = value['charset']

      if Php.is_array( value['length'] ):
        length = value['length']['length']
        truncate_by_byte_length = 'byte' == value['length']['type']
      else:
        length = False
        # Since we have no length, we'll never truncate.
        # Initialize the variable to False. True would take us
        # through an unnecessary (for this case) codepath below.
        truncate_by_byte_length = False

      # There's no charset to work with.
      if False is charset:
        continue

      # Column isn't a string.
      if not Php.is_string( value['value'] ):
        continue

      needs_validation = True
      if ( # latin1 can store any byte sequence
           'latin1' == charset
      or   # ASCII is always OK.
          (not Php.isset(value, 'ascii') and self.check_ascii(value['value']))
      ):
        truncate_by_byte_length = True
        needs_validation = False

      if truncate_by_byte_length:
        WiFc.mbstring_binary_safe_encoding()
        if False is not length and Php.strlen( value['value'] ) > length:
          #value[ 'value'] = Php.substr( value['value'], 0, length )
          data[k]['value'] = Php.substr( value['value'], 0, length )
        WiFc.reset_mbstring_encoding()

        if not needs_validation:
          continue

      # utf8 can be handled by regex, which is a bunch faster than a DB lookup.
      if ( 'utf8' == charset or 'utf8mb3' == charset or 'utf8mb4' == charset
          ) and Php.function_exists( 'mb_strlen' ):
        regex = ( '/'    # REMOVE ALL SPACE IN regex !!!
          '((?:[\\x00-\\x7F]'         # single-byte sequences 0xxxxxxx
          '|[\\xC2-\\xDF][\\x80-\\xBF]'  # double-byte sequences 110xxxxx 10xxxxxx
          '|\\xE0[\\xA0-\\xBF][\\x80-\\xBF]' # triple-byte seq 1110xxxx 10xxxxxx *2
          '|[\\xE1-\\xEC][\\x80-\\xBF]{2}'
          '|\\xED[\\x80-\\x9F][\\x80-\\xBF]'
          '|[\\xEE-\\xEF][\\x80-\\xBF]{2}' )
         #'((?:[0x00-0x7F]'         # single-byte sequences 0xxxxxxx
         #'|[0xC2-0xDF][0x80-0xBF]'  # double-byte sequences 110xxxxx 10xxxxxx
         #'|0xE0[0xA0-0xBF][0x80-0xBF]' # triple-byte seq 1110xxxx 10xxxxxx *2
         #'|[0xE1-0xEC][0x80-0xBF]{2}'
         #'|0xED[0x80-0x9F][0x80-0xBF]'
         #'|[0xEE-0xEF][0x80-0xBF]{2}' )

        if 'utf8mb4' == charset:
          regex += (
            '|\\xF0[\\x90-\\xBF][\\x80-\\xBF]{2}' # 4-byte seq 11110xxx 10xxxxxx *3
            '|[\\xF1-\\xF3][\\x80-\\xBF]{3}'
            '|\\xF4[\\x80-\\x8F][\\x80-\\xBF]{2}'
           #'|0xF0[0x90-0xBF][0x80-0xBF]{2}' # 4-byte seq 11110xxx 10xxxxxx *3
           #'|[0xF1-0xF3][0x80-0xBF]{3}'
           #'|0xF4[0x80-0x8F][0x80-0xBF]{2}'
          )

        regex += ('){1,40}'                          # ...one or more times
          ')'
        # '|.' #VT Don't know why but must remove it to work!! # anything else
          '/' )
        # '/x')        php.net/manual/en/reference.pcre.pattern.modifiers.php
        ''' x PCRE-EXTENDED:  If this modifier is set, whitespace data characters in the pattern are totally ignored except when escaped or inside a character class, and characters between an unescaped # outside a character class and the next newline character, inclusive, are also ignored. This is equivalent to Perl's /x modifier, and makes it possible to include commentary inside complicated patterns. Note, however, that this applies only to data characters. Whitespace characters may never appear within special character sequences in a pattern, for example within the sequence (?( which introduces a conditional subpattern. '''
        #value['value'] = Php.preg_replace( regex, '$1', value['value'] )
        #data[i]['value'] = Php.preg_replace( regex, '$1', value['value'] )
        data[k][ 'value'] = Php.preg_replace( regex, '\\1', value['value'] )


        if False != length and \
              Php.mb_strlen( value['value'], 'UTF-8' ) > length:
          #value['value'] = Php.mb_substr(value['value'], 0, length, 'UTF-8')
          #data[i]['value'] = Php.mb_substr(value['value'], 0, length,'UTF-8')
          data[k][ 'value'] = Php.mb_substr(value['value'], 0, length,'UTF-8')
        continue

      # We couldn't use any local conversions, send it to the DB.
      #value['db'] = db_check_string = True
      #data[i]['db'] = db_check_string = True
      data[k][ 'db'] = db_check_string = True

    #end:# for i, value in enumerate(data):

    #del value   # Remove by reference. # no need since no ref in py

    if db_check_string:
      queries = array()
      for col, value in data.items():
        if not Php.empty(value, 'db'):
          # We're going to need to truncate by characters or bytes, depending
          #     on the length value we have.
          # wp> $data['a'] => bool(false)
          # wp> $data['a']['b'] => NULL
          #if 'byte' == value['length']['type']:  #since value['length']=False
          if (Php.is_array( value['length']) and
              'byte' == value['length'].get('type', None)):
            # Using binary causes LEFT() to truncate by bytes.
            charset = 'binary'
          else:
            charset = value['charset']

          if self.charset:
            connection_charset = self.charset
          else:
            if self.use_mysqli:
              connection_charset = mysqli_character_set_name( self.dbh )
            else:
              connection_charset = mysql_client_encoding()

          if Php.is_array( value['length'] ):
            queries[ col ] = self.prepare(
                    "CONVERT( LEFT( CONVERT( %s USING {} ), %.0f ) USING {} )"
                    .format(charset, connection_charset), value['value'],
                            value['length']['length'] )
          elif 'binary' != charset:
            # If we don't have a length, there's no need to convert binary
            #    - it will always return the same result.
            queries[ col ] = self.prepare(
                    "CONVERT( CONVERT( %s USING {} ) USING {} )"
                    .format(charset, connection_charset), value['value'] )

          del data[ col ]['db']

      sql = array()
      for column, query in queries.items():
        if not query:
          continue
        sql[None] = query + " AS x_column"

      self.check_current_query = False
      #row = self.get_row( "SELECT " + implode( ', ', sql ), ARRAY_A )
      row  = self.get_row( "SELECT " + ', '.join( sql ), ARRAY_A )
      if not row:
        return WcE.WP_Error( 'wpdb_strip_invalid_text_failure' )

      for column in Php.array_keys( data ):
        if Php.isset(row, "x_"+ str(column)):
          data[ column ]['value'] = row["x_"+ str(column)]

    return data


  def strip_invalid_text_from_query(self, query ):
    ''' Strips any invalid characters from the query.
    @param string query Query to convert.
    @return string|WP_Error The converted query, or a WP_Error object if the conversion fails.
    '''
    # We don't need to check the collation for queries that don't read data.
    trimmed_query = Php.ltrim( query, "\r\n\t (" )
    if Php.preg_match( '/^(?:SHOW|DESCRIBE|DESC|EXPLAIN|CREATE)\s/i', trimmed_query ):
      return query

    table = self.get_table_from_query( query )
    if table:
      charset = self.get_table_charset( table )
      if self.Wj.is_wp_error( charset ):
        return charset

      # We can't reliably strip text from tables containing binary/blob columns
      if 'binary' == charset:
        return query
    else:
      charset = self.charset

    data = array(
      ('value'  , query),
      ('charset', charset),
      ('ascii'  , False),
      ('length' , False),
    )

    #L.debug('wpdb.strip_invalid_text_from_query: data = {}', dict(data))
    data = self.strip_invalid_text( array( data ) )
    if self.Wj.is_wp_error( data ):
      return data

    return data[0]['value']


  def strip_invalid_text_for_column(self, table, column, value ):
    ''' Strips any invalid characters from the string for a given table and column.
    @param string table  Table name.
    @param string column Column name.
    @param string value  The text to check.
    @return string|WP_Error The converted string, or a WP_Error object if the conversion fails.
    '''
    if not Php.is_string( value ):
      return value

    charset = self.get_col_charset( table, column )
    if not charset:
      # Not a string column.
      return value
    elif self.Wj.is_wp_error( charset ):
      # Bail on real errors.
      return charset

    data = array(
      (column, array(
        ('value'  , value),
        ('charset', charset),
        ('length' , self.get_col_length( table, column )),
      ))
    )

    data = self.strip_invalid_text( data )
    if self.Wj.is_wp_error( data ):
      return data

    return data[ column ]['value']


  def get_table_from_query(self, query ):
    ''' Find the first table name referenced in a query.
    @param string query The query to search.
    @return string|False table The table name found, or False if a table couldn't be found.
    '''
    # Remove characters that can legally trail the table name.
    query = Php.rtrim( query, ';/-#' )

    # Allow (select...) union [...] style queries. Use the first query's table name.
    query = Php.ltrim( query, "\r\n\t (" )

    # Strip everything between parentheses except nested selects.
    query = Php.preg_replace( '/\((?!\s*select)[^(]*?\)/is', '()', query )
    #L.debug('wpdb.get_table_from_query query= {}', query)

    # Quickly match most common queries.
    Result, maybe = Php.preg_match_Result( '/^\s*(?:'
         'SELECT.*?\s+FROM'
         '|INSERT(?:\s+LOW_PRIORITY|\s+DELAYED|\s+HIGH_PRIORITY)?(?:\s+IGNORE)?(?:\s+INTO)?'
         '|REPLACE(?:\s+LOW_PRIORITY|\s+DELAYED)?(?:\s+INTO)?'
         '|UPDATE(?:\s+LOW_PRIORITY)?(?:\s+IGNORE)?'
        #'|DELETE(?:\s+LOW_PRIORITY|\s+QUICK|\s+IGNORE)*(?:\s+FROM)?' #VT4.6.1
         '|DELETE(?:\s+LOW_PRIORITY|\s+QUICK|\s+IGNORE)*(?:.+?FROM)?'
         ')\s+((?:[0-9a-zA-Z$_.`-]|[\\xC2-\\xDF][\\x80-\\xBF])+)/is', query)
        #')\s+((?:[0-9a-zA-Z$_.`-]|[0xC2-0xDF][0x80-0xBF])+)/is', query)
    #if len(maybe) > 0:
    #  L.debug('wpdb.get_table_from_query maybe 1= {}', maybe)
    if Result:
      return Php.str_replace( '`', '', maybe[1] )

    ## SHOW TABLE STATUS and SHOW TABLES                 # WP 4.6.1 Start
    #Result, maybe = Php.preg_match_Result( '/^\s*(?:'
    #     'SHOW\s+TABLE\s+STATUS.+(?:LIKE\s+|WHERE\s+Name\s*=\s*)'
    #     '|SHOW\s+(?:FULL\s+)?TABLES.+(?:LIKE\s+|WHERE\s+Name\s*=\s*)'
    #     ')\W((?:[0-9a-zA-Z$_.`-]|[\\xC2-\\xDF][\\x80-\\xBF])+)\W/is', query)
    #    #')\W((?:[0-9a-zA-Z$_.`-]|[0xC2-0xDF][0x80-0xBF])+)\W/is', query)
    #if Result:
    #  return Php.str_replace( '`', '', maybe[1] )       # WP 4.6.1 End

    # SHOW TABLE STATUS and SHOW TABLES WHERE Name = 'wp_posts'
    Result, maybe = Php.preg_match_Result( '/^\s*SHOW\s+(?:TABLE\s+STATUS|(?:FULL\s+)?TABLES).+WHERE\s+Name\s*=\s*("|\')((?:[0-9a-zA-Z$_.-]|[\xC2-\xDF][\x80-\xBF])+)\\1/is', query )
    if Result:
      return maybe[2]

    # SHOW TABLE STATUS LIKE and SHOW TABLES LIKE 'wp\_123\_%'
    # This quoted LIKE operand seldom holds a full table name.
    # It is usually a pattern for matching a prefix so we just
    # strip the trailing % and unescape the _ to get 'wp_123_'
    # which drop-ins can use for routing these SQL statements.
    Result, maybe = Php.preg_match_Result( '/^\s*SHOW\s+(?:TABLE\s+STATUS|(?:FULL\s+)?TABLES)\s+(?:WHERE\s+Name\s+)?LIKE\s*("|\')((?:[\\\\0-9a-zA-Z$_.-]|[\xC2-\xDF][\x80-\xBF])+)%?\\1/is', query )
    #if len(maybe) > 0:
    #  L.debug('wpdb.get_table_from_query maybe 2= {}', maybe)
    if Result:
      return Php.str_replace( '\\_', '_', maybe[2] )

    # Big pattern for the rest of the table-related queries.
    Result, maybe = Php.preg_match_Result( '/^\s*(?:'
         '(?:EXPLAIN\s+(?:EXTENDED\s+)?)?SELECT.*?\s+FROM'
         '|DESCRIBE|DESC|EXPLAIN|HANDLER'
         '|(?:LOCK|UNLOCK)\s+TABLE(?:S)?'
         '|(?:RENAME|OPTIMIZE|BACKUP|RESTORE|CHECK|CHECKSUM|ANALYZE|REPAIR).*\s+TABLE'
         '|TRUNCATE(?:\s+TABLE)?'
         '|CREATE(?:\s+TEMPORARY)?\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?'
         '|ALTER(?:\s+IGNORE)?\s+TABLE'
         '|DROP\s+TABLE(?:\s+IF\s+EXISTS)?'
         '|CREATE(?:\s+\w+)?\s+INDEX.*\s+ON'
         '|DROP\s+INDEX.*\s+ON'
         '|LOAD\s+DATA.*INFILE.*INTO\s+TABLE'
         '|(?:GRANT|REVOKE).*ON\s+TABLE'
         '|SHOW\s+(?:.*FROM|.*TABLE)'
         ')\s+\(*\s*((?:[0-9a-zA-Z$_.`-]|[\\xC2-\\xDF][\\x80-\\xBF])+)\s*\)*/is',
        #')\s+\(*\s*((?:[0-9a-zA-Z$_.`-]|[0xC2-0xDF][0x80-0xBF])+)\s*\)*/is',
         query)
    #if len(maybe) > 0:
    #  L.debug('wpdb.get_table_from_query maybe 3= {}', maybe)
    if Result:
      return Php.str_replace( '`', '', maybe[1] )

    return False


  def load_col_info(self):
    ''' Load the column metadata from the last query.
    @access protected
    '''
    if self.col_info:
      return
    self.col_info = array() #VT Added.  Php need not init, but py need to init

    if self.use_mysqli:
      num_fields = Php.mysqli_num_fields( self.dbh ) # Orig: result --> dbh
      #for ( i = 0; i < num_fields; i++ ) {
      for i in range( num_fields ):
        #self.col_info[ i ] = mysqli_fetch_field( self.result )
        self.col_info[ i ] = Php.mysqli_fetch_field(self.dbh, i) #result-->dbh
    else:
      num_fields = Php.mysql_num_fields( self.dbh ) # Orig: result --> dbh
      #for ( i = 0; i < num_fields; i++ ) {
      for i in range( num_fields ):
        self.col_info[ i ] = Php.mysql_fetch_field(self.dbh, i) #result-->dbh


  def get_col_info(self, info_type = 'name', col_offset = -1 ):
    ''' Retrieve column metadata from the last query.
    @param string info_type  Optional. Type one of name, table, def, max_length, not_null, primary_key, multiple_key, unique_key, numeric, blob, type, unsigned, zerofill
    @param int    col_offset Optional. 0: col name. 1: which table the col's in. 2: col's max length. 3: if the col is numeric. 4: col's type
    @return mixed Column Results
    '''
    self.load_col_info()

    if self.col_info:
      if col_offset == -1:
        i = 0
        new_array = array()
        for col in Php.Array( self.col_info ):
          new_array[i] = getattr(col, info_type)
          i += 1
        return new_array
      else:
        return getattr(self.col_info[col_offset], info_type)


  def timer_start(self):
    ''' Starts the timer, for debugging purposes.
    @return True
    '''
    self.time_start = Php.microtime( True )
    return True


  def timer_stop(self):
    ''' Stops the debugging timer.
    @return float Total time spent on the query, in seconds
    '''
    return ( Php.microtime( True ) - self.time_start )


  def bail(self, message, error_code = '500' ):
    ''' Wraps errors in a nice header and footer and dies.
    Will not die if wpdb::show_errors is False.
    @param string message    The Error message
    @param string error_code Optional. A Computer readable string to identify the error.
    @return False|void
    '''
    if not self.show_errors:
      if Php.class_exists( 'WP_Error', False ):
        self.error = WcE.WP_Error(error_code, message)
      else:
        self.error = message
      L.errorrint("wpdb.bail {}", self.error)
      if error_code != 500:   # VT Added this so 500 error_code will wp_die !
        # err msg=LDb.db_connect:  Unable to connect to db2:3306 to read table
        return False
    WiFc.wp_die(message)


  def close(self):
    ''' Closes the current database connection.
    @return bool True if the connection was successfully closed, False if it wasn't,
                 or the connection doesn't exist.
    '''
    if not self.dbh:
      return False

    if self.use_mysqli:
      closed = Php.mysqli_close( self.dbh )
    else:
      closed = Php.mysql_close( self.dbh )

    if closed:
      self.dbh = None
      self.ready = False
      self.has_connected = False

    return closed


  def check_database_version(self):
    ''' Whether MySQL database is at least the required minimum version.
    @global string wp_version
    @global string required_mysql_version
    @return WP_Error|void
    '''
    #global var==>self.Wj.var, except: var=self.Wj.var=same Obj,mutable array
    # global required_mysql_version
    required_mysql_version = self.Wj.required_mysql_version
    wp_version = self.Wj.wp_version   # global wp_version

    # Make sure the server has the required MySQL version
    if Php.version_compare(self.db_version(), required_mysql_version, '<'):
      # translators: 1: WordPress version number, 2: Minimum required MySQL version number
      return WcE.WP_Error('database_version',__('ERROR: WordPress {} requires'
            'MySQL {} or higher' ).format(wp_version, required_mysql_version))


  def supports_collation(self):
    ''' Whether the database supports collation.
    Called when WordPress is generating the table scheme.
    Use `wpdb::has_cap( 'collation' )`.
    @deprecated 3.5.0 Use wpdb::has_cap()
    @return bool True if collation is supported, False if version does not
    '''
    #_deprecated_function( __FUNCTION__, '3.5.0', 'wpdb::has_cap( \'collation\' )' )
    return self.has_cap( 'collation' )


  def get_charset_collate(self):
    ''' The database character collate.
    @return string The database character collate.
    '''
    charset_collate = ''

    if not Php.empty(self, 'charset'):
      charset_collate = "DEFAULT CHARACTER SET "+ self.charset
    if not Php.empty(self, 'collate'):
      charset_collate += " COLLATE "+ self.collate

    return charset_collate


  def has_cap(self, db_cap ):
    ''' Determine if a database supports a particular feature.
    @see wpdb::db_version()
    @param string db_cap The feature to check for. Accepts 'collation',
                          'group_concat', 'subqueries', 'set_charset',
                          or 'utf8mb4'.
    @return int|False Whether the database feature is supported, False otherwise.
    '''
    version = self.db_version()

    DbCapLower = db_cap.lower()
    if DbCapLower in ('collation', 'group_concat', 'subqueries'):
      return Php.version_compare( version, '4.1', '>=' )
    if DbCapLower == 'set_charset':
      return Php.version_compare( version, '5.0.7', '>=' )
    if DbCapLower == 'utf8mb4':
      if Php.version_compare( version, '5.5.3', '<' ):
        return False
      if self.use_mysqli:
        client_version = Php.mysqli_get_client_info()
      else:
        client_version = Php.mysql_get_client_info()

      # libmysql has supported utf8mb4 since 5.5.3, same as MySQL server.
      # mysqlnd has supported utf8mb4 since 5.0.9.
      #if False !== Php.strpos( client_version, 'mysqlnd' ):
      if 'mysqlnd' in client_version:
        client_version = Php.preg_replace( '/^\D+([\d.]+).*/', '\\1', client_version )
        return Php.version_compare( client_version, '5.0.9', '>=' )
      else:
        return Php.version_compare( client_version, '5.5.3', '>=' )
    if DbCapLower == 'utf8mb4_520':
      return Php.version_compare( version, '5.6', '>=' )

    return False


  def get_caller(self):
    ''' Retrieve the name of the function that called wpdb.
    Searches up the list of functions until it reaches
    the one that would most logically had called this method.
    @return string|array The name of the calling function
    '''
    return WiFc.wp_debug_backtrace_summary( '__CLASS__' )
    #import pyx.func   as xFn
    #return xFn.caller_name()


  def db_version(self):
    ''' Retrieves the MySQL server version.
    @return None|string Null on failure, version number on success.
    '''
    if self.use_mysqli:
      server_info = Php.mysqli_get_server_info( self.dbh )
    else:
      server_info = Php.mysql_get_server_info( self.dbh )
    return Php.preg_replace( '/[^0-9.].*/', '', server_info )


  def IsObjInstanceOfCursor(self, Obj, Cursor=SqlCur.Cursor):  #VT Added
    ''' isinstance( Wj.wpdb.dbh, SqlCur.Cursor)          #Out=True
        isinstance( Wj.wpdb.dbh, SqlCur.DictCursorMixin) #Out=True
        isinstance( Wj.wpdb.dbh, SqlCur.SSCursor)        #Out=False
    '''
    return isinstance(Obj, Cursor)




class WpDbSingletonCls(wpdb_cls, metaclass = xTp.Singleton):
  '''class wpdb(xTp.SingletonBaseClass):
  instantiate singleton only once
  id(wpdb_cls())         == id(wpdb_cls())         #=> False!! Diff instance!!
  id(WpDbSingletonCls()) == id(WpDbSingletonCls()) #=> True!!  same instance!!
  '''
  # wpdb_cls.__metaclass__ = xTp.Singleton #doesn't work, use metaclass= abvoe
  # __metaclass__ = xTp.Singleton          #also doesn't work
  pass
  #def __init__(self, *args, **kwargs):
  #  wpdb_cls.__init__(self, *args, **kwargs)


# instantiate singleton only once
# id(wpdb_cls()) ==  id(wpdb_cls())  #==> True !!  same instance!!
#wpdb = WpDbSingletonCls()


'''
wp> $wpdb->query("CREATE TEMPORARY TABLE IF NOT EXISTS table2 AS (SELECT * FROM  wp_bp_activity limit 5)")
wp> $wpdb->query( $wpdb->prepare("update table2 set action=%s where ID=%d", $Act, 8))
wp> $Act = '<a href="http://wordpy.com/members/aksylin/" title="千妍姬">千妍姬</a> 已成为注册成员'
wp> $wpdb->prepare("update table2 set action=%s where ID=%d", $Act, 8)
=> string(139) "update table2 set action='<a href=\"http://wordpy.com/members/aksylin/\" title=\"千妍姬\">千妍姬</a> 已成为注册成员' where ID=8"


wpdb.query("CREATE TEMPORARY TABLE IF NOT EXISTS table2 AS (SELECT * FROM  wp_bp_activity limit 5)")
wpdb.query("select * from table2")
wpdb.last_result
Act = '<a href="http://wordpy.com/members/aksylin/" title="千妍姬">千妍姬</a> 已成为注册成员'
Sql = wpdb.prepare("update table2 set action=%s where ID=%d", Act, 8)
wpdb.query( Sql )
Wj.GDB.Exec("select * from table2 where ID=8")

'''


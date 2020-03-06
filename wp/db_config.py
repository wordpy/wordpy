#!/usr/bin/python3
import wpy.db_conf


def DbCallback(query, wpdb):
  #if ( preg_match("/^wp_(?:bp_|users$|usermeta$)/i", $wpdb->table))
  if   wpdb.table in Bj.BDB.Tbs.TbsFed.values():
    return self.GDB.DbDSet
  #if (substr(wpdb.table, 0, 6) === 'wp_7_')
  if   wpdb.table.startswith(self.BDB.Tbs.TbPfx):
    return self.BDB.DbDSet
  raise ValueError("DbCallback: wpdb.table = {} not in GDB or BDB!!")
  #assert self.BDB.Tbs.TbPfx == self.BDB.SPfx + str(BId) +'_'  #if BId > 1

# #########################################################
#  /fs/web/p/ludicrousdb/ludicrousdb/drop-ins/db-config.php
# #########################################################

def db_config(self):
  " LudicrousDB configuration file "

  # charset (string)
  # This sets the default character set. Since WordPress 4.2, the suggested
  # setting is "utf8mb4". We strongly recommend not downgrading to utf8,
  # using latin1, or sticking to the default: utf8mb4.
  # Default: utf8mb4
  self.wpdb.charset = 'utf8mb4'

  # collate (string)
  # This sets the default column collation. For best results, investigate
  # which collation is recommended for your specific character set.
  # Default: utf8mb4_unicode_ci
  self.wpdb.collate = 'utf8mb4_unicode_ci'

  # save_queries (bool)
  # This is useful for debugging. Queries are saved in self.wpdb.queries. It
  # is not a constant because you might want to use it momentarily.
  # Default: False
  self.wpdb.save_queries = False

  # persistent (bool)
  # This determines whether to use mysql_connect or mysql_pconnect. The
  # effects of this setting may vary and should be carefully tested.
  # Default: False
  self.wpdb.persistent = False

  # max_connections (int)
  # This is the number of mysql connections to keep open. Increase if you
  # expect to reuse a lot of connections to different servers. This is ignored
  # if you enable persistent connections.
  # Default: 10
  self.wpdb.max_connections = 10   # Try increase to 30 for better performance

  # check_tcp_responsiveness
  # Enables checking TCP responsiveness by fsockopen prior to mysql_connect or
  # mysql_pconnect. This was added because PHP's mysql funcs do not provide a
  # variable timeout setting. Disabling it may improve average performance by
  # a very tiny margin but lose protection against connections failing slowly.
  # Default: True
  #VT potential error: wordpress.org/support/topic/hyperdb-causing-frequent-mysql-connection-errors
  self.wpdb.check_tcp_responsiveness = True

  # This is the most basic way to add a server to LudicrousDB using only the
  # required parameters: host, user, password, name.
  # This adds the DB defined in wp-config.php as a read/write server for
  # the 'global' dataset. (Every table is in 'global' by default.)
  #self.wpdb.add_database( {
  #  'host'     : DB_HOST,     # If port is other than 3306, use host:port.
  #  'user'     : DB_USER,
  #  'password' : DB_PASSWORD,
  #  'name'     : DB_NAME,
  #} )

  # adds the same server again, only this time it is configured as a slave.
  # The last 3 parameters are set to the defaults but are shown for clarity.
  #self.wpdb.add_database( {
  #  'host'     : DB_HOST,     # If port is other than 3306, use host:port.
  #  'user'     : DB_USER,
  #  'password' : DB_PASSWORD,
  #  'name'     : DB_NAME,
  #  'write'    : 0,
  #  'read'     : 1,
  #  'dataset'  : 'global',
  #  'timeout'  : 0.2,
  #} )



  # #########################################################
  # wp/db-config.php
  # #########################################################

  # HyperDB configuration file
  # This file should be installed at ABSPATH/db-config.php
  # wpdb is an instance of the hyperdb class which extends the wpdb class.
  # HyperDB can manage connections to a large number of databases. Queries are
  # distributed to appropriate servers by mapping table names to datasets.
  # A dataset is defined as a group of tables that are located in the same
  # database. There may be similarly-named databases containing different
  # tables on different servers. There may also be many replicas of a database
  # on different servers. The term "dataset" removes any ambiguity. Consider a
  # dataset as a group of tables that can be mirrored on many servers.
  # Configuring HyperDB involves defining databases and datasets. Defining a
  # database involves specifying the server connection details, the dataset it
  # contains, and its capabilities and priorities for reading and writing.
  # Defining a dataset involves specifying its exact table names or register-
  # ing one or more callback functions that translate table names to datasets.

  # save_queries (bool)
  # This is useful for debugging. Queries are saved in self.wpdb.queries. It
  # is not a constant because you might want to use it momentarily.
  # Default: False
  #self.wpdb.save_queries = False   #Set above
  # For Hyperdb & Query Monitor, stackoverflow.com/questions/2473079/how-to-display-all-database-queries-made-by-wordpress
  #self.wpdb.save_queries = defined('SAVEQUERIES') && SAVEQUERIES = True

  # persistent (bool)
  # This determines whether to use mysql_connect or mysql_pconnect. The
  # effects of this setting may vary and should be carefully tested.
  # Default: False
  #self.wpdb.persistent = False   #Set above

  # max_connections (int)
  # This is the number of mysql connections to keep open. Increase if you
  # expect to reuse a lot of connections to different servers. This is ignored
  # if you enable persistent connections.
  # Default: 10
  #self.wpdb.max_connections = 10   #Set above

  # Enables checking TCP responsiveness by fsockopen prior to mysql_connect or
  # mysql_pconnect. This was added because PHP's mysql funcs do not provide a
  # variable timeout setting. Disabling it may improve average performance by
  # a very tiny margin but lose protection against connections failing slowly.
  # Default: True
  #self.wpdb.check_tcp_responsiveness = True   #Set above

  #AddDbCallBack(self)
  #AddDbs(self)
  wpy.db_conf.WpDbConfigPy(self)


  #self.wpdb.add_callback('my_db_callback')
  #def my_db_callback(query, wpdb):
  #  #error_log(self.wpdb.table)
  #  # Multisite blog tables are "{base_prefix}{blog_id}_*"
  #  #if ( preg_match("/^{self.wpdb.base_prefix}\d+_/i", self.wpdb.table) )
  #  #if preg_match("/^{self.wpdb.base_prefix}20_/i", self.wpdb.table):
  #  #if (self.wpdb.table === 'wp_users' || self.wpdb.table === 'wp_users' ||
  #  if preg_match("/^wp_(?:bp_|users$|usermeta$)/i", self.wpdb.table):
  #    return GDB_DSET
  #  #elif substr(self.wpdb.table, 0, 7) === 'wp_22_':
  #  #  return DS_WPY
  #  else:
  #    return WDB_DSET

def AddDbs(self):

  # db hosts = db1,db2,db3.  Stores wp_global database
  GDB_USER  = 'wpdb_user'
  GDB_PASS  = 'wpdb_pass'
  GDB_DSET  = 'global' # = 'global'       # DSET = dataset
  GDB_NAME  = 'wp_global' # = 'wp_'. GDB_DSET = wp_global

  # db hosts = wdb1,wdb2
  WDB_USER = 'wpdb_user'
  WDB_PASS = 'wpdb_pass'
  WDB_DSET = 'wpdb_dset'
  WDB_NAME = 'wp_wpdb_dset'   # = 'wp_'. WDB_DSET

  self.wpdb.add_database( {
    'host'     : 'db1',
    'user'     : GDB_USER,
    'password' : GDB_PASS,
    'name'     : GDB_NAME,
    'write'    : 1,
    'read'     : 1,
    'dataset'  : GDB_DSET,
    'timeout'  : 0.2,
  } )
  self.wpdb.add_database( {
    'host'     : 'db2',
    'user'     : GDB_USER,
    'password' : GDB_PASS,
    'name'     : GDB_NAME,
    'write'    : 1,
    'read'     : 1,
    'dataset'  : GDB_DSET,
    'timeout'  : 0.2,
  } )

  self.wpdb.add_database( {
    'host'     : 'wdb1',
    'user'     : WDB_USER,
    'password' : WDB_PASS,
    'name'     : WDB_NAME,
    'write'    : 1,
    'read'     : 1,
    'dataset'  : WDB_DSET,
    'timeout'  : 0.2,
  } )
  self.wpdb.add_database( {
    'host'     : 'wdb2',
    'user'     : WDB_USER,
    'password' : WDB_PASS,
    'name'     : WDB_NAME,
    'write'    : 1,
    'read'     : 1,
    'dataset'  : WDB_DSET,
    'timeout'  : 0.2,
  } )

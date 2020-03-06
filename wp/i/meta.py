#!/usr/bin/python3
# Fixed all &value pass by reference
import pyx.func    as xFn
import pyx.php     as Php
#import wpy.db     as wDB
#import wpy.xmlcli as XmlC       # Xml Client Class
import wp.conf     as WpC
import wp.i.cache  as WiCa
import wp.i.format as WiF
import wp.i.func   as WiFc
import wp.i.plugin as WiPg
array = Php.array

#from   wp.i.wpdb import wpdb
#wpdb set in Web.WpBlogCls
#    for Module in (WpT, WiM, WiU, WiO, WpTx):
#      Module.wpdb = self.Wj.wpdb


class MetaC:
  ''' replicate from wp-includes/meta.php
  Core Metadata API
  Functions for retrieving and manipulating metadata of various WP object
  types. Metadata for an object is a represented by a simple key-value pair.
  Objects may contain multiple metadata entries that share the same key and
  differ only in their value.
  '''
  Sj = Bj = Exit = XmlCli = GDB = SDB = BDB = WC0 =None


# Move all staticmethods to module fuctions. staticmethod has no benifit other than grouping them in a class, but we're already grouping all in this module

def add_metadata(meta_type, object_id, meta_key, meta_value, unique = False):
  '''
  Add metadata for the specified object.
  @global wpdb wpdb WordPress database abstraction object.
  @param string meta_type  Type of object metadata is for
                           (e.g., comment, post, or user)
  @param int    object_id  ID of the object metadata is for
  @param string meta_key   Metadata key
  @param mixed  meta_value Metadata value. Must be serializable if non-scalar
  @param bool   unique     Optional, default is False.
                           Whether the specified metadata key should be
                           unique for the object. If True, and the object
                           already has a value for the specified metadata
                           key, no change will be made.
  @return int|False The meta ID on success, False on failure.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if not meta_type or not meta_key or not isinstance(object_id, int):
    return False

  object_id = abs( object_id )
  if not object_id:
    return False

  table = _get_meta_table( meta_type )
  if not table:
    return False

  print("add_metadata: ", meta_type, object_id, meta_key, meta_value, unique)
  column = WiF.sanitize_key(meta_type + '_id')

  # expected_slashed (meta_key)
  meta_key   = WiF.wp_unslash(meta_key)
  meta_value = WiF.wp_unslash(meta_value)
  meta_value = sanitize_meta( meta_key, meta_value, meta_type )

  # Filter whether to add metadata of a specific type.
  # The dynamic portion of the hook, `meta_type`, refers to the meta
  # object type (comment, post, or user). Returning a non-None value
  # will effectively short-circuit the function.
  # @param None|bool check      Whether to allow adding metadata for
  #                             given type.
  # @param int       object_id  Object ID.
  # @param string    meta_key   Meta key.
  # @param mixed     meta_value Meta val. Must be serializable if non-scalar.
  # @param bool      unique     Whether the specified meta key should be
  #                             unique for the object. Optional.Default False
  check = WiPg.apply_filters("add_{}_metadata".format(meta_type), None,
                             object_id, meta_key, meta_value, unique )
  print("add_metadata: ", column, meta_key, meta_value, check)
  if check is not None:
    return check

  #Sql = "SELECT COUNT(*) FROM {} WHERE meta_key = %s AND {} = %d".format(
  # PyMySQL convert int & all to formatted quoted str. Can only use %s!!
  Sql = "SELECT COUNT(*) FROM {} WHERE meta_key = %s AND {} = %s".format(
        table, column)
  #RowDict = wDB.GetDB(MetaC,table).Exec(Sql,(meta_key,object_id,),'fetchone')
  #if unique and RowDict: # RowDict is only 1 dict
  if unique and wpdb.get_var( wpdb.prepare(Sql, meta_key, object_id )):
    return False

  _meta_value = meta_value
  print("add_metadata: ", column, meta_key, meta_value, type(meta_value))
  meta_value = WiFc.maybe_serialize( meta_value )

  # Fires immediately before meta of a specific type is added.
  # The dynamic portion of the hook, `meta_type`, refers to the meta
  # object type (comment, post, or user).
  # @param int    object_id  Object ID.
  # @param string meta_key   Meta key.
  # @param mixed  meta_value Meta value.
  WiPg.do_action( "add_{}_meta".format(meta_type), object_id, meta_key, _meta_value )

  mid = wpdb.insert(table, array( (column, object_id),
                         ('meta_key', meta_key), ('meta_value', meta_value) ))
  if not mid:
    return False
  mid = int(mid)

  WiCa.wp_cache_delete(object_id, meta_type + '_meta')

  # Fires immediately after meta of a specific type is added.
  # The dynamic portion of the hook, `meta_type`, refers to the meta
  # object type (comment, post, or user).
  # @param int    mid        The meta ID after successful update.
  # @param int    object_id  Object ID.
  # @param string meta_key   Meta key.
  # @param mixed  meta_value Meta value.
  WiPg.do_action( "added_{}_meta".format(meta_type), mid, object_id, meta_key, _meta_value )
  return mid


def update_metadata(meta_type, object_id, meta_key, meta_value,
                    prev_value = ''):
  '''Update metadata for the specified object.
       If no value already exists for the specified object
  ID and metadata key, the metadata will be added.
  @global wpdb wpdb WordPress database abstraction object.
  @param string meta_type  Type of object metadata is for
                             (e.g., comment, post, or user)
  @param int    object_id  ID of the object metadata is for
  @param string meta_key   Metadata key
  @param mixed  meta_value Metadata value.Must be serializable if non-scalar.
  @param mixed  prev_value Optional. If specified, only update existing
                           metadata entries with the specified value.
                           Otherwise, update all entries.
  @return int|bool Meta ID if the key didn't exist, True on successful
                           update, False on failure.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if not meta_type or not meta_key or not isinstance(object_id, int):
    return False

  object_id = abs( object_id )
  if not object_id:
    return False

  table = _get_meta_table( meta_type )
  if not table:
    return False

  print("update_metadata:", meta_type, object_id, meta_key, meta_value,
                            prev_value )
  column = WiF.sanitize_key(meta_type + '_id')
  id_column = 'umeta_id' if 'user' == meta_type else 'meta_id'

  # expected_slashed (meta_key)
  raw_meta_key = meta_key
  meta_key     = WiF.wp_unslash(meta_key)
  passed_value = meta_value
  meta_value   = WiF.wp_unslash(meta_value)
  meta_value   = sanitize_meta( meta_key, meta_value, meta_type )

  # Filter whether to update metadata of a specific type.
  # The dynamic portion of the hook, `meta_type`, refers to the meta
  # object type (comment, post, or user). Returning a non-None value
  # will effectively short-circuit the function.
  # @param None|bool check     Whether to allow updating metadata for the
  #                              given type.
  # @param int      object_id  Object ID.
  # @param string   meta_key   Meta key.
  # @param mixed    meta_value Meta value. Must be serializable if non-scalar
  # @param mixed    prev_value Optional. If specified, only update existing
  #                            metadata entries with the specified value.
  #                            Otherwise, update all entries.
  check = WiPg.apply_filters( "update_{}_metadata".format(meta_type), None,
                              object_id, meta_key, meta_value, prev_value )
  if check is not None:
    return bool(check)

  # Compare existing value to new value if no prev value given and
  #     the key exists only once.
  if not prev_value:   # if Php.empty(locals(), 'prev_value'):
    old_value = get_metadata(meta_type, object_id, meta_key)
    if len(old_value) == 1:
      if old_value[0] == meta_value:
        return False

  # meta_ids = wpdb->get_col( wpdb->prepare("SELECT $id_column FROM
  #    $table WHERE meta_key = %s AND $column = %d", $meta_key, $object_id ))
  # meta_ids = wpdb->get_col( wpdb->prepare(
  #Sql = ("SELECT {} FROM {} WHERE meta_key = %s AND {} = %d"
  # PyMySQL convert int & all to formatted quoted str. Can only use %s!!

  Sql = ("SELECT {} FROM {} WHERE meta_key = %s AND {} = %s"
         .format(id_column, table, column))
  meta_ids = wpdb.get_col( wpdb.prepare( Sql, meta_key, object_id ) )
  #RowDicts = wDB.GetDB(MetaC, table).Exec(Sql, (meta_key, object_id,) )
  #if RowDicts:
  #  meta_ids = [ Row[id_column] for Row in RowDicts ]
  #  print("\nupdate_metadata meta_ids=", meta_ids)
  #else:
  if not meta_ids:   # if Php.empty(locals(), 'meta_ids'):
    return add_metadata( meta_type, object_id, raw_meta_key,
                               passed_value )

  _meta_value = meta_value
  meta_value = WiFc.maybe_serialize( meta_value )

  data  = {'meta_value': meta_value}   # compact(locals(), 'meta_value' )
  where = array( (column, object_id), ('meta_key', meta_key) )

  if prev_value:   # if not Php.empty(locals(), 'prev_value'):
    prev_value = WiFc.maybe_serialize(prev_value)
    where['meta_value'] = prev_value

  for meta_id in meta_ids:
    # Fires immediately before updating metadata of a specific type.
    # The dynamic portion of the hook, `meta_type`, refers to the meta
    # object type (comment, post, or user).
    # @param int    meta_id    ID of the metadata entry to update.
    # @param int    object_id  Object ID.
    # @param string meta_key   Meta key.
    # @param mixed  meta_value Meta value.
    WiPg.do_action( "update_{}_meta".format(meta_type), meta_id, object_id, meta_key,
               _meta_value )

    if 'post' == meta_type:
      # Fires immediately before updating a post's metadata.
      # @param int    meta_id    ID of metadata entry to update.
      # @param int    object_id  Object ID.
      # @param string meta_key   Meta key.
      # @param mixed  meta_value Meta value.
      WiPg.do_action( 'update_postmeta', meta_id, object_id, meta_key, meta_value)

  result = wpdb.update( table, data, where )
  if not result:
    return False

  WiCa.wp_cache_delete(object_id, meta_type + '_meta')

  for meta_id in meta_ids:
    # Fires immediately after updating metadata of a specific type.
    # The dynamic portion of the hook, `meta_type`, refers to the meta
    # object type (comment, post, or user).
    # @param int    meta_id    ID of updated metadata entry.
    # @param int    object_id  Object ID.
    # @param string meta_key   Meta key.
    # @param mixed  meta_value Meta value.
    WiPg.do_action( "updated_{}_meta".format(meta_type), meta_id, object_id,
                    meta_key, _meta_value )

    if 'post' == meta_type:
      # Fires immediately after updating a post's metadata.
      # @param int    meta_id    ID of updated metadata entry.
      # @param int    object_id  Object ID.
      # @param string meta_key   Meta key.
      # @param mixed  meta_value Meta value.
      WiPg.do_action('updated_postmeta', meta_id, object_id, meta_key, meta_value)

  return True


def delete_metadata(meta_type, object_id, meta_key, meta_value = '', delete_all = False):
  ''' Delete metadata for the specified object.
  @global wpdb wpdb WordPress database abstraction object.
  @param string meta_type  Type of object metadata is for (e.g., comment, post, or user)
  @param int    object_id  ID of the object metadata is for
  @param string meta_key   Metadata key
  @param mixed  meta_value Optional. Metadata value. Must be serializable if
                           non-scalar. If specified, only delete metadata
                           entries with this value. Otherwise, delete all
                           entries with the specified meta_key.
                           Pass `None, `False`, or an empty string to skip
                           this check.
  @param bool   delete_all Optional, default is False. If True, delete
                           matching metadata entries for all objects,
                           ignoring the specified object_id. Otherwise, only
                           delete matching metadata entries for
                           the specified object_id.
  @return bool True on successful delete, False on failure.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if (not meta_type or not meta_key or not isinstance(object_id, int) and
      not delete_all):
    return False

  object_id = abs( object_id )
  if not object_id and not delete_all:
    return False

  table = _get_meta_table( meta_type )
  if not table:
    return False

  type_column= WiF.sanitize_key(meta_type + '_id')
  id_column  = 'umeta_id' if 'user' == meta_type else 'meta_id'
  # expected_slashed (meta_key)
  meta_key   = WiF.wp_unslash(meta_key)
  meta_value = WiF.wp_unslash(meta_value)

  # Filter whether to delete metadata of a specific type.
  # The dynamic portion of the hook, `meta_type`, refers to the meta
  # object type (comment, post, or user). Returning a non-None value
  # will effectively short-circuit the function.
  # @param None|bool delete  Whether to allow metadata deletion of given type
  # @param int    object_id  Object ID.
  # @param string meta_key   Meta key.
  # @param mixed  meta_value Meta value. Must be serializable if non-scalar.
  # @param bool   delete_all Whether to delete the matching metadata entries
  #         for all objects, ignoring the specified object_id.  Default False
  check = WiPg.apply_filters( "delete_{}_metadata".format(meta_type), None,
                              object_id, meta_key, meta_value, delete_all )
  if check is not None:
    return bool(check)

  _meta_value = meta_value
  meta_value = WiFc.maybe_serialize( meta_value )

  Sql     = "SELECT {} FROM {} WHERE meta_key = %s".format(id_column, table)
  #SqlDict= (meta_key,)
  query   = wpdb.prepare( Sql, meta_key )

  if not delete_all:
    # PyMySQL convert int & all to formatted quoted str. Can only use %s!!
    #Sql    += " AND {} = %s".format(type_column)   # changed from %d to %s
    query   += wpdb.prepare( " AND {} = %s".format(type_column), object_id )
    #SqlDict+= (object_id, )
  #if '' != meta_value and meta_value is not None and False is not meta_value:
  if meta_value:
    Sql     += wpdb.prepare( " AND meta_value = %s", meta_value )
    #SqlDict+= (meta_value, )

  #RowDicts = wDB.GetDB(MetaC, table).Exec(Sql, SqlDict)
  #meta_ids = [ Row(id_column) for Row in RowDicts ]
  meta_ids = wpdb.get_col( query )
  print(RowDicts, "\n meta_ids=", meta_ids)
  if not Php.count( meta_ids ):    #if not meta_ids:
    return False

  if delete_all:
    value_clause = ''
    #value_tuple  = ()
    #if '' != meta_value and meta_value is not None and False != meta_value:
    if meta_value:
      value_clause = wpdb.prepare( " AND meta_value = %s", meta_value)
      #value_tuple  = (meta_value, )

    Sql = ("SELECT {} FROM {} WHERE meta_key = %s {}"
           .format(type_column, table, value_clause))
    #RowDicts = wDB.GetDB(MetaC, table).Exec(Sql, (meta_key,)+ value_tuple )
    #object_ids = [ Row(id_column) for Row in RowDicts ]
    object_ids = wpdb.get_col( wpdb.prepare( Sql, meta_key ))

  # Fires immediately before deleting metadata of a specific type.
  # The dynamic portion of the hook, `meta_type`, refers to the meta
  # object type (comment, post, or user).
  # @param array  meta_ids   An array of metadata entry IDs to delete.
  # @param int    object_id  Object ID.
  # @param string meta_key   Meta key.
  # @param mixed  meta_value Meta value.
  WiPg.do_action( "delete_{}_meta".format(meta_type), Php.Array(meta_ids),
              object_id, meta.meta_key, meta._meta_value )

  # Old-style action.
  if 'post' == meta_type:
    # Fires immediately before deleting metadata for a post.
    # @since 2.9.0
    # @param array meta_ids An array of post metadata entry IDs to delete.
    WiPg.do_action( 'delete_postmeta', meta_ids )

  query = ("DELETE FROM {} WHERE {} IN( {} )"
           .format(table, id_column, ','.join( meta_ids )))
  #count= wDB.GetDB(MetaC, table).Exec(query)
  count = wpdb.query(query)

  if not count:
    return False

  if delete_all:
    for o_id in Php.Array(object_ids):
      WiCa.wp_cache_delete(o_id, meta_type + '_meta')
  else:
    WiCa.wp_cache_delete(object_id, meta_type + '_meta')

  # Fires immediately after deleting metadata of a specific type.
  # The dynamic portion of the hook name, `meta_type`, refers to the meta
  # object type (comment, post, or user).
  # @param array  meta_ids   An array of deleted metadata entry IDs.
  # @param int    object_id  Object ID.
  # @param string meta_key   Meta key.
  # @param mixed  meta_value Meta value.
  WiPg.do_action( "deleted_{}_meta".format(meta_type), Php.Array(meta_ids), object_id,
             meta.meta_key, meta._meta_value )
  return True


def get_metadata(meta_type, object_id, meta_key = '', single = False):
  '''
   Retrieve metadata for the specified object.
   @param string meta_type Type of object metadata is for
                           (e.g., comment, post, or user)
   @param int    object_id ID of the object metadata is for
   @param string meta_key  Optional. Metadata key. If not specified,
                           retrieve all metadata for the specified object.
   @param bool   single    Optional, default is False.
                           If True, return only the first value of the
                           specified meta_key. This parameter has no effect
                           if meta_key is not specified.
   @return mixed Single metadata value, or array of values = list = [] !!!
  '''
  if not meta_type or not isinstance(object_id, int):
    return False
  object_id = abs(object_id)
  if not object_id:
    return False
  print('get_metadata meta_type={}, object_id ={}, meta_key={}'
        .format(meta_type, object_id, meta_key))

  # Filter whether to retrieve metadata of a specific type.
  # The dynamic portion of the hook, `meta_type`, refers to the meta
  # object type (comment, post, or user). Returning a non-None value
  # will effectively short-circuit the function.
  # @param None|array|string value  The value get_metadata() should return -
  #                           a single metadata value, or an array of values.
  # @param int     object_id Object ID.
  # @param string  meta_key  Meta key.
  # @param bool    single    Whether to return only the first value of the
  #                          specified meta_key.
  check = WiPg.apply_filters( "get_{}_metadata".format(meta_type), None,
                         object_id, meta_key, single )
  if check is not None:
    if single and Php.is_array( check ):
      return check[0]
    else:
      return check
  meta_cache = WiCa.wp_cache_get(object_id, meta_type + '_meta')

  if not meta_cache:
    meta_cache = update_meta_cache( meta_type, array(object_id) )
    # wp> $m = false; wp> $m[1] => NULL
    meta_cache = meta_cache[object_id]
    # The folllowing is BAD! since meta_cache = array( (object_id, array))
    #   so object_id in meta_cache is always False!
    #meta_cache  = meta_cache[object_id] if object_id in meta_cache else None
    # Can use array_key_exists or object_id in meta_cache.keys()

  if not meta_key:
    print('\n get_metadata not meta_key, return meta_cache =', meta_cache)
    return meta_cache

  #if meta_cache.get(meta_key, None) is not None:
  if Php.isset(meta_cache, meta_key):
    mkey = meta_cache[meta_key]
    print('get_metadata:', meta_type, object_id, meta_key, single, mkey)
    if single:
      return WiFc.maybe_unserialize( mkey[0] )
    else:
      #print('get_metadata return:', Php.array_map(WiFc.maybe_unserialize, mkey))
      #return [ WiFc.maybe_unserialize(v) for v in mkey ]
      return  Php.array_map( WiFc.maybe_unserialize, mkey )  #same as:

  #print('\n get_metadata not isset(meta_cache, meta_key)', meta_cache, meta_key)
  if single:
    return ''
  else:
    return array()


def metadata_exists( meta_type, object_id, meta_key ):
  ''' Determine if a meta key is set for a given object
  @param string meta_type Type of object metadata is for (e.g., comment, post, or user)
  @param int    object_id ID of the object metadata is for
  @param string meta_key  Metadata key.
  @return bool True of the key is set, False if not.
  '''
  if not meta_type or not Php.is_numeric( object_id ):
    return False

  object_id = xFn.AbsInt( object_id )
  if not object_id:
    return False

  # This filter is documented in wp-includes/meta.php */
  check = WiPg.apply_filters( "get_{}_metadata".format(meta_type),
                          None, object_id, meta_key, True )
  if None is not check:
    return bool(check)

  meta_cache = WiCa.wp_cache_get( object_id, meta_type + '_meta' )

  if not meta_cache:
    meta_cache = update_meta_cache( meta_type, array( object_id ) )
    meta_cache = meta_cache[object_id]

  if Php.isset(meta_cache, meta_key):
    return True
  return False


def update_meta_cache(meta_type, object_ids):
  '''Update the metadata cache for the specified objects.
  @param string    meta_type  Type of object metadata is for
                              (e.g., comment, post, or user)
  @param int|array object_ids Array or comma delimited list of object IDs
                              to update cache for
  @return array|False         Metadata cache for the specified objects,
                              or False on failure.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  print('update_meta_cache meta_type={}, object_ids={}'
        .format(meta_type, object_ids))

  if not meta_type or not object_ids:
    print('update_meta_cache not meta_type or not object_ids:')
    return False
  table = _get_meta_table( meta_type )
  if not table:
    print('update_meta_cache not table:')
    return False

  column = WiF.sanitize_key(meta_type + '_id')

  #if not isinstance(object_ids, (list,tuple,)):
  if not Php.is_array(object_ids):
    #import re
    #Re = re.compile('[^0-9,]')
    #object_ids = Re.sub('', object_ids)
    object_ids = Php.preg_replace('|[^0-9,]|', '', object_ids)
    #object_ids= object_ids.split(',')
    object_ids = Php.explode(',', object_ids)
    # object_ids = [ val for val in object_ids.values() ]

  #object_ids = [int(val) for val in object_ids]   #same as:
  object_ids= Php.array_map(Php.intval, object_ids)
  print('update_meta_cache object_ids=', object_ids)

  cache_key = meta_type + '_meta'
  ids   = array()
  cache = array()
  for Id in object_ids:
    cached_object = WiCa.wp_cache_get( Id, cache_key )
    if False is cached_object:
      ids[None] = Id
    else:
      cache[Id] = cached_object

  if not ids:    # if Php.empty(locals(), 'ids'):
    return cache

  # Get meta info
  #id_list = ','.join(str(ids))  #BAD!!#= [,2,6,8,3,4,]
  id_list = ','.join( [str(Id) for Id in ids] )
  id_column = 'umeta_id' if 'user' == meta_type else 'meta_id'
  #meta_list = wpdb->get_results( "SELECT $column, meta_key, meta_value FROM $table WHERE $column IN ($id_list) ORDER BY $id_column ASC", ARRAY_A )
  # in wp-db.php get_results( , ARRAY_A) = column name-keyed row arrays
  Sql = ("SELECT {}, meta_key, meta_value FROM {} WHERE {} IN ({}) ORDER BY "
         "{} ASC".format(column, table, column, id_list, id_column))
  #meta_list = wDB.GetDB(MetaC, table).Exec(Sql)
  meta_list = wpdb.get_results( Sql, 'ARRAY_A' )
  # in wp-db.php get_results( , ARRAY_A) = column name-keyed row arrays
  print('\n update_meta_cache meta_list =', meta_list)

  if meta_list:    # if not Php.empty(locals(), 'meta_list'):
    for metarow in meta_list:
      mpid = int(metarow[column])
      mkey = metarow['meta_key']
      mval = metarow['meta_value']

      # Force subkeys to be arry type:
      if not Php.isset(cache, mpid) or not Php.is_array(cache[mpid]):
        cache[mpid]       = array()
      if (not Php.isset(cache[mpid], mkey)  or
          not Php.is_array(cache[mpid][mkey]) ):
        cache[mpid][mkey] = array()

      # Add a value to the current pid/key:
      cache[mpid][mkey][None] = mval

  for Id in ids:
    if not Php.isset(cache, Id):
      cache[Id] = array()
    WiCa.wp_cache_add( Id, cache[Id], cache_key )

  print('\n update_meta_cache return cache =', cache)
  return cache


def _get_meta_table(Type):
  '''Retrieve the name of the metadata table for the specified object Type.
  @param str Type  Type of object to get metadata table for
                          (e.g., comment, post, or user)
  @return str|False Metadata table name, or False if no metadata table exists
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  #if not wpdb:
  #  print("wpdb in _get_meta_table is empty")
  #  import sys; sys.exit()

  table_name = Type + 'meta'

  print("_get_meta_table Type={}; wpdb.{} = {}"
        .format(Type, table_name, getattr(wpdb, table_name, False)))
  #return getattr(wpdb, table_name, False) #same as:
  if Php.empty(wpdb, table_name):
    return False
  return getattr(wpdb, table_name)






def sanitize_meta( meta_key, meta_value, object_type ):
  ''' Sanitize meta value.
  @param string meta_key   Meta key
  @param mixed  meta_value Meta value to sanitize
  @param string meta_type  Type of meta
  @return mixed Sanitized meta_value
  '''
  # Filter the sanitization of a specific meta key of a specific meta type.
  # The dynamic portions of the hook name, `meta_type`, and `meta_key`,
  # refer to the metadata object type (comment, post, or user) and the meta
  # key value, respectively.
  # @param mixed  meta_value   Meta value to sanitize.
  # @param string meta_key     Meta key.
  # @param string object_type  Object type.
  return WiPg.apply_filters( "sanitize_{}_meta_{}".format(object_type, meta_key), meta_value, meta_key, object_type )
  #return meta_value



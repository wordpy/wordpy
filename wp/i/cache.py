# Fixed all &value pass by reference
import pyx.php   as Php
import wp.conf   as WpC
import wp.i.func as WiFc
#from  wp.conf import WB  # can't use WB here, since WpC.WB was init to None
#                         #   before end of wpy.web: WpC.WB = WB = WpBlogCls()
array = Php.array

# in wp_cache_init(self):
# global wp_object_cache
# WpC.WB.Wj.wp_object_cache = self.wp_object_cache = WP_Object_Cache(self)


''' From wp/cache.php
 * Object Cache API
 * @link codex.wordpress.org/Class_Reference/WP_Object_Cache
 * @package WordPress * @subpackage Cache
'''

def wp_cache_add( key, data, group = '', expire = 0 ):
  ''' Adds data to the cache, if the cache key doesn't already exist.
  @see WP_Object_Cache::add()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  
  @param int|str key    The cache key to use for retrieval later.
  @param mixed   data   The data to add to the cache.
  @param string  group  Optional. The group to add the cache to. Enables the
                        same key to be used across groups. Default empty.
  @param int     expire Optional. When the cache data should expire,
                        in seconds. Default 0 (no expiration).
  @return bool False if cache key and group already exist, True on success.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.add( key, data, group, int(expire) )


def wp_cache_close():
  ''' Closes the cache.
  This function has ceased to do anything since WordPress 2.5. The
  functionality was removed along with the rest of the persistent cache.
  This does not mean that plugins can't implement this function when they need
  to make sure that the cache is cleaned up after WordPress no longer needs it
  @return True Always returns True.
  '''
  return True


def wp_cache_decr( key, offset = 1, group = '' ):
  ''' Decrements numeric cache item's value.
  @see WP_Object_Cache::decr()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param int|str key    The cache key to decrement.
  @param int     offset Optional. The amount by which to decrement the item's
                        value. Default 1.
  @param str     group  Optional. The group the key is in. Default empty.
  @return False|int False on failure, the item's new value on success.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.decr( key, offset, group )


def wp_cache_delete( key, group = '' ):
  ''' Removes the cache contents matching key and group.
  @see WP_Object_Cache::delete()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param int|string key   What the contents in the cache are called.
  @param string     group Optional. Where the cache contents are grouped.
                    Default empty.
  @return bool True on successful removal, False on failure.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.delete(key, group)


def wp_cache_flush():
  ''' Removes all cache items.
  @see WP_Object_Cache::flush()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @return bool False on failure, True on success
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.flush()


#def wp_cache_get( key, group = '', force = False, &found = None ):
# php pass &query by reference can be translated to py without the ref,
#    since query, key, and clause below are not modified below:
def wp_cache_get( key, group = '', force = False, found = None ):
  ''' Retrieves the cache contents from the cache by key and group.
  @see WP_Object_Cache::get()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param int|string  key    The key under which the cache contents are stored.
  @param string      group  Optional. Where the cache contents are grouped. Default empty.
  @param bool        force  Optional. Whether to force an update of the local cache from the persistent
                             cache. Default False.
  @param bool        found  Optional. Whether the key was found in the cache. Disambiguates a return of False,
                             a storable value. Passed by reference. Default None.
  @return bool|mixed False on failure to retrieve contents or the cache
                           contents on success
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.get( key, group, force, found )


def wp_cache_incr( key, offset = 1, group = '' ):
  ''' Increment numeric cache item's value
  @see WP_Object_Cache::incr()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param int|string key    The key for the cache contents that should be incremented.
  @param int        offset Optional. The amount by which to increment the item's value. Default 1.
  @param string     group  Optional. The group the key is in. Default empty.
  @return False|int False on failure, the item's new value on success.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.incr( key, offset, group )


def wp_cache_init(self):
  ''' Sets up Object Cache Global and assigns it.
  @global WP_Object_Cache wp_object_cache
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #@GLOBALS['wp_object_cache'] = new WP_Object_Cache()
  #WpC.WB.Wj.wp_object_cache = WP_Object_Cache()
  #global wp_object_cache
  # Cannot use WpC.WB.Wj.wp_object_cache since WpC.WB.Wj (=self) is not initialized yet.
  self.wp_object_cache = WP_Object_Cache(self)  # = WpC.WB.Wj.wp_object_cache 
  #print('\n\n wp_cache_init wp_object_cache =', WP_Object_Cache(self),'\n\n')


def wp_cache_replace( key, data, group = '', expire = 0 ):
  ''' Replaces the contents of the cache with new data.
  @see WP_Object_Cache::replace()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param int|string key    The key for the cache data that should be replaced.
  @param mixed      data   The new data to store in the cache.
  @param string     group  Optional. The group for the cache data that should be replaced.
                            Default empty.
  @param int        expire Optional. When to expire the cache contents, in seconds.
                            Default 0 (no expiration).
  @return bool False if original value does not exist, True if contents were replaced
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.replace( key, data, group, int(expire) )


def wp_cache_set( key, data, group = '', expire = 0 ):
  ''' Saves the data to the cache.
  Differs from wp_cache_add() and wp_cache_replace() in that it will always write data.
  @see WP_Object_Cache::set()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param int|string key    The cache key to use for retrieval later.
  @param mixed      data   The contents to store in the cache.
  @param string     group  Optional. Where to group the cache contents. Enables the same key
                            to be used across groups. Default empty.
  @param int        expire Optional. When to expire the cache contents, in seconds.
                            Default 0 (no expiration).
  @return bool False on failure, True on success
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  return WpC.WB.Wj.wp_object_cache.set( key, data, group, int(expire) )


def wp_cache_switch_to_blog( blog_id ):
  ''' Switches the internal blog ID.
  This changes the blog id used to create keys in blog specific groups.
  @see WP_Object_Cache::switch_to_blog()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param int blog_id Site ID.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  WpC.WB.Wj.wp_object_cache.switch_to_blog( blog_id )


# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
#def wp_cache_add_global_groups(groups):
def wp_cache_add_global_groups(groups, Wj=None):
  ''' Adds a group or set of groups to the list of global groups.
  @see WP_Object_Cache::add_global_groups()
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  @param string|array groups A group or an array of groups to add.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  if Wj is None:
    Wj = WpC.WB.Wj
  Wj.wp_object_cache.add_global_groups( groups )


def wp_cache_add_non_persistent_groups(groups ):
  ''' Adds a group or set of groups to the list of non-persistent groups.
  @param string|array groups A group or an array of groups to add.
  '''
  # Default cache doesn't persist so nothing to do here.
  #global wp_object_cache
  pass

def wp_cache_reset():
  ''' Reset internal cache keys and structures.
  If the cache back end uses global blog or site IDs as part of its cache keys,
  this function instructs the back end to reset those keys and perform any cleanup
  since blog or site IDs have changed since cache init.
  This function is deprecated. Use wp_cache_switch_to_blog() instead of this
  function when preparing the cache for a blog switch. For clearing the cache
  during unit tests, consider using wp_cache_init(). wp_cache_init() is not
  recommended outside of unit tests as the performance penalty for using it is
  high.
  @global WP_Object_Cache wp_object_cache Object cache global instance.
  '''
  #_deprecated_function( __FUNCTION__, '3.5.0' )
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_object_cache
  WpC.WB.Wj.wp_object_cache.reset()



class WP_Object_Cache(Php.stdClass):
  ''' Core class that implements an object cache.
  The WordPress Object Cache is used to save on trips to the database. The
  Object Cache stores all of the cache data to memory and makes the cache
  contents available by using a key, which is used to name and later retrieve
  the cache contents.
  The Object Cache can be replaced by other caching mechanisms by placing
  files in the wp-content folder which is looked at in wp-settings. If that
  file exists, then this file will not be included.
  '''
  def __init__(self, Wj):
    ''' Sets up object properties; PHP 5 style constructor.
    All global vars in this obj are under Wj.vars
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    self.Wj = Wj

    # Holds the cached objects.
    # @access private  @var dict
    self.cache = array()    # {}

    # The amount of times the cache data was already stored in the cache.
    # @access public  @var int
    self.cache_hits = 0

    # Amount of times the cache did not have the request in cache.
    # @access public  @var int
    self.cache_misses = 0

    # List of global cache groups.
    # @access protected  @var dict
    self.global_groups = array()    # {}

    # Holds the value of is_multisite().
    # @access private  @var bool
    #self.multisite = None
    self.multisite = self.Wj.is_multisite()

    # The blog prefix to prepend to keys in non-global groups.
    # @access private  @var int
    #self.blog_prefix = None
    self.blog_prefix = str(Wj.get_current_blog_id()) + ':' if self.multisite else ''

    # @todo This should be moved to the PHP4 style constructor, PHP5
    # already calls __destruct()
    #register_shutdown_function( array( this, '__destruct' ) )
    #register_shutdown_function( this.__destruct )


  def __destruct(self):
    ''' Saves the object cache before object is completely destroyed.
    Called upon object destruction, which should be when PHP ends.
    @return True Always returns True.
    '''
    return True


  #def __getattr__(self, name):
  def __get(self, name ):
    ''' Makes private properties readable for backward compatibility.
    @param string name Property to get.
    @return mixed Property.
    '''
    return getattr(self, name)

  #def __setattr__(self, name, value):  #Canot replace super().__setattr__
  def __set(self, name, value):
    ''' Makes private properties settable for backward compatibility.
    @param string name  Property to set.
    @param mixed  value Property value.
    @return mixed Newly-set property.
    '''
    setattr(self, name, value)
    return value

  def __isset(self, name ):
    ''' Makes private properties checkable for backward compatibility.
    @param string name Property to check if set.
    @return bool Whether the property is set.
    '''
    return Php.isset(self, 'name' )

  #def __delattr__(self, name):
  def __unset(self, name ):
    '''Makes private properties un-settable for backward compatibility.
    @param string name Property to unset.
    '''
    delattr(self, name)

  def add(self, key, data, group = 'default', expire = 0 ):
    ''' Adds data to the cache if it doesn't already exist.
    @uses WP_Object_Cache::_exists() Checks to see if the cache already has data.
    @uses WP_Object_Cache::set()     Sets the data after the checking the cache
     	                            contents existence.
    @param int|string key    What to call the contents in the cache.
    @param mixed      data   The contents to store in the cache.
    @param string     group  Optional. Where to group the cache contents. Default 'default'.
    @param int        expire Optional. When to expire the cache contents. Default 0 (no expiration).
    @return bool False if cache key and group already exist, True on success
    '''
    if WiFc.wp_suspend_cache_addition():
      return False

    if not group:    # if Php.empty(locals(), 'group'):
      group = 'default'

    Id = key
    if self.multisite and not Php.isset(self.global_groups, group):
      Id = self.blog_prefix + str(key)

    if self._exists( Id, group ):
      return False

    return self.set( key, data, group, int(expire) )
 

  def add_global_groups(self, groups ):
    ''' Sets the list of global cache groups.
    @param array groups List of groups that are global.
    '''
    groups = Php.Array(groups)
    groups = Php.array_fill_keys( groups, True )
    self.global_groups = Php.array_merge( self.global_groups, groups )


  def decr(self, key, offset = 1, group = 'default' ):
    ''' Decrements numeric cache item's value.
    @param int|string key    The cache key to decrement.
    @param int        offset Optional. The amount by which to decrement the item's value. Default 1.
    @param string     group  Optional. The group the key is in. Default 'default'.
    @return False|int False on failure, the item's new value on success.
    '''
    if not group:    # if Php.empty(locals(), 'group'):
      group = 'default'

    if self.multisite and not Php.isset(self.global_groups, group):
      key = self.blog_prefix + str(key)

    if not self._exists( key, group ):
      return False

    if not is_numeric( self.cache[ group ][ key ] ):
      self.cache[ group ][ key ] = 0

    offset = int(offset)

    self.cache[ group ][ key ] -= offset

    if self.cache[ group ][ key ] < 0:
      self.cache[ group ][ key ] = 0

    return self.cache[ group ][ key ]


  def delete(self, key, group = 'default', deprecated = False ):
    ''' Removes the contents of the cache key in the group.
    If the cache key does not exist in the group, then nothing will happen.
    @param int|string key        What the contents in the cache are called.
    @param string     group      Optional. Where the cache contents are grouped. Default 'default'.
    @param bool       deprecated Optional. Unused. Default False.
    @return bool False if the contents weren't deleted and True on success.
    '''
    if not group:    # if Php.empty(locals(), 'group'):
      group = 'default'

    if self.multisite and not Php.isset(self.global_groups, group):
      key = self.blog_prefix + str(key)

    if not self._exists( key, group ):
      return False

    del self.cache[group][key]
    return True


  def flush(self):
    ''' Clears the object cache of all data.
    @return True Always returns True.
    '''
    self.cache = array()
    return True


  #def get( key, group = 'default', force = False, &found = None ):
  # since found passed by ref, need to return found
  def get(self, key, group = 'default', force = False, ReturnFound = False ):
    ''' Retrieves the cache contents, if it exists.
    The contents will be first attempted to be retrieved by searching by the
    key in the cache group. If the cache is hit (success) then the contents
    are returned.
    On failure, the number of cache misses will be incremented.
    @param int|string key    What the contents in the cache are called.
    @param string     group  Optional. Where the cache contents are grouped. Default 'default'.
    @param string     force  Optional. Unused. Whether to force a refetch rather than relying on the local
                              cache. Default False.
    @param bool       found  Optional. Whether the key was found in the cache. Disambiguates a return of
                              False, a storable value. Passed by reference. Default None.
    @return False|mixed False on failure to retrieve contents or the cache contents on success.
    ''' 
    if not group:    # if Php.empty(locals(), 'group'):
      group = 'default'

    if self.multisite and not Php.isset(self.global_groups, group):
      key = self.blog_prefix + str(key)

    if self._exists( key, group ):
      found = True
      self.cache_hits += 1
      if Php.is_object(self.cache[group][key]):
        Cache = Php.clone(self.cache[group][key])
        return Cache
      else:
        Cache = self.cache[group][key]
      #since found passed by ref, need to return found
      return (Cache, found) if ReturnFound else Cache

    found = False
    self.cache_misses += 1
    #return False
    #since found passed by ref, need to return found
    return (False, found) if ReturnFound else False


  def incr(self, key, offset = 1, group = 'default' ):
    ''' Increments numeric cache item's value.
    @param int|string key    The cache key to increment
    @param int        offset Optional. The amount by which to increment the item's value. Default 1.
    @param string     group  Optional. The group the key is in. Default 'default'.
    @return False|int False on failure, the item's new value on success.
    '''
    if not group:    # if Php.empty(locals(), 'group'):
      group = 'default'

    if self.multisite and not Php.isset(self.global_groups, group):
      key = self.blog_prefix + str(key)

    if not self._exists( key, group ):
      return False

    if not is_numeric( self.cache[ group ][ key ] ):
      self.cache[ group ][ key ] = 0

    offset = int(offset)

    self.cache[ group ][ key ] += offset

    if self.cache[ group ][ key ] < 0:
      self.cache[ group ][ key ] = 0

    return self.cache[ group ][ key ]


  def replace(self, key, data, group = 'default', expire = 0 ):
    ''' Replaces the contents in the cache, if contents already exist.
    @see WP_Object_Cache::set()
    @param int|string key    What to call the contents in the cache.
    @param mixed      data   The contents to store in the cache.
    @param string     group  Optional. Where to group the cache contents. Default 'default'.
    @param int        expire Optional. When to expire the cache contents. Default 0 (no expiration).
    @return bool False if not exists, True if contents were replaced.
    '''
    if not group:    # if Php.empty(locals(), 'group'):
      group = 'default'

    Id = key
    if self.multisite and not Php.isset(self.global_groups, group):
      Id = self.blog_prefix + str(key)

    if not self._exists( Id, group ):
      return False

    return self.set( key, data, group, int(expire) )


  def reset(self):
    ''' Resets cache keys.
    @deprecated 3.5.0 Use switch_to_blog()
    @see switch_to_blog()
    '''
    _deprecated_function( __FUNCTION__, '3.5.0', 'switch_to_blog()' )

    # Clear out non-global caches since the blog ID has changed.
    for group in self.cache.keys():   #same as# Php.array_keys( self.cache ):
      if not Php.isset(self.global_groups, group):
        del self.cache[ group ]

  def set(self, key, data, group = 'default', expire = 0 ):
    ''' Sets the data contents into the cache.
    The cache contents is grouped by the group parameter followed by the
    key. This allows for duplicate ids in unique groups. Therefore, naming of
    the group should be used with care and should follow normal function
    naming guidelines outside of core WordPress usage.
    The expire parameter is not used, because the cache will automatically
    expire for each time a page is accessed and PHP finishes. The method is
    more for cache plugins which use files.
    @param int|string key    What to call the contents in the cache.
    @param mixed      data   The contents to store in the cache.
    @param string     group  Optional. Where to group the cache contents. Default 'default'.
    @param int        expire Not Used.
    @return True Always returns True.
    '''
    if not group:    # if Php.empty(locals(), 'group'):
      group = 'default'

    if self.multisite and not Php.isset(self.global_groups, group):
      key = self.blog_prefix + str(key)

    if Php.is_object( data ):
      data = Php.clone( data )

    if group not in self.cache:
      self.cache = array( (group, array()), )
    elif key not in self.cache[group]:
      self.cache[group] = array()
    self.cache[group][key] = data
    return True


  def stats(self):
    ''' Echoes the stats of the caching.
    Gives the cache hits, and cache misses. Also prints every cached group,
    key and the data.
    '''
    #echo "<p>"
    #echo "<strong>Cache Hits:</strong> {self.cache_hits}<br />"
    #echo "<strong>Cache Misses:</strong> {self.cache_misses}<br />"
    #echo "</p>"
    #echo '<ul>'
    #for group, cache in self.cache:
    #  echo "<li><strong>Group:</strong> group - ( " + number_format(
    #                len( serialize( cache ) ) / KB_IN_BYTES, 2 ) + 'k )</li>'
    #echo '</ul>'
    print("Cache Hits:  ", self.cache_hits)
    print("Cache Misses:", self.cache_misses)
    for group, cache in self.cache:
      print("  Group: group - ( " + Php.number_format(
                     len( Php.serialize( cache ) ) / KB_IN_BYTES, 2 ) + 'k')


  def switch_to_blog(self, blog_id ):
    ''' Switches the internal blog ID.
    This changes the blog ID used to create keys in blog specific groups.
    @param int blog_id Blog ID.
    '''
    blog_id = int(blog_id)
    self.blog_prefix = blog_id + ':' if self.multisite else ''

  def _exists(self, key, group ):
    ''' Serves as a utility function to determine whether a key exists in the cache.
    @param int|string key   Cache key to check for existence.
    @param string     group Cache group for the key existence check.
    @return bool Whether the key exists in the cache for the given group.
    '''
		#return isset( $this->cache[ $group ] ) && (
    #         isset( $this->cache[ $group ][ $key ] ) ||
    #         array_key_exists( $key, $this->cache[ $group ] ) );
    #return group in self.cache and (
    #          key in self.cache[ group ] or key in self.cache[ group ] )
    return Php.isset(self.cache, group) and ( Php.isset(self.cache[ group ],
                     key) or Php.array_key_exists( key, self.cache[ group ] ))



# wp-includes/load.php
#wp_cache_init()


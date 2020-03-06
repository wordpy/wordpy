#!/usr/bin/python3
import re
#import wp.rss  as WpR    # no need to use wp.rss, use phpserialize.py in:
import pyx.func      as xFn
import pyx.php       as Php
import wp.conf       as WpC
import wp.i.format   as WiF
import wp.i.cls.list_util as WcLU
array = Php.array


def current_time( Type, gmt = 0 ): # gmt = UTC
  ''' Retrieve the current time based on specified Type.
  The 'datetime' Type will return the py datetime format (VT Added!!)
  The 'mysql' Type will return the time in the format for MySQL DATETIME field.
  The 'timestamp' Type will return the current timestamp.
  Other strings will be interpreted as PHP date formats (e.g. 'Y-m-d').
  If gmt is set to either '1' or 'True', then both types will use GMT time.
  if gmt is False, the output is adjusted with the GMT offset in the WordPress option.
  @param string   Type Type of time to retrieve. Accepts 'mysql', 'timestamp',
                       or PHP date format string (e.g. 'Y-m-d').
  @param int|bool gmt  Optional. Whether to use GMT timezone. Default False.
  @return int|string Integer if Type is 'timestamp', string otherwise.

  weston.ruter.net/2013/04/02/do-not-change-the-default-timezone-from-utc-in-wordpress/
  [Default tz hardcoded as UTC]wordpress.stackexchange.com/questions/30946/
  '''
  from datetime import datetime, timedelta
  import wpy.time as wTm
  import wp.i.option   as WiO
  #BlogWebHostLocation =  WpC.WB.Wj.Bj.WH0.DcNum
  #DtNow= wTm.DtNowWithLocalSysTz() #can't use datetime.now() w/ no timezone!
  if gmt:
    #UtcNow = wTm.DtToUtc(DtNow, BlogWebHostLocation)
    DtNowUtc     = wTm.DtNowInUtcTz()
  else:
    #HoursFromNow = timedelta(hours = int(WiO.get_option('gmt_offset')))
    #HoursFromUtc = wTm.DtToUtc(DtNow + HoursFromNow, BlogWebHostLocation)
    DtNowWebHost = wTm.DtNowInWebHostTz()

  if Type == 'datetime':   # VT Added to return py datetime format
    #return UtcNow if gmt else HoursFromUtc
    return DtNowUtc if gmt else DtNowWebHost
  if Type == 'mysql':
    #return gmdate('Y-m-d H:i:s') if gmt else gmdate('Y-m-d H:i:s', ( time()
    #             + ( WiO.get_option('gmt_offset') * self.HOUR_IN_SECONDS )))
    #return (      UtcNow.strftime('%Y-%m-%d %H:%M:%S') if gmt else
    #        HoursFromUtc.strftime('%Y-%m-%d %H:%M:%S') )
    return (    DtNowUtc.strftime('%Y-%m-%d %H:%M:%S') if gmt else
            DtNowWebHost.strftime('%Y-%m-%d %H:%M:%S') )
  if Type == 'timestamp':
    #return time() if gmt else time() + (
    #                   WiO.get_option('gmt_offset') * self.HOUR_IN_SECONDS )
    #return int(UtcNow.timestamp()) if gmt else int(HoursFromUtc.timestamp())
    return int(DtNowUtc.timestamp()) if gmt else float(  # matches wp php out
               DtNowWebHost.replace(tzinfo=None).timestamp())

  #return date(Type) if gmt else date(Type, time() +
  #                ( WiO.get_option('gmt_offset') * self.HOUR_IN_SECONDS ))
  raise TypeError('WiFc.current_time got Unsupported Type = '+ Type)

#>>> from datetime import datetime
#>>> datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#'2017-01-06 07:31:29'
#>>> import time
#>>> time.strftime('%Y-%m-%d %H:%M:%S')
#'2017-01-06 07:31:46'




def maybe_unserialize( original ):
  ''' Unserialize value only if it was serialized. wp-includes/functions.php
  @param string original Maybe unserialized original, if is needed.
  @return mixed Unserialized data can be any type.
  '''
  # don't attempt to unserialize data that wasn't serialized going in
  if is_serialized( original ):
    #"@" before a function call silences php errors the function could raise
    # return @unserialize( original )
    return Php.unserialize( original )
  return original


def is_serialized( data, strict = True ):
  ''' Check value to find if it was serialized. wp-includes/functions.php
  If data is not an string, then returned value will always be False.
  Serialized data is always a string.
  @param string data   Value to check to see if was serialized.
  @param bool   strict Optional. Whether to be strict about the end of the
                                 string. Default True.
  @return bool False if not serialized and True if it was.
  '''
  # if it isn't a string, it isn't serialized.
  if not isinstance(data, str):
    return False
  data = data.strip()
  if 'N;' == data:
    return True
  if len( data ) < 4:
    return False
  if ':' != data[1]:
    return False
  if strict:
    #lastc = substr( data, -1 )
    lastc = data[-1]
    if ';' != lastc and '}' != lastc:
      return False
  # Php: strpos(haystack, needle) = int position of 1st occurrence of a str
  # =Py: haystack.find(needle) = pos, = -1 when not found, otherwise = Php
  # Php: strpos(haystack, needle) !== FALSE;  ===Py: needle in haystack
  else:
    semicolon = data.find(';')  # = strpos( data, ';' )   #Py = Php
    brace     = data.find('}')  # = strpos( data, '}' )   #Py = Php
    # Either ; or } must exist.
    # Php: if ( False === $semicolon and False === $brace )  # equals to Py:
    if ';' not in data and '}' not in data: #if -1==semicolon and -1==brace:
      return False
    # But neither must be in the first X characters.
    # Php: if False != semicolon and semicolon < 3:
    if ';' in data and semicolon < 3:
      return False
    # Php: if False != brace and brace < 4:
    if '}' in data and brace < 4:
      return False

  token = data[0]
  if token == 's':
    if strict:
      #if '"' != substr( data, -2, 1 ):
      if '"' != data[-2, -1]:
        return False
    #elif False == strpos( data, '"' ):
    elif '"' not in data:
      return False
    # or else fall through
  if token in ('a', 'O'):
    #return (bool) preg_match( "/^{$token}:[0-9]+:/s", data )
    Re1 = re.compile( "^{}:[0-9]+:".format(token), re.DOTALL )
    return bool( Re1.search( data ) )
  if token in ('b', 'i', 'd'):
    end = '$' if strict else ''
    #return (bool) preg_match( "/^{$token}:[0-9.E-]+;$end/", data )
    Re2 = re.compile( "^{}:[0-9.E-]+;{}".format(token, end) )
    return bool( Re2.search( data ) )

  return False


def is_serialized_string( data ):
  '''Check whether serialized data is of string type wp-includes/functions.php
  @param str or bytes data Serialized data.
  @return bool False if not a serialized string, True if it is.
  '''
  # if it isn't a string, it isn't a serialized string.
  #if ! is_string( data ):
  if data is None or not isinstance(data, (str, bytes,)):
    return False
  if isinstance(data, (bytes,)):
    data = data.decode()
  data = data.strip()
  if len( data ) < 4:
    return False
  elif ':' != data[1]:
    return False
  elif ';' != data[-1:]:   #=Php: substr( data, -1 ):
    return False
  elif data[0] != 's':
    return False
  elif '"' != data[-2:-1]: #=Php: substr( data, -2, 1 ):
    return False
  else:
    return True
#Test
#>>> data = WPs.Dumps('abc')      #= b's:3:"abc";'
#>>> is_serialized_string(data)   #= True



''' codex.wordpress.org/Function_Reference/maybe_serialize
# Strings are returned untouched.
maybe_serialize( 'Hello World!' ); #Output: Hello World!

# Integers, floats and boolean values are also returned untouched.
maybe_serialize( 55   ); #Output: 55
maybe_serialize( 4.56 ); #Output: 4.56
maybe_serialize( true ); #Output: true
maybe_serialize( null ); #Output: null

# An array or object will be returned as a serialized string.
maybe_serialize( array( 1 => 'Hello World!', 'foo' => 'bar' ) )
#Output: a:2:{i:1;s:12:"Hello World!";s:3:"foo";s:3:"bar";}

wp> $U = get_user_by('ID',1001)
wp> serialize($U);    #WATCH OUT FOR stdClass below!!!
string(3289) "O:7:"WP_User":7:{s:4:"data";O:8:"stdClass":12:{s:2:"ID";s:4:"1001";s:10:"user_login";s:11:"wordpy_info";s:9:"user_pass" ......
'''

def maybe_serialize( data ):
  ''' Serialize data, if needed.  wp-includes/functions.php
  @param string|array|object data Data that might be serialized.
  @return mixed A scalar data
  '''
  if data is None or isinstance(data, (bool, str, bytes, int,float, complex)):
    return data
  
  from datetime import datetime  #VT Added since py has datetime
  if isinstance(data, datetime):
    #return datetime.strftime(data,'%Y-%m-%d %H:%M:%S')#format=wTm.DashYMDHMS
    return data # don't convert datetime so dt will be inserted directly into db

  #if isinstance(data, (list, tuple, array)):
  #  #return serialize( data )
  #  import phpserialize  as ps
  #  return ps.dumps(data).decode()
  #elif inspect.isclass( data ):
  #  return Php.serialize( data )
  data = Php.serialize(data)

  # core.trac.wordpress.org/ticket/12930
  # Double serialization is required for backward compatibility.
  #   A serialized string will be serialized again.
  #   maybe_serialize( 'a:2:{i:1;s:12:"Hello World!";s:3:"foo";s:3:"bar";}' )
  #   Output: s:50:"a:2:{i:1;s:12:"Hello World!";s:3:"foo";s:3:"bar";}"
  # if is_serialized( data, False ):
  #   return Php.serialize( data )
  # VT: No need for backward compatibility, so comment out!
  return data


def wp_normalize_path( path ):
  ''' Normalize a filesystem path.
  On windows systems, replaces backslashes with forward slashes
  and forces upper-case drive letters.
  Allows for two leading slashes for Windows network shares, but
  ensures that all other duplicate slashes are reduced to a single.
  @since 4.4.0 Ensures upper-case drive letters on Windows systems.
  @since 4.5.0 Allows for Windows network shares.
  @param string path Path to normalize.
  @return string Normalized path.
  '''
  path = Php.str_replace( '\\', '/', path )
  path = Php.preg_replace( '|(?<=.)/+|', '/', path )
  if ':' == Php.substr( path, 1, 1 ):
    path = Php.ucfirst( path )
  return path


def wp_die(message = '', title = '', args = array() ):
  WpC.WB.Bj.Exit(message)


def wp_parse_args( args, defaults = '' ):
  '''/fs/web/wp/wp-includes/functions.php
  Merge user defined arguments into defaults array.
  This function is used throughout WordPress to allow for both string or array
  to be merged into another array.
  @param string|array|object args     Value to merge with defaults.
  @param array               defaults Optional. Array that serves as the
                             defaults. Default empty.
  @return array Merged user defined values with defaults.
  '''
  if Php.is_object( args ):
    r= Php.get_object_vars( args )  #same as:
    #r = array( (attr, getattr(args, attr, None)) for attr in dir(args)
    #             if not attr.startswith(('_',)) )
  elif Php.is_array(args):
    r = args   # no need for & args since array is mutable
  else: #elif isinstance(args, str):
    #Php# WiF.wp_parse_str( args, r )
    r =   WiF.wp_parse_str( args )

  if Php.is_array( defaults ):
    return Php.array_merge( defaults, r )
  return r


def wp_parse_id_list( List ):
  '''/fs/web/wp/wp-includes/functions.php
  Clean up an array, comma- or space-separated List of IDs.
  @param list|string list List of ids.
  @return list Sanitized list of IDs.
  '''
  if not Php.is_array( List ):
    List = Php.preg_split( '/[\s,]+/', List )
  #if not isinstance(List):
  #  List=     preg_split( '/[\s,]+/', List )
  #  import re  # www.php2python.com/wiki/function.preg-split/
  #  List = re.split(   '[\s,]+' , List)
  '''wp> $List = preg_split('/[\s,]+/', '1 b -1,0 , e')
     => array(5) {[0]=> str(1) "1" , [1]=> str(1) "b", [2]=> str(2) "-1",
                  [3]=> str(1) "0", [4]=> str(1) "e" }
     wp> array_map('absint', $List)
     => array(5) {[0]=> int(1), [1]=> int(0), [2]=> int(1),
                  [3]=> int(0), [4]=>, int(0) }
     >>> re.split('[\s,]+', '1 b -1,0 , e')
     ['1', 'b', '-1', '0', 'e']
  '''
  #return array_unique(array_map('absint', List))               #php, to py:
  #print('wp_parse_id_list', List)
  return  Php.array_unique(Php.array_map( xFn.AbsInt, List )) #same as:
  #return  list(set( [ xFn.AbsInt(v) for v in List ] ))


def wp_parse_slug_list( List ):
  ''' Clean up an array, comma- or space-separated list of slugs.
  @param  array|string List List of slugs.
  @return array Sanitized array of slugs.
  '''
  if not Php.is_array( List ):
    List = Php.preg_split( '/[\s,]+/', List )
  
  for key, value in List.items():
    List[ key ] = sanitize_title( value )
  
  return Php.array_unique( List )


def wp_array_slice_assoc( arr, keys ):
  '''/fs/web/wp/wp-includes/functions.php
  Extract a slice of a array, given a list of keys.
  @param array  arr The original array.
  @param array  keys  The list of keys.
  @return array  The array Slice.
  '''
  Slice = array()
  for key in keys:
    if key in arr:
      Slice[ key ] = arr[ key ]
  return Slice


def wp_is_numeric_array( data ):
  '''/fs/web/wp/wp-includes/functions.php
  Determines if the variable is a numeric-indexed array.
  @param mixed data Variable to check.
  @return bool Whether the variable is a list.
  '''
  if not Php.is_array( data):
    return False

  keys = data.keys()
  string_keys  = Php.array_filter( keys, Php.is_string )
  #string_keys = array( isinstance(k, str) for k in keys )
  return  len(string_keys ) ==  0


def wp_filter_object_list( List, args = array(), operator = 'and',
                           field = False ):
  ''' Filters a list of objects, based on a set of key => value arguments.
  @since 4.7.0 Uses WP_List_Util class.
  @param array List     An array of objects to filter
  @param array args     Optional. An array of key => value arguments to match
                       against each object. Default empty array.
  @param str   operator Optional. The logical operation to perform. 'or' means
                        only one element from the array needs to match; 'and'
                        means all elements must match; 'not' means no elements
                        may match. Default 'and'.
  @param bool|str field A field from the object to place instead of the entire
                        object. Default False.
  @return array A list of objects or object fields.
  '''
  if not Php.is_array(List):
    return array()
  
  # List = wp_list_filter( List, args, operator )     # Old wp.4.6.1 below
  # if field:
  #   List = wp_list_pluck( List, field )
  # print(List)
  # return List
  util = WcLU.WP_List_Util( List )
  util.filter( args, operator )
  if field:
    util.pluck( field )
  return util.get_output()



# Test: wp_list_filter, wp_list_pluck
# jondavidjohn.com/wordpress-wp_list_pluck-and-wp_list_filter/
#people=array(array(('id',1),('name','Jon'   ),('favorite_color','red'  ),),
#             array(('id',2),('name','Frank' ),('favorite_color','blue' ),),
#             array(('id',3),('name','Bill'  ),('favorite_color','red'  ),),
#             array(('id',4),('name','James' ),('favorite_color','green'),),
#             array(('id',5),('name','Nathan'),('favorite_color','blue' ),),)
#import wp.i.func as WiFc
#names = WiFc.wp_list_pluck(people, 'name')
##out# array('Jon', 'Frank', 'Bill', 'James', 'Nathan');
#criteria = array( ('favorite_color', 'blue'))
#blue_lovers = WiFc.wp_list_filter(people, criteria)
#criteria = array( ('favorite_color', 'green'))
#blue_lovers = WiFc.wp_list_filter(people, criteria)


def wp_list_filter( List, args = array(), operator = 'AND' ):
  ''' Filters a list of objects, based on a set of key => value arguments.
  @since 4.7.0 Uses WP_List_Util class.
  @param array List   A array of objects to filter.
  @param array args   Optional. An array of key => value arguments to match
                     against each object. Default empty array.
  @param str operator Optional. The logical operation to perform. 'AND' means
                      all elements from the array must match. 'OR' means only
                      one element needs to match. 'NOT' means no elements may
                      match. Default 'AND'.
  @return array Dict of found values.
  '''
  if not Php.is_array(List):
    return array()

  util = WcLU.WP_List_Util( List )
  return util.filter( args, operator )


def wp_list_pluck( List, field, index_key = None ):
  ''' Pluck a certain field out of each object in a List.
  This has the same functionality and prototype of
  array_column() (PHP 5.5) but also supports objects.
  @since 4.7.0 Uses WP_List_Util class.
  @param array      List       Dict of objects or arrays
  @param int|string field     Field from the object to place instead of the entire object
  @param int|string index_key Optional. Field from the object to use as keys for the new array.
                               Default None.
  @return array Array of found values. If `index_key` is set, an array of found values with keys
                corresponding to `index_key`. If `index_key` is None, array keys from the original
                `List` will be preserved in the results.
  '''
  util = WcLU.WP_List_Util( List )
  return util.pluck( field, index_key )   #below moved to WP_List_Util.pluck


def wp_list_sort( List, orderby = array(), order = 'ASC',
                  preserve_keys = False ):
  ''' Sorts a list of objects, based on one or more orderby arguments.
  @param array        List An array of objects to filter.
  @param str|array orderby Optional. Either the field name to order by or an
                          array of multiple orderby fields as orderby => order
  @param str       order   Optional. Either 'ASC' or 'DESC'. Only used if
                           orderby is a string.
  @param bool preserve_keys Optional. Whether to preserve keys. Default False.
  @return array The sorted array.
  '''
  if not Php.is_array( List ):
    return array()
  
  util = WcLU.WP_List_Util( List )
  return util.sort( orderby, order, preserve_keys )


def _doing_it_wrong( function, message, version ):
  ''' Mark something as being incorrectly called.
  There is a hook {@see 'doing_it_wrong_run'} that will be called that can be
  used to get the backtrace up to what file and function called the deprecated
  function.
  The current behavior is to trigger a user error if `WP_DEBUG` is True.
  @param string function The function that was called.
  @param string message  A message explaining what has been done incorrectly.
  @param string version  The version of WordPress where the message was added
  '''
  print('\n\n', function, message, version, '\n\n')
  #Fires when the given function is being used incorrectly.
  #@param string function The function that was called.
  #@param string message  A message explaining what has been done incorrectly
  #@param string version  The version of WordPress where the message was added
  #do_action( 'doing_it_wrong_run', function, message, version )

  # Filters whether to trigger an error for _doing_it_wrong() calls.
  # @param bool trigger Whether to trigger the error for _doing_it_wrong() calls. Default True.
  #if WP_DEBUG and apply_filters( 'doing_it_wrong_trigger_error', True ):
  #  if function_exists( '__' ):
  #    if is_null( version ):
  #      version = ''
  #    else:
  #      # translators: %s: version number
  #      version = sprintf( __( '(This message was added in version %s.)' ), version )
  #    # translators: %s: Codex URL
  #    message .= ' ' . sprintf( __( 'Please see <a href="%s">Debugging in WordPress</a> for more information.' ),
  #      __( 'https://codex.wordpress.org/Debugging_in_WordPress' )
  #    )
  #    # translators: Developer debugging message. 1: PHP function name, 2: Explanatory message, 3: Version information message
  #    trigger_error( sprintf( __( '%1s was called <strong>incorrectly</strong>. %2s %3s' ), function, message, version ) )
  #  else:
  #    if is_null( version ):
  #      version = ''
  #    else:
  #      version = sprintf( '(This message was added in version %s.)', version )
  #    message .= sprintf( ' Please see <a href="%s">Debugging in WordPress</a> for more information.',
  #      'https://codex.wordpress.org/Debugging_in_WordPress'
  #    )
  #    trigger_error( sprintf( '%1s was called <strong>incorrectly</strong>. %2s %3s', function, message, version ) )


@Php.static_vars( _suspend = False )
def wp_suspend_cache_addition( suspend = None ):
  ''' Temporarily suspend cache additions.
  Stops more data being added to the cache, but still allows cache retrieval.
  This is useful for actions, such as imports, when a lot of data would otherwise
  be almost uselessly added to the cache.
  Suspension lasts for a single page load at most. Remember to call this
  function again if you wish to re-enable cache adds earlier.
  @staticvar bool _suspend
  @param bool suspend Optional. Suspends additions if True, re-enables them if False.
  @return bool The current suspend setting
  '''
  #static _suspend = False
  if Php.is_bool( suspend ):
    wp_suspend_cache_addition._suspend = suspend
  return wp_suspend_cache_addition._suspend


def wp_suspend_cache_invalidation( suspend = True ):
  ''' Suspend cache invalidation.
  Turns cache invalidation on and off. Useful during imports where you don't wont to do
  invalidations every time a post is inserted. Callers must be sure that what they are
  doing won't lead to an inconsistent cache when invalidation is suspended.
  @global bool _wp_suspend_cache_invalidation
  @param bool suspend Optional. Whether to suspend or enable cache invalidation. Default True.
  @return bool The current suspend setting.
  '''
  #global _wp_suspend_cache_invalidation
  #_wp_suspend_cache_invalidation = WpC.WB.Wj._wp_suspend_cache_invalidation

  current_suspend = WpC.WB.Wj._wp_suspend_cache_invalidation
  WpC.WB.Wj._wp_suspend_cache_invalidation = suspend
  return current_suspend


def wp_debug_backtrace_summary( ignore_class = None, skip_frames = 0,
                                pretty = True ):
  ''' Return a comma-separated string of functions that have been called to get
  to the current point in code.
  @see https://core.trac.wordpress.org/ticket/19589
  @param str ignore_class Optional. A class to ignore all function calls within
                          - useful when you want to just give info about the
                          callee. Default None.
  @param int skip_frames  Optional. Number of stack frames to skip - useful for
                          unwinding back to the source of the issue. Default 0.
  @param bool pretty      Optional. Whether or not you want a comma separated
                          string or raw array returned. Default True.
  @return str|array Either a string containing a reversed comma separated trace
                    or an array of individual calls.
  Better to use Php.debug_backtracereturn rather than xFn.caller_name()
  '''
  #if Php.version_compare( Php.PHP_VERSION, '5.2.5', '>=' ):
  #  trace = Php.debug_backtrace( False )
  #else:
  #  trace = Php.debug_backtrace()
  #
  #caller = array()
  #check_class = not Php.is_null( ignore_class )
  #skip_frames += 1  # skip this function
  #
  #for call in trace:
  #  if skip_frames > 0:
  #    skip_frames -= 1
  #  elseif isset( call['class'] ):
  #    if ( check_class and ignore_class == call['class'] )
  #      continue   # Filter out calls
  #
  #    caller[None] = "{}{}{}".format(call['class'], call['type'],
  #                                   call['function']            )
  #  else:
  #    if Php.in_array( call['function'], array( 'do_action', 'apply_filters' )):
  #      caller[None] = "{}('{}')".format(call['function'], call['args'][0])
  #    elif (Php.in_array( call['function'],
  #          array( 'include', 'include_once', 'require', 'require_once' ) )):
  #      caller[None] = call['function'] + "('" + Php.str_replace(
  #                       array( WP_CONTENT_DIR, ABSPATH ) , '', call['args'][0]
  #                       ) + "')"
  #    else:
  #      caller[None] = call['function']

  caller = array( *Php.debug_backtrace( False ) )
  if pretty:
    return Php.Join( ', ', Php.array_reverse( caller ) )
  else:
    return caller



def wp_checkdate( month, day, year, source_date ):
  ''' Test if the supplied date is valid for the Gregorian calendar.
  @see checkdate()
  @param  int    month       Month number.
  @param  int    day         Day number.
  @param  int    year        Year number.
  @param  string source_date The date to filter.
  @return bool True if valid date, False if not valid date.
  '''
  # Filter whether the given date is valid for the Gregorian calendar.
  # @param bool   checkdate   Whether the given date is valid.
  # @param string source_date Date to check.
  #return apply_filters( 'wp_checkdate', checkdate( month, day, year ), source_date )
  return Php.checkdate( month, day, year )


@Php.static_vars( encodings=array(), overloaded = None )
def mbstring_binary_safe_encoding( reset = False ):
  '''Set the mbstring internal encoding to a binary safe encoding when
  func_overload is enabled. When mbstring.func_overload is in use for
  multi-byte encodings, the results from strlen() and similar functions
  respect the utf8 characters, causing binary data to return incorrect lengths
  This function overrides the mbstring encoding to a binary-safe encoding, and
  resets it to the users expected encoding afterwards through the
  `reset_mbstring_encoding` function.
  It is safe to recursively call this function, however each
  `mbstring_binary_safe_encoding()` call must be followed up with an equal
  number of `reset_mbstring_encoding()` calls.
  @see reset_mbstring_encoding()
  @staticvar array encodings
  @staticvar bool  overloaded
  @param bool reset Optional. Whether to reset the encoding back to a
                               previously-set encoding. Default False.
  L5152 '''
  #static encodings = array()   #set @Php.statc_vars above
  #static overloaded = None     #set @Php.statc_vars above

  #if Php.is_null( overloaded ):
  if  mbstring_binary_safe_encoding.overloaded is None:
    mbstring_binary_safe_encoding.overloaded = bool(
                            Php.function_exists('mb_internal_encoding') and
                          ( int(Php.ini_get('mbstring.func_overload')) & 2 ))
  if False is mbstring_binary_safe_encoding.overloaded:
    return

  if not reset:
    encoding = Php.mb_internal_encoding()
    Php.array_push( mbstring_binary_safe_encoding.encodings, encoding )
    Php.mb_internal_encoding( 'ISO-8859-1' )

  if reset and mbstring_binary_safe_encoding.encodings:
    encoding = Php.array_pop( mbstring_binary_safe_encoding.encodings )
    Php.mb_internal_encoding( encoding )


def reset_mbstring_encoding():
  ''' Reset the mbstring internal encoding to a users previously set encoding.
  @see mbstring_binary_safe_encoding()
  L5181 '''
  mbstring_binary_safe_encoding( True )



def wp_cache_get_last_changed( group ):
  ''' Get last changed date for the specified cache group.
  @param group Where the cache contents are grouped.
  @return string last_changed UNIX timestamp with microseconds representing when the group was last changed.
  '''
  import wp.i.cache    as WiCa
  last_changed = WiCa.wp_cache_get( 'last_changed', group )
  if not last_changed:
    last_changed = Php.microtime()
    WiCa.wp_cache_set( 'last_changed', last_changed, group )


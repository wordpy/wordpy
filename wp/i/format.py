import re, unicodedata
import wp.conf    as WpC
import wp.i.kses  as WiK
import pyx.php    as Php
array = Php.array


def _wp_specialchars( string, quote_style = 'ENT_NOQUOTES', charset = False, double_encode = False ):
  ''' wp-includes/formatting.php
  Converts a number of special characters into their HTML entities.
  Specifically deals with: &, <, >, ", and '.
     quote_style can be set to ENT_COMPAT to encode " to &quot;, or ENT_QUOTES
     to do both. Default is ENT_NOQUOTES where no quotes are encoded.
  @staticvar string _charset
  @param string     string         The text which is to be encoded.
  @param int|string quote_style    Optional. Converts double quotes if set to ENT_COMPAT,
                                    both single and double if set to ENT_QUOTES or none if set to ENT_NOQUOTES.
                                    Also compatible with old values; converting single quotes if set to 'single',
                                    double if set to 'double' or both if otherwise set.
                                    Default is ENT_NOQUOTES.
  @param string     charset        Optional. The character encoding of the string. Default is False.
  @param bool       double_encode  Optional. Whether to encode existing html entities. Default is False.
  @return string The encoded text with HTML entities.
  '''
  string = str(string)
  if 0 == len( string ):
    return ''
  
  # Don't bother if there are no specialchars - saves some processing
  #if ! preg_match( '/[&<>"\']/', string ):
  import re  # to match anywhere in str, use re.search() instead of re.match()
  if not re.search( '[&<>"\']', string ):
    return string
  
  # Account for the previous behaviour of the function when the quote_style is not an accepted value
  if not quote_style:  # if ( empty( quote_style ) )
    quote_style = 'ENT_NOQUOTES'
  #elif ! in_array( quote_style, array( 0, 2, 3, 'single', 'double' ), True ):
  #in_array() checks the types of needle in haystack, if 3rd param strict=TRUE
  elif quote_style not in ( 0, 2, 3, 'single', 'double' ):
    quote_style = 'ENT_QUOTES'
  
  # Store the site charset as a static to avoid multiple calls to wp_load_alloptions()
  if not charset:
    # static _charset = None
    # if not isset( {**locals(), **_wp_specialchars.__dict__}, '_charset' ):
    #   alloptions = wp_load_alloptions()
    #   _charset = isset( alloptions['blog_charset'] 
    #                    ) ? alloptions['blog_charset'] : ''
    # charset = _charset
    charset = 'UTF-8'
  
  if charset in ( 'utf8', 'utf-8', 'UTF8' ):
    charset = 'UTF-8'
  
  _quote_style = quote_style
  
  if quote_style == 'double':
    quote_style = 'ENT_COMPAT'
    _quote_style = 'ENT_COMPAT'
  elif quote_style == 'single':
    quote_style = 'ENT_NOQUOTES'
  
  if not double_encode:
    # Guarantee every &entity; is valid, convert &garbage; into &amp;garbage
    # This is required for PHP < 5.4.0 because ENT_HTML401 flag is unavailable
    string = WiK.wp_kses_normalize_entities( string )
  
  string = Php.htmlspecialchars( string, quote_style, charset, double_encode)
  
  # Backwards compatibility
  if 'single' == _quote_style:
    string = string.replace("'", '&#039;')
  
  return string


def wp_check_invalid_utf8( string, strip = False ):
  ''' wp-includes/formatting.php
  Checks for invalid UTF8 in a string.
  #@staticvar bool is_utf8
  @staticvar bool utf8_pcre
  
  @param string  string The text which is to be checked.
  @param bool    strip Optional. Whether to attempt to strip out invalid UTF8. Default is False.
  @return string The checked text.
  L1024 '''
  string = str(string)
  if 0 == len( string ):
    return ''
  
  ## Store the site charset as static to avoid multiple calls to get_option()
  #static is_utf8 = None
  #if ! isset( is_utf8 ):
  #  #is_utf8 = in_array( get_option( 'blog_charset' ), array( 'utf8', 'utf-8', 'UTF8', 'UTF-8' ) )
  #  #>>> WpO.get_option('blog_charset') == 'UTF-8'  #Always = 'UTF-8'
  #  is_utf8 = 'UTF-8' in ( 'utf8', 'utf-8', 'UTF8', 'UTF-8' )
  #if not is_utf8:
  #  return string
  
  ## Check for support for utf8 in the installed PCRE library once and store the result in a static
  #static utf8_pcre = None
  #if ! isset( utf8_pcre ):
  #  utf8_pcre = @preg_match( '/^./u', 'a' )
  ## We can't demand utf8 in the PCRE installation, so just return the string in those cases
  #if !utf8_pcre:
  #  return string
  
  ## preg_match fails when it encounters invalid UTF8 in string
  #if 1 == @preg_match( '/^./us', string ):
  #  return string
  ## Attempt to strip the bad chars if requested (not recommended)
  #if strip and Php.function_exists( 'iconv' ):
  #  return iconv( 'utf-8', 'utf-8', string )
  #return ''

  #stackoverflow.com/questions/26541968/delete-every-non-utf-8-symbols-froms-string
  #b'\x80abc'.decode("utf-8", "ignore") docs.python.org/3.5/howto/unicode.html
  return string.encode('utf-8').decode('utf-8', 'ignore')


def utf8_uri_encode( utf8_string, length = 0, HexToLower=False ):
  ''' L1072 Encode the Unicode values to be used in the URI.
  @param string utf8_string
  @param int    length Max  length of the string
  @return string String with Unicode encoded for URI.

  docs.python.org/3.5/library/urllib.parse.html
  urllib.parse.quote_plus(string, safe='', encoding=None, errors=None)
  Like quote(), but also replace spaces by plus signs, as required for quoting HTML form values when building up a query string to go into a URL. Plus signs in the original string are escaped unless they are included in safe. It also does not have safe default to '/'.
  Example: quote_plus('/El Niño/') yields '%2FEl+Ni%C3%B1o%2F'.
  >>> parse.quote_plus("EFI收购Cr")      #Out=      'EFI%E6%94%B6%E8%B4%ADCr'
  wp> utf8_uri_encode( "EFI收购Cr" ); => string(31) "EFI%e6%94%b6%e8%b4%adCr"
  Note that php yields lower case hex while QuotedStr yields UPPER case hex
  So change to lowercase case: Php.UrlEncodedHexToLowercase(QuotedStr)
  >>> WiF.utf8_uri_encode("EFI收购Cr") == "EFI%e6%94%b6%e8%b4%adCr" #= True
  >>> WiF.utf8_uri_encode("/El Niño/") == "/El Ni%c3%b1o/" #= True = WP php
  '''
  from urllib.parse import quote_plus
  QuotedStr = quote_plus( utf8_string, safe='/' )

  # Not need: change to lowercase case
  #[urlencode - Is URL percent-encoding case sensitive?]
  #   (stackoverflow.com/questions/7994287/)
  # URL percent-encoding is NOT case sensitive. According to RFC 3986:
  # Percent-Encoding: uppercase hexadecimal digits 'A~F'=== lowercase 'a~f'
  #   2 URIs are eq if differ only in hex digits used in percent-encoded octets.
  if HexToLower:
    QuotedStr = Php.UrlEncodedHexToLowercase(QuotedStr)
  #BAD! replace '+' with  ' ' to match WordPress
  #QuotedStr = QuotedStr.replace('+', ' ')

  # [urlencode - When to encode space to plus (+) or %20?]
  #    (stackoverflow.com/questions/2678551/)
  # '+' means a space only in application/x-www-form-urlencoded content,
  #    such as the query part of a URL:
  return QuotedStr if length == 0 else QuotedStr[:length]

  '''
  values = array()
  num_octets = 1
  unicode_length = 0

  import wp.i.func  as WiFc
  WiFc.mbstring_binary_safe_encoding()
  string_length = strlen( utf8_string )
  WiFc.reset_mbstring_encoding()

  for (i = 0; i < string_length; i++ ) {

    value = ord( utf8_string[ i ] )

    if value < 128:
      if length and ( unicode_length >= length ):
        break
      unicode += chr(value)
      unicode_length++
    else:
      if len( values ) == 0:
        if value < 224:
          num_octets = 2
        elif value < 240:
          num_octets = 3
        else:
          num_octets = 4

      values[] = value

      if length and ( unicode_length + (num_octets * 3) ) > length:
        break
      if len( values ) == num_octets:
        for ( j = 0; j < num_octets; j++ ) {
          unicode += '%' + dechex( values[ j ] )

        unicode_length += num_octets * 3

        values = array()
        num_octets = 1

  return unicode
  '''


def sanitize_title_for_query( title ):
  ''' wp-includes/formatting.php
  Sanitizes a title with the 'query' context.
  Used for querying the database for a value from URL.
  @param str title The str to be sanitized.
  @return str The sanitized str.
  '''
  return sanitize_title( title, '', 'query' )


def sanitize_title_with_dashes( title, raw_title = '', context = 'display' ):
  ''' Sanitizes a title, replacing whitespace and a few other characters with dashes.
 * Limits the output to alphanumeric characters, underscore (_) and dash (-).
 * Whitespace becomes a dash.
 * @param string title     The title to be sanitized.
 * @param string raw_title Optional. Not used.
 * @param string context   Optional. The operation for which the string is sanitized.
 * @return string The sanitized title.
  '''
  title = Php.strip_tags(title)
  # Preserve escaped octets.
  #title= Php.preg_replace('|%([a-fA-F0-9][a-fA-F0-9])|', '---$1---', title)
  title = Php.preg_replace('|%([a-fA-F0-9][a-fA-F0-9])|', '---\\1---', title)
  # Remove percent signs that are not part of an octet.
  title = Php.str_replace('%', '', title)
  # Restore octets.
  #title= Php.preg_replace('|---([a-fA-F0-9][a-fA-F0-9])---|', '%$1', title)
  title = Php.preg_replace('|---([a-fA-F0-9][a-fA-F0-9])---|', '%\\1', title)

  #if seems_utf8(title):
  if Php.function_exists('mb_strtolower'):
    title = Php.mb_strtolower(title, 'UTF-8')
  title = utf8_uri_encode(title, 200)

  title = Php.strtolower(title)

  if 'save' == context:
    # Convert nbsp, ndash and mdash to hyphens
    title = Php.str_replace( ( '%c2%a0', '%e2%80%93', '%e2%80%94' ), '-', title )
    # Convert nbsp, ndash and mdash HTML entities to hyphens
    title = Php.str_replace( ( '&nbsp;', '&#160;', '&ndash;', '&#8211;', '&mdash;', '&#8212;' ), '-', title )

    # Strip these characters entirely
    title = Php.str_replace( (
      # iexcl and iquest
      '%c2%a1', '%c2%bf',
      # angle quotes
      '%c2%ab', '%c2%bb', '%e2%80%b9', '%e2%80%ba',
      # curly quotes
      '%e2%80%98', '%e2%80%99', '%e2%80%9c', '%e2%80%9d',
      '%e2%80%9a', '%e2%80%9b', '%e2%80%9e', '%e2%80%9f',
      # copy, reg, deg, hellip and trade
      '%c2%a9', '%c2%ae', '%c2%b0', '%e2%80%a6', '%e2%84%a2',
      # acute accents
       '%c2%b4', '%cb%8a', '%cc%81', '%cd%81',
      # grave accent, macron, caron
      '%cc%80', '%cc%84', '%cc%8c',
    ), '', title )

    # Convert times to x
    title = Php.str_replace( '%c3%97', 'x', title )

  title = Php.preg_replace('/&.+?;/', '', title); # kill entities
  title = Php.str_replace('.', '-', title)

  title = Php.preg_replace('/[^%a-z0-9 _-]/', '', title)
  title = Php.preg_replace('/\s+/', '-', title)
  title = Php.preg_replace('|-+|', '-', title)
  title = Php.trim(title, '-')

  return title


def format_to_edit( content, rich_text = False ):
  ''' wp-includes/formatting.php
  Acts on text which is about to be edited.
  The content is run through esc_textarea(), which uses htmlspecialchars()
  to convert special characters to HTML entities. If richedit is set to True,
  it is simply a holder for the 'format_to_edit' filter.
  @param string content   The text about to be edited.
  @param bool   rich_text Optional.
               Whether `content` should be considered rich text, in which case
               it would not be passed through esc_textarea(). Default False.
  @return str  The text after the filter (and possibly htmlspecialchars())
               has been run.
  '''
  # Filter the text to be formatted for editing.
  # @param string content The text, prior to formatting for editing.
  #content = apply_filters( 'format_to_edit', content )
  if not rich_text:
    content = esc_textarea( content )
  return content


def trailingslashit( Str ):   # string is a py module
  ''' Appends a trailing slash.
  remove trailing forward and backslashes if it exists already before adding
  a trailing forward slash. This prevents double slashing a string or path.
  primary use of this is for paths and thus should be used for paths. It is
  not restricted to paths and offers no specific path support.
  @param string Str What to add the trailing slash to.
  @return string String with trailing slash added.
  '''
  return untrailingslashit(Str) + '/'

def untrailingslashit( Str ):
  ''' Removes trailing forward slashes and backslashes if they exist.
  primary use of this is for paths and thus should be used for paths. It is
  not restricted to paths and offers no specific path support.
  @param string Str What to remove the trailing slashes from.
  @return string String without the trailing slashes.
  '''
  #return Php.rtrim(Str, '/\\')
  return  Str.rstrip('/\\')


def wp_unslash( value ):
  ''' Remove slashes from a str or array of strings.
  This should be used to remove slashes from data passed to core API that
  expects data to be unslashed.
  @param str|array value String or array of strings to unslash.
  @return str|array Unslashed value
  '''
  return stripslashes_deep( value )

def stripslashes_deep( value ):
  ''' Navigates through an array, object, or scalar, and removes slashes from
  the values.
  @param mixed value The value to be stripped.
  @return mixed Stripped value.
  '''
  return map_deep( value, stripslashes_from_strings_only )

def stripslashes_from_strings_only( value ):
  ''' Callback function for `stripslashes_deep()` which strips slashes
  from strings
  @param mixed value The array or str to be stripped.
  @return mixed value The stripped value.
  '''
  return Php.stripslashes( value ) if Php.is_string(value) else value

def map_deep( value, callback ):
  ''' Maps a function to all non-iterable elements of an array or an object.
  This is similar to `array_walk_recursive()` but acts upon objects too.
  @param mixed    value    The array, object, or scalar.
  @param callable callback The function to map onto value.
  @return mixed   The value with the callback applied to all non-arrays and
                  non-objects inside it.
  refer to Php.serialize FlattenObj()
  '''
  #from copy import deepcopy
  #val = deepcopy(value)

  if value is None:
    return None
  #from datetime import datetime
  #if isinstance(value, Php.SeqSetTypes): #= (list,tuple,range,set,frozenset,)
  #  value = [ map_deep( item, callback) for item in value ]
  #isinstance( value, Php.MappingTypes): #= (dict, ODict, array)
  if Php.is_array( value ):
    for index, item in value.items():
      value[ index ] = map_deep( item, callback )
  elif Php.is_object(value):
    #if inspect.isclass(value):  # class, not instance of a class
    #  element = Func(value, Func)
    #else:                       # by now, must be instance of class
    object_vars = Php.get_object_vars( value )
    for property_name, property_value in object_vars.items():
      setattr(value, property_name, map_deep( property_value, callback ))
  else: #elif isinstance( value, Php.ScalarTypes +(datetime,) ):
    # Php.ScalarTypes = (bool, str, bytes, int, float, complex,)
    value = callback( value )
  #else:
  #  raise TypeError("map_deep value={} has wrong type!".format(value))

  return value


#RegEx = re.compile('(?:[^a-z0-9.\-@])', re.IGNORECASE) # Exclude space & Underscore=Space in wiki

#strip_tags = Php.strip_tags 


def wp_strip_all_tags(Str, remove_breaks = False):
  ''' Properly strip all HTML tags including script and style
  This differs from strip_tags() because it removes the contents of
  the `<script>` and `<style>` tags. E.g. `strip_tags( '<script>something</script>' )`
  will return 'something'. wp_strip_all_tags will return ''
  @param string Str        String containing HTML tags
  @param bool   remove_breaks Optional. Whether to remove left over line breaks and white space chars
  @return string The processed string.
  '''
	#Str = Php.preg_replace( '@<(script|style)[^>]*?>.*?</\\1>@si', '', Str )
	#Str = Php.strip_tags(Str)
  RegExRmScripts = re.compile(r'<(script|style)[^>]*?>.*?</\1>',
                              re.IGNORECASE | re.DOTALL)
  Str = RegExRmScripts.sub('', Str)
  #print(Str)
  Str = Php.strip_tags(Str)
  if Str is None or Str == '':
    return None
  if remove_breaks:
		#Str = Php.preg_replace('/[\r\n\t ]+/', ' ', Str)
    RegExRmBreaks = re.compile('[\r\n\t ]+')  # don't use (r'\n') = '\'+'n'
    Str = RegExRmBreaks.sub(' ', Str)
    #print(Str)
	#return Php.trim( Str )
  return Str.strip()


def remove_accents(Str, accents=('COMBINING ACUTE ACCENT',
                                 'COMBINING GRAVE ACCENT', 'COMBINING TILDE')):
    accents = set(map(unicodedata.lookup, accents))
    chars = [c for c in unicodedata.normalize('NFD',Str) if c not in accents]
    return unicodedata.normalize('NFC', ''.join(chars))


def sanitize_user( username, strict = False ):
  ''' Sanitizes a username, stripping out unsafe characters.
  Removes tags, octets, entities, and if strict is enabled, will only keep
  alphanumeric, _, space, ., -, @. After sanitizing, it passes the username,
  raw username (the username in the parameter), and the value of strict as
  parameters for the 'sanitize_user' filter.
  @param str username The username to be sanitized.
  @param bool   strict   If set limits username to specific characters.
                         Default False.
  @return str The sanitized username, after passing through filters.
  '''
  raw_username = username
  username = wp_strip_all_tags( username )
  if not username:   # if username is None or username == '':
    return None
  username = remove_accents( username )
  ReKillOctets = re.compile(r'%([a-fA-F0-9][a-fA-F0-9])')
  username = ReKillOctets.sub('', username )     # Kill octets
  ReKillEntities = re.compile(r'&.+?;')
  username = ReKillEntities.sub('', username );  # Kill entities
  # If strict, reduce to ASCII for max portability.
  if strict :
    ReStrict = re.compile(r'[^a-z0-9 _.\-@]')
    username = ReStrict.sub('', username, re.IGNORECASE )
  username = username.strip()
  # Consolidate contiguous whitespaces
  ReCompactSpaces = re.compile('\s+')     # don't use (r'\s') = '\'+'s'
  username = ReCompactSpaces.sub(' ', username )

  # Filter a sanitized username str.
  # @param str username     Sanitized username.
  # @param str raw_username The username prior to sanitization.
  # @param bool   strict       Whether to limit the sanitization to specific characters. Default False.
  #return apply_filters( 'sanitize_user', username, raw_username, strict )
  if not username:  # username is None or username == '':
    return None
  return username

#wp> sanitize_user("mcdonald's")
#string(10) "mcdonald's"
#wp> sanitize_user("mcdonald's", true)
#string(9) "mcdonalds"

def sanitize_user_strict( username ):
  if username is None or username == '':
    return None
  ReStrict = re.compile(r'[^a-z0-9 _.\-@]')
  return ReStrict.sub('', username, re.IGNORECASE )


def sanitize_key( key ):
  ''' Sanitizes a str key.
  Keys are used as internal identifiers. Lowercase alphanumeric characters,
       dashes and underscores are allowed.
  @param str key String key
  @return str Sanitized key
  '''
  raw_key = key
  key = key.lower()
  ReSanKey = re.compile(r'[^a-z0-9_\-]')
  key = ReSanKey.sub('', key)

  # Filter a sanitized key str.
  # @param str key     Sanitized key.
  # @param str raw_key The key prior to sanitization.
  #return apply_filters( 'sanitize_key', key, raw_key )
  return key


# developer.wordpress.org/reference/functions/wp_insert_term/
#     uses:  wp-includes/formatting.php: sanitize_title()

def sanitize_title( title, fallback_title = '', context = 'save' ):
  '''Sanitize a title, or return a fallback title. HTML and PHP tags are
  stripped. If title is empty & fallback_title is set, the latter will be used
  @param str title          The str to be sanitized.
  @param str fallback_title Optional. A title to use if title is empty.
  @param str context        Optional.
                               The operation for which the str is sanitized
  @return str The sanitized str.
  '''
  #import wp.i.plugin  as WiPg
  raw_title = title
  if 'save' == context:
    title = remove_accents(title)
  #VT Added to  substitute multiple spaces with single space
  title = ' '.join(title.split())

  # In wp.i.default_filters :
  # WiPg.add_filter('sanitize_title', WiF.sanitize_title_with_dashes, 10, 3)

  #WiPg.add_action( 'check_comment_flood', 'check_comment_flood_db', 10, 4 )
  # Filter a sanitized title str.
  # @param str title     Sanitized title.
  # @param str raw_title The title prior to sanitization.
  # @param str context  The context for which the title is being sanitized
  '''
  # VT Purposedly not apply_filters(WiF.sanitize_title_with_dashes)
  # if apply filters: all titles and terms will be encoded.
  title = WiPg.apply_filters( 'sanitize_title', title, raw_title, context )
  '''
  if '' == title or False is title: # if not title:
    title = fallback_title
  return title


#def get_gmt_from_date( string, Format = 'Y-m-d H:i:s' ):
def  get_gmt_from_date( Str, Format = '%Y-%m-%d %H:%M:%S' ):
  ''' Returns a date in the GMT equivalent.
  Requires and returns a date in the Y-m-d H:i:s Format. If there is a
  timezone_string available, the date is assumed to be in that timezone,
  otherwise it simply [ subtracts ] the value of the 'gmt_offset' option.
      Return Format can be overridden using the Format parameter.
  @param string Str The date to be converted.
  @param string Format The Format string for the returned date (default is Y-m-d H:i:s)
  @return string GMT version of the date provided.
  weston.ruter.net/2013/04/02/do-not-change-the-default-timezone-from-utc-in-wordpress/
  [Default tz hardcoded as UTC]wordpress.stackexchange.com/questions/30946/
  '''
  import wp.i.option as WiO
  from datetime import datetime
  import wpy.time as wTm
  tz = WiO.get_option( 'timezone_string' )  # default = '', can set to ='UTC'

  if tz:
    #datetime = date_create( Str, new DateTimeZone( tz ) )
    Dt = datetime.strptime(Str, Format)
    if not Dt:
      #return gmdate( Format, 0 )
      Dt = wTm.DtMin  # = datetime.min +1day, else err convert tz -n hr
    #datetime->setTimezone( new DateTimeZone( 'UTC' ) )
    UtcDt      = wTm.DtToUtc(Dt, tz )
    #string_gmt = datetime->Format( Format )
  else:
    Result, matches = Php.preg_match_Result( '#([0-9]{1,4})-([0-9]{1,2})-'
                  '([0-9]{1,2}) ([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2})#', Str)
    if not Result:
      #datetime = strtotime( Str )
      Dt = datetime.strptime(Str, Format)
      if not Dt:    # datetime:
        #return gmdate( Format, 0 )
        Dt = wTm.DtMin  # = datetime.min +1day, else err convert tz -n hr
      #return gmdate( Format, datetime )
      #BlogWebHostLocation = WpC.WB.Wj.Bj.WH0.DcNum
      #BlogWebHostUtc      = wTm.DtToUtc(Dt, BlogWebHostLocation )
      #return BlogWebHostUtc.strftime(Format)
      return wTm.SetDtToUtc(Dt)

    #string_time = gmmktime( matches[4], matches[5], matches[6],
    #                        matches[2], matches[3], matches[1] )
    #string_gmt = gmdate( Format, string_time -
    #                     get_option( 'gmt_offset' ) * HOUR_IN_SECONDS )
    # UtcDt = Dt - gmt_offset  # [ subtract ] !!!
    UtcDt = datetime( matches[1], matches[2], matches[3], matches[4] -
                    int(WiO.get_option('gmt_offset')), matches[5], matches[6])

  string_gmt = UtcDt.strftime(Format)
  return string_gmt
  # raise ValueError("WiF.get_gmt_from_date Unknown timezone tz="+ tz)


def  GetGmtDtFromDt( Dt ):
  ''' Returns a dt datetime in the GMT equivalent.
  Requires and returns a py datetime format.
  '''
  import wp.i.option as WiO
  from datetime import datetime, timedelta
  import wpy.time as wTm
  tz = WiO.get_option( 'timezone_string' )  # default = '', can set to ='UTC'

  if tz:
    if not Dt:
      Dt = wTm.DtMin  # = datetime.min +1day, else err convert tz -n hr
    return wTm.DtToUtc(Dt, tz )
  # UtcDt = Dt - gmt_offset  # [ subtract ] !!!
  return Dt - timedelta( hours= int(WiO.get_option('gmt_offset')) )


#def get_date_from_gmt( string, Format = 'Y-m-d H:i:s' ):
def  get_date_from_gmt( Str, Format = '%Y-%m-%d %H:%M:%S' ):
  ''' Converts a GMT date into the correct Format for the blog.
  Requires and returns a date in the Y-m-d H:i:s Format. If there is a
  timezone_string available, the returned date is in that timezone, otherwise
  it simply [ adds ] the value of gmt_offset. Return Format can be overridden
  using the Format parameter
  @param string Str The date to be converted.
  @param string Format The Format string for the returned date (default is Y-m-d H:i:s)
  @return string Formatted date relative to the timezone / GMT offset.
  weston.ruter.net/2013/04/02/do-not-change-the-default-timezone-from-utc-in-wordpress/
  [Default tz hardcoded as UTC]wordpress.stackexchange.com/questions/30946/
  '''
  import wp.i.option as WiO
  from datetime import datetime
  import wpy.time as wTm
  tz = WiO.get_option( 'timezone_string' )  # default = '', can set to ='UTC'
  if tz:
    #Dt = date_create( Str, new DateTimeZone( 'UTC' ) )
    GmtDt = wTm.SetDtToUtc( datetime.strptime(Str, Format) )  #Gmt = Utc
    if not GmtDt:
      #return date( Format, 0 )
      GmtDt = wTm.DtMin  # = datetime.min +1day, else err convert tz -n hr
    #Dt->setTimezone( new DateTimeZone( tz ) )
    #string_localtime = Dt->Format( Format )
    LocalDt = wTm.UtcToDt(GmtDt, tz)
    string_localtime = LocalDt.strftime(Format)
  else:
    Result, matches = Php.preg_match_Result( '#([0-9]{1,4})-([0-9]{1,2})-'
                  '([0-9]{1,2}) ([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2})#', Str)
    if not Result:
      #return date( Format, 0 )
      #return datetime.min   # = datetime.datetime(1, 1, 1, 0, 0)
      LocalDt = wTm.DtMin  # = datetime.min +1day, else err convert tz -n hr
    else:
      LocalDt = datetime( matches[1], matches[2], matches[3], matches[4] +
                    int(WiO.get_option('gmt_offset')), matches[5], matches[6])
    #string_time = gmmktime( matches[4], matches[5], matches[6], matches[2],
    #                        matches[3], matches[1] )
    #string_localtime = gmdate( Format, string_time +
    #                  int(WiO.get_option( 'gmt_offset' )) * HOUR_IN_SECONDS )
    # LocalDt = GmtDt + gmt_offset  # [ add ] !!!
    string_localtime = LocalDt.strftime(Format)

  return string_localtime


def  GetDtFromGmtDt( GmtDt ):
  import wp.i.option as WiO
  from datetime import datetime, timedelta
  import wpy.time as wTm
  tz = WiO.get_option( 'timezone_string' )  # default = '', can set to ='UTC'
  if tz:
    if not GmtDt:
      GmtDt = wTm.DtMin  # = datetime.min +1day, else err convert tz -n hr
    return wTm.UtcToDt(GmtDt, tz)
  # LocalDt = GmtDt + gmt_offset  # [ add ] !!!
  return GmtDt + timedelta( hours= int(WiO.get_option('gmt_offset')) )


def esc_sql( data ):
  ''' Escapes data for use in a MySQL query.
  Usually you should prepare queries using wpdb::prepare().
  Sometimes, spot-escaping is required or useful. One example
  is preparing an array for use in an IN clause.
  @global wpdb wpdb WordPress database abstraction object.
  @param string|array data Unescaped data
  @return string|array Escaped data
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wpdb._escape( data )


def esc_js( text ):
  ''' wp-includes/formatting.php
  Escape single quotes, htmlspecialchar " < > &, and fix line endings.
  Escapes text str for echoing in JS. It is intended to be used for inline JS
  (in a tag attribute, for example onclick="..."). Note that the str have to
  be in single quotes. The filter 'js_escape' is also applied here.
  @param string text The text to be escaped.
  @return string Escaped text.
  '''
  safe_text = wp_check_invalid_utf8( text )
  safe_text = _wp_specialchars( safe_text, 'ENT_COMPAT' )
  #safe_text= preg_replace( '/&#(x)?0*(?(1)27|39);?/i', "'",
  #                         stripslashes( safe_text ) )
  import re
  safe_text = re.sub('&#(x)?0*(?(1)27|39);?', "'",
                     Php.stripslashes( safe_text ), flags=re.IGNORECASE )
  safe_text = safe_text.replace("\r", '')
  safe_text = Php.addslashes( safe_text ).replace("\n", '\\n')
  # Filter a string cleaned and escaped for output in JavaScript.
  # Text passed to esc_js() is stripped of invalid or special characters,
  # and properly slashed for output.
  # @param string safe_text The text after it has been escaped.
  # @param string text      The text prior to being escaped.
  #return apply_filters( 'js_escape', safe_text, text )
  return safe_text
#>>> WpF.esc_js('<script></script>')  #==>'&lt;script&gt;&lt;/script&gt;'


def esc_html( text ):
  ''' wp-includes/formatting.php
  Escaping for HTML blocks.
  @param string text
  @return string
  '''
  safe_text = wp_check_invalid_utf8( text )
  safe_text = _wp_specialchars( safe_text, 'ENT_QUOTES' )
  # Filter a string cleaned and escaped for output in HTML.
  # Text passed to esc_html() is stripped of invalid or special characters
  # before output.
  # @param string safe_text The text after it has been escaped.
  # @param string text      The text prior to being escaped.
  #return apply_filters( 'esc_html', safe_text, text )
  return safe_text


def esc_attr( text ):
  ''' wp-includes/formatting.php
  Escaping for HTML attributes.
  @param string text
  @return string
  '''
  safe_text = wp_check_invalid_utf8( text )
  safe_text = _wp_specialchars( safe_text, 'ENT_QUOTES' )
  # Filter a string cleaned and escaped for output in an HTML attribute.
  # Text passed to esc_attr() is stripped of invalid or special characters
  # before output.
  # @param string safe_text The text after it has been escaped.
  # @param string text      The text prior to being escaped.
  #return apply_filters( 'attribute_escape', safe_text, text )
  return safe_text


def esc_textarea( text ):
  ''' wp-includes/formatting.php
  Escaping for textarea values.
  @param string text
  @return string
  >>> WpO.get_option('blog_charset') == 'UTF-8'  #Always = 'UTF-8'
  '''
  #Php.htmlspecialchars( text, 'ENT_QUOTES', get_option('blog_charset') )
  safe_text = Php.htmlspecialchars( text, 'ENT_QUOTES', 'UTF-8' )
  # Filter a string cleaned and escaped for output in a textarea element.
  # @param string safe_text The text after it has been escaped.
  # @param string text      The text prior to being escaped.
  #return apply_filters( 'esc_textarea', safe_text, text )
  return  safe_text


#def wp_parse_str( Str, &arr ):  # Orig wp php
def  wp_parse_str( Str ):
  ''' Parses a str into variables to be stored in an arr.
  Uses {@link www.php.net/parse_str parse_str()} and stripslashes if
  {@link www.php.net/magic_quotes magic_quotes_gpc} is on.
  @param str Str The Str to be parsed.
  @param dict  arr  Variables will be stored in this arr.
    parse_qs('abc')                         #out=# {}  !!!
    parse_qs('abc', keep_blank_values=True) #out=# {'abc': ['']}
  so need keep_blank_values=True to match php:
    wp> wp_parse_str('abc', $r) #Out# r=# => arr(1) {["abc"]=> string(0)""}
  '''
  # parse_str( Str, arr )
  # www.php2python.com/wiki/function.parse-str/
  from urllib.parse import parse_qs
  arr = parse_qs(Str, keep_blank_values=True)
  # >>> parse_qs('first=value&sec=foo+bar')
  #    {'first': ['value'], 'sec': ['foo bar']} '''
  #arr = ODict([ (k,v[0]) for k,v in arr.items() ])
  #converts to:  ODict([('sec', 'foo bar'), ('first', 'value')])
  arr = array( *[ (k,v[0]) for k,v in arr.items() ])

  #if get_magic_quotes_gpc():
  #  arr = stripslashes_deep( arr )

  # Filter the arr of variables derived from a parsed str.
  # @param array arr The array populated with variables.
  #arr = apply_filters( 'wp_parse_str', arr )
  return arr




allowedentitynames = (  # no need array() since, below is only place to use it
  'nbsp',    'iexcl',  'cent',    'pound',  'curren', 'yen',
  'brvbar',  'sect',   'uml',     'copy',   'ordf',   'laquo',
  'not',     'shy',    'reg',     'macr',   'deg',    'plusmn',
  'acute',   'micro',  'para',    'middot', 'cedil',  'ordm',
  'raquo',   'iquest', 'Agrave',  'Aacute', 'Acirc',  'Atilde',
  'Auml',    'Aring',  'AElig',   'Ccedil', 'Egrave', 'Eacute',
  'Ecirc',   'Euml',   'Igrave',  'Iacute', 'Icirc',  'Iuml',
  'ETH',     'Ntilde', 'Ograve',  'Oacute', 'Ocirc',  'Otilde',
  'Ouml',    'times',  'Oslash',  'Ugrave', 'Uacute', 'Ucirc',
  'Uuml',    'Yacute', 'THORN',   'szlig',  'agrave', 'aacute',
  'acirc',   'atilde', 'auml',    'aring',  'aelig',  'ccedil',
  'egrave',  'eacute', 'ecirc',   'euml',   'igrave', 'iacute',
  'icirc',   'iuml',   'eth',     'ntilde', 'ograve', 'oacute',
  'ocirc',   'otilde', 'ouml',    'divide', 'oslash', 'ugrave',
  'uacute',  'ucirc',  'uuml',    'yacute', 'thorn',  'yuml',
  'quot',    'amp',    'lt',      'gt',     'apos',   'OElig',
  'oelig',   'Scaron', 'scaron',  'Yuml',   'circ',   'tilde',
  'ensp',    'emsp',   'thinsp',  'zwnj',   'zwj',    'lrm',
  'rlm',     'ndash',  'mdash',   'lsquo',  'rsquo',  'sbquo',
  'ldquo',   'rdquo',  'bdquo',   'dagger', 'Dagger', 'permil',
  'lsaquo',  'rsaquo', 'euro',    'fnof',   'Alpha',  'Beta',
  'Gamma',   'Delta',  'Epsilon', 'Zeta',   'Eta',    'Theta',
  'Iota',    'Kappa',  'Lambda',  'Mu',     'Nu',     'Xi',
  'Omicron', 'Pi',     'Rho',     'Sigma',  'Tau',    'Upsilon',
  'Phi',     'Chi',    'Psi',     'Omega',  'alpha',  'beta',
  'gamma',   'delta',  'epsilon', 'zeta',   'eta',    'theta',
  'iota',    'kappa',  'lambda',  'mu',     'nu',     'xi',
  'omicron', 'pi',     'rho',     'sigmaf', 'sigma',  'tau',
  'upsilon', 'phi',    'chi',     'psi',    'omega',  'thetasym',
  'upsih',   'piv',    'bull',    'hellip', 'prime',  'Prime',
  'oline',   'frasl',  'weierp',  'image',  'real',   'trade',
  'alefsym', 'larr',   'uarr',    'rarr',   'darr',   'harr',
  'crarr',   'lArr',   'uArr',    'rArr',   'dArr',   'hArr',
  'forall',  'part',   'exist',   'empty',  'nabla',  'isin',
  'notin',   'ni',     'prod',    'sum',    'minus',  'lowast',
  'radic',   'prop',   'infin',   'ang',    'and',    'or',
  'cap',     'cup',    'int',     'sim',    'cong',   'asymp',
  'ne',      'equiv',  'le',      'ge',     'sub',    'sup',
  'nsub',    'sube',   'supe',    'oplus',  'otimes', 'perp',
  'sdot',    'lceil',  'rceil',   'lfloor', 'rfloor', 'lang',
  'rang',    'loz',    'spades',  'clubs',  'hearts', 'diams',
  'sup1',    'sup2',   'sup3',    'frac14', 'frac12', 'frac34',
  'there4',
)


def valid_unicode(i):
  ''' Helper func to determine if a Unicode value is valid.
  @param int i Unicode value
  @return bool True if the value was a valid Unicode number
  '''
  i = int(i)
  return ( i == 0x9 or i == 0xa or i == 0xd or
          (i >= 0x20    and i <= 0xd7ff  )  or
          (i >= 0xe000  and i <= 0xfffd  )  or
          (i >= 0x10000 and i <= 0x10ffff)    )


def wp_kses_named_entities(MatchObj):
  ''' wp-includes/kses.php
  Callback for wp_kses_normalize_entities() regular expression.
  This func only accepts valid named entity references, which are finite,
  case-sensitive, and highly scrutinized by HTML and XML validators.
  @global array allowedentitynames
  @param  object MatchObj re.sub() MatchObj object
  @return string Correctly encoded entity
  '''
  if not MatchObj.group(1):   # don't use Php.empty since using py match obj
    return ''

  i = MatchObj.group(1)
  #return ( ! in_array( $i, allowedentitynames ) ) ? "&amp;$i;" : "&$i;"
  return "&amp;{};".format(i) if i not in allowedentitynames else "&{};".format(i)


def wp_kses_normalize_entities2(MatchObj):
  ''' Callback for wp_kses_normalize_entities() regular expression.
  This func helps {@see wp_kses_normalize_entities()} to only accept 16-bit
  values and nothing more for `&#number;` entities.
  @param  object MatchObj re.sub() MatchObj object
  @return string Correctly encoded entity
  '''
  if not MatchObj.group(1):   # don't use Php.empty since using py match obj
    return ''

  i = MatchObj.group(1)
  if valid_unicode(i):
    #i= str_pad(ltrim(i,'0'), 3, '0', STR_PAD_LEFT)
    # php2python.com/wiki/function.str-pad/
    # result = input.rjust(pad_length, pad_char) # STR_PAD_LEFT = rjust !!!!
    # php2python.com/wiki/function.ltrim/
    # result = myStr.lstrip(charlist)
    i = i.lstrip('0').rjust(3, '0')              # STR_PAD_LEFT = rjust !!!!
    i = "&#{};".format(i)
  else:
    i = "&amp;#{};".format(i)
  return i


def wp_kses_normalize_entities3(MatchObj):
  ''' Callback for wp_kses_normalize_entities() for regular expression.
  This func helps wp_kses_normalize_entities() to only accept valid Unicode
  numeric entities in hex form.
  @param  object MatchObj re.sub() MatchObj object
  @return string Correctly encoded entity
  '''
  if not MatchObj.group(1):   # don't use Php.empty since using py match obj
    return ''

  hexchars = MatchObj.group(1)
  # php: hexdec(hexchars)  => py: int(hexchars, 16)
  # php: ltrim             => py: myStr.lstrip(charlist)
  return "&amp;#x{};".format(hexchars) if not valid_unicode( int(hexchars, 16)
         ) else '&#x' + hexchars.lstrip('0') + ';'


def wp_kses_normalize_entities(string):
  ''' wp-includes/kses.php
  Converts and fixes HTML entities.
  normalizes HTML entities. convert `AT&T` to the correct
  `AT&amp;T`, `&#00058;` to `&#058;`, `&#XYZZY;` to `&amp;#XYZZY;` and so on.
  #           Orig WRONG!!   &#58;  .  See Test below.
  @param string string Content to normalize entities
  @return string Content with normalized entities
  '''
  import re
  # Disarm all entities by converting & to &amp
  string = string.replace('&', '&amp;')

  # Change back the allowed entities in our entity whitelist
  #string = preg_replace_callback('/&amp;([A-Za-z]{2,8}[0-9]{0,2});/',
  #                               'wp_kses_named_entities', string)
  #string = preg_replace_callback('/&amp;#(0*[0-9]{1,7});/',
  #                               'wp_kses_normalize_entities2', string)
  #string = preg_replace_callback('/&amp;#[Xx](0*[0-9A-Fa-f]{1,6});/',
  #                               'wp_kses_normalize_entities3', string)
  string = re.sub('&amp;([A-Za-z]{2,8}[0-9]{0,2});',
                  wp_kses_named_entities     , string)
  string = re.sub('&amp;#(0*[0-9]{1,7});',
                  wp_kses_normalize_entities2, string)
  string = re.sub('&amp;#[Xx](0*[0-9A-Fa-f]{1,6});',
                  wp_kses_normalize_entities3, string)
  return string

''' http://php.net/manual/function.preg-replace-callback.php
Perform a regular expression search and replace using a callback
mixed preg_replace_callback ( mixed $pattern , callback $callback , mixed $subject [, int $limit= -1 [, int &$count ]] )
callback will be called and passed an array of matched elements in the subject string. The callback should return the replacement string.
$matches[0] is the complete match

www.php2python.com/wiki/function.preg-replace-callback/
result = re.sub(pattern, callback, subject, limit)

docs.python.org/3/library/re.html
 re.sub(pattern, repl, string, count=0, flags=0)
If repl is a func, it is called for every non-overlapping occurrence of pattern. The func takes a single match object argument, and returns the replacement string. For example:
>>> def dashrepl(matchobj):
...     if matchobj.group(0) == '-': return ' '
...     else: return '-'
>>> re.sub('-{1,2}', dashrepl, 'pro----gram-files')
'pro--gram files'
>>> re.sub(r'\sAND\s', ' & ', 'Baked Beans And Spam', flags=re.IGNORECASE)
'Baked Beans & Spam'

>>> def CB(matchobj):
...   return matchobj.group(0) * 2
>>> re.sub( '[&<>"\']', CB, string )
'da^&&dfa7147890>>N""<<a '


Test:

wp> wp_kses_normalize_entities('AT&T')      #=> string(8) "AT&amp;T"
wp> wp_kses_normalize_entities('&#00058;')  #=> string(6) "&#058;"
wp> wp_kses_normalize_entities('`&#XYZZY;') #=> string(13) "`&amp;#XYZZY;"
>>> PyK.wp_kses_normalize_entities('AT&T')     #=> 'AT&amp;T'
>>> PyK.wp_kses_normalize_entities('&#00058;') #=> '&#058;'
>>> PyK.wp_kses_normalize_entities('&#XYZZY;') #=> '&amp;#XYZZY;'

'''


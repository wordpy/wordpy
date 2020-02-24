import pyx.php as Php
array = Php.array

# WP_MatchesMapRegex helper class
# @package WordPress


class WP_MatchesMapRegex:
  ''' Helper class to remove the need to use eval to replace matches[] in query strings.
  '''

  #def __construct(subject, matches):
  def __init__(self, subject, matches):
    ''' constructor
    @param string subject subject if regex
    @param array  matches data to use in map
    '''
    # store for matches
    # @access private
    # @var array
    self._matches = None   #VT init to None, orig just declared var

    # store for mapping result
    # @access public
    # @var string
    self.output = None   #VT init to None, orig just declared var

    # subject to perform mapping on (query string containing matches[] references
    # @access private
    # @var string
    self._subject = None   #VT init to None, orig just declared var

    # regexp pattern to match matches[] references
    # @var string
    self._pattern = '(\$matches\[[1-9]+[0-9]*\])'; # magic number

    self._subject = subject
    self._matches = matches
    self.output = self._map()


  @staticmethod
  def Apply(subject, matches):
    ''' Substitute substring matches in subject.
    static helper function to ease use
    @static
    @access public
    @param string subject subject
    @param array  matches data used for substitution
    @return string
    '''
    oSelf = WP_MatchesMapRegex(subject, matches)
    return oSelf.output


  def _map(self):
    ''' do the actual mapping
    @access private
    @return string
    '''
    #callback = array(self, 'callback')
    callback  = self.callback
    return preg_replace_callback(self._pattern, callback, self._subject)


  def callback(self, matches):
    ''' preg_replace_callback hook
    @access public
    @param  array matches preg_replace regexp matches
    @return string
    '''
    index = intval(substr(matches[0], 9, -1))
    return urlencode(self._matches[index]) if Php.isset(self._matches, index) else ''


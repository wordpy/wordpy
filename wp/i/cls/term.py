import wp.conf        as WpC
import wp.i.cls.error as WcE  # WP_Error
import wp.i.cache     as WiCa
import wp.i.l10n      as WiTr
import pyx.php   as Php
array = Php.array

''' Taxonomy API: WP_Term class
@package WordPress  @subpackage Taxonomy
'''
__, _x, _n_noop = WiTr.__, WiTr._x, WiTr._n_noop


#final class WP_Term {
class WP_Term(Php.stdClass):
  " Core class used to implement the WP_Term object. "


  def __init__( self, term ):
    ''' Constructor.
    @param WP_Term|object term Term object.
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    # Term ID.
    # @access public  @var int
    #$term_id
    self.term_id = None

    # The term's name.
    # @access public  @var string
    self.name = ''

    # The term's slug.
    # @access public  @var string
    self.slug = ''

    # The term's term_group.
    # @access public  @var string
    self.term_group = ''

    # Term Taxonomy ID.
    # @access public  @var int
    self.term_taxonomy_id = 0

    # The term's taxonomy name.
    # @access public  @var string
    self.taxonomy = ''

    # The term's description.
    # @access public  @var string
    self.description = ''

    # ID of a term's parent term.
    # @access public  @var int
    self.parent = 0

    # Cached object count for this term.
    # @access public  @var int
    self.count = 0

    # Stores the term object's sanitization level.
    # Does not correspond to a database field.
    # @access public  @var string
    self.filter = 'raw'

    if isinstance(term, array): # super().__init__(arg): Php.stdClass._obj = arg
      self._obj = term # term is already in array so don't need to setattr below
    else:
      for key, value in Php.get_object_vars( term ).items():
        #$this->$key = $value
        setattr(self, key, value)


  @staticmethod
  def get_instance( term_id, taxonomy = None ):
    ''' Retrieve WP_Term instance.
    @access public  @static
    @global wpdb wpdb WordPress database abstraction object.
    @param int    term_id  Term ID.
    @param string taxonomy Optional. Limit matched terms to those matching `taxonomy`. Only used for
                            disambiguating potentially shared terms.
    @return WP_Term|WP_Error|False Term object, if found. WP_Error if `term_id` is shared between taxonomies and
                                   there's insufficient data to distinguish which term is intended.
                                   False for other failures.
    '''
    wpdb = WpC.WB.Wj.wpdb  # global wpdb
    import wp.i.taxonomy as WpTx

    if (not Php.is_numeric( term_id ) or term_id != Php.floor( term_id ) or
        not term_id):
      return False

    term_id = int(term_id)
       
    _term = WiCa.wp_cache_get( term_id, 'terms' )

    # If there isn't a cached version, hit the database.
    if not _term or ( taxonomy and taxonomy != _term.taxonomy ):
      # Grab all matching terms, in case any are shared between taxonomies.
      terms = wpdb.get_results( wpdb.prepare( "SELECT t.*, tt.* FROM {} AS t INNER JOIN {} AS tt ON t.term_id = tt.term_id WHERE t.term_id = %d".format(wpdb.terms, wpdb.term_taxonomy), term_id ))
      if not terms:
        return False

      # If a taxonomy was specified, find a match.
      if taxonomy:
        for match in terms:
          if taxonomy == match.taxonomy:
            _term = match
            break

      # If only one match was found, it's the one we want.
      elif 1 == len( terms ):
        _term = reset( terms )

      # Otherwise, the term must be shared between taxonomies.
      else:
        # If the term is shared only with invalid taxonomies, return the one valid term.
        for t in terms:
          if not WpTx.taxonomy_exists( t.taxonomy ):
            continue

          # Only hit if we've already identified a term in a valid taxonomy.
          if _term:
            return WcE.WP_Error( 'ambiguous_term_id', __( 'Term ID is shared between multiple taxonomies' ), term_id )

          _term = t

      if not _term:
        return False

      # Don't return terms from invalid taxonomies.
      if not WpTx.taxonomy_exists( _term.taxonomy ):
        return WcE.WP_Error( 'invalid_taxonomy', __( 'Invalid taxonomy.' ) )

      _term = WpTx.sanitize_term( _term, _term.taxonomy, 'raw' )

      # Don't cache terms that are shared between taxonomies.
      if 1 == len( terms ):
        WiCa.wp_cache_add( term_id, _term, 'terms' )

    term_obj = WP_Term( _term )
    term_obj.filter( term_obj.filter )

    return term_obj


  def filter(self, filter ):
    ''' Sanitizes term fields, according to the filter type provided.
    @param string filter Filter context. Accepts 'edit', 'db', 'display', 'attribute', 'js', 'raw'.
    '''
    import wp.i.taxonomy as WpTx
    WpTx.sanitize_term( self, self.taxonomy, filter )


  def to_array(self):
    ''' Converts an object to array.
    @return array Object as array.
    '''
    return Php.get_object_vars( self )


  def __getattr__(self, key):
    ''' Getter.
    @param string key Property to get.
    @return mixed Property value.
    '''
    import wp.i.taxonomy as WpTx
    if key == '_obj':             # VT Added as a subclass of Php.stdClass
      return super().__getattribute__(key)
    #switch ( key ) {
    #  case 'data' :
    if key == 'data':
      data = Php.stdClass()
      columns = ('term_id', 'name', 'slug', 'term_group','term_taxonomy_id',
                 'taxonomy', 'description', 'parent', 'count')
      for column in columns:
        #$data->{$column} = ( Php.isset( self, $column ) ?
        #                     self->{$column} : null )
        setattr(data, column, getattr( self, column, None ))

      return WpTx.sanitize_term( data, data.taxonomy, 'raw' )
    #return super().__getattribute__(key)
    return super().__getattr__(key)

  __get = __getattr__

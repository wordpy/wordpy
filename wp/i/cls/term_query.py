import wp.conf       as WpC
import wp.i.cls.meta_query  as WcMQ
import wp.i.cache    as WiCa
import wp.i.format   as WiF
import wp.i.func     as WiFc
import wp.i.plugin   as WiPg
import pyx.php       as Php
array = Php.array
# Module.Wj   = self.Wj  set in Web.WpBlogCls

''' Taxonomy API: WP_Term_Query class.
@package WordPress   @subpackage Taxonomy
'''

class WP_Term_Query(Php.stdClass):
  ''' Class used for querying terms.
  @see WP_Term_Query::__construct() for accepted arguments.
  '''
  def __init__(self, query = ''):
    '''Constructor.
    Sets up the term query, based on the query vars passed.
    @param str|array query {
     Optional. Array or query str of term query parameters. Default empty.
     @type str|array taxonomy Taxonomy name, or array of taxonomies, to which
                                 results should be limited.
     @type int|array object_ids Optional. Object ID, or array of object IDs.
               Results will be limited to terms associated with these objects.
     @type str orderby  Field(s) to order terms by. Accepts term fields
               ('name', 'slug', 'term_group', 'term_id', 'id', 'description'),
               'count' for term taxonomy count, 'include' to match the
               'order' of the include param, 'meta_value', 'meta_value_num',
               the value of `meta_key`, the array keys of `meta_query`, or
               'none' to omit the ORDER BY clause. Defaults to 'name'.
     @type str order  Whether to order terms in ascending or descending order.
                      Accepts 'ASC' (ascending) or 'DESC' (descending).
                      Default 'ASC'.
     @type bool|int   hide_empty   Whether to hide terms not assigned to any
                             posts. Accepts 1|True or 0|False. Default 1|True.
     @type array|str include Array or comma/space-separated str of term ids to include.
                                Default empty array.
     @type array|str exclude Array or comma/space-separated str of term ids to exclude.
                                If include is non-empty, exclude is ignored.
                                Default empty array.
     @type array|str exclude_tree Array or comma/space-separated str of term ids to exclude
                               along with all of their descendant terms. If include is
                               non-empty, exclude_tree is ignored. Default empty array.
     @type int|str   number Maximum number of terms to return. Accepts ''|0 (all) or any
                               positive number. Default ''|0 (all).
     @type int offset The number by which to offset the terms query. Default empty.
     @type str fields Term fields to query for. Accepts 'all' (returns an
             array of complete term objects), 'ids' (returns an array of ids),
             array of term objects with the 'object_id' param; only works
             when the `fields` parameter is 'object_ids' ), 'ids'
             (returns an array of ids), 'tt_ids' (returns an array of
             term taxonomy ids), 'id=>parent' (returns an associative
             array with ids as keys, parent term IDs as values), 'names'
             (returns an array of term names), 'count' (returns the number
             of matching terms), 'id=>name' (returns an associative array
             with ids as keys, term names as values), or 'id=>slug'
             (returns an associative array with ids as keys, term slugs
             as values). Default 'all'.
     @type bool         count  Whether to return a term count (True) or array of term objects
                               (False). Will take precedence over `fields` if True.
                               Default False.
     @type str|array name   Optional. Name or array of names to return term(s) for.
                               Default empty.
     @type str|array slug   Optional. Slug or array of slugs to return term(s) for.
                               Default empty.
     @type int|array    term_taxonomy_id Optional. Term taxonomy ID, or array of term taxonomy IDs,
                                   to match when querying terms.
     @type bool   hierarchical Whether to include terms that have non-empty descendants (even
                                   if hide_empty is set to True). Default True.
     @type str    search       Search criteria to match terms. Will be SQL-formatted with
                                   wildcards before and after. Default empty.
     @type str    name__like   Retrieve terms with criteria by which a term is LIKE
                                   `name__like`. Default empty.
     @type str    description__like Retrieve terms where the description is LIKE
                                   `description__like`. Default empty.
     @type bool   pad_counts   Whether to pad the quantity of a term's children in the
                                   quantity of each term's "count" object variable.
                                   Default False.
     @type str    get          Whether to return terms regardless of ancestry or whether the
                                   terms are empty. Accepts 'all' or empty (disabled).
                                   Default empty.
     @type int    child_of     Term ID to retrieve child terms of. If multiple taxonomies
                                   are passed, child_of is ignored. Default 0.
     @type int|str parent       Parent term ID to retrieve direct-child terms of.
                                   Default empty.
     @type bool   childless    True to limit results to terms that have no children.
                               This parameter has no effect on non-hierarchical taxonomies.
                               Default False.
     @type str   cache_domain Unique cache key to be produced when this query is stored in
                                 an object cache. Default is 'core'.
     @type bool  update_term_meta_cache Whether to prime meta caches for matched terms. Default True.
     @type array meta_query Optional. Meta query clauses to limit retrieved
                            terms by. See `WP_Meta_Query`. Default empty.
     @type str meta_key   Limit terms to those matching a specific metadata key.
                               Can be used in conjunction with `meta_value`.
     @type str meta_value Limit terms to those matching a specific metadata value.
                                 Usually used in conjunction with `meta_key`.
    }
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    # SQL string used to perform database query.
    # @access public  @var string
    #self.request

    # Metadata query container.
    # @access public  @var object WP_Meta_Query
    self.meta_query = False

    # Metadata query clauses.
    # @access protected  @var array
    #self.meta_query_clauses

    # SQL query clauses.
    # @access protected  @var array
    self.sql_clauses = array(
      ('select' , ''),
      ('from'   , ''),
      ('where'  , array()),    # array(),
      ('orderby', ''),
      ('limits' , ''),
    )

    # Query vars set by the user.
    # @access public  @var array
    #self.query_vars

    # Default values for query vars.
    # @access public  @var array
    #self.query_var_defaults

    # List of terms located by the query.
    # @access public
    # @var array
    #self.terms

    self.query_var_defaults = array(
      ('taxonomy'              , None),
      ('object_ids'            , None),
      ('orderby'               , 'name'),
      ('order'                 , 'ASC'),
      ('hide_empty'            , True),
      ('include'               , array()),
      ('exclude'               , array()), #wp_parse_id_list(exclude=List)
      ('exclude_tree'          , array()), #wp_parse_id_list(exclude_tree)
      ('number'                , ''),
      ('offset'                , ''),
      ('fields'                , 'all'),
      ('count'                 , False),
      ('name'                  , ''),
      ('slug'                  , ''),
      ('term_taxonomy_id'      , ''),
      ('hierarchical'          , True),
      ('search'                , ''),
      ('name__like'            , ''),
      ('description__like'     , ''),
      ('pad_counts'            , False),
      ('get'                   , ''),
      ('child_of'              , 0),
      ('parent'                , ''),
      ('childless'             , False),
      ('cache_domain'          , 'core'),
      ('update_term_meta_cache', True),
      ('meta_query'            , ''),
      ('meta_key'              , ''),
      ('meta_value'            , ''),
      ('meta_type'             , ''),
      ('meta_compare'          , ''),
    )

    if query:    # if not Php.empty(locals(), 'query'):
      self.query( query )


  def parse_query(self, query = '' ):
    ''' Parse arguments passed to the term query with default query parameters
    @param string|array query WP_Term_Query arguments. See WP_Term_Query::__construct()
    '''
    if not query:    # if Php.empty(locals(), 'query'):
      query = self.query_vars

    print("WcTQ.parse_query: query=", query)
    taxonomies = Php.Array(query['taxonomy']
                          ) if Php.isset(query, 'taxonomy') else None
    print("WcTQ.parse_query: taxonomies=", taxonomies)

    # Filters the terms query default arguments.
    # Use {@see 'get_terms_args'} to filter the passed arguments.
    # @param array defaults   An array of default get_terms() arguments.
    # @param array taxonomies An array of taxonomies.
    self.query_var_defaults = WiPg.apply_filters( 'get_terms_defaults',
                                         self.query_var_defaults, taxonomies )

    query = WiFc.wp_parse_args( query, self.query_var_defaults )
    print("WcTQ.parse_query: query=", query)

    query['number'] = Php.absint( query['number'] )
    query['offset'] = Php.absint( query['offset'] )

    # 'parent' overrides 'child_of'.
    #must use Php.intval or int(''): invalid literal for int() with base 10: ''
    if 0 < Php.intval( query['parent'] ):
      query['child_of'] = False

    if 'all' == query['get']:
      query['childless'] = False
      query['child_of'] = 0
      query['hide_empty'] = 0
      query['hierarchical'] = False
      query['pad_counts'] = False

    query['taxonomy'] = taxonomies
    print("WcTQ.parse_query: taxonomies=", taxonomies)

    self.query_vars = query

    # Fires after term query vars have been parsed.
    # @param WP_Term_Query self Current instance of WP_Term_Query.
    WiPg.do_action( 'parse_term_query', self )


  def query(self, query):
    ''' Sets up the query for retrieving terms.
    @param string|array query Array or URL query string of parameters.
    @return array|int List of terms, or number of terms when 'count' is passed as a query var.
    '''
    print("WP_Term_Query.query(): self.query=")
    self.query_vars = WiFc.wp_parse_args( query )
    return self.get_terms()


  def get_terms(self):
    ''' Get terms, based on query_vars.
    @global wpdb wpdb WordPress database abstraction object.
    @return array
    '''
    import wp.i.taxonomy as WiTx
    wpdb = WpC.WB.Wj.wpdb  # global wpdb

    self.parse_query( self.query_vars )
    args = self.query_vars
    #pprint(self.query_vars)  # TypeError: unhashable type: 'instancemethod'
    # userdata is array, inspect.ismethod(A.__repr__) is True
    print('WP_Term_Query.get_terms: self.query_vars=', self.query_vars)

    # Set up meta_query so it's available to 'pre_get_terms'.
    self.meta_query = WcMQ.WP_Meta_Query()
    self.meta_query.parse_query_vars( args )

    # Fires before terms are retrieved.
    # @param WP_Term_Query self Current instance of WP_Term_Query.
    WiPg.do_action( 'pre_get_terms', self )

    taxonomies = args['taxonomy']
    print("WcTQ.get_terms: taxonomies=", taxonomies)

    # Save queries by not crawling the tree in the case of multiple taxes or a flat tax.
    has_hierarchical_tax = False
    if taxonomies:
      for _tax in taxonomies:
        if WiTx.is_taxonomy_hierarchical( _tax ):
          has_hierarchical_tax = True

    if not has_hierarchical_tax:
      args['hierarchical'] = False
      args['pad_counts'] = False

    # 'parent' overrides 'child_of'.
    if 0 < Php.intval( args['parent'] ):
      args['child_of'] = False

    if 'all' == args['get']:
      args['childless'] = False
      args['child_of'] = 0
      args['hide_empty'] = 0
      args['hierarchical'] = False
      args['pad_counts'] = False

    # Filters the terms query arguments.
    # @param array args       An array of get_terms() arguments.
    # @param array taxonomies An array of taxonomies.
    args = WiPg.apply_filters( 'get_terms_args', args, taxonomies )
    #pprint(args)  # TypeError: unhashable type: 'instancemethod'
    # userdata is array, inspect.ismethod(A.__repr__) is True
    print('WP_Term_Query.get_terms: args=', args)

    # Avoid the query if the queried parent/child_of term has no descendants.
    child_of = args['child_of']
    parent   = args['parent']

    if child_of:
      _parent = child_of
    elif parent:
      _parent = parent
    else:
      _parent = False

    if _parent:
      in_hierarchy = False
      for _tax in taxonomies:
        hierarchy = WiTx._get_term_hierarchy( _tax )

        if Php.isset(hierarchy, _parent):
          in_hierarchy = True

      if not in_hierarchy:
        return array()

    # 'term_order' is a legal sort order only when joining the relationship
    #    table.
    _orderby = self.query_vars['orderby']
    if 'term_order' == _orderby and Php.empty( self.query_vars, 'object_ids'):
      _orderby = 'term_id'
    orderby = self.parse_orderby( _orderby )

    if orderby:
      orderby = "ORDER BY "+ orderby

    order = self.parse_order( self.query_vars['order'] )

    if taxonomies:
      self.sql_clauses['where']['taxonomy'] = ("tt.taxonomy IN ('"
         + Php.implode("', '", Php.array_map(WiF.esc_sql, taxonomies)) + "')")

    exclude      = args['exclude']
    exclude_tree = args['exclude_tree']
    include      = args['include']

    inclusions = ''
    if include:    # if not Php.empty(locals(), 'include'):
      exclude = ''
      exclude_tree = ''
      inclusions = Php.implode( ',', WiFc.wp_parse_id_list( include ) )

    if inclusions:    # if not Php.empty(locals(), 'inclusions'):
      self.sql_clauses['where']['inclusions'] = ('t.term_id IN ( ' +
                                                 inclusions + ' )'  )

    exclusions = array() # Php.array_map( int, exclusions=List)
    if exclude_tree:     # if not Php.empty(locals(), 'exclude_tree'):
      exclude_tree = WiFc.wp_parse_id_list( exclude_tree )
      excluded_children = exclude_tree
      for extrunk in exclude_tree:
        excluded_children = Php.array_merge(
          excluded_children,
          Php.Array( get_terms( taxonomies[0], array(
            ('child_of'  , Php.intval( extrunk )),
            ('fields'    , 'ids'),
            ('hide_empty', 0),
          ) ))
        )
      exclusions = Php.array_merge( excluded_children, exclusions )

    if exclude:    # if not Php.empty(locals(), 'exclude'):
      exclusions = Php.array_merge( WiFc.wp_parse_id_list( exclude ), exclusions )

    # 'childless' terms are those without an entry in the flattened term hierarchy.
    childless = bool( args['childless'] )
    if childless:
      for _tax in taxonomies:
        term_hierarchy = WiTx._get_term_hierarchy( _tax )
        exclusions = Php.array_merge( Php.array_keys( term_hierarchy ), exclusions )

    if exclusions:    # if not Php.empty(locals(), 'exclusions'):
      exclusions = 't.term_id NOT IN (' + Php.implode( ',', Php.array_map( Php.intval, exclusions ) ) + ')'
    else:
      exclusions = ''

    # Filters the terms to exclude from the terms query.
    # @param string exclusions `NOT IN` clause of the terms query.
    # @param array  args       An array of terms query arguments.
    # @param array  taxonomies An array of taxonomies.
    exclusions = WiPg.apply_filters( 'list_terms_exclusions', exclusions, args, taxonomies )

    if exclusions:    # if not Php.empty(locals(), 'exclusions'):
      # Must do string manipulation here for backward compatibility with filter.
      self.sql_clauses['where']['exclusions'] = preg_replace( '/^\s*AND\s*/', '', exclusions )

    print("\n WcTQ.get_terms: args['name'] =", args['name'])

    print("WcTQ.get_terms: taxonomies=", taxonomies)
    if not Php.empty(args, 'name'):
      names = Php.Array( args['name'] )
      print("WcTQ.get_terms: names=", names, taxonomies)
      #foreach ( names as &_name ) {
      #modify list entries during for loop stackoverflow.com/questions/4081217
      for k,_name in names.items():  #use enumerate(names) if type(names)=list
        # `sanitize_term_field()` returns slashed data.
        #_name = Php.stripslashes( WiTx.sanitize_term_field(
        #                      'name', _name, 0, Php.reset(taxonomies), 'db'))
        names[k] = Php.stripslashes( WiTx.sanitize_term_field(
                               'name', _name, 0, Php.reset(taxonomies), 'db'))

      print("WcTQ.get_terms: names=", names, taxonomies)
      self.sql_clauses['where']['name'] = "t.name IN ('" + Php.implode( "', '",
                                   Php.array_map( WiF.esc_sql, names ) ) + "')"

    if not Php.empty(args, 'slug'):
      if Php.is_array( args['slug'] ):
        slug = Php.array_map( WiF.sanitize_title, args['slug'] )
        self.sql_clauses['where']['slug'] = "t.slug IN ('" + Php.implode(
                                            "', '", slug ) + "')"
      else:
        slug = WiF.sanitize_title( args['slug'] )
        self.sql_clauses['where']['slug'] = "t.slug = 'slug'"

    if not Php.empty(args, 'term_taxonomy_id'):
      if Php.is_array( args['term_taxonomy_id'] ):
        tt_ids = Php.implode( ',', Php.array_map( Php.intval,
                              args['term_taxonomy_id'] ) )
        self.sql_clauses['where']['term_taxonomy_id'] = \
                                    "tt.term_taxonomy_id IN ({})".format(tt_ids)
      else:
        self.sql_clauses['where']['term_taxonomy_id'] = wpdb.prepare(
          "tt.term_taxonomy_id = %s", args['term_taxonomy_id']) # PyMySQL %d->%s

    if not Php.empty(args, 'name__like'):
      self.sql_clauses['where']['name__like'] = wpdb.prepare( "t.name LIKE %s",
                               '%' + wpdb.esc_like( args['name__like'] ) + '%' )

    if not Php.empty(args, 'description__like'):
      self.sql_clauses['where']['description__like'] = wpdb.prepare(
                      "tt.description LIKE %s", '%' + wpdb.esc_like(
                                             args['description__like'] ) + '%' )

    if not Php.empty( args, 'object_ids' ):
      object_ids = args['object_ids']
      if not Php.is_array( object_ids ):
        object_ids = array( object_ids )
    
      object_ids = Php.implode( ', ', Php.array_map( Php.intval, object_ids ))
      self.sql_clauses['where']['object_ids'] = "tr.object_id IN ({})".format(
                                                object_ids)
    
    # When querying for object relationships, the 'count > 0' check
    # added by 'hide_empty' is superfluous.
    if not Php.empty( args['object_ids'] ):
      args['hide_empty'] = False

    if '' != parent:
      parent = Php.intval( parent )
      self.sql_clauses['where']['parent'] = "tt.parent = 'parent'"

    hierarchical = args['hierarchical']
    if 'count' == args['fields']:
      hierarchical = False
    if args['hide_empty'] and not hierarchical:
      self.sql_clauses['where']['count'] = 'tt.count > 0'

    number = args['number']
    offset = args['offset']

    # Don't limit the query results when we have to descend the family tree.
    if number and not hierarchical and not child_of and '' == parent:
      if offset:
        limits = 'LIMIT ' + offset + ',' + number
      else:
        limits = 'LIMIT ' + number
    else:
      limits = ''


    if not Php.empty(args, 'search'):
      self.sql_clauses['where']['search'] = self.get_search_sql( args['search'])

    # Meta query support.
    join = ''
    distinct = ''

    # Reparse meta_query query_vars, in case they were modified in a 'pre_get_terms' callback.
    self.meta_query.parse_query_vars( self.query_vars )
    mq_sql = self.meta_query.get_sql( 'term', 't', 'term_id' )
    meta_clauses = self.meta_query.get_clauses()

    if not Php.empty(args, 'meta_clauses'):
      join += mq_sql['join']
      self.sql_clauses['where']['meta_query'] = preg_replace( '/^\s*AND\s*/',
                                                          '', mq_sql['where'] )
      distinct += "DISTINCT"


    selects = array()
    #switch ( args['fields'] ) {
    #  case 'all':
    AF = args['fields']
    if AF in ('all', 'all_with_object_id', 'tt_ids', 'slugs'):
      selects = array( 't.*', 'tt.*' )
      if ( 'all_with_object_id' == args['fields'] and
            not Php.empty( args, 'object_ids' ) ):
        selects[None] = 'tr.object_id'

    #elif AF in ('ids', 'id=>parent'):
    elif  AF in ('ids', 'id=>parent', 'id.parent'):
      selects = array( 't.term_id', 'tt.parent', 'tt.count', 'tt.taxonomy' )
    elif AF == 'names':
      selects = array( 't.term_id', 'tt.parent', 'tt.count','t.name',
                       'tt.taxonomy')
    elif AF == 'count':
      orderby = ''
      order = ''
      selects = array( 'COUNT(*)', )
    #elif AF == 'id=>name':
    elif  AF in ('id=>name', 'id.name'):
      selects = array( 't.term_id', 't.name', 'tt.count', 'tt.taxonomy' )
    #elif AF == 'id=>slug':
    elif  AF in ('id=>slug', 'id.slug'):
      selects = array( 't.term_id', 't.slug', 'tt.count', 'tt.taxonomy' )

    _fields = args['fields']

    # Filters the fields to select in the terms query.
    # Field lists modified using this filter will only modify the term fields returned
    # by the function when the `fields` parameter set to 'count' or 'all'. In all other
    # cases, the term fields in the results array will be determined by the `fields`
    # parameter alone.
    # Use of this filter can result in unpredictable behavior, and is not recommended.
    # @param array selects    An array of fields to select for the terms query.
    # @param array args       An array of term query arguments.
    # @param array taxonomies An array of taxonomies.
    fields = Php.implode( ', ', WiPg.apply_filters( 'get_terms_fields',
                          selects, args, taxonomies ) )
    join += (" INNER JOIN "+ wpdb.term_taxonomy + 
             " AS tt ON t.term_id = tt.term_id")

    if not Php.empty( self.query_vars, 'object_ids' ):
      join += (" INNER JOIN {} AS tr ON tr.term_taxonomy_id = "
               "tt.term_taxonomy_id".format(wpdb.term_relationships))
    where = Php.implode( ' AND ', self.sql_clauses['where'] )

    # Filters the terms query SQL clauses.
    # @param array pieces     Terms query SQL clauses.
    # @param array taxonomies An array of taxonomies.
    # @param array args       An array of terms query arguments.
    pieces = ('fields', 'join', 'where','distinct','orderby','order','limits')
    clauses = WiPg.apply_filters( 'terms_clauses',
                             Php.compact(locals(), pieces ), taxonomies, args)

    #fields = isset( clauses[ 'fields' ] ) ? clauses[ 'fields' ] : ''
    fields  = clauses.get('fields'  , '')
    join    = clauses.get('join'    , '')
    where   = clauses.get('where'   , '')
    distinct= clauses.get('distinct', '')
    orderby = clauses.get('orderby' , '')
    order   = clauses.get('order'   , '')
    limits  = clauses.get('limits'  , '')

    if where:
      where = "WHERE "+ where

    self.sql_clauses['select']  = "SELECT {} {}".format(distinct, fields)
    self.sql_clauses['from']    = "FROM {} AS t {}".format(wpdb.terms, join)
    self.sql_clauses['orderby'] = orderby +" "+ order if orderby else ''
    self.sql_clauses['limits']  = limits

    #self.request = "{self.sql_clauses['select']} {self.sql_clauses['from']} {where} {self.sql_clauses['orderby']} {self.sql_clauses['limits']}"
    self.request = "{} {} {} {} {}".format(self.sql_clauses['select'], self.sql_clauses['from'], where, self.sql_clauses['orderby'], self.sql_clauses['limits'])

    # args can be anything. Only use the args defined in defaults to compute the key.
    key = Php.md5( Php.serialize( WiFc.wp_array_slice_assoc(
                   args, Php.array_keys( self.query_var_defaults ) ) )
                   + Php.serialize( taxonomies ) + self.request )
    last_changed = WiFc.wp_cache_get_last_changed( 'terms' )
    cache_key = "get_terms:{}:{}".format(key, last_changed)
    cache = WiCa.wp_cache_get( cache_key, 'terms' )
    if False != cache:
      if 'all' == _fields:
        cache = Php.array_map( WiTx.get_term, cache )

      self.terms = cache
      print("WcTQ get_terms 1 self.terms=", self.terms)
      return self.terms

    if 'count' == _fields:
      count = wpdb.get_var( self.request )
      WiCa.wp_cache_set( cache_key, count, 'terms' )
      return count

    terms = wpdb.get_results( self.request )
    print("WcTQ get_terms 2 terms=", terms)
    if 'all' == _fields or 'all_with_object_id' == _fields:
      WiTx.update_term_cache( terms )
    print("WcTQ get_terms 3 terms=", terms)

    # Prime termmeta cache.
    if args['update_term_meta_cache']:
      term_ids = WiFc.wp_list_pluck( terms, 'term_id' )
      WiTx.update_termmeta_cache( term_ids )

    
    print("WcTQ get_terms 4 terms=", terms)
    if not terms:   # if Php.empty(locals(), 'terms'):
      WiCa.wp_cache_add( cache_key, array(), 'terms', WpC.WB.Wj.DAY_IN_SECONDS )
      return array()

    print("WcTQ get_terms 5 terms=", terms)
    if child_of:
      for _tax in taxonomies:
        children = WiTx._get_term_hierarchy( _tax )
        if children:   # if not Php.empty(locals(), 'children'):
          terms = _get_term_children( child_of, terms, _tax )
          print("WcTQ get_terms 6 terms=", terms)

    # Update term counts to include children.
    if args['pad_counts'] and 'all' == _fields:
      for _tax in taxonomies:
        _pad_term_counts( terms, _tax )

    # Make sure we show empty categories that have children.
    if hierarchical and args['hide_empty'] and Php.is_array( terms ):
      for k, term in terms.items():
        Continue2 = False   #VT added to translate php: continue 2
        if not term.count:
          children = get_term_children( term.term_id, term.taxonomy )
          if Php.is_array( children ):
            for child_id in children:
              child = WiTx.get_term( child_id, term.taxonomy )
              if child.count:
                #continue 2
                Continue2 = True #VT added to translate php: continue 2
                continue         #VT added to translate php: continue 2
          # It really is empty.
          del terms[ k ]
        if Continue2:   #VT added to translate php: continue 2
          continue      #VT added to translate php: continue 2

    print("WcTQ get_terms 7 terms=", terms)

    # When querying for terms connected to objects, we may get
    # duplicate results. The duplicates should be preserved if
    # `fields` is 'all_with_object_id', but should otherwise be
    # removed.
    if not Php.empty( args, 'object_ids') and 'all_with_object_id' != _fields:
      _tt_ids = array()    # need to be sperate mutable obj
      _terms  = array()    # need to be sperate mutable obj
      for term in terms:
        if Php.isset( _tt_ids, getattr(term, 'term_id', None) ):
          continue
        _tt_ids[ term.term_id ] = 1
        _terms[None] = term
    
      terms = _terms


    _terms = array()    # array()
    #if 'id=>parent' == _fields:
    if _fields in ('id=>parent','id.parent'):
      for term in terms:
        _terms[ term.term_id ] = term.parent
    elif 'ids' == _fields:
      #for i,term in enumerate(terms):
      #  _terms[i] = int(term.term_id)
      for term in terms:
        _terms[None] = int(term.term_id)
    elif 'tt_ids' == _fields:
      for term in terms:
        _terms[None] = int(term.term_taxonomy_id)
    elif 'names' == _fields:
      #for i,term in enumerate(terms):
      #  _terms[i] = term.name
      for term in terms:
        _terms[None] = term.name
    elif 'slug' == _fields:
      for term in terms:
        _terms[None] = term.slug
    #elif 'id=>name' == _fields:
    elif _fields in ('id=>name','id.name'):
      for term in terms:
        _terms[ term.term_id ] = term.name
    #elif 'id=>slug' == _fields:
    elif _fields in ('id=>slug','id.slug'):
      for term in terms:
        _terms[ term.term_id ] = term.slug

    if _terms:   # if not Php.empty(locals(), '_terms'):
      terms = _terms

    # Hierarchical queries are not limited, so 'offset' and 'number' must be handled now.
    if hierarchical and number and Php.is_array( terms ):
      if offset >= len( terms ):
        terms = array()    # array()
      else:
        terms = Php.array_slice( terms, offset, number, True )

    WiCa.wp_cache_add( cache_key, terms, 'terms', WpC.WB.Wj.DAY_IN_SECONDS )

    if 'all' == _fields or 'all_with_object_id' == _fields:
      terms = Php.array_map( WiTx.get_term, terms )

    self.terms = terms
    return self.terms


  def parse_orderby(self, orderby_raw ):
    ''' Parse and sanitize 'orderby' keys passed to the term query.
    @global wpdb wpdb WordPress database abstraction object.
    @param string orderby_raw Alias for the field to order by.
    @return string|False Value to used in the ORDER clause. False otherwise.
    '''
    _orderby = Php.strtolower( orderby_raw )
    maybe_orderby_meta = False

    if   Php.in_array( _orderby,
                    array( 'term_id', 'name', 'slug', 'term_group' ), True ):
      orderby = "t.$_orderby"
    elif Php.in_array( _orderby, array( 'count', 'parent', 'taxonomy',
                                 'term_taxonomy_id', 'description' ), True ):
      orderby = "tt."+ _orderby
    elif 'term_order' == _orderby:
      orderby = 'tr.term_order'
    if 'count' == _orderby:
      orderby = 'tt.count'
    elif 'name' == _orderby:
      orderby = 't.name'
    elif 'slug' == _orderby:
      orderby = 't.slug'

    elif 'include' == _orderby and not Php.empty(self.query_vars, 'include'):
      include = Php.implode( ',',
                         WiFc.wp_parse_id_list( self.query_vars['include'] ))
      orderby = "FIELD( t.term_id, {} )".format(include)
    elif 'none' == _orderby:
      orderby = ''     # elif Php.empty(locals(), '_orderby') or ...
    elif not _orderby or 'id' == _orderby or 'term_id' == _orderby:
      orderby = 't.term_id'
    else:
      orderby = 't.name'

      # This may be a value of orderby related to meta.
      maybe_orderby_meta = True

    # Filters the ORDERBY clause of the terms query.
    # @param string orderby    `ORDERBY` clause of the terms query.
    # @param array  args       An array of terms query arguments.
    # @param array  taxonomies An array of taxonomies.
    orderby = WiPg.apply_filters( 'get_terms_orderby', orderby, self.query_vars, self.query_vars['taxonomy'] )

    # Run after the 'get_terms_orderby' filter for backward compatibility.
    if maybe_orderby_meta:
      maybe_orderby_meta = self.parse_orderby_meta( _orderby )
      if maybe_orderby_meta:
        orderby = maybe_orderby_meta

    return orderby


  def parse_orderby_meta(self, orderby_raw ):
    ''' Generate the ORDER BY clause for an 'orderby' param that is potentially related to a meta query.
    @param string orderby_raw Raw 'orderby' value passed to WP_Term_Query.
    @return string
    '''
    orderby = ''

    # Tell the meta query to generate its SQL, so we have access to table aliases.
    self.meta_query.get_sql( 'term', 't', 'term_id' )
    meta_clauses = self.meta_query.get_clauses()
    if not meta_clauses or not orderby_raw:
      return orderby

    allowed_keys = array()
    primary_meta_key = None
    primary_meta_query = Php.reset( meta_clauses )
    if not Php.empty(primary_meta_query, 'key'):
      primary_meta_key = primary_meta_query['key']
      allowed_keys.append(primary_meta_key)

    allowed_keys.append('meta_value')
    allowed_keys.append('meta_value_num')
    allowed_keys = Php.array_merge( allowed_keys, Php.array_keys( meta_clauses ) )

    if not Php.in_array( orderby_raw, allowed_keys, True ):
      return orderby

    #switch( orderby_raw ) {
    #  case primary_meta_key:
    #  case 'meta_value':
    if orderby_raw in (primary_meta_key, 'meta_value'):
      if not Php.empty(primary_meta_query, 'type'):
        orderby = "CAST({}.meta_value AS {})".format(
                    primary_meta_query['alias'], primary_meta_query['cast'])
      else:
        orderby = primary_meta_query['alias'] +".meta_value"

    elif orderby_raw == 'meta_value_num':
      orderby = primary_meta_query['alias'] +".meta_value+0"

    else:
      if orderby_raw in meta_clauses:
        # orderby corresponds to a meta_query clause.
        meta_clause = meta_clauses[ orderby_raw ]
        orderby = "CAST({}.meta_value AS {})".format(
                   meta_clause['alias'], meta_clause['cast'])

    return orderby


  def parse_order(self, order ):
    ''' Parse an 'order' query variable and cast it to ASC or DESC as necessary
    @param string order The 'order' query variable.
    @return string The sanitized 'order' query variable.
    '''
    #if not Php.is_string( order ) or Php.empty(locals(),'order')
    if  not Php.is_string( order ) or not order:
      return 'DESC'

    if 'ASC' == order.upper():
      return 'ASC'
    else:
      return 'DESC'


  def get_search_sql(self, string ):
    ''' Used internally to generate a SQL string related to the 'search' parameter.
    @access protected
    @global wpdb wpdb WordPress database abstraction object.
    @param string string
    @return string
    '''
    global wpdb

    like = '%' + wpdb.esc_like( string ) + '%'

    return wpdb.prepare( '((t.name LIKE %s) OR (t.slug LIKE %s))', like, like )


'''  Test
import wp.i.cls.term_query as WcTQ; term_query = WcTQ.WP_Term_Query()
args = Php.array(('name', '濡備粖涔犱互涓哄父鐨?), ('hide_empty', False), ('taxonomy', Php.array((0, 'post_tag'))))
terms = term_query.query( args )
'''

# Fixed all &value pass by reference
from collections import OrderedDict as ODict
import wp.conf       as WpC
import wp.i.format   as WiF
import wp.i.meta     as WiM
import wp.i.plugin   as WiPg
import pyx.php       as Php
array, ODict = Php.array, Php.ODict

''' Meta API: WP_Meta_Query class
@package WordPress  @subpackage Meta
'''

class WP_Meta_Query(Php.stdClass):
  ''' Core class used to implement meta queries for the Meta API.
  Used for generating SQL clauses that filter a primary query according to metadata keys and values.
  WP_Meta_Query is a helper that allows primary query classes, such as WP_Query and WP_User_Query,
  to filter their results by object metadata, by generating `JOIN` and `WHERE` subclauses to be attached
  to the primary SQL query string.
  '''
  def __init__(self, meta_query = False ):
    ''' Constructor.
    @param array meta_query {
      Array of meta query clauses. When first-order clauses or sub-clauses use
      strings as their array keys, they may be referenced in the 'orderby'
      parameter of the parent query.
      @type str relation Optional. The MySQL keyword used to join the clauses
                         of the query. Accepts 'AND', or 'OR'. Default 'AND'.
      @type array {
        Optional. An array of first-order clause parameters, or another
        fully-formed meta query.
        @type str key     Meta key to filter by.
        @type str value   Meta value to filter by.
        @type str compare MySQL operator used for comparing the value. Accepts
                           '=', '!=', '>', '>=', '<', '<=', 'LIKE','NOT LIKE',
                           'IN', 'NOT IN', 'BETWEEN', 'NOT BETWEEN', 'REGEXP',
                           'NOT REGEXP', 'RLIKE', 'EXISTS' or 'NOT EXISTS'.
                           Default is 'IN' when `value`=array, '=' otherwise.
        @type str type MySQL data type that the meta_value column will be CAST
              to for comparisons. Accepts 'NUMERIC', 'BINARY', 'CHAR', 'DATE',
              'DATETIME', 'DECIMAL', 'SIGNED', 'TIME', or 'UNSIGNED'.
              Default is 'CHAR'.
    } }
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    # Array of metadata queries.
    # See WP_Meta_Query::__init__() for information on meta query arguments.
    # @access public  @var array
    self.queries = array()

    # The relation between the queries. Can be one of 'AND' or 'OR'.
    # @access public  @var string
    "self.relation"

    # Database table to query for the metadata.
    # @access public  @var string
    "self.meta_table"

    # Column in meta_table that represents the ID of the object the metadata belongs to.
    # @access public  @var string
    "self.meta_id_column"

    # Database table that where the metadata's objects are stored (eg self.wpdb.users).
    # @access public  @var string
    "self.primary_table"

    # Column in primary_table that represents the ID of the object.
    # @access public  @var string
    "self.primary_id_column"

    # A flat list of table aliases used in JOIN clauses.
    # @access protected  @var array
    self.table_aliases = array()

    # A flat list of clauses, keyed by clause 'name'.
    # @access protected  @var array
    self.clauses = array()

    # Whether the query contains any OR relations.
    # @access protected  @var bool
    "self.has_or_relation = False"

    if not meta_query:
      return

    #if 'relation' in meta_query and strtoupper( meta_query['relation'] ) == 'OR':
    if (Php.isset(meta_query , 'relation') and
        Php.strtoupper(meta_query['relation']) == 'OR'):
      self.relation = 'OR'
    else:
      self.relation = 'AND'

    self.queries = self.sanitize_query( meta_query )


  def sanitize_query(self, queries ):
    ''' Ensure the 'meta_query' argument passed to the class constructor is well-formed.
    Eliminates empty items and ensures that a 'relation' is set.
    @param array queries Array of query clauses.
    @return array Sanitized array of query clauses.
    '''
    clean_queries = array()

    if not  Php.is_array( queries ):
      return clean_queries

    for key, query in queries.items():
      if 'relation' == key:
        relation = query

      elif not Php.is_array( query ):
        continue

      # First-order clause.
      elif self.is_first_order_clause( query ):
        #if 'value' in query and array() == query['value']:
        if Php.isset(query , 'value') and array() == query['value']:
          unset( query['value'] )

        clean_queries[ key ] = query

      # Otherwise, it's a nested query, so we recurse.
      else:
        cleaned_query = self.sanitize_query( query )

        if cleaned_query:    # if not Php.empty(locals(), 'cleaned_query'):
          clean_queries[ key ] = cleaned_query

    if not clean_queries:    # if Php.empty(locals(), 'clean_queries'):
      return clean_queries

    # Sanitize the 'relation' key provided in the query.
    if Php.isset(locals(), 'relation') and 'OR' == relation.upper():
      clean_queries['relation'] = 'OR'
      self.has_or_relation = True

    # If there is only a single clause, call the relation 'OR'.
    # This value will not actually be used to join clauses, but it
    # simplifies the logic around combining key-only queries.
    elif 1 == len( clean_queries ):
      clean_queries['relation'] = 'OR'

    # Default to AND.
    else:
      clean_queries['relation'] = 'AND'

    return clean_queries


  def is_first_order_clause(self, query ):
    ''' Determine whether a query clause is first-order.
    A first-order meta query clause is one that has either a 'key' or
    a 'value' array key.
    @param array query Meta query arguments.
    @return bool Whether the query clause is a first-order clause.
    '''
    return Php.isset(query, 'key') or Php.isset(query, 'value')


  def parse_query_vars(self, qv ):
    ''' Constructs a meta query based on 'meta_*' query vars
    @param array qv The query variables
    '''
    meta_query = array()    # ODict()    # array()

    # For orderby=meta_value to work correctly, simple query needs to be
    # first (so that its table join is against an unaliased meta table) and
    # needs to be its own clause (so it doesn't interfere with the logic of
    # the rest of the meta_query).
    primary_meta_query = array()    # ODict()    # array()
    for key in ( 'key', 'compare', 'type' ):
      if not Php.empty(qv, "meta_"+ key):
        primary_meta_query[ key ] = qv[ "meta_"+ key ]

    # WP_Query sets 'meta_value' = '' by default.
    if Php.isset(qv, 'meta_value') and '' != qv['meta_value'] and ( not Php.is_array( qv['meta_value'] ) or qv['meta_value'] ):
      primary_meta_query['value'] = qv['meta_value']

    existing_meta_query = qv['meta_query'] if (Php.isset(qv, 'meta_query') and
                   Php.is_array( qv['meta_query'] )) else array()    # ODict()    # array()

    #if not Php.empty(locals(), 'primary_meta_query') and existing_meta_query:
    if primary_meta_query and existing_meta_query:
      meta_query = array(      # Supports array( ('a',11), 22, 33, (2,22) )
        ('relation', 'AND'),
        primary_meta_query,
        existing_meta_query,
      )
    elif primary_meta_query:   #not Php.empty(locals(),'primary_meta_query'):
      meta_query = array(      # Supports array( ('a',11), 22, 33, (2,22) )
          primary_meta_query
      )
    elif existing_meta_query:  #not Php.empty(locals(),'existing_meta_query'):
      meta_query = existing_meta_query

    self.__init__( meta_query )


  def get_cast_for_type(self, Type = '' ):
    ''' Return the appropriate alias for the given meta type if applicable.
    @param string Type MySQL type to cast meta_value.
    @return string MySQL type.
    '''
    if not Type:    #if Php.empty(locals(),'Type'):
      return 'CHAR'

    meta_type = Type.upper()

    if not Php.preg_match( '/^(?:BINARY|CHAR|DATE|DATETIME|SIGNED|UNSIGNED|TIME|NUMERIC(?:\(\d+(?:,\s?\d+)?\))?|DECIMAL(?:\(\d+(?:,\s?\d+)?\))?)$/', meta_type ):
      return 'CHAR'

    if 'NUMERIC' == meta_type:
      meta_type = 'SIGNED'

    return meta_type


  def get_sql(self, Type, primary_table, primary_id_column, context = None ):
    ''' Generates SQL clauses to be appended to a main query.
    @param string Type              Type of meta, eg 'user', 'post'.
    @param string primary_table     Database table where the object being filtered is stored (eg wp_users).
    @param string primary_id_column ID column for the filtered object in primary_table.
    @param object context           Optional. The main query object.
    @return False|array {
        Array containing JOIN and WHERE SQL clauses to append to the main query.
        @type string join  SQL fragment to append to the main JOIN clause.
        @type string where SQL fragment to append to the main WHERE clause.
    } '''
    meta_table = WiM._get_meta_table( Type )
    if not meta_table:
      return False

    self.table_aliases = array()

    self.meta_table     = meta_table
    self.meta_id_column = WiF.sanitize_key( Type + '_id' )

    self.primary_table     = primary_table
    self.primary_id_column = primary_id_column

    sql = self.get_sql_clauses()

    # If any JOINs are LEFT JOINs (as in the case of NOT EXISTS), then all JOINs should
    # be LEFT. Otherwise posts with no metadata will be excluded from results.
    #if False !== strpos( sql['join'], 'LEFT JOIN' ):
    if 'LEFT JOIN' in sql['join']:
      sql['join'] = Php.str_replace( 'INNER JOIN', 'LEFT JOIN', sql['join'])

    # Filters the meta query's generated SQL.
    # @param array  clauses           Array containing the query's JOIN and WHERE clauses.
    # @param array  queries           Array of meta queries.
    # @param string Type              Type of meta.
    # @param string primary_table     Primary table.
    # @param string primary_id_column Primary column ID.
    # @param object context           The main query object.
    return WiPg.apply_filters_ref_array( 'get_meta_sql', array( sql, self.queries, Type, primary_table, primary_id_column, context ) )


  def get_sql_clauses(self):
    ''' Generate SQL clauses to be appended to a main query.
    Called by the public WP_Meta_Query::get_sql(), this method is abstracted
    out to maintain parity with the other Query classes.
    @return array {
        Array containing JOIN and WHERE SQL clauses to append to the main query.
        @type string join  SQL fragment to append to the main JOIN clause.
        @type string where SQL fragment to append to the main WHERE clause.
    } '''
    # queries are passed by reference to get_sql_for_query() for recursion.
    # To keep self.queries unaltered, pass a copy.
    queries = self.queries
    sql = self.get_sql_for_query( queries )

    if not Php.empty(sql, 'where'):
      sql['where'] = ' AND ' + sql['where']

    return sql


  #def get_sql_for_query( &query, depth = 0 ):
  # php pass &query by reference can be translated to py without the ref,
  #    since query, key, and clause below are not modified below:
  #       for key, clause in query.items():
  def get_sql_for_query(self, query, depth = 0 ):
    ''' Generate SQL clauses for a single query array.
    If nested subqueries are found, this method recurses the tree to
    produce the properly nested SQL.
    @param array query Query to parse, passed by reference.
    @param int   depth Optional. Number of tree levels deep we currently are.
                        Used to calculate indentation. Default 0.
    @return array {
        Array containing JOIN and WHERE SQL clauses to append to a single query array.
        @type string join  SQL fragment to append to the main JOIN clause.
        @type string where SQL fragment to append to the main WHERE clause.
    } '''
    sql_chunks = array(
      ('join' , array()),
      ('where', array()),
    )

    sql = array(
      ('join' , ''),
      ('where', ''),
    )

    indent = ''
    #for ( i = 0; i < depth; i++ ) {
    for i in range(depth):
      indent += "  "

    for key, clause in query.items():
      if 'relation' == key:
        relation = query['relation']
      elif Php.is_array( clause ):

        # This is a first-order clause.
        if self.is_first_order_clause( clause ):
          clause_sql = self.get_sql_for_clause( clause, query, key )

          where_count = len( clause_sql['where'] )
          if not where_count:
            sql_chunks['where'][None] = ''
          elif 1 is where_count:
            sql_chunks['where'][None] = clause_sql['where'][0]
          else:
            sql_chunks['where'][None] = '( ' + Php.implode( ' AND ', clause_sql['where'] ) + ' )'

          sql_chunks['join'] = Php.array_merge( sql_chunks['join'], clause_sql['join'] )
        # This is a subquery, so we recurse.
        else:
          clause_sql = self.get_sql_for_query( clause, depth + 1 )

          sql_chunks['where'][None] = clause_sql['where']
          sql_chunks['join' ][None] = clause_sql['join' ]

    # Filter to remove empties.
    sql_chunks['join']  = Php.array_filter( sql_chunks['join'] )
    sql_chunks['where'] = Php.array_filter( sql_chunks['where'] )

    if Php.empty(locals(), 'relation'):
      relation = 'AND'

    # Filter duplicate JOIN clauses and combine into a single string.
    if not Php.empty(sql_chunks, 'join'):
      sql['join'] = Php.implode( ' ', Php.array_unique( sql_chunks['join'] ) )

    # Generate a single WHERE clause with proper brackets and indentation.
    if not Php.empty(sql_chunks, 'where'):
      sql['where'] = '( ' + "\n  " + indent + Php.implode( ' ' + "\n  " + indent + relation + ' ' + "\n  " + indent, sql_chunks['where'] ) + "\n" + indent + ')'

    return sql

  #def get_sql_for_clause( &clause, parent_query, clause_key = '' ):
  # since clause passed by ref, need to return clause
  def get_sql_for_clause(self, clause, parent_query, clause_key = '' ):
    ''' Generate SQL JOIN and WHERE clauses for a first-order query clause.
    "First-order" means that it's an array with a 'key' or 'value'.
    @global wpdb wpdb WordPress database abstraction object.
    @param array  clause       Query clause, passed by reference.
    @param array  parent_query Parent query array.
    @param string clause_key   Optional. The array key used to name the clause
                               in the original `meta_query` parameters. If not
                               provided, a key will be generated automatically
    @return array {
      Array containing JOIN & WHERE SQL clauses to append to a 1st-order query
      @type string join  SQL fragment to append to the main JOIN clause.
      @type string where SQL fragment to append to the main WHERE clause.
    }
    @return array clause    since clause passed by ref, need to return clause
    '''
    wpdb = WpC.WB.Wj.wpdb  # global wpdb

    sql_chunks = array(
      ('where', array()),
      ('join' , array()),
    )

    if Php.isset(clause, 'compare'):
      clause['compare'] = clause['compare'].upper()
    else:
      clause['compare'] = 'IN' if (Php.isset(clause, 'value') and
                          Php.is_array( clause['value'] )) else '='

    if ( not Php.in_array( clause['compare'], array(
      '=', '!=', '>', '>=', '<', '<=',
      'LIKE', 'NOT LIKE',
      'IN', 'NOT IN',
      'BETWEEN', 'NOT BETWEEN',
      'EXISTS', 'NOT EXISTS',
      'REGEXP', 'NOT REGEXP', 'RLIKE'
    ) ) ):
      clause['compare'] = '='

    meta_compare = clause['compare']

    # First build the JOIN clause, if one is required.
    join = ''

    # We prefer to avoid joins if possible. Look for an existing join compatible with this clause.
    alias = self.find_compatible_table_alias( clause, parent_query )
    if False is alias:
      i = len( self.table_aliases )
      alias = 'mt' + i if i else self.meta_table

      # JOIN clauses for NOT EXISTS have their own syntax.
      if 'NOT EXISTS' == meta_compare:
        join += " LEFT JOIN self.meta_table"
        join += " AS "+ alias if i else ''
        join += wpdb.prepare( " ON (self.primary_table.self.primary_id_column = {} AND {} = %s )".format(alias.self.meta_id_column, alias.meta_key), clause['key'] )

      # All other JOIN clauses.
      else:
        join += " INNER JOIN self.meta_table"
        join += " AS alias" if i else ''
        join += " ON ( self.primary_table.self.primary_id_column = {} )".format(alias.self.meta_id_column)

      self.table_aliases[None] = alias
      sql_chunks['join'][None] = join

    # Save the alias to this clause, for future siblings to find.
    clause['alias'] = alias

    # Determine the data type.
    _meta_type = clause['type'] if Php.isset(clause, 'type') else ''
    meta_type  = self.get_cast_for_type( _meta_type )
    clause['cast'] = meta_type

    # Fallback for clause keys is the table alias. Key must be a string.
    if is_int( clause_key ) or not clause_key:
      clause_key = clause['alias']

    # Ensure unique clause keys, so none are overwritten.
    iterator = 1
    clause_key_base = clause_key
    while Php.isset(self.clauses, clause_key):
      clause_key = clause_key_base + '-' + iterator
      iterator += 1

    # Store the clause in our flat array.
    #self.clauses[ clause_key ] =& clause
    # =& is assignment by reference, "means that both vars pointing at the
    #    same data, and nothing is copied anywhere"
    self.clauses[ clause_key ] = clause  # py array or {} are mutable same obj


    # Next, build the WHERE clause.

    # meta_key.
    if 'key' in clause:
      if 'NOT EXISTS' == meta_compare:
        sql_chunks['where'][None] = alias + '.' + self.meta_id_column + ' IS NULL'
      else:
        sql_chunks['where'][None] = wpdb.prepare( "alias.meta_key = %s", trim( clause['key'] ) )

    # meta_value.
    if 'value' in clause:
      meta_value = clause['value']

      if meta_compare in ( 'IN', 'NOT IN', 'BETWEEN', 'NOT BETWEEN' ):
        if not Php.is_array( meta_value ):
          meta_value = preg_split( '/[,\s]+/', meta_value )
      else:
        meta_value = trim( meta_value )

      #switch ( meta_compare ) {
      if meta_compare in ('IN', 'NOT IN'):
        meta_compare_string = '(' + substr( str_repeat( ',%s', len( meta_value ) ), 1 ) + ')'
        where = wpdb.prepare( meta_compare_string, meta_value )

      elif meta_compare in ('BETWEEN', 'NOT BETWEEN'):
        meta_value = Php.array_slice( meta_value, 0, 2 )
        where = wpdb.prepare( '%s AND %s', meta_value )

      elif meta_compare in ('LIKE', 'NOT LIKE'):
        meta_value = '%' + wpdb.esc_like( meta_value ) + '%'
        where = wpdb.prepare( '%s', meta_value )

      # EXISTS with a value is interpreted as '='.
      elif meta_compare == 'EXISTS' :
        meta_compare = '='
        where = wpdb.prepare( '%s', meta_value )

      # 'value' is ignored for NOT EXISTS.
      elif meta_compare == 'NOT EXISTS' :
        where = ''

      else:
        where = wpdb.prepare( '%s', meta_value )


      if where:
        if 'CHAR' == meta_type:
          sql_chunks['where'][None] = "{} {} {}".format(alias.meta_value, meta_compare, where)
        else:
          sql_chunks['where'][None] = "CAST({} AS {}) {} {}".format(alias.meta_value, meta_type, meta_compare, where)

    # Multiple WHERE clauses (for meta_key and meta_value) should
    # be joined in parentheses.
    if 1 < len( sql_chunks['where'] ):
      sql_chunks['where'] = array( '( ' + Php.implode( ' AND ', sql_chunks['where'] ) + ' )' )

    #return sql_chunks
    return sql_chunks, clause  #since clause passed by ref, need to return


  def get_clauses(self):
    ''' Get a flattened list of sanitized meta clauses.
    This array should be used for clause lookup, as when the table alias and CAST type must be determined for
    a value of 'orderby' corresponding to a meta clause.
    @return array Meta clauses.
    '''
    return self.clauses

    ''' Identify an existing table alias that is compatible with the current
    query clause.
    We avoid unnecessary table joins by allowing each clause to look for
    an existing table alias that is compatible with the query that it
    needs to perform.
    An existing alias is compatible if (a) it is a sibling of `clause`
    (ie, it's under the scope of the same relation), and (b) the combination
    of operator and relation between the clauses allows for a shared table join.
    In the case of WP_Meta_Query, this only applies to 'IN' clauses that are
    connected by the relation 'OR'.
    @param  array       clause       Query clause.
    @param  array       parent_query Parent query of clause.
    @return string|bool Table alias if found, otherwise False.
    '''
  def find_compatible_table_alias(self, clause, parent_query ):
    alias = False

    for sibling in parent_query:
      # If the sibling has no alias yet, there's nothing to check.
      if Php.empty(sibling, 'alias'):
        continue

      # We're only interested in siblings that are first-order clauses.
      if not Php.is_array( sibling ) or not self.is_first_order_clause( sibling ):
        continue

      compatible_compares = array()

      # Clauses connected by OR can share joins as long as they have "positive" operators.
      if 'OR' == parent_query['relation']:
        compatible_compares = array( '=', 'IN', 'BETWEEN', 'LIKE', 'REGEXP', 'RLIKE', '>', '>=', '<', '<=' )

      # Clauses joined by AND with "negative" operators share a join only if they also share a key.
      elif (Php.isset(sibling, 'key') and Php.isset(clause, 'key') and
            sibling['key'] == clause['key']):
        compatible_compares = array( '!=', 'NOT IN', 'NOT LIKE' )

      clause_compare  = clause['compare'].upper()
      sibling_compare = sibling['compare'].upper()
      if (Php.in_array( clause_compare,  compatible_compares ) and
          Php.in_array( sibling_compare, compatible_compares )):
        alias = sibling['alias']
        break

    # Filters the table alias identified as compatible with the current clause.
    # @param string|bool alias        Table alias, or False if none was found.
    # @param array       clause       First-order query clause.
    # @param array       parent_query Parent of clause.
    # @param object      self         WP_Meta_Query object.
    return WiPg.apply_filters( 'meta_query_find_compatible_table_alias', alias, clause, parent_query, self ) 


  def has_or_relation(self):
    ''' Checks whether the current query has any OR relations.
    In some cases, the presence of an OR relation somewhere in the query will require
    the use of a `DISTINCT` or `GROUP BY` keyword in the `SELECT` clause. The current
    method can be used in these cases to determine whether such a clause is necessary.
    @return bool True if the query contains any `OR` relations, otherwise False.
    '''
    return self.has_or_relation

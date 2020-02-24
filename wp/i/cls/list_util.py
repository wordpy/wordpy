import pyx.php       as Php
array = Php.array

# WordPress List utility class
# @package WordPress

class WP_List_Util(Php.stdClass):
  ''' List utility.
  Utility class to handle operations on an array of objects.
  '''
  def __init__( self, Input ):
    ''' Constructor.
    Sets the input array.
    @param array input Array to perform operations on.
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    # The input array.
    # @since 4.7.0
    # @access private
    # @var array
    #self.input = array()

    # The output array.
    # @since 4.7.0
    # @access private
    # @var array
    #self.output = array()

    # Temporary arguments for sorting.
    # @since 4.7.0
    # @access private
    # @var array
    self.orderby = array()

    #self.output= self.input = Input
    self.output = Php.clone(Input) # VT Added to prevent change of mutable array
    self.input  = Php.clone(Input) # VT Added to prevent change of mutable array


  def get_input(self):
    ''' Returns the original input array.
    @access public
    @return array The input array.
    '''
    return self.input

  def get_output(self):
    ''' Returns the output array.
    @access public
    @return array The output array.
    '''
    return self.output

  def filter( self, args = array(), operator = 'AND' ):
    ''' Filters the list, based on a set of key, value arguments.
    @param array  args     Optional. An array of key, value arguments to match
                            against each object. Default empty array.
    @param string operator Optional. The logical operation to perform. 'AND' means
                            all elements from the array must match. 'OR' means only
                            one element needs to match. 'NOT' means no elements may
                            match. Default 'AND'.
    @return array Array of found values.
    '''
    if Php.empty( locals(), 'args' ):
      return self.output

    operator = Php.strtoupper( operator )

    if not Php.in_array( operator, array( 'AND', 'OR', 'NOT' ), True ):
      return array()

    count = Php.count( args )
    filtered = array()

    for key, obj in self.output.items():
      #print('WP_List_Util.filter key, obj=', key, obj)
      to_match = Php.Array( obj )

      matched = 0
      for m_key, m_value in args.items():
        #print('WP_List_Util.filter m_key, m_value=', m_key, m_value)
        if (Php.array_key_exists( m_key, to_match ) and
            m_value == to_match[ m_key ] ):
          matched += 1
          #print('WP_List_Util.filter matched=', matched)

      if (( 'AND' == operator and matched == count ) or
          ( 'OR'  == operator and matched > 0  ) or
          ( 'NOT' == operator and 0 == matched ) ):
        filtered[key] = obj
        #print('WP_List_Util.filter filtered[{}]= {}'.format(key, obj))

    self.output = filtered

    return self.output


  def pluck( self, field, index_key = None ):
    ''' Plucks a certain field out of each object in the list.
    This has the same functionality and prototype of
    array_column() (PHP 5.5) but also supports objects.
    @param int|str field     Field from the object to place instead of the
                             entire object
    @param int|str index_key Optional. Field from the object to use as keys
                             for the new array. Default None.
    @return array Array of found values. If `index_key` is set, an array of
                  found values with keys corresponding to `index_key`. If
                  `index_key` is None, array keys from the original
                  `list` will be preserved in the results.
    '''
    if not index_key:
      # This is simple. Could at some point wrap array_column()
      # if we knew we had an array of arrays.
      for key, value in self.output.items():
        print('pluck', field, key, value)
        if Php.is_object( value ):
          #self.output[ $key ] = $value->$field
          #Php returns None if no attr found, rather than raise error
          self.output[ key ] = getattr(value, field, None)
        else:
          try:    self.output[ key ] = value[ field ]
          except: self.output[ key ] = None      # Php> false[1]  #Out=> NULL
      return self.output

    # When index_key is not set for a particular item, push the value
    # to the end of the stack. This is how array_column() behaves.
    newlist = array()
    for value in self.output:
      if Php.is_object( value ):
        #if isset( $value->$index_key ):
        if Php.isset( value, index_key ):
          #$newlist[ $value->$index_key ] = $value->$field
          newlist[ getattr(value, index_key) ] = getattr(value, field)
        else:
          #$newlist[] = $value->$field
          newlist[None] = getattr(value, field)
      else:
        if Php.isset( value, index_key ):
          newlist[ value[ index_key ] ] = value[ field ]
        else:
          newlist[None] = value[ field ]

    self.output = newlist

    return self.output


  def sort( self, orderby = array(), order = 'ASC', preserve_keys = False ):
    ''' Sorts the list, based on one or more orderby arguments.
    @param str|array orderby Optional. Either the field name to order by or an
                           array of multiple orderby fields as orderby, order.
    @param str       order   Optional. Either 'ASC' or 'DESC'. Only used if
                                 orderby is a string.
    @param bool preserve_keys Optional. Whether to preserve keys.Default False
    @return array The sorted array.
    '''
    if Php.empty( locals(), 'orderby' ):
      return self.output

    if is_string( orderby ):
      orderby = array( (orderby, order) )

    for field, direction in orderby.items():
      orderby[ field ] = ( 'DESC' if 'DESC' == Php.strtoupper( direction )
                                  else 'ASC' )

    self.orderby = orderby

    if preserve_keys:
      #uasort( self.output, array( self, 'sort_callback' ) )
      Php.uasort( self.output, self.sort_callback )
    else:
      #usort( self.output, array( self, 'sort_callback' ) )
      Php.usort(  self.output, self.sort_callback )

    self.orderby = array()

    return self.output


  def sort_callback( self, a, b ):
    ''' Callback to sort the list by specific fields.
    @access private
    @see WP_List_Util::sort()
    @param object|array a One object to compare.
    @param object|array b The other object to compare.
    @return int 0 if both objects equal.
               -1 if second object should come first, 1 otherwise.
    '''
    if Php.empty( self, 'orderby' ):
      return 0

    a = Php.Array( a )
    b = Php.Array( b )

    for field, direction in self.orderby.items():
      if not Php.isset( a, field ) or not Php.isset( b, field ):
        continue
      if a[ field ] == b[ field ]:
        continue

      #results = 'DESC' === direction ? array( 1, -1 ) : array( -1, 1 )
      results  = array( 1, -1 ) if 'DESC' == direction else array( -1, 1 )

      if Php.is_numeric( a[ field ] ) and Php.is_numeric( b[ field ] ):
        #return ( a[ field ] < b[ field ] ) ? results[0] : results[1]
        return results[0] if ( a[ field ] < b[ field ] ) else results[1]

      #return 0 > strcmp( a[ field ], b[ field ] ) ? results[0] : results[1]
      return results[0] if ( 0 > Php.strcmp( a[ field ], b[ field ] )
                        ) else results[1]

    return 0



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



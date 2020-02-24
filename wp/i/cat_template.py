import wp.conf        as WpC
import wp.i.cache     as WiCa
import wp.i.func      as WiFc
import wp.i.taxonomy  as WiTx
import pyx.php        as Php
array = Php.array

# Taxonomy API: Core category-specific template tags
# @package WordPress
# @subpackage Template
# @since 1.2.0


def get_category_link( category ):
  ''' Retrieve category link URL.
  @see get_term_link()
  @param int|object category Category ID or object.
  @return string Link on success, empty string if category does not exist.
  '''
  if not Php.is_object( category ):
    category = int( category )

  category = get_term_link( category, 'category' )

  if WpC.WB.Wj.is_wp_error( category ):
    return ''

  return category


def get_category_parents( Id, link = False, separator = '/', nicename = False,
                          visited = array() ):
  ''' Retrieve category parents with separator.
  @param int Id Category ID.
  @param bool link Optional, default is False. Whether to format with link.
  @param string separator Optional, default is '/'. How to separate categories.
  @param bool nicename Optional, default is False. Whether to use nice name for display.
  @param array visited Optional. Already linked to categories to prevent duplicates.
  @return string|WP_Error A list of category parents on success, WP_Error on failure.
  '''
  chain = ''
  parent = get_term( Id, 'category' )
  if WpC.WB.Wj.is_wp_error( parent ):
    return parent

  if nicename:
    name = parent.slug
  else:
    name = parent.name

  if parent.parent and ( parent.parent != parent.term_id ) and not in_array( parent.parent, visited ):
    visited.append( parent.parent )
    chain += get_category_parents( parent.parent, link, separator, nicename, visited )

  if link:
    chain += '<a href="' + esc_url( get_category_link( parent.term_id ) ) + '">'+ name +'</a>' + separator
  else:
    chain += name.separator
  return chain


def get_the_category( Id = False ):
  ''' Retrieve post categories.
  This tag may be used outside The Loop by passing a post id as the parameter.
  Note: This function only returns results from the default "category" taxonomy.
  For custom taxonomies use get_the_terms().
  @param int Id Optional, default to current post ID. The post ID.
  @return array Array of WP_Term objects, one for each category assigned to the post.
  '''
  categories = get_the_terms( Id, 'category' )
  if not categories or WpC.WB.Wj.is_wp_error( categories ):
    categories = array()

  categories = Php.array_values( categories )

  for key in Php.array_keys( categories ):
    _make_cat_compat( categories[key] )

  # Filters the array of categories to return for a post.
  # @since 4.4.0 Added `Id` parameter.
  # @param array categories An array of categories to return for the post.
  # @param int   Id         ID of the post.
  return WiPg.apply_filters( 'get_the_categories', categories, Id )


def _usort_terms_by_name( a, b ):
  ''' Sort categories by name.
  Used by usort() as a callback, should not be used directly. Can actually be
  used to sort any term object.
  @access private
  @param object a
  @param object b
  @return int
  '''
  return strcmp( a.name, b.name )


def _usort_terms_by_ID( a, b ):
  ''' Sort categories by ID.
  Used by usort() as a callback, should not be used directly. Can actually be
  used to sort any term object.
  @access private
  @param object a
  @param object b
  @return int
  '''
  if a.term_id > b.term_id:
    return 1
  elif a.term_id < b.term_id:
    return -1
  else:
    return 0


def get_the_category_by_ID( cat_ID ):
  ''' Retrieve category name based on category ID.
  @param int cat_ID Category ID.
  @return string|WP_Error Category name on success, WP_Error on failure.
  '''
  cat_ID = int( cat_ID )
  category = get_term( cat_ID, 'category' )

  if WpC.WB.Wj.is_wp_error( category ):
    return category

  return category.name if category else ''


def get_the_category_list( separator = '', parents='', post_id = False ):
  ''' Retrieve category list in either HTML list or custom format.
  @global WP_Rewrite wp_rewrite
  @param string separator Optional, default is empty string. Separator for between the categories.
  @param string parents Optional. How to display the parents.
  @param int post_id Optional. Post ID to retrieve categories.
  @return string
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  if not is_object_in_taxonomy( get_post_type( post_id ), 'category' ):
    # This filter is documented in wp-includes/category-template.php
    return WiPg.apply_filters( 'the_category', '', separator, parents )

  # Filters the categories before building the category list.
  # @param array    categories An array of the post's categories.
  # @param int|bool post_id    ID of the post we're retrieving categories for. When `False`, we assume the
  #                             current post in the loop.
  categories = WiPg.apply_filters( 'the_category_list', get_the_category( post_id ), post_id )

  if Php.empty( categories ):
    # This filter is documented in wp-includes/category-template.php
    return WiPg.apply_filters( 'the_category', __( 'Uncategorized' ), separator, parents )

  rel = 'rel="category tag"' if ( Php.is_object( wp_rewrite ) and wp_rewrite.using_permalinks() ) else 'rel="category"'

  thelist = ''
  if '' == separator:
    thelist += '<ul class="post-categories">'
    for category in categories:
      thelist += "\n\t<li>"
      #switch ( strtolower( parents ) ) {
      ParentsLower = Php.strtolower( parents )
      if   ParentsLower == 'multiple':
        if category.parent:
          thelist += get_category_parents( category.parent, True, separator )
        thelist += '<a href="' + esc_url( get_category_link( category.term_id ) ) + '" ' + rel + '>' + category.name +'</a></li>'
      elif ParentsLower == 'single':
        thelist += '<a href="' + esc_url( get_category_link( category.term_id ) ) + '"  ' + rel + '>'
        if category.parent:
          thelist += get_category_parents( category.parent, False, separator )
        thelist += category.name +'</a></li>'
      #if  ParentsLower == '':
      else:
        thelist += '<a href="' + esc_url( get_category_link( category.term_id ) ) + '" ' + rel + '>' + category.name +'</a></li>'

    thelist += '</ul>'
  else:
    i = 0
    for category in categories:
      if 0 < i:
        thelist += separator
      #switch ( strtolower( parents ) ) {
      ParentsLower = Php.strtolower( parents )
      if   ParentsLower == 'multiple':
        if category.parent:
          thelist += get_category_parents( category.parent, True, separator )
        thelist += '<a href="' + esc_url( get_category_link( category.term_id ) ) + '" ' + rel + '>' + category.name +'</a>'
      elif ParentsLower == 'single':
        thelist += '<a href="' + esc_url( get_category_link( category.term_id ) ) + '" ' + rel  +'>'
        if category.parent:
          thelist += get_category_parents( category.parent, False, separator )
        thelist += category.name +"</a>"
      #if  ParentsLower == '':
      else:
        thelist += '<a href="' + esc_url( get_category_link( category.term_id ) ) + '" ' + rel + '>' + category.name +'</a>'
      i += 1

  # Filters the category or list of categories.
  # @param array  thelist   List of categories for the current post.
  # @param string separator Separator used between the categories.
  # @param string parents   How to display the category parents. Accepts 'multiple',
  #                          'single', or empty.
  return WiPg.apply_filters( 'the_category', thelist, separator, parents )


def in_category( category, post = None ):
  ''' Check if the current post in within any of the given categories.
  The given categories are checked against the post's categories' term_ids, names and slugs.
  Categories given as integers will only be checked against the post's categories' term_ids.
  Prior to v2.5 of WordPress, category names were not supported.
  Prior to v2.7, category slugs were not supported.
  Prior to v2.7, only one category could be compared: in_category( single_category ).
  Prior to v2.7, this function could only be used in the WordPress Loop.
  As of 2.7, the function can be used anywhere if it is provided a post ID or post object.
  @param int|string|array category Category ID, name or slug, or array of said.
  @param int|object post Optional. Post to check instead of the current post. (since 2.7.0)
  @return bool True if the current post is in any of the given categories.
  '''
  if Php.empty( category ):
    return False

  return has_category( category, post )


def the_category( separator = '', parents='', post_id = False ):
  ''' Display the category list for the post.
  @param string separator Optional, default is empty string. Separator for between the categories.
  @param string parents Optional. How to display the parents.
  @param int post_id Optional. Post ID to retrieve categories.
  '''
  Php.echo( get_the_category_list( separator, parents, post_id ))


def category_description( category = 0 ):
  ''' Retrieve category description.
  @param int category Optional. Category ID. Will use global category ID by default.
  @return string Category description, available.
  '''
  return term_description( category, 'category' )


def wp_dropdown_categories( args = '' ):
  ''' Display or retrieve the HTML dropdown list of categories.
  The 'hierarchical' argument, which is disabled by default, will override the
  depth argument, unless it is True. When the argument is False, it will
  display all of the categories. When it is enabled it will use the value in
  the 'depth' argument.
  @since 4.2.0 Introduced the `value_field` argument.
  @since 4.6.0 Introduced the `required` argument.
  @param string|array args {
      Optional. Array or string of arguments to generate a categories drop-down element.
      @type string       show_option_all   Text to display for showing all categories. Default empty.
      @type string       show_option_none  Text to display for showing no categories. Default empty.
      @type string       option_none_value Value to use when no category is selected. Default empty.
      @type string       orderby           Which column to use for ordering categories. See get_terms() for a list
                                            of accepted values. Default 'id' (term_id).
      @type string       order             Whether to order terms in ascending or descending order. Accepts 'ASC'
                                            or 'DESC'. Default 'ASC'.
      @type bool         pad_counts        See get_terms() for an argument description. Default False.
      @type bool|int     show_count        Whether to include post counts. Accepts 0, 1, or their bool equivalents.
                                            Default 0.
      @type bool|int     hide_empty        Whether to hide categories that don't have any posts. Accepts 0, 1, or
                                            their bool equivalents. Default 1.
      @type int          child_of          Term ID to retrieve child terms of. See get_terms(). Default 0.
      @type array|string exclude           Array or comma/space-separated string of term ids to exclude.
                                            If `include` is non-empty, `exclude` is ignored. Default empty array.
      @type bool|int     echo              Whether to echo or return the generated markup. Accepts 0, 1, or their
                                            bool equivalents. Default 1.
      @type bool|int     hierarchical      Whether to traverse the taxonomy hierarchy. Accepts 0, 1, or their bool
                                            equivalents. Default 0.
      @type int          depth             Maximum depth. Default 0.
      @type int          tab_index         Tab index for the select element. Default 0 (no tabindex).
      @type string       name              Value for the 'name' attribute of the select element. Default 'cat'.
      @type string       id                Value for the 'id' attribute of the select element. Defaults to the value
                                            of `name`.
      @type string       Class             Value for the 'class' attribute of the select element. Default 'postform'.
      @type int|string   selected          Value of the option that should be selected. Default 0.
      @type string       value_field       Term field that should be used to populate the 'value' attribute
                                            of the option elements. Accepts any valid term field: 'term_id', 'name',
                                            'slug', 'term_group', 'term_taxonomy_id', 'taxonomy', 'description',
                                            'parent', 'count'. Default 'term_id'.
      @type string|array taxonomy          Name of the category or categories to retrieve. Default 'category'.
      @type bool         hide_if_empty     True to skip generating markup if no categories are found.
                                            Default False (create select element even if no categories are found).
      @type bool         required          Whether the `<select>` element should have the HTML5 'required' attribute.
                                            Default False.
  }
  @return string HTML content only if 'echo' argument is 0.
  '''
  defaults = array(
    ('show_option_all'  , ''),
    ('show_option_none' , ''),
    ('orderby'          , 'id'),
    ('order'            , 'ASC'),
    ('show_count'       , 0),
    ('hide_empty'       , 1),
    ('child_of'         , 0),
    ('exclude'          , ''),
    ('echo'             , 1),
    ('selected'         , 0),
    ('hierarchical'     , 0),
    ('name'             , 'cat'),
    ('id'               , ''),
    ('class'            , 'postform'),
    ('depth'            , 0),
    ('tab_index'        , 0),
    ('taxonomy'         , 'category'),
    ('hide_if_empty'    , False),
    ('option_none_value', -1),
    ('value_field'      , 'term_id'),
    ('required'         , False),
  )

  defaults['selected'] = get_query_var( 'cat' ) if ( is_category() ) else 0

  # Back compat.
  if Php.isset( args, 'type' ) and 'link' == args['type']:
    #translators: 1: "type => link", 2: "taxonomy => link_category" alternative
    _deprecated_argument( __FUNCTION__, '3.0.0',
      Php.sprintf( __( '%1$s is deprecated. Use %2$s instead.' ),
        '<code>type => link</code>',
        '<code>taxonomy => link_category</code>'
      )
    )
    args['taxonomy'] = 'link_category'

  r = wp_parse_args( args, defaults )
  option_none_value = r['option_none_value']

  if not Php.isset( r, 'pad_counts' ) and r['show_count'] and r['hierarchical']:
    r['pad_counts'] = True

  tab_index = r['tab_index']

  tab_index_attribute = ''
  if int( tab_index ) > 0:
    tab_index_attribute = ' tabindex="{}"'.format(tab_index)

  # Avoid clashes with the 'name' param of get_terms().
  get_terms_args = r
  unset( get_terms_args['name'] )
  categories = get_terms( r['taxonomy'], get_terms_args )

  name = esc_attr( r['name'] )
  Class = esc_attr( r['class'] )
  Id = esc_attr( r['id'] ) if r['id'] else name
  required = 'required' if r['required'] else ''

  if not r['hide_if_empty'] or not Php.empty( categories ):
    output = "<select {} name='{}' id='{}' class='{}' {}>\n".format(required, name, Id, Class, tab_index_attribute)
  else:
    output = ''

  if Php.empty( categories ) and not r['hide_if_empty'] and not Php.empty( r['show_option_none'] ):

    # Filters a taxonomy drop-down display element.
    # A variety of taxonomy drop-down display elements can be modified
    # just prior to display via this filter. Filterable arguments include
    # 'show_option_none', 'show_option_all', and various forms of the
    # term name.
    # @see wp_dropdown_categories()
    # @param string element Taxonomy element to list.
    show_option_none = WiPg.apply_filters( 'list_cats', r['show_option_none'] )
    output += "\t<option value='" + esc_attr( option_none_value ) + "' selected='selected'>{}</option>\n".format(show_option_none)

  if not Php.empty( categories ):

    if r['show_option_all']:

      # This filter is documented in wp-includes/category-template.php
      show_option_all = WiPg.apply_filters( 'list_cats', r['show_option_all'] )
      selected = " selected='selected'" if ( '0' == strval(r['selected']) ) else ''
      output += "\t<option value='0'{}>{}</option>\n".format(selected, show_option_all)

    if r['show_option_none']:

      # This filter is documented in wp-includes/category-template.php
      show_option_none = WiPg.apply_filters( 'list_cats', r['show_option_none'] )
      selected = selected( option_none_value, r['selected'], False )
      output += "\t<option value='" + esc_attr( option_none_value ) + "'{}>{}</option>\n".format(selected, show_option_none)

    if r['hierarchical']:
      depth = r['depth'];  # Walk the full depth.
    else:
      depth = -1; # Flat.
    output += walk_category_dropdown_tree( categories, depth, r )

  if not r['hide_if_empty'] or not Php.empty( categories ):
    output += "</select>\n"

  # Filters the taxonomy drop-down output.
  # @param string output HTML output.
  # @param array  r      Arguments used to build the drop-down.
  output = WiPg.apply_filters( 'wp_dropdown_cats', output, r )

  if r['echo']:
    Php.echo( output)
  return output


def wp_list_categories( args = '' ):
  ''' Display or retrieve the HTML list of categories.
  @since 4.4.0 Introduced the `hide_title_if_empty` and `separator` arguments. The `current_category` argument was modified to
               optionally accept an array of values.
  @param string|array args {
      Array of optional arguments.
      @type int          child_of              Term ID to retrieve child terms of. See get_terms(). Default 0.
      @type int|array    current_category      ID of category, or array of IDs of categories, that should get the
                                                'current-cat' class. Default 0.
      @type int          depth                 Category depth. Used for tab indentation. Default 0.
      @type bool|int     echo                  True to echo markup, False to return it. Default 1.
      @type array|string exclude               Array or comma/space-separated string of term IDs to exclude.
                                                If `hierarchical` is True, descendants of `exclude` terms will also
                                                be excluded; see `exclude_tree`. See get_terms().
                                                Default empty string.
      @type array|string exclude_tree          Array or comma/space-separated string of term IDs to exclude, along
                                                with their descendants. See get_terms(). Default empty string.
      @type string       feed                  Text to use for the feed link. Default 'Feed for all posts filed
                                                under [cat name]'.
      @type string       feed_image            URL of an image to use for the feed link. Default empty string.
      @type string       feed_type             Feed type. Used to build feed link. See get_term_feed_link().
                                                Default empty string (default feed).
      @type bool|int     hide_empty            Whether to hide categories that don't have any posts attached to them.
                                                Default 1.
      @type bool         hide_title_if_empty   Whether to hide the `title_li` element if there are no terms in
                                                the list. Default False (title will always be shown).
      @type bool         hierarchical          Whether to include terms that have non-empty descendants.
                                                See get_terms(). Default True.
      @type string       order                 Which direction to order categories. Accepts 'ASC' or 'DESC'.
                                                Default 'ASC'.
      @type string       orderby               The column to use for ordering categories. Default 'ID'.
      @type string       separator             Separator between links. Default '<br />'.
      @type bool|int     show_count            Whether to show how many posts are in the category. Default 0.
      @type string       show_option_all       Text to display for showing all categories. Default empty string.
      @type string       show_option_none      Text to display for the 'no categories' option.
                                                Default 'No categories'.
      @type string       style                 The style used to display the categories list. If 'list', categories
                                                will be output as an unordered list. If left empty or another value,
                                                categories will be output separated by `<br>` tags. Default 'list'.
      @type string       taxonomy              Taxonomy name. Default 'category'.
      @type string       title_li              Text to use for the list title `<li>` element. Pass an empty string
                                                to disable. Default 'Categories'.
      @type bool|int     use_desc_for_title    Whether to use the category description as the title attribute.
                                                Default 1.
  }
  @return False|string HTML content only if 'echo' argument is 0.
  '''
  defaults = array(
    ('child_of'           , 0),
    ('current_category'   , 0),
    ('depth'              , 0),
    ('echo'               , 1),
    ('exclude'            , ''),
    ('exclude_tree'       , ''),
    ('feed'               , ''),
    ('feed_image'         , ''),
    ('feed_type'          , ''),
    ('hide_empty'         , 1),
    ('hide_title_if_empty', False),
    ('hierarchical'       , True),
    ('order'              , 'ASC'),
    ('orderby'            , 'name'),
    ('separator'          , '<br />'),
    ('show_count'         , 0),
    ('show_option_all'    , ''),
    ('show_option_none'   , __( 'No categories' )),
    ('style'              , 'list'),
    ('taxonomy'           , 'category'),
    ('title_li'           , __( 'Categories' )),
    ('use_desc_for_title' , 1),
  )

  r = wp_parse_args( args, defaults )

  if not Php.isset( r, 'pad_counts' ) and r['show_count'] and r['hierarchical']:
    r['pad_counts'] = True

  # Descendants of exclusions should be excluded too.
  if True == r['hierarchical']:
    exclude_tree = array()

    if r['exclude_tree']:
      exclude_tree = array_merge( exclude_tree, WiFc.wp_parse_id_list( r['exclude_tree'] ) )

    if r['exclude']:
      exclude_tree = array_merge( exclude_tree, WiFc.wp_parse_id_list( r['exclude'] ) )

    r['exclude_tree'] = exclude_tree
    r['exclude'] = ''

  if not Php.isset( r, 'class' ):
    r['class'] = 'categories' if ( 'category' == r['taxonomy'] ) else r['taxonomy']

  if not taxonomy_exists( r['taxonomy'] ):
    return False

  show_option_all = r['show_option_all']
  show_option_none = r['show_option_none']

  categories = get_categories( r )

  output = ''
  if r['title_li'] and 'list' == r['style'] and ( not Php.empty( categories ) or not r['hide_title_if_empty'] ):
    output = '<li class="' + esc_attr( r['class'] ) + '">' + r['title_li'] + '<ul>'

  if Php.empty( categories ):
    if not Php.empty( show_option_none ):
      if 'list' == r['style']:
        output += '<li class="cat-item-none">' + show_option_none + '</li>'
      else:
        output += show_option_none
  else:
    if not Php.empty( show_option_all ):

      posts_page = ''

      # For taxonomies that belong only to custom post types, point to a valid archive.
      taxonomy_object = get_taxonomy( r['taxonomy'] )
      if not in_array( 'post', taxonomy_object.object_type ) and not in_array( 'page', taxonomy_object.object_type ):
        for object_type in taxonomy_object.object_type:
          _object_type = get_post_type_object( object_type )

          # Grab the first one.
          if not Php.empty( _object_type.has_archive ):
            posts_page = get_post_type_archive_link( object_type )
            break

      # Fallback for the 'All' link is the posts page.
      if not posts_page:
        if 'page' == get_option( 'show_on_front' ) and get_option( 'page_for_posts' ):
          posts_page = get_permalink( get_option( 'page_for_posts' ) )
        else:
          posts_page = home_url( '/' )

      posts_page = esc_url( posts_page )
      if 'list' == r['style']:
        output += "<li class='cat-item-all'><a href='{}'>{}</a></li>".format(posts_page, show_option_all)
      else:
        output += "<a href='{}'>{}</a>".format(posts_page, show_option_all)

    if Php.empty( r['current_category'] ) and ( is_category() or is_tax() or is_tag() ):
      current_term_object = get_queried_object()
      if current_term_object and r['taxonomy'] == current_term_object.taxonomy:
        r['current_category'] = get_queried_object_id()

    if r['hierarchical']:
      depth = r['depth']
    else:
      depth = -1; # Flat.

    output += walk_category_tree( categories, depth, r )

  if r['title_li'] and 'list' == r['style']:
    output += '</ul></li>'

  # Filters the HTML output of a taxonomy list.
  # @param string output HTML output.
  # @param array  args   An array of taxonomy-listing arguments.
  html = WiPg.apply_filters( 'wp_list_categories', output, args )

  if r['echo']:
    Php.echo( html)
  else:
    return html


def wp_tag_cloud( args = '' ):
  ''' Display tag cloud.
  The text size is set by the 'smallest' and 'largest' arguments, which will
  use the 'unit' argument value for the CSS text size unit. The 'format'
  argument can be 'flat' (default), 'list', or 'array'. The flat value for the
  'format' argument will separate tags with spaces. The list value for the
  'format' argument will format the tags in a UL HTML list. The array value for
  the 'format' argument will return in PHP array type format.
  The 'orderby' argument will accept 'name' or 'count' and defaults to 'name'.
  The 'order' is the direction to sort, defaults to 'ASC' and can be 'DESC'.
  The 'number' argument is how many tags to return. By default, the limit will
  be to return the top 45 tags in the tag cloud list.
  The 'topic_count_text' argument is a nooped plural from _n_noop() to generate the
  text for the tooltip of the tag link.
  The 'topic_count_text_callback' argument is a function, which given the count
  of the posts with that tag returns a text for the tooltip of the tag link.
  The 'post_type' argument is used only when 'link' is set to 'edit'. It determines the post_type
  passed to edit.php for the popular tags edit links.
  The 'exclude' and 'include' arguments are used for the get_tags() function. Only one
  should be used, because only one will be used and the other ignored, if they are both set.
  @param array|string|None args Optional. Override default arguments.
  @return void|array Generated tag cloud, only if no failures and 'array' is set for the 'format' argument.
                     Otherwise, this function outputs the tag cloud.
  '''
  defaults = array(
    ('smallest', 8), ('largest', 22), ('unit', 'pt'), ('number', 45),
    ('format', 'flat'), ('separator', "\n"), ('orderby', 'name'),
    ('order', 'ASC'), ('exclude', ''), ('include', ''), ('link', 'view'),
    ('taxonomy', 'post_tag'), ('post_type', ''), ('echo', True),
  )
  args = wp_parse_args( args, defaults )

  tags = get_terms( args['taxonomy'], array_merge( args, [ 'orderby', 'count', 'order', 'DESC' ] ) ); # Always query top tags

  if Php.empty( tags ) or WpC.WB.Wj.is_wp_error( tags ):
    return

  for key, tag in tags.items():
    if 'edit' == args['link']:
      link = get_edit_term_link( tag.term_id, tag.taxonomy, args['post_type'] )
    else:
      link = get_term_link( intval(tag.term_id), tag.taxonomy )
    if WpC.WB.Wj.is_wp_error( link ):
      return

    tags[ key ].link = link
    tags[ key ].id = tag.term_id

  Return = wp_generate_tag_cloud( tags, args ); # Here's where those top tags get sorted according to args

  # Filters the tag cloud output.
  # @param string Return HTML output of the tag cloud.
  # @param array  args   An array of tag cloud arguments.
  Return = WiPg.apply_filters( 'wp_tag_cloud', Return, args )

  if 'array' == args['format'] or Php.empty(args['echo']):
    return Return

  Php.echo( Return)


def default_topic_count_scale( count ):
  ''' Default topic count scaling for tag links
  @param int count number of posts with that tag
  @return int scaled count
  '''
  return round(log10(count + 1) * 100)


def wp_generate_tag_cloud( tags, args = '' ):
  ''' Generates a tag cloud (heatmap) from provided data.
  @todo Complete functionality.
  @param array tags List of tags.
  @param string|array args {
      Optional. Array of string of arguments for generating a tag cloud.
      @type int      smallest                   Smallest font size used to display tags. Paired
                                                 with the value of `unit`, to determine CSS text
                                                 size unit. Default 8 (pt).
      @type int      largest                    Largest font size used to display tags. Paired
                                                 with the value of `unit`, to determine CSS text
                                                 size unit. Default 22 (pt).
      @type string   unit                       CSS text size unit to use with the `smallest`
                                                 and `largest` values. Accepts any valid CSS text
                                                 size unit. Default 'pt'.
      @type int      number                     The number of tags to return. Accepts any
                                                 positive integer or zero to return all.
                                                 Default 0.
      @type string   format                     Format to display the tag cloud in. Accepts 'flat'
                                                 (tags separated with spaces), 'list' (tags displayed
                                                 in an unordered list), or 'array' (returns an array).
                                                 Default 'flat'.
      @type string   separator                  HTML or text to separate the tags. Default "\n" (newline).
      @type string   orderby                    Value to order tags by. Accepts 'name' or 'count'.
                                                 Default 'name'. The {@see 'tag_cloud_sort'} filter
                                                 can also affect how tags are sorted.
      @type string   order                      How to order the tags. Accepts 'ASC' (ascending),
                                                 'DESC' (descending), or 'RAND' (random). Default 'ASC'.
      @type int|bool filter                     Whether to enable filtering of the final output
                                                 via {@see 'wp_generate_tag_cloud'}. Default 1|True.
      @type string   topic_count_text           Nooped plural text from _n_noop() to supply to
                                                 tag tooltips. Default None.
      @type callable topic_count_text_callback  Callback used to generate nooped plural text for
                                                 tag tooltips based on the count. Default None.
      @type callable topic_count_scale_callback Callback used to determine the tag count scaling
                                                 value. Default default_topic_count_scale().
  }
  @return string|array Tag cloud as a string or an array, depending on 'format' argument.
  '''
  defaults = array(
    ('smallest', 8), ('largest', 22), ('unit', 'pt'), ('number', 0),
    ('format','flat'), ('separator',"\n"), ('orderby','name'),('order','ASC'),
    ('topic_count_text', None), ('topic_count_text_callback', None),
    ('topic_count_scale_callback', 'default_topic_count_scale'), ('filter',1),
  )

  args = wp_parse_args( args, defaults )

  Return = array() if ( 'array' == args['format'] ) else ''

  if Php.empty( tags ):
    return Return

  # Juggle topic count tooltips:
  if Php.isset( args, 'topic_count_text' ):
    # First look for nooped plural support via topic_count_text.
    translate_nooped_plural = args['topic_count_text']
  elif not Php.empty( args['topic_count_text_callback'] ):
    # Look for the alternative callback style. Ignore the previous default.
    if args['topic_count_text_callback'] == 'default_topic_count_text':
      translate_nooped_plural = _n_noop( '%s topic', '%s topics' )
    else:
      translate_nooped_plural = False

  elif Php.isset( args, 'single_text' ) and Php.isset( args, 'multiple_text' ):
    # If no callback exists, look for the old-style single_text and multiple_text arguments.
    translate_nooped_plural = _n_noop( args['single_text'], args['multiple_text'] )
  else:
    # This is the default for when no callback, plural, or argument is passed in.
    translate_nooped_plural = _n_noop( '%s topic', '%s topics' )

  # Filters how the items in a tag cloud are sorted.
  # @param array tags Ordered array of terms.
  # @param array args An array of tag cloud arguments.
  tags_sorted = WiPg.apply_filters( 'tag_cloud_sort', tags, args )
  if Php.empty( tags_sorted ):
    return Return

  if tags_sorted != tags:
    tags = tags_sorted
    unset( tags_sorted )
  else:
    if 'RAND' == args['order']:
      shuffle( tags )
    else:
      # SQL cannot save you; this is a second (potentially different) sort on a subset of data.
      if 'name' == args['orderby']:
        uasort( tags, '_wp_object_name_sort_cb' )
      else:
        uasort( tags, '_wp_object_count_sort_cb' )

      if 'DESC' == args['order']:
        tags = array_reverse( tags, True )

  if args['number'] > 0:
    tags = array_slice( tags, 0, args['number'] )

  counts = array()
  real_counts = array(); # For the alt tag
  for key, tag in Php.Array(tags).items():
    real_counts[ key ] = tag.count
    counts[ key ] = Php.call_user_func( args['topic_count_scale_callback'], tag.count )

  # Php min() = Php.Min() here is is different from the py builtin min() !!
  min_count = Php.Min( counts )
  # Php max() = Php.Max() here is is different from the py builtin max() !!
  spread = Php.Max( counts ) - min_count
  if spread <= 0:
    spread = 1
  font_spread = args['largest'] - args['smallest']
  if font_spread < 0:
    font_spread = 1
  font_step = font_spread / spread

  # Assemble the data that will be used to generate the tag cloud markup.
  tags_data = array()
  for key, tag in tags.items():
    tag_id = tag.id if Php.isset( tag, id ) else key

    count = counts[ key ]
    real_count = real_counts[ key ]

    if translate_nooped_plural:
      title = Php.sprintf( translate_nooped_plural( translate_nooped_plural, real_count ), number_format_i18n( real_count ) )
    else:
      title = Php.call_user_func( args['topic_count_text_callback'], real_count, tag, args )

    Php.ArrayAppend( tags_data, array(
      ('id'        , tag_id),
      ('url'       , tag.link if '#' != tag.link else '#'),
      ('name'	     , tag.name),
      ('title'     , title),
      ('slug'      , tag.slug),
      ('real_count', real_count),
      ('class'	   , 'tag-link-' + tag_id),
      ('font_size' , args['smallest'] + ( count - min_count ) * font_step),
    ) )

  # Filters the data used to generate the tag cloud.
  # @param array tags_data An array of term data for term used to generate the tag cloud.
  tags_data = WiPg.apply_filters( 'wp_generate_tag_cloud_data', tags_data )

  a = array()

  # generate the output links array
  for key, tag_data in tags_data.items():
    Class = tag_data['class'] + ' tag-link-position-' + ( key + 1 )
    Php.ArrayAppend(a, "<a href='" + esc_url( tag_data['url'] ) + "' class='" + esc_attr( Class ) + "' title='" + esc_attr( tag_data['title'] ) + "' style='font-size: " + esc_attr( str_replace( ',', '.', tag_data['font_size'] ) + args['unit'] ) + ";'>" + esc_html( tag_data['name'] ) + "</a>")

  #switch ( args['format'] ) {
  if   args['format'] == 'array' :
    Return = a    # no need for php: & a, since a is a mutable array
  elif args['format'] == 'list' :
    Return = "<ul class='wp-tag-cloud'>\n\t<li>"
    Return += join( "</li>\n\t<li>", a )
    Return += "</li>\n</ul>\n"
  else:
    Return = join( args['separator'], a )

  if args['filter']:
    # Filters the generated output of a tag cloud.
    # The filter is only evaluated if a True value is passed
    # to the filter argument in wp_generate_tag_cloud().
    # @see wp_generate_tag_cloud()
    # @param array|string Return String containing the generated HTML tag cloud output
    #                             or an array of tag links if the 'format' argument
    #                             equals 'array'.
    # @param array        tags   An array of terms used in the tag cloud.
    # @param array        args   An array of wp_generate_tag_cloud() arguments.
    return WiPg.apply_filters( 'wp_generate_tag_cloud', Return, tags, args )

  else:
    return Return


def _wp_object_name_sort_cb( a, b ):
  ''' Serves as a callback for comparing objects based on name.
  Used with `uasort()`.
  @access private
  @param object a The first object to compare.
  @param object b The second object to compare.
  @return int Negative number if `a.name` is less than `b.name`, zero if they are equal,
              or greater than zero if `a.name` is greater than `b.name`.
  '''
  return strnatcasecmp( a.name, b.name )


def _wp_object_count_sort_cb( a, b ):
  ''' Serves as a callback for comparing objects based on count.
  Used with `uasort()`.
  @access private
  @param object a The first object to compare.
  @param object b The second object to compare.
  @return bool Whether the count value for `a` is greater than the count value for `b`.
  '''
  return ( a.count > b.count )


#
# Helper functions
#

def walk_category_tree( *AllArgs ):
  ''' Retrieve HTML list content for category list.
  @uses Walker_Category to create HTML list content.
  @see Walker_Category::walk() for parameters and return description.
  @return string
  '''
  args = Php.func_get_args( AllArgs )   #  = array( *AllArgs )
  # the user's options are the third parameter
  if Php.empty( args[2]['walker'] ) or not isinstance( args[2]['walker'], Walker ):
    walker = Walker_Category()
  else:
    walker = args[2]['walker']
  return Php.call_user_func_array( array( walker, 'walk' ), args )


def walk_category_dropdown_tree( *AllArgs ):
  ''' Retrieve HTML dropdown (select) content for category list.
  @uses Walker_CategoryDropdown to create HTML dropdown content.
  @see Walker_CategoryDropdown::walk() for parameters and return description.
  @return string
  '''
  args = Php.func_get_args( AllArgs )   #  = array( *AllArgs )
  # the user's options are the third parameter
  if Php.empty( args[2]['walker'] ) or not isinstance( args[2]['walker'], Walker ):
    walker = Walker_CategoryDropdown()
  else:
    walker = args[2]['walker']
  return Php.call_user_func_array( array( walker, 'walk' ), args )


#
# Tags
#

def get_tag_link( tag ):
  ''' Retrieve the link to the tag.
  @see get_term_link()
  @param int|object tag Tag ID or object.
  @return string Link on success, empty string if tag does not exist.
  '''
  if not Php.is_object( tag ):
    tag = int( tag )

  tag = get_term_link( tag, 'post_tag' )

  if WpC.WB.Wj.is_wp_error( tag ):
    return ''

  return tag


def get_the_tags( Id = 0 ):
  ''' Retrieve the tags for a post.
  @param int Id Post ID.
  @return array|False|WP_Error Array of tag objects on success, False on failure.
  '''

  # Filters the array of tags for the given post.
  # @see get_the_terms()
  # @param array terms An array of tags for the given post.
  return WiPg.apply_filters( 'get_the_tags', get_the_terms( Id, 'post_tag' ) )


def get_the_tag_list( before = '', sep = '', after = '', Id = 0 ):
  ''' Retrieve the tags for a post formatted as a string.
  @param string before Optional. Before tags.
  @param string sep Optional. Between tags.
  @param string after Optional. After tags.
  @param int Id Optional. Post ID. Defaults to the current post.
  @return string|False|WP_Error A list of tags on success, False if there are no terms, WP_Error on failure.
  '''

  # Filters the tags list for a given post.
  # @param string tag_list List of tags.
  # @param string before   String to use before tags.
  # @param string sep      String to use between the tags.
  # @param string after    String to use after tags.
  # @param int    Id       Post ID.
  return WiPg.apply_filters( 'the_tags', get_the_term_list( Id, 'post_tag', before, sep, after ), before, sep, after, Id )


def the_tags( before = None, sep = ', ', after = '' ):
  ''' Retrieve the tags for a post.
  @param string before Optional. Before list.
  @param string sep Optional. Separate items using this.
  @param string after Optional. After list.
  '''
  if None is before:
    before = __('Tags: ')
  Php.echo( get_the_tag_list(before, sep, after))


def tag_description( tag = 0 ):
  ''' Retrieve tag description.
  @param int tag Optional. Tag ID. Will use global tag ID by default.
  @return string Tag description, available.
  '''
  return term_description( tag )


def term_description( term = 0, taxonomy = 'post_tag' ):
  ''' Retrieve term description.
  @param int term Optional. Term ID. Will use global term ID by default.
  @param string taxonomy Optional taxonomy name. Defaults to 'post_tag'.
  @return string Term description, available.
  '''
  if not term and ( is_tax() or is_tag() or is_category() ):
    term = get_queried_object()
    if term:
      taxonomy = term.taxonomy
      term = term.term_id

  description = get_term_field( 'description', term, taxonomy )
  return '' if WpC.WB.Wj.is_wp_error( description ) else description



def get_the_terms( post, taxonomy ):
  ''' Retrieve the terms of the taxonomy that are attached to the post.
  @param int|object post Post ID or object.
  @param string taxonomy Taxonomy name.
  @return array|False|WP_Error Array of WP_Term objects on success, False if
            there are no terms or the post does not exist, WP_Error on failure
  '''
  import wp.i.post      as WiP
  post = WiP.get_post( post )
  if not post:
    return False

  terms = WiTx.get_object_term_cache( post.ID, taxonomy )
  if False is terms:
    terms = WiTx.wp_get_object_terms( post.ID, taxonomy )
    if not WpC.WB.Wj.is_wp_error( terms ):
      term_ids = WiFc.wp_list_pluck( terms, 'term_id' )
      WiCa.wp_cache_add( post.ID, term_ids, taxonomy + '_relationships' )

  # Filter the list of terms attached to the given post.
  # @param array|WP_Error terms  List of attached terms,or WP_Error on failure
  # @param int            post_id  Post ID.
  # @param string         taxonomy Name of the taxonomy.
  #terms = WiPg.apply_filters( 'get_the_terms', terms, post.ID, taxonomy )

  if not terms:
    return False
  return terms


def get_the_term_list( Id, taxonomy, before = '', sep = '', after = '' ):
  ''' Retrieve a post's terms as a list with specified format.
  @param int Id Post ID.
  @param string taxonomy Taxonomy name.
  @param string before Optional. Before list.
  @param string sep Optional. Separate items using this.
  @param string after Optional. After list.
  @return string|False|WP_Error A list of terms on success, False if there are no terms, WP_Error on failure.
  '''
  terms = get_the_terms( Id, taxonomy )

  if WpC.WB.Wj.is_wp_error( terms ):
    return terms

  if Php.empty( terms ):
    return False

  links = array()

  for term in terms:
    link = get_term_link( term, taxonomy )
    if WpC.WB.Wj.is_wp_error( link ):
      return link

    Php.ArrayAppend(links, '<a href="' + esc_url( link ) + '" rel="tag">' + term.name + '</a>')

  # Filters the term links for a given taxonomy.
  # The dynamic portion of the filter name, `taxonomy`, refers
  # to the taxonomy slug.
  # @param array links An array of term links.
  term_links = WiPg.apply_filters( "term_links-"+ taxonomy, links )

  return before + join( sep, term_links ) + after


def the_terms( Id, taxonomy, before = '', sep = ', ', after = '' ):
  ''' Display the terms in a list.
  @param int Id Post ID.
  @param string taxonomy Taxonomy name.
  @param string before Optional. Before list.
  @param string sep Optional. Separate items using this.
  @param string after Optional. After list.
  @return False|void False on WordPress error.
  '''
  term_list = get_the_term_list( Id, taxonomy, before, sep, after )

  if WpC.WB.Wj.is_wp_error( term_list ):
    return False

  # Filters the list of terms to display.
  # @param array  term_list List of terms to display.
  # @param string taxonomy  The taxonomy name.
  # @param string before    String to use before the terms.
  # @param string sep       String to use between the terms.
  # @param string after     String to use after the terms.
  Php.echo( WiPg.apply_filters( 'the_terms', term_list, taxonomy, before, sep, after ))


def has_category( category = '', post = None ):
  ''' Check if the current post has any of given category.
  @param string|int|array category Optional. The category name/term_id/slug or array of them to check for.
  @param int|object post Optional. Post to check instead of the current post.
  @return bool True if the current post has any of the given categories (or any category, if no category specified).
  '''
  return has_term( category, 'category', post )


def has_tag( tag = '', post = None ):
  ''' Check if the current post has any of given tags.
  The given tags are checked against the post's tags' term_ids, names and slugs.
  Tags given as integers will only be checked against the post's tags' term_ids.
  If no tags are given, determines if post has any tags.
  Prior to v2.7 of WordPress, tags given as integers would also be checked against the post's tags' names and slugs (in addition to term_ids)
  Prior to v2.7, this function could only be used in the WordPress Loop.
  As of 2.7, the function can be used anywhere if it is provided a post ID or post object.
  @param string|int|array tag Optional. The tag name/term_id/slug or array of them to check for.
  @param int|object post Optional. Post to check instead of the current post. (since 2.7.0)
  @return bool True if the current post has any of the given tags (or any tag, if no tag specified).
  '''
  return has_term( tag, 'post_tag', post )


def has_term( term = '', taxonomy = '', post = None ):
  ''' Check if the current post has any of given terms.
  The given terms are checked against the post's terms' term_ids, names and slugs.
  Terms given as integers will only be checked against the post's terms' term_ids.
  If no terms are given, determines if post has any terms.
  @param string|int|array term Optional. The term name/term_id/slug or array of them to check for.
  @param string taxonomy Taxonomy name
  @param int|object post Optional. Post to check instead of the current post.
  @return bool True if the current post has any of the given tags (or any tag, if no tag specified).
  '''
  post = WiP.get_post(post)

  if not post:
    return False

  r = is_object_in_term( post.ID, taxonomy, term )
  if WpC.WB.Wj.is_wp_error( r ):
    return False

  return r


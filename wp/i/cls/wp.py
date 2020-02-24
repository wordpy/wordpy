import wp.conf     as WpC
import wp.i.format as WiF
import wp.i.plugin as WiPg
import pyx.php     as Php
array = Php.array

#def InitWpGlobals(self):
#  "global var==>self.var, except: var=self.var=same Obj,mutable[],{},array"
#  #global wp_rewrite
#  #global wp_query, wp_the_query, GLOBALS
#  #wp_rewrite   = self.wp_rewrite
#  #wp_query     = self.wp_query
#  #wp_the_query = self.wp_the_query
#  #GLOBALS      = self.__dict__  # = WpC.WB.Wj.__dict__
#  pass


class WP(Php.stdClass):
  ''' WordPress environment setup class.
  @package WordPress
  '''

  def __init__(self):
    "Inherited classes no long need to define 'self._obj=array()' in __init__()"
    # Public query variables.
    # Long list of public query variables.
    # @access public @var array
    #self.public_query_vars is list, not tuple, since: public_query_vars.append
    self.public_query_vars = array('m', 'p', 'posts', 'w', 'cat', 'withcomments', 'withoutcomments', 's', 'search', 'exact', 'sentence', 'calendar', 'page', 'paged', 'more', 'tb', 'pb', 'author', 'order', 'orderby', 'year', 'monthnum', 'day', 'hour', 'minute', 'second', 'name', 'category_name', 'tag', 'feed', 'author_name', 'static', 'pagename', 'page_id', 'error', 'attachment', 'attachment_id', 'subpost', 'subpost_id', 'preview', 'robots', 'taxonomy', 'term', 'cpage', 'post_type', 'embed' )

    # Private query variables.
    # Long list of private query variables.
    # @access public
    # @var array
    self.private_query_vars = array( 'offset', 'posts_per_page', 'posts_per_archive_page', 'showposts', 'nopaging', 'post_type', 'post_status', 'category__in', 'category__not_in', 'category__and', 'tag__in', 'tag__not_in', 'tag__and', 'tag_slug__in', 'tag_slug__and', 'tag_id', 'post_mime_type', 'perm', 'comments_per_page', 'post__in', 'post__not_in', 'post_parent', 'post_parent__in', 'post_parent__not_in', 'title' )

    # Extra query variables set by the user.
    # @access public
    # @var array
    self.extra_query_vars = array()    # array()

    # Query variables for setting up the WordPress Query Loop.
    # @access public
    # @var array
    self.query_vars = None   #VT init to None, orig just declared var

    # String parsed to set the query variables.
    # @access public
    # @var string
    self.query_string = None   #VT init to None, orig just declared var

    # The request path, e.g. 2015/05/06.
    # @access public
    # @var string
    self.request = None   #VT init to None, orig just declared var

    # Rewrite rule the request matched.
    # @access public
    # @var string
    self.matched_rule = None   #VT init to None, orig just declared var

    # Rewrite query the request matched.
    # @access public
    # @var string
    self.matched_query = None   #VT init to None, orig just declared var

    # Whether already did the permalink.
    # @access public
    # @var bool
    self.did_permalink = False

  def add_query_var(self, qv):
    ''' Add name to list of public query variables.
    # @access public
    # @param string qv Query variable name.
    '''
    if not Php.in_array(qv, self.public_query_vars):
      self.public_query_vars.append(qv)

  def remove_query_var(self,  name ):
    ''' Removes a query variable from a list of public query variables.
    @access public
    @param string name Query variable name.
    '''
    self.public_query_vars = Php.array_diff( self.public_query_vars, array( name ) )

  def set_query_var(self, key, value):
    ''' Set the value of a query variable.
    @access public
    @param string key Query variable name.
    @param mixed value Query variable value.
    '''
    self.query_vars[key] = value

  def parse_request(self, extra_query_vars = ''):
    ''' Parse request to find correct WordPress query.
    Sets up the query variables based on the request. There are also many
    filters and actions that can be used to further manipulate the result.
    @access public
    @global WP_Rewrite wp_rewrite
    @param array|string extra_query_vars Set the extra query variables.
    '''
    import wp.i.taxonomy as WiTx
    wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

    # Filters whether to parse the request.
    # @param bool         bool             Whether or not to parse the request. Default True.
    # @param WP           self             Current WordPress environment instance.
    # @param array|string extra_query_vars Extra passed query variables.
    if not  apply_filters( 'do_parse_request', True, self, extra_query_vars ):
      return

    self.query_vars = array()
    post_type_query_vars = array()

    if Php.is_array( extra_query_vars ):
      #self.extra_query_vars = & extra_query_vars
      self.extra_query_vars = extra_query_vars  # mutable array don't need &
    elif extra_query_vars:  # elif not Php.empty(locals(),'extra_query_vars'):
      parse_str( extra_query_vars, self.extra_query_vars )
    # Process PATH_INFO, REQUEST_URI, and 404 for permalinks.

    # Fetch the rewrite rules.
    rewrite = wp_rewrite.wp_rewrite_rules()

    if rewrite:  #  if not Php.empty(locals(), 'rewrite'):
      # If we match a rewrite rule, this will be cleared.
      error = '404'
      self.did_permalink = True

      #pathinfo=_SERVER['PATH_INFO'] if Php.isset(_SERVER,'PATH_INFO') else ''
      pathinfo = getattr(_SERVER, 'PATH_INFO', '')
      #list( pathinfo ) = explode( '?', pathinfo )
      pathinfo = Php.explode( '?', pathinfo )[0]
      pathinfo = Php.str_replace( "%", "%25", pathinfo )

      #list( req_uri ) = explode( '?', _SERVER['REQUEST_URI'] )
      req_uri = Php.explode( '?', _SERVER['REQUEST_URI'] )[0]
      self = _SERVER['PHP_SELF']
      home_path = trim( parse_url( home_url(), PHP_URL_PATH ), '/' )
      home_path_regex = sprintf( '|^%s|i', preg_quote( home_path, '|' ) )

      # Trim path info from the end and the leading home path from the
      # front. For path info requests, this leaves us with the requesting
      # filename, if any. For 404 requests, this leaves us with the
      # requested permalink.
      req_uri = Php.str_replace(pathinfo, '', req_uri)
      req_uri = trim(req_uri, '/')
      req_uri = preg_replace( home_path_regex, '', req_uri )
      req_uri = trim(req_uri, '/')
      pathinfo = trim(pathinfo, '/')
      pathinfo = preg_replace( home_path_regex, '', pathinfo )
      pathinfo = trim(pathinfo, '/')
      self = trim(self, '/')
      self = preg_replace( home_path_regex, '', self )
      self = trim(self, '/')

      # The requested permalink is in pathinfo for path info requests and
      #  req_uri for other requests.
      #if not Php.empty(locals(), 'pathinfo') and ...:
      if pathinfo and not Php.preg_match('|^.*' + wp_rewrite.index + '$|',
                                         pathinfo):
        requested_path = pathinfo
      else:
        # If the request uri is the index, blank it out so that we don't try to match it against a rule.
        if req_uri == wp_rewrite.index:
          req_uri = ''
        requested_path = req_uri

      requested_file = req_uri

      self.request = requested_path

      # Look for matches.
      request_match = requested_path
      if not request_match: #if Php.empty(locals(), 'request_match'):
        # An empty request could only match against ^$ regex
        if Php.isset(rewrite, '$'):
          self.matched_rule = '$'
          query = rewrite['$']
          matches = array('')
      else:
        for match, query in Php.Array( rewrite ).items():
          # If the requested file is the anchor of the match, prepend it to the path info.
          #if not Php.empty(locals(), 'requested_file') and ...:
          if requested_file and Php.strpos(match, requested_file) is 0 and requested_file != requested_path:
            request_match = requested_file + '/' + requested_path

          if ( Php.preg_match("#^{}#".format(match), request_match, matches) or
            Php.preg_match("#^{}#".format(match), urldecode(request_match), matches) ):

            if wp_rewrite.use_verbose_page_rules and Php.preg_match( '/pagename=\$matches\[([0-9]+)\]/', query, varmatch ):
              # This is a verbose page match, let's check to be sure about it.
              page = get_page_by_path( matches[ varmatch[1] ] )
              if not page:
                continue

              post_status_obj = get_post_status_object( page.post_status )
              if ( not post_status_obj.public and not post_status_obj.protected
                and not post_status_obj.private and post_status_obj.exclude_from_search ):
                continue

            # Got a match.
            self.matched_rule = match
            break

      if Php.isset(self, 'matched_rule'):
        # Trim the query of everything up to the '?'.
        query = preg_replace("!^.+\?!", '', query)

        # Substitute the substring matches into the query.
        query = Php.addslashes(WP_MatchesMapRegex.Apply(query, matches))

        self.matched_query = query

        # Parse the query.
        parse_str(query, perma_query_vars)

        # If we're processing a 404 request, clear the error var since we found something.
        if '404' == error:
          unset( error, _GET['error'] )

      # If req_uri is empty or if it is a request for ourself, unset error.
      #if Php.empty(locals(), 'requested_path') and ...:
      if not requested_path or requested_file == self or Php.strpos(_SERVER['PHP_SELF'], 'wp-admin/') is not False:
        unset( error, _GET['error'] )

        if ( Php.isset(locals(), 'perma_query_vars') and
            #Php.strpos(_SERVER['PHP_SELF'], 'wp-admin/') is not False ):
            'wp-admin/' not in _SERVER['PHP_SELF'] ):
          del perma_query_vars   # unset( perma_query_vars )

        self.did_permalink = False

    # Filters the query variables whitelist before processing.
    # Allows (publicly allowed) query vars to be added, removed, or changed prior
    # to executing the query. Needed to allow custom rewrite rules using your own arguments
    # to work, or any other custom query variables you want to be publicly available.
    # @param array public_query_vars The array of whitelisted query variables.
    self.public_query_vars = apply_filters( 'query_vars', self.public_query_vars )

    for post_type, t in get_post_types( array(), 'objects' ).items():
      if is_post_type_viewable( t ) and t.query_var:
        post_type_query_vars[t.query_var] = post_type

    for wpvar in self.public_query_vars:
      if Php.isset(self.extra_query_vars, wpvar):
        self.query_vars[wpvar] = self.extra_query_vars[wpvar]
      elif Php.isset(_POST, wpvar):
        self.query_vars[wpvar] = _POST[wpvar]
      elif Php.isset(_GET, wpvar):
        self.query_vars[wpvar] = _GET[wpvar]
      elif Php.isset(perma_query_vars, wpvar):
        self.query_vars[wpvar] = perma_query_vars[wpvar]

      if not Php.empty(self.query_vars, wpvar):
        if not Php.is_array( self.query_vars[wpvar] ):
          self.query_vars[wpvar] = str( self.query_vars[wpvar] )
        else:
          for vkey, v in self.query_vars[wpvar].items():
            if not is_object( v ):
              self.query_vars[wpvar][vkey] = str(v)

        if Php.isset(post_type_query_vars, wpvar):
          self.query_vars['post_type'] = post_type_query_vars[wpvar]
          self.query_vars['name'] = self.query_vars[wpvar]

    # Convert urldecoded spaces back into +
    for taxonomy, t in WiTx.get_taxonomies( array(), 'objects' ).items():
      if t.query_var and Php.isset(self.query_vars, t.query_var):
        self.query_vars[t.query_var] = Php.str_replace( ' ', '+',
                                                self.query_vars[t.query_var] )

    # Don't allow non-publicly queryable taxonomies to be queried from the
    #     front end.
    if not is_admin():
      for taxonomy, t in WiTx.get_taxonomies(
                  array( ('publicly_queryable', False) ), 'objects' ).items():
        # Disallow when set to the 'taxonomy' query var.
        # Non-publicly queryable taxonomies cannot register custom query
        #     vars. See register_taxonomy().
        if ( Php.isset(self.query_vars, 'taxonomy') and
             taxonomy == self.query_vars['taxonomy']):
          unset( self.query_vars['taxonomy'], self.query_vars['term'] )

    # Limit publicly queried post_types to those that are publicly_queryable
    if Php.isset(self.query_vars, 'post_type'):
      queryable_post_types = get_post_types( array(
                                             ('publicly_queryable', True)) )
      if not Php.is_array( self.query_vars['post_type'] ):
        if not Php.in_array( self.query_vars['post_type'],
                             queryable_post_types ):
          unset( self.query_vars['post_type'] )
      else:
        self.query_vars['post_type'] = array_intersect(
                          self.query_vars['post_type'], queryable_post_types )

    # Resolve conflicts between posts with numeric slugs and date archive queries.
    self.query_vars = wp_resolve_numeric_slug_conflicts( self.query_vars )

    for var in Php.Array( self.private_query_vars ):
      if Php.isset(self.extra_query_vars, var):
        self.query_vars[var] = self.extra_query_vars[var]

    if Php.isset(locals(), 'error'):
      self.query_vars['error'] = error

    # Filters the array of parsed query variables.
    # @param array query_vars The array of requested query variables.
    self.query_vars = apply_filters( 'request', self.query_vars )

    # Fires once all query variables for the current request have been parsed.
    # @param WP &self Current WordPress environment instance (passed by reference).
    WiPg.do_action_ref_array( 'parse_request', array( self ) ) # &self ) )


  def send_headers(self):
    ''' Sends additional HTTP headers for caching, content type, etc.
    Sets the Content-Type header. Sets the 'error' status (if passed) and optionally exits.
    If showing a feed, it will also send Last-Modified, ETag, and 304 status if needed.
    @since 4.4.0 `X-Pingback` header is added conditionally after posts have been queried in handle_404().
    @access public
    '''
    headers = array()    # array()
    status = None
    exit_required = False

    if is_user_logged_in():
      headers = array_merge(headers, wp_get_nocache_headers())
    if Php.empty(self.query_vars, 'error'):
      status = int( self.query_vars['error'] )
      if 404 == status:
        if not is_user_logged_in():
          headers = array_merge(headers, wp_get_nocache_headers())
        headers['Content-Type'] = get_option('html_type') + '; charset=' + get_option('blog_charset')
      elif Php.in_array( status, array( 403, 500, 502, 503 ) ):
        exit_required = True

    elif Php.empty(self.query_vars, 'feed'):
      headers['Content-Type'] = get_option('html_type') + '; charset=' + get_option('blog_charset')
    else:
      # Set the correct content type for feeds
      Type = self.query_vars['feed']
      if 'feed' == self.query_vars['feed']:
        Type = get_default_feed()

      headers['Content-Type'] = feed_content_type( Type ) + '; charset=' + get_option( 'blog_charset' )

      # We're showing a feed, so WP is indeed the only thing that last changed
      if ( not Php.empty(self.query_vars, 'withcomments')
        #or False !== strpos( self.query_vars['feed'], 'comments-' )
        or 'comments-' in self.query_vars['feed']
        or ( Php.empty( self.query_vars, 'withoutcomments' )
          and ( not Php.empty(self.query_vars, 'p')
            or not Php.empty(self.query_vars, 'name')
            or not Php.empty(self.query_vars, 'page_id')
            or not Php.empty(self.query_vars, 'pagename')
            or not Php.empty(self.query_vars, 'attachment')
            or not Php.empty(self.query_vars, 'attachment_id')
          )
        )
      ):
        wp_last_modified = mysql2date('D, d M Y H:i:s',
                                       get_lastcommentmodified('GMT'), False)
      else:
        wp_last_modified = mysql2date('D, d M Y H:i:s',
                                       get_lastpostmodified('GMT'), False)
      if not wp_last_modified:
        wp_last_modified = date( 'D, d M Y H:i:s' )
      wp_last_modified += ' GMT'

      wp_etag = '"' + md5(wp_last_modified) + '"'
      headers['Last-Modified'] = wp_last_modified
      headers['ETag'] = wp_etag

      # Support for Conditional GET
      if Php.isset(_SERVER, 'HTTP_IF_NONE_MATCH'):
        client_etag = WiF.wp_unslash( _SERVER['HTTP_IF_NONE_MATCH'] )
      else:
        client_etag = False

      client_last_modified = '' if Php.empty(_SERVER, 'HTTP_IF_MODIFIED_SINCE'
                                ) else trim(_SERVER['HTTP_IF_MODIFIED_SINCE'])
      # If string is empty, return 0. If not, attempt to parse into a timestamp
      client_modified_timestamp = strtotime(client_last_modified) if client_last_modified else 0

      # Make a timestamp for our most recent modification...
      wp_modified_timestamp = strtotime(wp_last_modified)

      if ( ((client_modified_timestamp >= wp_modified_timestamp) and (client_etag == wp_etag))
           if (client_last_modified and client_etag) else
           ((client_modified_timestamp >= wp_modified_timestamp) or (client_etag == wp_etag)) ):
        status = 304
        exit_required = True

    # Filters the HTTP headers before they're sent to the browser.
    # @param array headers The list of headers to be sent.
    # @param WP    self    Current WordPress environment instance.
    headers = apply_filters( 'wp_headers', headers, self )

    if status:  # if not Php.empty(locals(), 'status'):
      status_header( status )

    # If Last-Modified is set to False, it should not be sent (no-cache situation).
    if (Php.isset(headers, 'Last-Modified') and
        False is headers['Last-Modified'] ):
      Php.unset( headers, 'Last-Modified' )

      # In PHP 5.3+, make sure we are not sending a Last-Modified header.
      if function_exists( 'header_remove' ):
        #@header_remove( 'Last-Modified' )
        header_remove( 'Last-Modified' )
      else:
        # In PHP 5.2, send an empty Last-Modified header, but only as a
        # last resort to override a header already sent. #WP23021
        for header in headers_list():
          if 0 is stripos( header, 'Last-Modified' ):
            headers['Last-Modified'] = ''
            break

    for name, field_value in Php.Array( headers ).items():
      #@header(name +": "+ field_value)
      header(name +": "+ field_value)

    if exit_required:
      import sys
      sys.exit()

    # Fires once the requested HTTP headers for caching, content type, etc. have been sent.
    # @param WP &self Current WordPress environment instance (passed by reference).
    # remove & from &self since self won't get changed during func call
    WiPG.do_action_ref_array( 'send_headers',array( self ) ) # ( &self )


  def build_query_string(self):
    ''' Sets the query string property based off of the query variable property.
    The {@see 'query_string'} filter is deprecated, but still works. Plugins should
    use the {@see 'request'} filter instead.
    @access public
    '''
    self.query_string = ''
    for wpvar in Php.Array( Php.array_keys(self.query_vars) ):
      if '' != self.query_vars[wpvar]:
        self.query_string += '' if (strlen(self.query_string) < 1) else '&'
        if not is_scalar(self.query_vars[wpvar]): # Discard non-scalars.
          continue
        self.query_string += wpvar + '=' + rawurlencode(self.query_vars[wpvar])

    if has_filter( 'query_string' ):  # Don't bother filtering and parsing if no plugins are hooked in.
      # Filters the query string before parsing.
      # @deprecated 2.1.0 Use 'query_vars' or 'request' filters instead.
      # @param string query_string The query string to modify.
      self.query_string = apply_filters( 'query_string', self.query_string )
      parse_str(self.query_string, self.query_vars)


  def register_globals(self):
    ''' Set up the WordPress Globals.
    The query_vars property will be extracted to the GLOBALS. So care should
    be taken when naming global variables that might interfere with the
    WordPress environment.
    @access public
    @global WP_Query     wp_query
    @global string       query_string Query string for the loop.
    @global array        posts The found posts.
    @global WP_Post|None post The current post, if available.
    @global string       request The SQL statement for the request.
    @global int          more Only set, if single page or post.
    @global int          single If single page or post. Only set, if single page or post.
    @global WP_User      authordata Only set, if author archive.
    '''
    wp_query = WpC.WB.Wj.wp_query  # global wp_query
    GLOBALS = WpC.WB.Wj.__dict__  # global GLOBALS

    # Extract updated query vars back into global namespace.
    for key, value in Php.Array( wp_query.query_vars ).items():
      GLOBALS[ key ] = value

    GLOBALS['query_string'] = self.query_string
    #GLOBALS['posts'] = & wp_query.posts
    GLOBALS['posts'] = wp_query.posts  # array is mutable so won't need &
    #GLOBALS['post'] = wp_query.post if Php.isset(wp_query,'post') else None
    GLOBALS['post']  = getattr(wp_query, 'post', None)
    GLOBALS['request'] = wp_query.request

    if wp_query.is_single() or wp_query.is_page():
      GLOBALS['more']   = 1
      GLOBALS['single'] = 1

    if wp_query.is_author() and Php.isset( wp_query, 'post' ):
      GLOBALS['authordata'] = get_userdata( wp_query.post.post_author )


  def init(self):
    ''' Set up the current user.
    @access public
    '''
    wp_get_current_user()  #TODO


  def query_posts(self):
    ''' Set up the Loop based on the query variables.
    @access public
    @global WP_Query wp_the_query
    '''
    wp_the_query = WpC.WB.Wj.wp_the_query  # global wp_the_query
    self.build_query_string()
    wp_the_query.query(self.query_vars)


  def handle_404(self):
    ''' Set the Headers for 404, if nothing is found for requested URL.
    Issue a 404 if a request doesn't match any posts and doesn't match
    any object (e.g. an existing-but-empty category, tag, author) and a 404 was not already
    issued, and if the request was not a search or the homepage.
    Otherwise, issue a 200.
    This sets headers after posts have been queried. handle_404() really means "handle status."
    By inspecting the result of querying posts, seemingly successful requests can be switched to
    a 404 so that canonical redirection logic can kick in.
    # @access public
    @global WP_Query wp_query
    '''
    wp_query = WpC.WB.Wj.wp_query  # global wp_query

    # Filters whether to short-circuit default header status handling.
    # Returning a non-False value from the filter will short-circuit the handling
    # and return early.
    # @param bool     preempt  Whether to short-circuit default header status handling. Default False.
    # @param WP_Query wp_query WordPress Query object.
    if False is not apply_filters( 'pre_handle_404', False, wp_query ):
      return

    # If we've already issued a 404, bail.
    if is_404():
      return

    # Never 404 for the admin, robots, or if we found posts.
    if is_admin() or is_robots() or wp_query.posts:

      success = True
      if is_singular():
        p = False

        import wp.i.cls.post as WcP
        if isinstance(wp_query.post, WcP.WP_Post):
          p = Php.clone(wp_query.post)

        # Only set X-Pingback for single posts that allow pings.
        if p and pings_open( p ):
          #@header( 'X-Pingback: ' + get_bloginfo( 'pingback_url' ) )
          header( 'X-Pingback: ' + get_bloginfo( 'pingback_url', 'display' ) )

        # check for paged content that exceeds the max number of pages
        Next = '<!--nextpage-->'
        #if (p and False !== Php.strpos( p.post_content, Next ) and
        #    self.query_vars['page']):
        if ( p and Next in p.post_content and
             not Php.empty(self.query_vars, 'page') ):
          page = trim( self.query_vars['page'], '/' )
          success = int(page) <= ( substr_count( p.post_content, Next ) + 1 )

      if success:
        status_header( 200 )
        return

    # We will 404 for paged queries, as no posts were found.
    if not is_paged():

      # Don't 404 for authors without posts as long as they matched an author on self site.
      author = get_query_var( 'author' )
      if is_author() and is_numeric( author ) and author > 0 and is_user_member_of_blog( author ):
        status_header( 200 )
        return

      # Don't 404 for these queries if they matched an object.
      if ( is_tag() or is_category() or is_tax() or is_post_type_archive() ) and get_queried_object():
        status_header( 200 )
        return

      # Don't 404 for these queries either.
      if is_home() or is_search() or is_feed():
        status_header( 200 )
        return

    # Guess it's time to 404.
    wp_query.set_404()
    status_header( 404 )
    nocache_headers()


  def main(self, query_args = ''):
    ''' Sets up all of the variables required by the WordPress environment.
    The action {@see 'wp'} has one parameter that references the WP object. It
    allows for accessing the properties and methods to further manipulate the
    object.
    @access public
    @param string|array query_args Passed to parse_request().
    '''
    self.init()
    self.parse_request(query_args)
    self.send_headers()
    self.query_posts()
    self.handle_404()
    self.register_globals()

    # Fires once the WordPress environment has been set up.
    # @param WP &self Current WordPress environment instance (passed by reference).
    WiPg.do_action_ref_array( 'wp', array( self ) )   # ( &self ) )

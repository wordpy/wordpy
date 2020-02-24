import wp.conf        as WpC
import wp.i.cls.error as WcE  # WP_Error
#import wp.i.cls.rewrite   as WcR
import wp.i.format    as WiF
import wp.i.func      as WiFc
import wp.i.plugin    as WiPg
import wp.i.post      as WiP
import wp.i.l10n      as WiTr
import wp.i.option    as WiO
import wp.i.pluggable as WiPgbl
import pyx.php        as Php

array = Php.array

# WordPress Link Template Functions
# @package WordPress
# @subpackage Template

#def InitLinkTemplate(self):
#  "global var==>self.var, except: var=self.var=same Obj,mutable array"
#  #global wp_rewrite
#  #global Wj
#  #global paged, pagenow, is_IE, wp_version
#  #global wp_query
#  #wp_rewrite    = self.wp_rewrite
#  #Wj            = self

__, _x, _n_noop = WiTr.__, WiTr._x, WiTr._n_noop


def the_permalink( post = 0 ):
  ''' Displays the permalink for the current post.
  @since 4.4.0 Added the `post` parameter.
  @param int|WP_Post post Optional. Post ID or post object. Default is the global `post`.
  '''
  # Filters the display of the permalink for the current post.
  # @since 4.4.0 Added the `post` parameter.
  # @param string      permalink The permalink for the current post.
  # @param int|WP_Post post      Post ID, WP_Post object, or 0. Default 0.
  Php.echo( esc_url( WiPg.apply_filters( 'the_permalink', get_permalink( post ), post ) ))


def user_trailingslashit(string, type_of_url = ''):
  ''' Retrieves a trailing-slashed string if the site is set for adding trailing slashes.
  Conditionally adds a trailing slash if the permalink structure has a trailing
  slash, strips the trailing slash if not. The string is passed through the
  {@see 'user_trailingslashit'} filter. Will remove trailing slash from string, if
  site is not set to have them.
  @global WP_Rewrite wp_rewrite
  @param string string      URL with or without a trailing slash.
  @param string type_of_url Optional. The type of URL being considered (e.g. single, category, etc)
                             for use in the filter. Default empty string.
  @return string The URL with the trailing slash appended or stripped.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  if wp_rewrite.use_trailing_slashes:
    string = WiF.trailingslashit(string)
  else:
    string = WiF.untrailingslashit(string)

  # Filters the trailing-slashed string, depending on whether the site is set to use trailing slashes.
  # @param string string      URL with or without a trailing slash.
  # @param string type_of_url The type of URL being considered. Accepts 'single', 'single_trackback',
  #                           'single_feed', 'single_paged', 'commentpaged', 'paged', 'home', 'feed',
  #                           'category', 'page', 'year', 'month', 'day', 'post_type_archive'.
  return WiPg.apply_filters( 'user_trailingslashit', string, type_of_url )


def permalink_anchor( mode = 'id' ):
  ''' Displays the permalink anchor for the current post.
  The permalink mode title will use the post title for the 'a' element 'id'
  attribute. The id mode uses 'post-' with the post ID for the 'id' attribute.
  @param string mode Optional. Permalink mode. Accepts 'title' or 'id'. Default 'id'.
  '''
  post = WiP.get_post()
  if strtolower( mode ) == 'title':
    title = sanitize_title( post.post_title ) + '-' + str(post.ID)
    Php.echo( '<a id="'+title+'"></a>')
  else:   # if strtolower( mode ) == 'id':
    Php.echo( '<a id="post-' + str(post.ID) + '"></a>')


def get_the_permalink( post = 0, leavename = False ):
  ''' Retrieves the full permalink for the current post or post ID.
  This function is an alias for get_permalink().
  @see get_permalink()
  @param int|WP_Post post      Optional. Post ID or post object. Default is the global `post`.
  @param bool        leavename Optional. Whether to keep post name or page name. Default False.
  @return string|False The permalink URL or False if post does not exist.
  '''
  return get_permalink( post, leavename )


def get_permalink( post = 0, leavename = False ):
  '''
  Retrieves the full permalink for the current post or post ID.
  @param int|WP_Post post      Optional. Post ID or post object. Default is the global `post`.
  @param bool        leavename Optional. Whether to keep post name or page name. Default False.
  @return string|False The permalink URL or False if post does not exist.
  '''
  rewritecode = array(
    '%year%',
    '%monthnum%',
    '%day%',
    '%hour%',
    '%minute%',
    '%second%',
    '' if leavename else '%postname%',
    '%post_id%',
    '%category%',
    '%author%',
    '' if leavename else '%pagename%',
  )

  if Php.is_object( post ) and Php.isset( post, 'filter' ) and 'sample' == post.filter:
    sample = True
  else:
    post = WiP.get_post( post )
    sample = False

  if Php.empty(post, 'ID'):
    return False

  if post.post_type == 'page':
    return get_page_link(post, leavename, sample)
  elif post.post_type == 'attachment':
    return get_attachment_link( post, leavename )
  elif Php.in_array(post.post_type,
                    WiP.get_post_types( array(('_builtin', False),) ) ):
    return get_post_permalink(post, leavename, sample)

  permalink = WiO.get_option('permalink_structure')

  # Filters the permalink structure for a post before token replacement occurs.
  # Only applies to posts with post_type of 'post'.
  # @param string  permalink The site's permalink structure.
  # @param WP_Post post      The post in question.
  # @param bool    leavename Whether to keep the post name.
  permalink = WiPg.apply_filters( 'pre_post_link', permalink, post, leavename )

  if '' != permalink and not Php.in_array( post.post_status,
                         array('draft', 'pending', 'auto-draft', 'future') ):
    #unixtime = strtotime(post.post_date) #post_date = "2014-04-22 07:51:49"
    #DT= datetime.strptime(post.post_date, '%Y-%m-%d %H:%M:%S')
    DT = post.post_date     # already has type datetime.datetime

    category = ''
    if '%category%' in permalink:
      cats = get_the_category(post.ID)
      if cats:
        cats = WiFc.wp_list_sort( cats, array(
          ('term_id', 'ASC'),
        ) )

        #Filters the category that gets used in the %category% permalink token
        # @param WP_Term cat  The category to use in the permalink.
        # @param array   cats Array of all categories (WP_Term objects)
        #                     associated with the post
        # @param WP_Post post The post in question.
        category_object = WiPg.apply_filters( 'post_link_category', cats[0], cats, post )

        category_object = get_term( category_object, 'category' )
        category = category_object.slug
        parent = category_object.parent
        if parent:
          category = get_category_parents(parent, False, '/', True) + category

      # show default category in permalinks, without
      # having to assign it explicitly
      if Php.empty(locals(), 'category'):
        default_category = get_term( WiO.get_option( 'default_category' ), 'category' )
        if default_category and not WpC.WB.Wj.is_wp_error( default_category ):
          category = default_category.slug

    author = ''
    if '%author%' in permalink:
      authordata = get_userdata(post.post_author)
      author = authordata.user_nicename

    #date = explode(" ",date('Y m d H i s', unixtime))  # use DT=datetime above
    rewritereplace = array(
      #date[0], date[1],  date[2], date[3], date[4],   date[5],
      DT.year,  DT.month, DT.day,  DT.hour, DT.minute, DT.second,
      post.post_name,
      post.ID,
      category,
      author,
      post.post_name,
    )
    permalink = home_url( Php.str_replace(
                          rewritecode, rewritereplace, permalink) )
    permalink = user_trailingslashit(permalink, 'single')
  else:
    permalink = home_url('?p=' + str(post.ID))

  # Filters the permalink for a post.
  # Only applies to posts with post_type of 'post'.
  # @param string  permalink The post's permalink.
  # @param WP_Post post      The post in question.
  # @param bool    leavename Whether to keep the post name.
  return WiPg.apply_filters( 'post_link', permalink, post, leavename )


def get_post_permalink( Id = 0, leavename = False, sample = False ):
  '''
  Retrieves the permalink for a post of a custom post type.
  @global WP_Rewrite wp_rewrite
  @param int Id         Optional. Post ID. Default uses the global `post`.
  @param bool leavename Optional, defaults to False. Whether to keep post name. Default False.
  @param bool sample    Optional, defaults to False. Is it a sample permalink. Default False.
  @return string|WP_Error The post permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  post = WiP.get_post(Id)

  if WpC.WB.Wj.is_wp_error( post ):
    return post

  post_link = wp_rewrite.get_extra_permastruct(post.post_type)

  slug = post.post_name

  draft_or_pending = WiP.get_post_status( Id ) and Php.in_array( WiP.get_post_status( Id ), array( 'draft', 'pending', 'auto-draft', 'future' ) )

  post_type = WiP.get_post_type_object(post.post_type)

  if post_type.hierarchical:
    slug = WiP.get_page_uri( Id )
  

  if not Php.empty(locals(), 'post_link') and ( not draft_or_pending or sample ):
    if not  leavename:
      post_link = Php.str_replace("%{}%".format(post.post_type), slug, post_link)
    post_link = home_url( user_trailingslashit(post_link) )
  else:
    if post_type.query_var and ( Php.isset(post, 'post_status') and not draft_or_pending ):
      post_link = add_query_arg(post_type.query_var, slug, '')
    else:
      post_link = add_query_arg( array( ('post_type', post.post_type),
                                         ('p', post.ID) ), '')
    post_link = home_url(post_link)

  # Filters the permalink for a post of a custom post type.
  # @param string  post_link The post's permalink.
  # @param WP_Post post      The post in question.
  # @param bool    leavename Whether to keep the post name.
  # @param bool    sample    Is it a sample permalink.
  return WiPg.apply_filters( 'post_type_link', post_link, post, leavename, sample )


def get_page_link( post = False, leavename = False, sample = False ):
  '''
  Retrieves the permalink for the current page or page ID.
  Respects page_on_front. Use this one.
  @param int|WP_Post post      Optional. Post ID or object. Default uses the global `post`.
  @param bool        leavename Optional. Whether to keep the page name. Default False.
  @param bool        sample    Optional. Whether it should be treated as a sample permalink.
                                Default False.
  @return string The page permalink.
  '''
  post = WiP.get_post( post )

  if ('page'  == WiO.get_option( 'show_on_front' ) and
      post.ID == WiO.get_option( 'page_on_front' )    ):
    link = home_url('/')
  else:
    link = _get_page_link( post, leavename, sample )

  # Filters the permalink for a page.
  # @param string link    The page's permalink.
  # @param int    post_id The ID of the page.
  # @param bool   sample  Is it a sample permalink.
  return WiPg.apply_filters( 'page_link', link, post.ID, sample )


def _get_page_link( post = False, leavename = False, sample = False ):
  ''' Retrieves the page permalink.
  Ignores page_on_front. Internal use only.
  @access private
  @global WP_Rewrite wp_rewrite
  @param int|WP_Post post      Optional. Post ID or object. Default uses the global `post`.
  @param bool        leavename Optional. Whether to keep the page name. Default False.
  @param bool        sample    Optional. Whether it should be treated as a sample permalink.
                                Default False.
  @return string The page permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  post = WiP.get_post( post )

  draft_or_pending = Php.in_array( post.post_status, array( 'draft', 'pending', 'auto-draft' ) )

  link = wp_rewrite.get_page_permastruct()

  if not Php.empty(locals(), 'link') and ( ( Php.isset(post, 'post_status') and not draft_or_pending ) or sample ):
    if not leavename:
      link = Php.str_replace('%pagename%', WiP.get_page_uri( post ), link)

    link = home_url(link)
    link = user_trailingslashit(link, 'page')
  else:
    link = home_url( '?page_id=' + str(post.ID) )

  # Filters the permalink for a non-page_on_front page.
  # @param string link    The page's permalink.
  # @param int    post_id The ID of the page.
  return WiPg.apply_filters( '_get_page_link', link, post.ID )


def get_attachment_link( post = None, leavename = False ):
  ''' Retrieves the permalink for an attachment.
  This can be used in the WordPress Loop or outside of it.
  @global WP_Rewrite wp_rewrite
  @param int|object post      Optional. Post ID or object. Default uses the global `post`.
  @param bool       leavename Optional. Whether to keep the page name. Default False.
  @return string The attachment permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  link = False

  post = WiP.get_post( post )
  parent = WiP.get_post( post.post_parent ) if ( post.post_parent > 0 and post.post_parent != post.ID ) else False
  if parent and not Php.in_array( parent.post_type, WiP.get_post_types() ):
    parent = False

  if wp_rewrite.using_permalinks() and parent:
    if 'page' == parent.post_ty:
      parentlink = _get_page_link( post.post_parent ); # Ignores page_on_front
    else:
      parentlink = get_permalink( post.post_parent )

    if is_numeric(post.post_name) or '%category%' in WiO.get_option('permalink_structure'):
      name = 'attachment/' + post.post_name; # <permalink>/<int>/ is paged so we use the explicit attachment marker
    else:
      name = post.post_name

    if '?' not in parentlink:
      link = user_trailingslashit( WiF.trailingslashit(parentlink) + '%postname%' )

    if not leavename:
      link = Php.str_replace( '%postname%', name, link )
  elif wp_rewrite.using_permalinks() and not leavename:
    link = home_url( user_trailingslashit( post.post_name ) )

  if not link:
    link = home_url( '/?attachment_id=' + str(post.ID) )

  # Filters the permalink for an attachment.
  # @param string link    The attachment's permalink.
  # @param int    post_id Attachment ID.
  return WiPg.apply_filters( 'attachment_link', link, post.ID )


def get_year_link( year ):
  ''' Retrieves the permalink for the year archives.
  @global WP_Rewrite wp_rewrite
  @param int|bool year False for current year or year for permalink.
  @return string The permalink for the specified year archive.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  if not year:
    year = gmdate('Y', current_time('timestamp'))
  yearlink = wp_rewrite.get_year_permastruct()
  if not Php.empty(locals(), 'yearlink'):
    yearlink = Php.str_replace('%year%', year, yearlink)
    yearlink = home_url( user_trailingslashit( yearlink, 'year' ) )
  else:
    yearlink = home_url( '?m=' + year )

  # Filters the year archive permalink.
  # @param string yearlink Permalink for the year archive.
  # @param int    year     Year for the archive.
  return WiPg.apply_filters( 'year_link', yearlink, year )


def get_month_link(year, month):
  ''' Retrieves the permalink for the month archives with year.
  @global WP_Rewrite wp_rewrite
  @param bool|int year  False for current year. Integer of year.
  @param bool|int month False for current month. Integer of month.
  @return string The permalink for the specified month and year archive.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  if not year:
    year = gmdate('Y', current_time('timestamp'))
  if not month:
    month = gmdate('m', current_time('timestamp'))
  monthlink = wp_rewrite.get_month_permastruct()
  if not Php.empty(locals(), 'monthlink'):
    monthlink = Php.str_replace('%year%', year, monthlink)
    monthlink = Php.str_replace('%monthnum%', zeroise(intval(month), 2), monthlink)
    monthlink = home_url( user_trailingslashit( monthlink, 'month' ) )
  else:
    monthlink = home_url( '?m=' + year + zeroise( month, 2 ) )

  # Filters the month archive permalink.
  # @param string monthlink Permalink for the month archive.
  # @param int    year      Year for the archive.
  # @param int    month     The month for the archive.
  return WiPg.apply_filters( 'month_link', monthlink, year, month )


def get_day_link(year, month, day):
  ''' Retrieves the permalink for the day archives with year and month.
  @global WP_Rewrite wp_rewrite
  @param bool|int year  False for current year. Integer of year.
  @param bool|int month False for current month. Integer of month.
  @param bool|int day   False for current day. Integer of day.
  @return string The permalink for the specified day, month, and year archive.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  if not year:
    year = gmdate('Y', current_time('timestamp'))
  if not month:
    month = gmdate('m', current_time('timestamp'))
  if not day:
    day = gmdate('j', current_time('timestamp'))

  daylink = wp_rewrite.get_day_permastruct()
  if not Php.empty(locals(), 'daylink'):
    daylink = Php.str_replace('%year%', year, daylink)
    daylink = Php.str_replace('%monthnum%', zeroise(intval(month), 2), daylink)
    daylink = Php.str_replace('%day%', zeroise(intval(day), 2), daylink)
    daylink = home_url( user_trailingslashit( daylink, 'day' ) )
  else:
    daylink = home_url( '?m=' + year + zeroise( month, 2 ) + zeroise( day, 2 ) )

  # Filters the day archive permalink.
  # @param string daylink Permalink for the day archive.
  # @param int    year    Year for the archive.
  # @param int    month   Month for the archive.
  # @param int    day     The day for the archive.
  return WiPg.apply_filters( 'day_link', daylink, year, month, day )


def the_feed_link( anchor, feed = '' ):
  ''' Displays the permalink for the feed type.
  @param string anchor The link's anchor text.
  @param string feed   Optional. Feed type. Default empty.
  '''
  link = '<a href="' + esc_url( get_feed_link( feed ) ) + '">' + anchor + '</a>'

  # Filters the feed link anchor tag.
  # @param string link The complete anchor tag for a feed link.
  # @param string feed The feed type, or an empty string for the
  #                     default feed type.
  Php.echo( WiPg.apply_filters( 'the_feed_link', link, feed ))


def get_feed_link( feed = '' ):
  ''' Retrieves the permalink for the feed type.
  @global WP_Rewrite wp_rewrite
  @param string feed Optional. Feed type. Default empty.
  @return string The feed permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  permalink = wp_rewrite.get_feed_permastruct()
  if '' != permalink:
    if 'comments_' in feed:
      feed = Php.str_replace('comments_', '', feed)
      permalink = wp_rewrite.get_comment_feed_permastruct()

    if get_default_feed() == feed:
      feed = ''

    permalink = Php.str_replace('%feed%', feed, permalink)
    permalink = Php.preg_replace('#/+#', '/', "/"+ permalink)
    output =  home_url( user_trailingslashit(permalink, 'feed') )
  else:
    if Php.empty(locals(), 'feed'):
      feed = get_default_feed()

    if 'comments_' in feed:
      feed = Php.str_replace('comments_', 'comments-', feed)

    output = home_url("?feed="+ feed)

  # Filters the feed type permalink.
  # @param string output The feed permalink.
  # @param string feed   Feed type.
  return WiPg.apply_filters( 'feed_link', output, feed )


def get_post_comments_feed_link( post_id = 0, feed = '' ):
  ''' Retrieves the permalink for the post comments feed.
  @param int    post_id Optional. Post ID. Default is the ID of the global `post`.
  @param string feed    Optional. Feed type. Default empty.
  @return string The permalink for the comments feed for the given post.
  '''
  post_id = absint( post_id )

  if not post_id:
    post_id = get_the_ID()

  if Php.empty(locals(),  'feed' ):
    feed = get_default_feed()

  post = WiP.get_post( post_id )
  unattached = 'attachment' == post.post_type and 0 == int(post.post_parent)

  if '' != WiO.get_option('permalink_structure'):
    if 'page' == WiO.get_option('show_on_front') and post_id == WiO.get_option('page_on_front'):
      url = _get_page_link( post_id )
    else:
      url = get_permalink(post_id)

    if unattached:
      url =  home_url( '/feed/' )
      if feed != get_default_feed():
        url += feed +"/"
      url = add_query_arg( 'attachment_id', post_id, url )
    else:
      url = WiF.trailingslashit(url) + 'feed'
      if feed != get_default_feed():
        url += "/"+ feed
      url = user_trailingslashit(url, 'single_feed')
  else:
    if unattached:
      url = add_query_arg( array( ('feed', feed), ('attachment_id', post_id) ), home_url( '/' ) )
    elif 'page' == post.post_type:
      url = add_query_arg( array( ('feed', feed), ('page_id', post_id) ), home_url( '/' ) )
    else:
      url = add_query_arg( array( ('feed', feed), ('p', post_id) ), home_url( '/' ) )

  # Filters the post comments feed permalink.
  # @param string url Post comments feed permalink.
  return WiPg.apply_filters( 'post_comments_feed_link', url )


def post_comments_feed_link( link_text = '', post_id = '', feed = '' ):
  ''' Displays the comment feed link for a post.
  Prints out the comment feed link for a post. Link text is placed in the
  anchor. If no link text is specified, default text is used. If no post ID is
  specified, the current post is used.
  @param string link_text Optional. Descriptive link text. Default 'Comments Feed'.
  @param int    post_id   Optional. Post ID. Default is the ID of the global `post`.
  @param string feed      Optional. Feed format. Default empty.
  '''
  url = get_post_comments_feed_link( post_id, feed )
  if Php.empty(locals(),  'link_text' ):
    link_text = __('Comments Feed')

  link = '<a href="' + esc_url( url ) + '">' + link_text + '</a>'
  # Filters the post comment feed link anchor tag.
  # @param string link    The complete anchor tag for the comment feed link.
  # @param int    post_id Post ID.
  # @param string feed    The feed type, or an empty string for the default feed type.
  Php.echo( WiPg.apply_filters( 'post_comments_feed_link_html', link, post_id, feed ))


def get_author_feed_link( author_id, feed = '' ):
  ''' Retrieves the feed link for a given author.
  Returns a link to the feed for all posts by a given author. A specific feed
  can be requested or left blank to get the default feed.
  @param int    author_id Author ID.
  @param string feed      Optional. Feed type. Default empty.
  @return string Link to the feed for the author specified by author_id.
  '''
  author_id = int(author_id)
  permalink_structure = WiO.get_option('permalink_structure')

  if Php.empty(locals(), 'feed'):
    feed = get_default_feed()

  if '' == permalink_structure:
    link = home_url("?feed="+ feed +"&amp;author=" + author_id)
  else:
    link = get_author_posts_url(author_id)
    if feed == get_default_feed():
      feed_link = 'feed'
    else:
      feed_link = "feed/"+ feed

    link = WiF.trailingslashit(link) + user_trailingslashit(feed_link, 'feed')

  # Filters the feed link for a given author.
  # @param string link The author feed link.
  # @param string feed Feed type.
  link = WiPg.apply_filters( 'author_feed_link', link, feed )

  return link


def get_category_feed_link( cat_id, feed = '' ):
  ''' Retrieves the feed link for a category.
  Returns a link to the feed for all posts in a given category. A specific feed
  can be requested or left blank to get the default feed.
  @param int    cat_id Category ID.
  @param string feed   Optional. Feed type. Default empty.
  @return string Link to the feed for the category specified by cat_id.
  '''
  return get_term_feed_link( cat_id, 'category', feed )


def get_term_feed_link( term_id, taxonomy = 'category', feed = '' ):
  ''' Retrieves the feed link for a term.
  Returns a link to the feed for all posts in a given term. A specific feed
  can be requested or left blank to get the default feed.
  @param int    term_id  Term ID.
  @param string taxonomy Optional. Taxonomy of `term_id`. Default 'category'.
  @param string feed     Optional. Feed type. Default empty.
  @return string|False Link to the feed for the term specified by term_id and taxonomy.
  '''
  term_id = int(term_id)

  term = get_term( term_id, taxonomy  )

  if Php.empty(locals(),  'term' ) or WpC.WB.Wj.is_wp_error( term ):
    return False

  if Php.empty(locals(),  'feed' ):
    feed = get_default_feed()

  permalink_structure = WiO.get_option( 'permalink_structure' )

  if '' == permalink_structure:
    if 'category' == taxonomy:
      link = home_url("?feed={}&amp;cat={}".format(feed, term_id))
    elif 'post_tag' == taxonomy:
      link = home_url("?feed={}&amp;tag={}".format(feed, term.slug))
    else:
      t = get_taxonomy( taxonomy )
      link = home_url("?feed={}&amp;{}={}".format(feed, t.query_var, term.slug))
  else:
    link = get_term_link( term_id, term.taxonomy )
    if feed == get_default_feed():
      feed_link = 'feed'
    else:
      feed_link = "feed/"+ feed

    link = WiF.trailingslashit( link ) + user_trailingslashit( feed_link, 'feed' )

  if 'category' == taxonomy:
    # Filters the category feed link.
    # @param string link The category feed link.
    # @param string feed Feed type.
    link = WiPg.apply_filters( 'category_feed_link', link, feed )
  elif 'post_tag' == taxonomy:
    # Filters the post tag feed link.
    # @param string link The tag feed link.
    # @param string feed Feed type.
    link = WiPg.apply_filters( 'tag_feed_link', link, feed )
  else:
    # Filters the feed link for a taxonomy other than 'category' or 'post_tag'.
    # @param string link The taxonomy feed link.
    # @param string feed Feed type.
    # @param string feed The taxonomy name.
    link = WiPg.apply_filters( 'taxonomy_feed_link', link, feed, taxonomy )

  return link


def get_tag_feed_link( tag_id, feed = '' ):
  ''' Retrieves the permalink for a tag feed.
  @param int    tag_id Tag ID.
  @param string feed   Optional. Feed type. Default empty.
  @return string The feed permalink for the given tag.
  '''
  return get_term_feed_link( tag_id, 'post_tag', feed )


def get_edit_tag_link( tag_id, taxonomy = 'post_tag' ):
  ''' Retrieves the edit link for a tag.
  @param int    tag_id   Tag ID.
  @param string taxonomy Optional. Taxonomy slug. Default 'post_tag'.
  @return string The edit tag link URL for the given tag.
  '''
  # Filters the edit link for a tag (or term in another taxonomy).
  # @param string link The term edit link.
  return WiPg.apply_filters( 'get_edit_tag_link', get_edit_term_link( tag_id, taxonomy ) )


def edit_tag_link( link = '', before = '', after = '', tag = None ):
  ''' Displays or retrieves the edit link for a tag with formatting.
  @param string  link   Optional. Anchor text. Default empty.
  @param string  before Optional. Display before edit link. Default empty.
  @param string  after  Optional. Display after edit link. Default empty.
  @param WP_Term tag    Optional. Term object. If None, the queried object will be inspected.
                         Default None.
  '''
  link = edit_term_link( link, '', '', tag, False )

  # Filters the anchor tag for the edit link for a tag (or term in another taxonomy).
  # @param string link The anchor tag for the edit link.
  Php.echo( before + WiPg.apply_filters( 'edit_tag_link', link ) + after)


def get_edit_term_link( term_id, taxonomy = '', object_type = '' ):
  ''' Retrieves the URL for editing a given term.
  @since 4.5.0 The `taxonomy` argument was made optional.
  @param int    term_id     Term ID.
  @param string taxonomy    Optional. Taxonomy. Defaults to the taxonomy of the term identified
                             by `term_id`.
  @param string object_type Optional. The object type. Used to highlight the proper post type
                             menu on the linked page. Defaults to the first object_type associated
                             with the taxonomy.
  @return string|None The edit term link URL for the given term, or None on failure.
  '''
  term = get_term( term_id, taxonomy )
  if not term or WpC.WB.Wj.is_wp_error( term ):
    return

  tax = get_taxonomy( term.taxonomy )
  #if not tax or not current_user_can( tax.cap.edit_terms ):
  if not tax or not current_user_can( 'edit_term', term.term_id ):
    return

  args = array(
      ('taxonomy', taxonomy),
      ('tag_ID'  , term.term_id),
  )

  if object_type:
    args['post_type'] = object_type
  elif not Php.empty( tax, 'object_type' ):
    args['post_type'] = reset( tax.object_type )

  if tax.show_ui:
    location = add_query_arg( args, admin_url( 'term.php' ) )
  else:
    location = ''

  # Filters the edit link for a term.
  # @param string location    The edit link.
  # @param int    term_id     Term ID.
  # @param string taxonomy    Taxonomy name.
  # @param string object_type The object type (eg. the post type).
  return WiPg.apply_filters( 'get_edit_term_link', location, term_id, taxonomy, object_type )


def edit_term_link( link = '', before = '', after = '', term = None, echo = True ):
  ''' Displays or retrieves the edit term link with formatting.
  @param string link   Optional. Anchor text. Default empty.
  @param string before Optional. Display before edit link. Default empty.
  @param string after  Optional. Display after edit link. Default empty.
  @param object term   Optional. Term object. If None, the queried object will be inspected. Default None.
  @param bool   echo   Optional. Whether or not to echo the return. Default True.
  @return string|void HTML content.
  '''
  if is_null( term ):
    term = get_queried_object()

  if not term:
    return

  tax = get_taxonomy( term.taxonomy )
  #if not current_user_can( tax.cap.edit_terms ):
  if not current_user_can( 'edit_term', term.term_id ):
    return

  if Php.empty(locals(),  'link' ):
    link = __('Edit This')

  link = '<a href="' + get_edit_term_link( term.term_id, term.taxonomy ) + '">' + link + '</a>'

  # Filters the anchor tag for the edit link of a term.
  # @param string link    The anchor tag for the edit link.
  # @param int    term_id Term ID.
  link = before + WiPg.apply_filters( 'edit_term_link', link, term.term_id ) + after

  if echo:
    Php.echo(link)
  else:
    return link


def get_search_link( query = '' ):
  ''' Retrieves the permalink for a search.
  @global WP_Rewrite wp_rewrite
  @param string query Optional. The query string to use. If empty the current query is used. Default empty.
  @return string The search permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  if Php.empty(locals(), 'query'):
    search = get_search_query( False )
  else:
    search = stripslashes(query)

  permastruct = wp_rewrite.get_search_permastruct()

  if Php.empty(locals(),  'permastruct' ):
    link = home_url('?s=' + urlencode(search) )
  else:
    search = urlencode(search)
    search = Php.str_replace('%2F', '/', search); # %2F(/) is not valid within a URL, send it un-encoded.
    link = Php.str_replace( '%search%', search, permastruct )
    link = home_url( user_trailingslashit( link, 'search' ) )

  # Filters the search permalink.
  # @param string link   Search permalink.
  # @param string search The URL-encoded search term.
  return WiPg.apply_filters( 'search_link', link, search )


def get_search_feed_link(search_query = '', feed = ''):
  ''' Retrieves the permalink for the search results feed.
  @global WP_Rewrite wp_rewrite
  @param string search_query Optional. Search query. Default empty.
  @param string feed         Optional. Feed type. Default empty.
  @return string The search results feed permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  link = get_search_link(search_query)

  if Php.empty(locals(), 'feed'):
    feed = get_default_feed()

  permastruct = wp_rewrite.get_search_permastruct()

  if Php.empty(locals(), 'permastruct'):
    link = add_query_arg('feed', feed, link)
  else:
    link = WiF.trailingslashit(link)
    link += "feed/{}/".format(feed)

  # Filters the search feed link.
  # @param string link Search feed link.
  # @param string feed Feed type.
  # @param string type The search type. One of 'posts' or 'comments'.
  return WiPg.apply_filters( 'search_feed_link', link, feed, 'posts' )


def get_search_comments_feed_link(search_query = '', feed = ''):
  ''' Retrieves the permalink for the search results comments feed.
  @global WP_Rewrite wp_rewrite
  @param string search_query Optional. Search query. Default empty.
  @param string feed         Optional. Feed type. Default empty.
  @return string The comments feed search results permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  if Php.empty(locals(), 'feed'):
    feed = get_default_feed()

  link = get_search_feed_link(search_query, feed)

  permastruct = wp_rewrite.get_search_permastruct()

  if Php.empty(locals(), 'permastruct'):
    link = add_query_arg('feed', 'comments-' + feed, link)
  else:
    link = add_query_arg('withcomments', 1, link)

  # This filter is documented in wp-includes/link-template.php
  return WiPg.apply_filters( 'search_feed_link', link, feed, 'comments' )


def get_post_type_archive_link( post_type ):
  ''' Retrieves the permalink for a post type archive.
  @since 4.5.0 Support for posts was added.
  @global WP_Rewrite wp_rewrite
  @param string post_type Post type.
  @return string|False The post type archive permalink.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  post_type_obj = WiP.get_post_type_object( post_type )
  if not post_type_obj:
    return False

  if 'post' == post_type:
    show_on_front = WiO.get_option( 'show_on_front' )
    page_for_posts  = WiO.get_option( 'page_for_posts' )

    if 'page' == show_on_front and page_for_posts:
      link = get_permalink( page_for_posts )
    else:
      link = get_home_url()
    # This filter is documented in wp-includes/link-template.php
    return WiPg.apply_filters( 'post_type_archive_link', link, post_type )

  if not post_type_obj.has_archive:
    return False

  if WiO.get_option( 'permalink_structure' ) and Php.is_array( post_type_obj.rewrite ):
    struct = post_type_obj.rewrite['slug'] if ( True is post_type_obj.has_archive ) else post_type_obj.has_archive
    if post_type_obj.rewrite['with_front']:
      struct = wp_rewrite.front + struct
    else:
      struct = wp_rewrite.root + struct
    link = home_url( user_trailingslashit( struct, 'post_type_archive' ) )
  else:
    link = home_url( '?post_type=' + post_type )

  # Filters the post type archive permalink.
  # @param string link      The post type archive permalink.
  # @param string post_type Post type name.
  return WiPg.apply_filters( 'post_type_archive_link', link, post_type )


def get_post_type_archive_feed_link( post_type, feed = '' ):
  ''' Retrieves the permalink for a post type archive feed.
  @param string post_type Post type
  @param string feed      Optional. Feed type. Default empty.
  @return string|False The post type feed permalink.
  '''
  default_feed = get_default_feed()
  if Php.empty(locals(),  'feed' ):
    feed = default_feed

  link = get_post_type_archive_link( post_type )
  if not link:
    return False

  post_type_obj = WiP.get_post_type_object( post_type )
  if WiO.get_option( 'permalink_structure' ) and Php.is_array( post_type_obj.rewrite ) and post_type_obj.rewrite['feeds']:
    link = WiF.trailingslashit( link )
    link += 'feed/'
    if feed != default_feed:
      link += feed +"/"
  else:
    link = add_query_arg( 'feed', feed, link )

  # Filters the post type archive feed link.
  # @param string link The post type archive feed link.
  # @param string feed Feed type.
  return WiPg.apply_filters( 'post_type_archive_feed_link', link, feed )


def get_preview_post_link( post = None, query_args = array(), preview_link = '' ):
  ''' Retrieves the URL used for the post preview.
  Allows additional query args to be appended.
  @param int|WP_Post post         Optional. Post ID or `WP_Post` object. Defaults to global `post`.
  @param array       query_args   Optional. Array of additional query args to be appended to the link.
                                   Default empty array.
  @param string      preview_link Optional. Base preview link to be used if it should differ from the
                                   post permalink. Default empty.
  @return string|None URL used for the post preview, or None if the post does not exist.
  '''
  post = WiP.get_post( post )
  if not post:
    return

  post_type_object = WiP.get_post_type_object( post.post_type )
  if is_post_type_viewable( post_type_object ):
    if not preview_link:
      preview_link = set_url_scheme( get_permalink( post ) )

    query_args['preview'] = 'True'
    preview_link = add_query_arg( query_args, preview_link )

  # Filters the URL used for a post preview.
  # @since 4.0.0 Added the `post` parameter.
  # @param string  preview_link URL used for the post preview.
  # @param WP_Post post         Post object.
  return WiPg.apply_filters( 'preview_post_link', preview_link, post )


def get_edit_post_link( Id = 0, context = 'display' ):
  ''' Retrieves the edit post link for post.
  Can be used within the WordPress loop or outside of it. Can be used with
  pages, posts, attachments, and revisions.
  @param int    Id      Optional. Post ID. Default is the ID of the global `post`.
  @param string context Optional. How to output the '&' character. Default '&amp;'.
  @return string|None The edit post link for the given post. None if the post type is invalid or does
                      not allow an editing UI.
  '''
  post = WiP.get_post( Id )
  if not post:
    return

  if 'revision' == post.post_type:
    action = ''
  elif 'display' == context:
    action = '&amp;action=edit'
  else:
    action = '&action=edit'

  post_type_object = WiP.get_post_type_object( post.post_type )
  if not post_type_object:
    return

  if not current_user_can( 'edit_post', post.ID ):
    return

  if post_type_object._edit_link:
    link = admin_url( Php.sprintf( post_type_object._edit_link + action, post.ID ) )
  else:
    link = ''

  # Filters the post edit link.
  # @param string link    The edit link.
  # @param int    post_id Post ID.
  # @param string context The link context. If set to 'display' then ampersands
  #                        are encoded.
  return WiPg.apply_filters( 'get_edit_post_link', link, post.ID, context )


def edit_post_link( text = None, before = '', after = '', Id = 0, Class = 'post-edit-link' ):
  ''' Displays the edit post link for post.
  @since 4.4.0 The `Class` argument was added.
  @param string text   Optional. Anchor text. If None, default is 'Edit This'. Default None.
  @param string before Optional. Display before edit link. Default empty.
  @param string after  Optional. Display after edit link. Default empty.
  @param int    Id     Optional. Post ID. Default is the ID of the global `post`.
  @param string Class  Optional. Add custom Class to link. Default 'post-edit-link'.
  '''
  post = WiP.get_post( Id )
  if not post:
    return

  url = get_edit_post_link( post.ID )
  if not url:
    return

  if None is text:
    text = __( 'Edit This' )

  link = '<a class="' + esc_attr( Class ) + '" href="' + esc_url( url ) + '">' + text + '</a>'

  # Filters the post edit link anchor tag.
  # @param string link    Anchor tag for the edit link.
  # @param int    post_id Post ID.
  # @param string text    Anchor text.
  Php.echo( before + WiPg.apply_filters( 'edit_post_link', link, post.ID, text ) + after)


def get_delete_post_link( Id = 0, deprecated = '', force_delete = False ):
  ''' Retrieves the delete posts link for post.
  Can be used within the WordPress loop or outside of it, with any post type.
  @param int    Id           Optional. Post ID. Default is the ID of the global `post`.
  @param string deprecated   Not used.
  @param bool   force_delete Optional. Whether to bypass trash and force deletion. Default False.
  @return string|void The delete post link URL for the given post.
  '''
  if not Php.empty(locals(),  'deprecated' ):
    _deprecated_argument( __FUNCTION__, '3.0.0' )

  post = WiP.get_post( Id )
  if not post:
    return

  post_type_object = WiP.get_post_type_object( post.post_type )
  if not post_type_object:
    return

  if not current_user_can( 'delete_post', post.ID ):
    return

  action = 'delete' if ( force_delete or not EMPTY_TRASH_DAYS ) else 'trash'

  delete_link = add_query_arg( 'action', action, admin_url( Php.sprintf( post_type_object._edit_link, post.ID ) ) )

  # Filters the post delete link.
  # @param string link         The delete link.
  # @param int    post_id      Post ID.
  # @param bool   force_delete Whether to bypass the trash and force deletion. Default False.
  return WiPg.apply_filters( 'get_delete_post_link', wp_nonce_url( delete_link, "action-post_"+ str(post.ID) ), post.ID, force_delete )


def get_edit_comment_link( comment_id = 0 ):
  ''' Retrieves the edit comment link.
  @param int|WP_Comment comment_id Optional. Comment ID or WP_Comment object.
  @return string|void The edit comment link URL for the given comment.
  '''
  comment = get_comment( comment_id )

  if not current_user_can( 'edit_comment', comment.comment_ID ):
    return

  location = admin_url('comment.php?action=editcomment&amp;c=') + comment.comment_ID

  # Filters the comment edit link.
  # @param string location The edit link.
  return WiPg.apply_filters( 'get_edit_comment_link', location )


def edit_comment_link( text = None, before = '', after = '' ):
  ''' Displays the edit comment link with formatting.
  @param string text   Optional. Anchor text. If None, default is 'Edit This'. Default None.
  @param string before Optional. Display before edit link. Default empty.
  @param string after  Optional. Display after edit link. Default empty.
  '''
  comment = get_comment()

  if not current_user_can( 'edit_comment', comment.comment_ID ):
    return

  if None is text:
    text = __( 'Edit This' )

  link = '<a class="comment-edit-link" href="' + esc_url( get_edit_comment_link( comment ) ) + '">' + text + '</a>'

  # Filters the comment edit link anchor tag.
  # @param string link       Anchor tag for the edit link.
  # @param int    comment_id Comment ID.
  # @param string text       Anchor text.
  Php.echo( before + WiPg.apply_filters( 'edit_comment_link', link, comment.comment_ID, text ) + after)


def get_edit_bookmark_link( link = 0 ):
  ''' Displays the edit bookmark link.
  @param int|stdClass link Optional. Bookmark ID. Default is the Id of the current bookmark.
  @return string|void The edit bookmark link URL.
  '''
  link = get_bookmark( link )

  if not current_user_can('manage_links'):
    return

  location = admin_url('link.php?action=edit&amp;link_id=') + link.link_id

  # Filters the bookmark edit link.
  # @param string location The edit link.
  # @param int    link_id  Bookmark ID.
  return WiPg.apply_filters( 'get_edit_bookmark_link', location, link.link_id )


def edit_bookmark_link( link = '', before = '', after = '', bookmark = None ):
  ''' Displays the edit bookmark link anchor content.
  @param string link     Optional. Anchor text. Default empty.
  @param string before   Optional. Display before edit link. Default empty.
  @param string after    Optional. Display after edit link. Default empty.
  @param int    bookmark Optional. Bookmark ID. Default is the current bookmark.
  '''
  bookmark = get_bookmark(bookmark)

  if not current_user_can('manage_links'):
    return

  if Php.empty(locals(), 'link'):
    link = __('Edit This')

  link = '<a href="' + esc_url( get_edit_bookmark_link( bookmark ) ) + '">' + link + '</a>'

  # Filters the bookmark edit link anchor tag.
  # @param string link    Anchor tag for the edit link.
  # @param int    link_id Bookmark ID.
  Php.echo( before + WiPg.apply_filters( 'edit_bookmark_link', link, bookmark.link_id ) + after)


def get_edit_user_link( user_id = None ):
  ''' Retrieves the edit user link.
  @param int user_id Optional. User ID. Defaults to the current user.
  @return string URL to edit user page or empty string.
  '''
  if not user_id:
    user_id = get_current_user_id()

  if Php.empty(locals(),  'user_id' ) or not current_user_can( 'edit_user', user_id ):
    return ''

  user = get_userdata( user_id )

  if not user:
    return ''

  if get_current_user_id() == user.ID:
    link = get_edit_profile_url( user.ID )
  else:
    link = add_query_arg( 'user_id', user.ID, self_admin_url( 'user-edit.php' ) )

  # Filters the user edit link.
  # @param string link    The edit link.
  # @param int    user_id User ID.
  return WiPg.apply_filters( 'get_edit_user_link', link, user.ID )


# Navigation links

def get_previous_post( in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  '''
  Retrieves the previous post that is adjacent to the current post.
  @param bool         in_same_term   Optional. Whether post should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return None|string|WP_Post Post object if successful. Null if global post is not set. Empty string if no
                              corresponding post exists.
  '''
  return get_adjacent_post( in_same_term, excluded_terms, True, taxonomy )


def get_next_post( in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Retrieves the next post that is adjacent to the current post.
  @param bool         in_same_term   Optional. Whether post should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return None|string|WP_Post Post object if successful. Null if global post is not set. Empty string if no
                              corresponding post exists.
  '''
  return get_adjacent_post( in_same_term, excluded_terms, False, taxonomy )


def get_adjacent_post( in_same_term = False, excluded_terms = '', previous = True, taxonomy = 'category' ):
  ''' Retrieves the adjacent post.
  Can either be next or previous post.
  @global wpdb wpdb WordPress database abstraction object.
  @param bool         in_same_term   Optional. Whether post should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param bool         previous       Optional. Whether to retrieve previous post. Default True
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return None|string|WP_Post Post object if successful. Null if global post is not set. Empty string if no
                              corresponding post exists.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  post = WiP.get_post()
  if not post or not taxonomy_exists( taxonomy ):
    return None

  current_post_date = post.post_date

  join = ''
  where = ''
  adjacent = 'previous' if previous else 'next'

  if in_same_term or not Php.empty(locals(),  'excluded_terms' ):
    if not Php.empty(locals(),  'excluded_terms' ) and not Php.is_array( excluded_terms ):
      # back-compat, excluded_terms used to be excluded_terms with IDs separated by " and "
      if ' and ' in excluded_terms:
        _deprecated_argument( __FUNCTION__, '3.3.0', Php.sprintf( __( 'Use commas instead of %s to separate excluded terms.' ), "'and'" ) )
        excluded_terms = Php.explode( ' and ', excluded_terms )
      else:
        excluded_terms = Php.explode( ',', excluded_terms )

      excluded_terms = Php.array_map( 'intval', excluded_terms )

    if in_same_term:
      join += " INNER JOIN {} AS tr ON p.ID = tr.object_id INNER JOIN {} tt ON tr.term_taxonomy_id = tt.term_taxonomy_id".format(wpdb.term_relationships, wpdb.term_taxonomy)
      where += wpdb.prepare( "AND tt.taxonomy = %s", taxonomy )

      if not is_object_in_taxonomy( post.post_type, taxonomy ):
        return ''
      term_array = wp_get_object_terms( post.ID, taxonomy, array( ('fields', 'ids'),) )

      # Remove any exclusions from the term array to include.
      term_array = Php.array_diff( term_array, Php.Array( excluded_terms ))
      term_array = Php.array_map( 'intval', term_array )

      if not term_array or WpC.WB.Wj.is_wp_error( term_array ):
        return ''

      where += " AND tt.term_id IN (" + implode( ',', term_array ) + ")"

    # Filters the IDs of terms excluded from adjacent post queries.
    # The dynamic portion of the hook name, `adjacent`, refers to the type
    # of adjacency, 'next' or 'previous'.
    # @param string excluded_terms Array of excluded term IDs.
    excluded_terms = WiPg.apply_filters( "get_{}_post_excluded_terms".format(adjacent), excluded_terms )

    if not Php.empty(locals(),  'excluded_terms' ):
      where += " AND p.ID NOT IN ( SELECT tr.object_id FROM {} tr LEFT JOIN {} tt ON (tr.term_taxonomy_id = tt.term_taxonomy_id) WHERE tt.term_id IN (".format(wpdb.term_relationships, wpdb.term_taxonomy) + implode( ',', Php.array_map( 'intval', excluded_terms ) ) + ') )'

  # 'post_status' clause depends on the current user.
  if is_user_logged_in():
    user_id = get_current_user_id()

    post_type_object = WiP.get_post_type_object( post.post_type )
    if Php.empty(locals(),  'post_type_object' ):
      post_type_cap    = post.post_type
      read_private_cap = 'read_private_' + post_type_cap + 's'
    else:
      read_private_cap = post_type_object.cap.read_private_posts

    # Results should include private posts belonging to the current user, or private posts where the
    # current user has the 'read_private_posts' cap.
    private_states = get_post_stati( array( ('private', True),) )
    where += " AND ( p.post_status = 'publish'"
    for stage in Php.Array(private_states):
      if current_user_can( read_private_cap ):
        where += wpdb.prepare( " OR p.post_status = %s", state )
      else:
        where += wpdb.prepare( " OR (p.post_author = %d AND p.post_status = %s)", user_id, state )

    where += " )"
  else:
    where += " AND p.post_status = 'publish'"

  op = '<' if previous else '>'
  order = 'DESC' if previous else 'ASC'

  # Filters the JOIN clause in the SQL for an adjacent post query.
  # The dynamic portion of the hook name, `adjacent`, refers to the type
  # of adjacency, 'next' or 'previous'.
  # @since 4.4.0 Added the `taxonomy` and `post` parameters.
  # @param string  join           The JOIN clause in the SQL.
  # @param bool    in_same_term   Whether post should be in a same taxonomy term.
  # @param array   excluded_terms Array of excluded term IDs.
  # @param string  taxonomy       Taxonomy. Used to identify the term used when `in_same_term` is True.
  # @param WP_Post post           WP_Post object.
  join = WiPg.apply_filters( "get_{}_post_join".format(adjacent), join, in_same_term, excluded_terms, taxonomy, post )

  # Filters the WHERE clause in the SQL for an adjacent post query.
  # The dynamic portion of the hook name, `adjacent`, refers to the type
  # of adjacency, 'next' or 'previous'.
  # @since 4.4.0 Added the `taxonomy` and `post` parameters.
  # @param string where          The `WHERE` clause in the SQL.
  # @param bool   in_same_term   Whether post should be in a same taxonomy term.
  # @param array  excluded_terms Array of excluded term IDs.
  # @param string taxonomy       Taxonomy. Used to identify the term used when `in_same_term` is True.
  # @param WP_Post post           WP_Post object.
  where = WiPg.apply_filters( "get_{}_post_where".format(adjacent), wpdb.prepare( "WHERE p.post_date {} %s AND p.post_type = %s {}".format(op, where), current_post_date, post.post_type ), in_same_term, excluded_terms, taxonomy, post )

  # Filters the ORDER BY clause in the SQL for an adjacent post query.
  # The dynamic portion of the hook name, `adjacent`, refers to the type
  # of adjacency, 'next' or 'previous'.
  # @since 4.4.0 Added the `post` parameter.
  # @param string order_by The `ORDER BY` clause in the SQL.
  # @param WP_Post post    WP_Post object.
  sort  = WiPg.apply_filters( "get_{}_post_sort".format(adjacent), "ORDER BY p.post_date order LIMIT 1", post )

  query = "SELECT p.ID FROM {} AS p {} {} {}".format(wpdb.posts, join, where, sort)
  query_key = 'adjacent_post_' + md5( query )
  result = wp_cache_get( query_key, 'counts' )
  if False is not result:
    if result:
      result = WiP.get_post( result )
    return result

  result = wpdb.get_var( query )
  if None is result:
    result = ''

  wp_cache_set( query_key, result, 'counts' )

  if result:
    result = WiP.get_post( result )

  return result


def get_adjacent_post_rel_link( title = '%title', in_same_term = False, excluded_terms = '', previous = True, taxonomy = 'category' ):
  ''' Retrieves the adjacent post relational link.
  Can either be next or previous post relational link.
  @param string       title          Optional. Link title format. Default '%title'.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param bool         previous       Optional. Whether to display link to previous or next post. Default True.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return string|void The adjacent post relational link URL.
  '''
  post = WiP.get_post()
  if previous and is_attachment() and post:
    post = WiP.get_post( post.post_parent )
  else:
    post = get_adjacent_post( in_same_term, excluded_terms, previous, taxonomy )

  if Php.empty(locals(),  'post' ):
    return

  post_title = the_title_attribute( array( ('echo', False), ('post', post) ) )

  if Php.empty(locals(),  'post_title' ):
    post_title = __( 'Previous Post' ) if previous else __( 'Next Post' )

  date = mysql2date( WiO.get_option( 'date_format' ), post.post_date )

  title = Php.str_replace( '%title', post_title, title )
  title = Php.str_replace( '%date', date, title )

  link = "<link rel='prev' title='" if previous else "<link rel='next' title='"
  link += esc_attr( title )
  link += "' href='" + get_permalink( post ) + "' />\n"

  adjacent = 'previous' if previous else 'next'

  # Filters the adjacent post relational link.
  # The dynamic portion of the hook name, `adjacent`, refers to the type
  # of adjacency, 'next' or 'previous'.
  # @param string link The relational link.
  return WiPg.apply_filters( "{}_post_rel_link".format(adjacent), link )


def adjacent_posts_rel_link( title = '%title', in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Displays the relational links for the posts adjacent to the current post.
  @param string       title          Optional. Link title format. Default '%title'.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  '''
  Php.echo( get_adjacent_post_rel_link( title, in_same_term, excluded_terms, True, taxonomy ))
  Php.echo( get_adjacent_post_rel_link( title, in_same_term, excluded_terms, False, taxonomy ))


def adjacent_posts_rel_link_wp_head():
  ''' Displays relational links for the posts adjacent to the current post for single post pages.
  This is meant to be attached to actions like 'wp_head'. Do not call this directly in plugins
  or theme templates.
  @see adjacent_posts_rel_link()
  '''
  if not is_single() or is_attachment():
    return
  adjacent_posts_rel_link()


def next_post_rel_link( title = '%title', in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Displays the relational link for the next post adjacent to the current post.
  @see get_adjacent_post_rel_link()
  @param string       title          Optional. Link title format. Default '%title'.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  '''
  Php.echo( get_adjacent_post_rel_link( title, in_same_term, excluded_terms, False, taxonomy ))


def prev_post_rel_link( title = '%title', in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Displays the relational link for the previous post adjacent to the current post.
  @see get_adjacent_post_rel_link()
  @param string       title          Optional. Link title format. Default '%title'.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default True.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  '''
  Php.echo( get_adjacent_post_rel_link( title, in_same_term, excluded_terms, True, taxonomy ))


def get_boundary_post( in_same_term = False, excluded_terms = '', start = True, taxonomy = 'category' ):
  ''' Retrieves the boundary post.
  Boundary being either the first or last post by publish date within the constraints specified
  by in_same_term or excluded_terms.
  @param bool         in_same_term   Optional. Whether returned post should be in a same taxonomy term.
                                      Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs.
                                      Default empty.
  @param bool         start          Optional. Whether to retrieve first or last post. Default True
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return None|array Array containing the boundary post object if successful, None otherwise.
  '''
  post = WiP.get_post()
  if not post or not is_single() or is_attachment() or not taxonomy_exists( taxonomy ):
    return None

  query_args = array(
      ('posts_per_page', 1),
      ('order', 'ASC' if start else 'DESC'),
      ('update_post_term_cache', False),
      ('update_post_meta_cache', False),
  )

  term_array = array()

  if not Php.is_array( excluded_terms ):
    if not Php.empty(locals(),  'excluded_terms' ):
      excluded_terms = Php.explode( ',', excluded_terms )
    else:
      excluded_terms = array()

  if in_same_term or not Php.empty(locals(),  'excluded_terms' ):
    if in_same_term:
      term_array = wp_get_object_terms( post.ID, taxonomy, array( ('fields', 'ids'),) )

    if not empty(locals(),  'excluded_terms' ):
      excluded_terms = Php.array_map( 'intval', excluded_terms )
      excluded_terms = Php.array_diff( excluded_terms, term_array )

      inverse_terms = array()
      for excluded_term in excluded_terms:
        inverse_terms[None] = excluded_term * -1
      excluded_terms = inverse_terms

    query_args[ 'tax_query' ] = array( array(
      ('taxonomy', taxonomy),
      ('terms', array_merge( term_array, excluded_terms ))
    ) )

  return get_posts( query_args )


def get_previous_post_link( format = '&laquo; %link', link = '%title', in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Retrieves the previous post link that is adjacent to the current post.
  @param string       format         Optional. Link anchor format. Default '&laquo; %link'.
  @param string       link           Optional. Link permalink format. Default '%title%'.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return string The link URL of the previous post in relation to the current post.
  '''
  return get_adjacent_post_link( format, link, in_same_term, excluded_terms, True, taxonomy )


def previous_post_link( format = '&laquo; %link', link = '%title', in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Displays the previous post link that is adjacent to the current post.
  @see get_previous_post_link()
  @param string       format         Optional. Link anchor format. Default '&laquo; %link'.
  @param string       link           Optional. Link permalink format. Default '%title'.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  '''
  Php.echo( get_previous_post_link( format, link, in_same_term, excluded_terms, taxonomy ))


def get_next_post_link( format = '%link &raquo;', link = '%title', in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Retrieves the next post link that is adjacent to the current post.
  @param string       format         Optional. Link anchor format. Default '&laquo; %link'.
  @param string       link           Optional. Link permalink format. Default '%title'.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return string The link URL of the next post in relation to the current post.
  '''
  return get_adjacent_post_link( format, link, in_same_term, excluded_terms, False, taxonomy )


def next_post_link( format = '%link &raquo;', link = '%title', in_same_term = False, excluded_terms = '', taxonomy = 'category' ):
  ''' Displays the next post link that is adjacent to the current post.
  @see get_next_post_link()
  @param string       format         Optional. Link anchor format. Default '&laquo; %link'.
  @param string       link           Optional. Link permalink format. Default '%title'
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded term IDs. Default empty.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  '''
  Php.echo( get_next_post_link( format, link, in_same_term, excluded_terms, taxonomy ))


def get_adjacent_post_link( format, link, in_same_term = False, excluded_terms = '', previous = True, taxonomy = 'category' ):
  ''' Retrieves the adjacent post link.
  Can be either next post link or previous.
  @param string       format         Link anchor format.
  @param string       link           Link permalink format.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded terms IDs. Default empty.
  @param bool         previous       Optional. Whether to display link to previous or next post. Default True.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  @return string The link URL of the previous or next post in relation to the current post.
  '''
  if previous and is_attachment():
    post = WiP.get_post( WiP.get_post().post_parent )
  else:
    post = get_adjacent_post( in_same_term, excluded_terms, previous, taxonomy )

  if not post:
    output = ''
  else:
    title = post.post_title

    if Php.empty( post, 'post_title' ):
      title = __( 'Previous Post' ) if previous else __( 'Next Post' )

    # This filter is documented in wp-includes/post-template.php
    title = WiPg.apply_filters( 'the_title', title, post.ID )

    date = mysql2date( WiO.get_option( 'date_format' ), post.post_date )
    rel = 'prev' if previous else 'next'

    string = '<a href="' + get_permalink( post ) + '" rel="'+rel+'">'
    inlink = Php.str_replace( '%title', title, link )
    inlink = Php.str_replace( '%date', date, inlink )
    inlink = string + inlink + '</a>'

    output = Php.str_replace( '%link', inlink, format )

  adjacent = 'previous' if previous else 'next'

  # Filters the adjacent post link.
  # The dynamic portion of the hook name, `adjacent`, refers to the type
  # of adjacency, 'next' or 'previous'.
  # @since 4.2.0 Added the `adjacent` parameter.
  # @param string  output   The adjacent post link.
  # @param string  format   Link anchor format.
  # @param string  link     Link permalink format.
  # @param WP_Post post     The adjacent post.
  # @param string  adjacent Whether the post is previous or next.
  return WiPg.apply_filters( "{}_post_link".format(adjacent), output, format, link, post, adjacent )


def adjacent_post_link( format, link, in_same_term = False, excluded_terms = '', previous = True, taxonomy = 'category' ):
  ''' Displays the adjacent post link.
  Can be either next post link or previous.
  @param string       format         Link anchor format.
  @param string       link           Link permalink format.
  @param bool         in_same_term   Optional. Whether link should be in a same taxonomy term. Default False.
  @param array|string excluded_terms Optional. Array or comma-separated list of excluded category IDs. Default empty.
  @param bool         previous       Optional. Whether to display link to previous or next post. Default True.
  @param string       taxonomy       Optional. Taxonomy, if in_same_term is True. Default 'category'.
  '''
  Php.echo( get_adjacent_post_link( format, link, in_same_term, excluded_terms, previous, taxonomy ))


def get_pagenum_link(pagenum = 1, escape = True ):
  ''' Retrieves the link for a page number.
  @global WP_Rewrite wp_rewrite
  @param int  pagenum Optional. Page ID. Default 1.
  @param bool escape  Optional. Whether to escape the URL for display, with esc_url(). Defaults to True.
                        Otherwise, prepares the URL with esc_url_raw().
  @return string The link URL for the given page number.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  pagenum = int(pagenum)

  request = remove_query_arg( 'paged' )

  home_root = Php.parse_url(home_url())
  #home_root= home_root['path'] if ( Php.isset(home_root, 'path') ) else ''
  home_root = getattr(home_root, 'path', '')
  home_root = Php.preg_quote( home_root, '|' )

  request = Php.preg_replace('|^'+ home_root + '|i', '', request)
  request = Php.preg_replace('|^/+|', '', request)

  if not wp_rewrite.using_permalinks() or is_admin():
    base = WiF.trailingslashit( get_bloginfo( 'url' ) )

    if pagenum > 1:
      result = add_query_arg( 'paged', pagenum, base + request )
    else:
      result = base + request
  else:
    qs_regex = '|\?.*?$|'
    #preg_match( qs_regex, request, qs_match )
    qs_match = preg_match( qs_regex, request )

    if not Php.empty(qs_match,  0 ):
      query_string = qs_match[0]
      request = Php.preg_replace( qs_regex, '', request )
    else:
      query_string = ''

    request = Php.preg_replace( "|{}/\d+/?$|".format(wp_rewrite.pagination_base), '', request)
    request = Php.preg_replace( '|^' + Php.preg_quote( wp_rewrite.index, '|' ) + '|i', '', request)
    request = Php.ltrim(request, '/')

    base = WiF.trailingslashit( get_bloginfo( 'url' ) )

    if wp_rewrite.using_index_permalinks() and ( pagenum > 1 or '' != request ):
      base += wp_rewrite.index + '/'

    if pagenum > 1:
      request = ( WiF.trailingslashit( request ) if ( not Php.empty(locals(),  'request' ) ) else request ) + user_trailingslashit( wp_rewrite.pagination_base + "/" + pagenum, 'paged' )

    result = base + request + query_string

  # Filters the page number link for the current request.
  # @param string result The page number link.
  result = WiPg.apply_filters( 'get_pagenum_link', result )

  if escape:
    return esc_url( result )
  else:
    return esc_url_raw( result )


def get_next_posts_page_link(max_page = 0):
  ''' Retrieves the next posts page link.
  Backported from 2.1.3 to 2.0.10.
  @global int paged
  @param int max_page Optional. Max pages. Default 0.
  @return string|void The link URL for next posts page.
  '''
  # paged = WpC.WB.Wj.paged  # global paged

  if not is_single():
    if not WpC.WB.Wj.paged:
      WpC.WB.Wj.paged = 1
    nextpage = intval(WpC.WB.Wj.paged) + 1
    if not max_page or max_page >= nextpage:
      return get_pagenum_link(nextpage)


def next_posts( max_page = 0, echo = True ):
  ''' Displays or retrieves the next posts page link.
  @param int   max_page Optional. Max pages. Default 0.
  @param bool  echo     Optional. Whether to echo the link. Default True.
  @return string|void The link URL for next posts page if `echo = False`.
  '''
  output = esc_url( get_next_posts_page_link( max_page ) )

  if echo:
    Php.echo( output)
  else:
    return output


def get_next_posts_link( label = None, max_page = 0 ):
  ''' Retrieves the next posts page link.
  @global int      paged
  @global WP_Query wp_query
  @param string label    Content for link text.
  @param int    max_page Optional. Max pages. Default 0.
  @return string|void HTML-formatted next posts page link.
  '''
  #global paged
  wp_query = WpC.WB.Wj.wp_query  # global wp_query

  if not max_page:
    max_page = wp_query.max_num_pages

  if not WpC.WB.Wj.paged:
    WpC.WB.Wj.paged = 1

  nextpage = intval(WpC.WB.Wj.paged) + 1

  if None is label:
    label = __( 'Next Page &raquo;' )

  if not is_single() and ( nextpage <= max_page ):
    # Filters the anchor tag attributes for the next posts page link.
    # @param string attributes Attributes for the anchor tag.
    attr = WiPg.apply_filters( 'next_posts_link_attributes', '' )

    return '<a href="' + next_posts( max_page, False ) + '" {}>'.format(attr) + Php.preg_replace('/&([^#])(?![a-z]{1,8};)/i', r'&#038;\1', label) + '</a>'
  # php replacement= '$1' , in py= r'\1' . r= raw str so no need to escape \


def next_posts_link( label = None, max_page = 0 ):
  ''' Displays the next posts page link.
  @param string label    Content for link text.
  @param int    max_page Optional. Max pages. Default 0.
  '''
  Php.echo( get_next_posts_link( label, max_page ))


def get_previous_posts_page_link():
  ''' Retrieves the previous posts page link.
  Will only return string, if not on a single page or post.
  Backported to 2.0.10 from 2.1.3.
  @global int paged
  @return string|void The link for the previous posts page.
  '''
  #global paged

  if not is_single():
    nextpage = intval(WpC.WB.Wj.paged) - 1
    if nextpage < 1:
      nextpage = 1
    return get_pagenum_link(nextpage)


def previous_posts( echo = True ):
  ''' Displays or retrieves the previous posts page link.
  @param bool echo Optional. Whether to echo the link. Default True.
  @return string|void The previous posts page link if `echo = False`.
  '''
  output = esc_url( get_previous_posts_page_link() )

  if echo:
    Php.echo( output)
  else:
    return output


def get_previous_posts_link( label = None ):
  ''' Retrieves the previous posts page link.
  @global int paged
  @param string label Optional. Previous page link text.
  @return string|void HTML-formatted previous page link.
  '''
  #global paged

  if None is label:
    label = __( '&laquo; Previous Page' )

  if not is_single() and WpC.WB.Wj.paged > 1:
    # Filters the anchor tag attributes for the previous posts page link.
    # @param string attributes Attributes for the anchor tag.
    attr = WiPg.apply_filters( 'previous_posts_link_attributes', '' )
    return '<a href="' + previous_posts( False ) + '" {}>'.format(attr) + Php.preg_replace( '/&([^#])(?![a-z]{1,8};)/i', r'&#038;\1', label ) +'</a>'
  # php replacement= '$1' , in py= r'\1' . r= raw str so no need to escape \


def previous_posts_link( label = None ):
  ''' Displays the previous posts page link.
  @param string label Optional. Previous page link text.
  '''
  Php.echo( get_previous_posts_link( label ))


def get_posts_nav_link( args = array() ):
  ''' Retrieves the post pages link navigation for previous and next pages.
  @global WP_Query wp_query
  @param string|array args {
      Optional. Arguments to build the post pages link navigation.
      @type string sep      Separator character. Default '&#8212;'.
      @type string prelabel Link text to display for the previous page link.
                             Default '&laquo; Previous Page'.
      @type string nxtlabel Link text to display for the next page link.
                             Default 'Next Page &raquo;'.
  }
  @Return string The posts link navigation.
  '''
  wp_query = WpC.WB.Wj.wp_query  # global wp_query

  Return = ''

  if not Php.is_singular():
    defaults = array(
        ('sep', ' &#8212; '),
        ('prelabel', __('&laquo; Previous Page')),
        ('nxtlabel', __('Next Page &raquo;')),
    )
    args = wp_parse_args( args, defaults )

    max_num_pages = wp_query.max_num_pages
    paged = get_query_var('paged')

    #only have sep if there's both prev and next results
    if paged < 2 or paged >= max_num_pages:
      args['sep'] = ''

    if max_num_pages > 1:
      Return = get_previous_posts_link(args['prelabel'])
      #php replacement= '$1' , in py= r'\1' . r= raw str so no need to escape \
      Return += Php.preg_replace('/&([^#])(?![a-z]{1,8};)/i', r'&#038;\1', args['sep'])
      Return += get_next_posts_link(args['nxtlabel'])

  return Return


def posts_nav_link( sep = '', prelabel = '', nxtlabel = '' ):
  ''' Displays the post pages link navigation for previous and next pages.
  @param string sep      Optional. Separator for posts navigation links. Default empty.
  @param string prelabel Optional. Label for previous pages. Default empty.
  @param string nxtlabel Optional Label for next pages. Default empty.
  '''
  args = array_filter( compact(locals(),'sep', 'prelabel', 'nxtlabel') )
  Php.echo( get_posts_nav_link(args))


def get_the_post_navigation( args = array() ):
  ''' Retrieves the navigation to next/previous post, when applicable.
  @since 4.4.0 Introduced the `in_same_term`, `excluded_terms`, and `taxonomy` arguments.
  @param array args {
      Optional. Default post navigation arguments. Default empty array.
      @type string       prev_text          Anchor text to display in the previous post link. Default '%title'.
      @type string       next_text          Anchor text to display in the next post link. Default '%title'.
      @type bool         in_same_term       Whether link should be in a same taxonomy term. Default False.
      @type array|string excluded_terms     Array or comma-separated list of excluded term IDs. Default empty.
      @type string       taxonomy           Taxonomy, if `in_same_term` is True. Default 'category'.
      @type string       screen_reader_text Screen reader text for nav element. Default 'Post navigation'.
  }
  @return string Markup for post links.
  '''
  args = wp_parse_args( args, array(
    ('prev_text'         , '%title'),
    ('next_text'         , '%title'),
    ('in_same_term'      , False),
    ('excluded_terms'    , ''),
    ('taxonomy'          , 'category'),
    ('screen_reader_text', __( 'Post navigation' )),
  ) )

  navigation = ''

  previous = get_previous_post_link(
    '<div class="nav-previous">%link</div>',
    args['prev_text'],
    args['in_same_term'],
    args['excluded_terms'],
    args['taxonomy']
  )

  next = get_next_post_link(
    '<div class="nav-next">%link</div>',
    args['next_text'],
    args['in_same_term'],
    args['excluded_terms'],
    args['taxonomy']
  )

  # Only add markup if there's somewhere to navigate to.
  if previous or next:
    navigation = _navigation_markup( previous + next, 'post-navigation', args['screen_reader_text'] )

  return navigation


def the_post_navigation( args = array() ):
  ''' Displays the navigation to next/previous post, when applicable.
  @param array args Optional. See get_the_post_navigation() for available arguments.
                     Default empty array.
  '''
  Php.echo( get_the_post_navigation( args ))


def get_the_posts_navigation( args = array() ):
  ''' Returns the navigation to next/previous set of posts, when applicable.
  @global WP_Query wp_query WordPress Query object.
  @param array args {
      Optional. Default posts navigation arguments. Default empty array.
      @type string prev_text          Anchor text to display in the previous posts link.
                                       Default 'Older posts'.
      @type string next_text          Anchor text to display in the next posts link.
                                       Default 'Newer posts'.
      @type string screen_reader_text Screen reader text for nav element.
                                       Default 'Posts navigation'.
  }
  @return string Markup for posts links.
  '''
  GLOBALS = WpC.WB.Wj.__dict__  # global GLOBALS
  navigation = ''

  # Don't print empty markup if there's only one page.
  if GLOBALS['wp_query'].max_num_pages > 1:
    args = wp_parse_args( args, array(
      ('prev_text'         , __( 'Older posts' )),
      ('next_text'         , __( 'Newer posts' )),
      ('screen_reader_text', __( 'Posts navigation' )),
    ) )

    next_link = get_previous_posts_link( args['next_text'] )
    prev_link = get_next_posts_link( args['prev_text'] )

    if prev_link:
      navigation += '<div class="nav-previous">' + prev_link + '</div>'

    if next_link:
      navigation += '<div class="nav-next">' + next_link + '</div>'

    navigation = _navigation_markup( navigation, 'posts-navigation', args['screen_reader_text'] )

  return navigation


def the_posts_navigation( args = array() ):
  ''' Displays the navigation to next/previous set of posts, when applicable.
  @param array args Optional. See get_the_posts_navigation() for available arguments.
                     Default empty array.
  '''
  Php.echo( get_the_posts_navigation( args ))


def get_the_posts_pagination( args = array() ):
  ''' Retrieves a paginated navigation to next/previous set of posts, when applicable.
  @param array args {
      Optional. Default pagination arguments, see paginate_links().
      @type string screen_reader_text Screen reader text for navigation element.
                                       Default 'Posts navigation'.
  }
  @return string Markup for pagination links.
  '''
  GLOBALS = WpC.WB.Wj.__dict__  # global GLOBALS
  navigation = ''

  # Don't print empty markup if there's only one page.
  if GLOBALS['wp_query'].max_num_pages > 1:
    args = wp_parse_args( args, array(
      ('mid_size'          , 1),
      ('prev_text'         , _x( 'Previous', 'previous set of posts' )),
      ('next_text'         , _x( 'Next', 'next set of posts' )),
      ('screen_reader_text', __( 'Posts navigation' )),
    ) )

    # Make sure we get a string back. Plain is the next best thing.
    if Php.isset( args, 'type' ) and 'array' == args['type']:
      args['type'] = 'plain'

    # Set up paginated links.
    links = paginate_links( args )

    if links:
      navigation = _navigation_markup( links, 'pagination', args['screen_reader_text'] )

  return navigation


def the_posts_pagination( args = array() ):
  ''' Displays a paginated navigation to next/previous set of posts, when applicable.
  @param array args Optional. See get_the_posts_pagination() for available arguments.
                     Default empty array.
  '''
  Php.echo( get_the_posts_pagination( args ))


def _navigation_markup( links, Class = 'posts-navigation', screen_reader_text = '' ):
  ''' Wraps passed links in navigational markup.
  @access private
  @param string links              Navigational links.
  @param string class              Optional. Custom class for nav element. Default: 'posts-navigation'.
  @param string screen_reader_text Optional. Screen reader text for nav element. Default: 'Posts navigation'.
  @return string Navigation template tag.
  '''
  if Php.empty(locals(),  'screen_reader_text' ):
    screen_reader_text = __( 'Posts navigation' )

  template = '''
  <nav class="navigation %1$s" role="navigation">
    <h2 class="screen-reader-text">%2$s</h2>
    <div class="nav-links">%3$s</div>
  </nav>'''

  # Filters the navigation markup template.
  # Note: The filtered template HTML must contain specifiers for the navigation
  # class (%1$s), the screen-reader-text value (%2$s), and placement of the
  # navigation links (%3$s):
  #     <nav class="navigation %1$s" role="navigation">
  #         <h2 class="screen-reader-text">%2$s</h2>
  #         <div class="nav-links">%3$s</div>
  #     </nav>
  # @since 4.4.0
  # @param string template The default template.
  # @param string class    The class passed by the calling function.
  # @return string Navigation template.
  template = WiPg.apply_filters( 'navigation_markup_template', template, Class )

  return Php.sprintf( template, sanitize_html_class( Class ), esc_html( screen_reader_text ), links )


def get_comments_pagenum_link( pagenum = 1, max_page = 0 ):
  ''' Retrieves the comments page number link.
  @global WP_Rewrite wp_rewrite
  @param int pagenum  Optional. Page number. Default 1.
  @param int max_page Optional. The maximum number of comment pages. Default 0.
  @return string The comments page number link URL.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  pagenum = int(pagenum)

  result = get_permalink()

  if 'newest' == WiO.get_option('default_comments_page'):
    if pagenum != max_page:
      if wp_rewrite.using_permalinks():
        result = user_trailingslashit( WiF.trailingslashit(result) + wp_rewrite.comments_pagination_base + '-' + pagenum, 'commentpaged')
      else:
        result = add_query_arg( 'cpage', pagenum, result )
  elif pagenum > 1:
    if wp_rewrite.using_permalinks():
      result = user_trailingslashit( WiF.trailingslashit(result) + wp_rewrite.comments_pagination_base + '-' + pagenum, 'commentpaged')
    else:
      result = add_query_arg( 'cpage', pagenum, result )

  result += '#comments'

  # Filters the comments page number link for the current request.
  # @param string result The comments page number link.
  return WiPg.apply_filters( 'get_comments_pagenum_link', result )


def get_next_comments_link( label = '', max_page = 0 ):
  ''' Retrieves the link to the next comments page.
  @global WP_Query wp_query
  @param string label    Optional. Label for link text. Default empty.
  @param int    max_page Optional. Max page. Default 0.
  @return string|void HTML-formatted link for the next page of comments.
  '''
  wp_query = WpC.WB.Wj.wp_query  # global wp_query

  if not Php.is_singular():
    return

  page = get_query_var('cpage')

  if not page:
    page = 1

  nextpage = intval(page) + 1

  if Php.empty(locals(), 'max_page'):
    max_page = wp_query.max_num_comment_pages

  if Php.empty(locals(), 'max_page'):
    max_page = get_comment_pages_count()

  if nextpage > max_page:
    return

  if Php.empty(locals(), 'label'):
    label = __('Newer Comments &raquo;')

  # Filters the anchor tag attributes for the next comments page link.
  # @param string attributes Attributes for the anchor tag.
  return '<a href="' + esc_url( get_comments_pagenum_link( nextpage, max_page ) ) + '" ' + WiPg.apply_filters( 'next_comments_link_attributes', '' ) + '>'+ Php.preg_replace('/&([^#])(?![a-z]{1,8};)/i', r'&#038;\1', label) +'</a>'
  # php replacement= '$1' , in py= r'\1' . r= raw str so no need to escape \


def next_comments_link( label = '', max_page = 0 ):
  ''' Displays the link to the next comments page.
  @param string label    Optional. Label for link text. Default empty.
  @param int    max_page Optional. Max page. Default 0.
  '''
  Php.echo( get_next_comments_link( label, max_page ))


def get_previous_comments_link( label = '' ):
  ''' Retrieves the link to the previous comments page.
  @param string label Optional. Label for comments link text. Default empty.
  @return string|void HTML-formatted link for the previous page of comments.
  '''
  if not Php.is_singular():
    return

  page = get_query_var('cpage')

  if intval(page) <= 1:
    return

  prevpage = intval(page) - 1

  if Php.empty(locals(), 'label'):
    label = __('&laquo; Older Comments')

  # Filters the anchor tag attributes for the previous comments page link.
  # @param string attributes Attributes for the anchor tag.
  return '<a href="' + esc_url( get_comments_pagenum_link( prevpage ) ) + '" ' + WiPg.apply_filters( 'previous_comments_link_attributes', '' ) + '>' + Php.preg_replace('/&([^#])(?![a-z]{1,8};)/i', r'&#038;\1', label) +'</a>'
  # php replacement= '$1' , in py= r'\1' . r= raw str so no need to escape \


def previous_comments_link( label = '' ):
  ''' Displays the link to the previous comments page.
  @param string label Optional. Label for comments link text. Default empty.
  '''
  Php.echo( get_previous_comments_link( label ))


def paginate_comments_links( args = array() ):
  ''' Displays or retrieves pagination links for the comments on the current post.
  @see paginate_links()
  @since 2.7.0
  @global WP_Rewrite wp_rewrite
  @param string|array args Optional args. See paginate_links(). Default Php.empty array.
  @return string|void Markup for pagination links.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  if not Php.is_singular():
    return

  page = get_query_var('cpage')
  if not page:
    page = 1
  max_page = get_comment_pages_count()
  defaults = array(
    ('base'        , add_query_arg( 'cpage', '%#%' )),
    ('format'      , ''),
    ('total'       , max_page),
    ('current'     , page),
    ('echo'        , True),
    ('add_fragment', '#comments'),
  )
  if wp_rewrite.using_permalinks():
    defaults['base'] = user_trailingslashit(WiF.trailingslashit(get_permalink()) + wp_rewrite.comments_pagination_base + '-%#%', 'commentpaged')

  args = wp_parse_args( args, defaults )
  page_links = paginate_links( args )

  if args['echo']:
    Php.echo( page_links)
  else:
    return page_links


def get_the_comments_navigation( args = array() ):
  ''' Retrieves navigation to next/previous set of comments, when applicable.
  @param array args {
      Optional. Default comments navigation arguments.
      @type string prev_text          Anchor text to display in the previous comments link.
                                       Default 'Older comments'.
      @type string next_text          Anchor text to display in the next comments link.
                                       Default 'Newer comments'.
      @type string screen_reader_text Screen reader text for nav element. Default 'Comments navigation'.
  }
  @return string Markup for comments links.
  '''
  navigation = ''

  # Are there comments to navigate through?
  if get_comment_pages_count() > 1:
    args = wp_parse_args( args, array(
      ('prev_text'         , __( 'Older comments' )),
      ('next_text'         , __( 'Newer comments' )),
      ('screen_reader_text', __( 'Comments navigation' )),
    ) )

    prev_link = get_previous_comments_link( args['prev_text'] )
    next_link = get_next_comments_link( args['next_text'] )

    if prev_link:
      navigation += '<div class="nav-previous">' + prev_link + '</div>'

    if next_link:
      navigation += '<div class="nav-next">' + next_link + '</div>'

    navigation = _navigation_markup( navigation, 'comment-navigation', args['screen_reader_text'] )

  return navigation


def the_comments_navigation( args = array() ):
  ''' Displays navigation to next/previous set of comments, when applicable.
  @param array args See get_the_comments_navigation() for available arguments. Default empty array.
  '''
  Php.echo( get_the_comments_navigation( args ))


def get_the_comments_pagination( args = array() ):
  ''' Retrieves a paginated navigation to next/previous set of comments, when applicable.
  @see paginate_comments_links()
  @param array args {
      Optional. Default pagination arguments.
      @type string screen_reader_text Screen reader text for nav element. Default 'Comments navigation'.
  }
  @return string Markup for pagination links.
  '''
  navigation = ''
  args       = wp_parse_args( args, array(
    ('screen_reader_text', __( 'Comments navigation' )),
  ) )
  args['echo'] = False

  # Make sure we get plain links, so we get a string we can work with.
  args['type'] = 'plain'

  links = paginate_comments_links( args )

  if links:
    navigation = _navigation_markup( links, 'comments-pagination', args['screen_reader_text'] )

  return navigation


def the_comments_pagination( args = array() ):
  ''' Displays a paginated navigation to next/previous set of comments, when applicable.
  @param array args See get_the_comments_pagination() for available arguments. Default empty array.
  '''
  Php.echo( get_the_comments_pagination( args ))


def get_shortcut_link():
  ''' Retrieves the Press This bookmarklet link.
  @global bool   is_IE  Whether the browser matches an Internet Explorer user agent.
  '''
  GLOBALS = WpC.WB.Wj.__dict__  # global GLOBALS
  #global is_IE

  include_once( ABSPATH + 'wp-admin/includes/class-wp-press-this.php' )
  link = ''

  if WpC.WB.Wj.is_IE:
    # Return the old/shorter bookmarklet code for MSIE 8 and lower,
    # since they only support a max length of ~2000 characters for
    # bookmark[let] URLs, which is way to small for our smarter one.
    # Do update the version number so users do not get the "upgrade your
    # bookmarklet" notice when using PT in those browsers.
    ua = _SERVER['HTTP_USER_AGENT']
    # revert to wp.4.6.1 for now.  not yet implemented 4.7.1 WP_Press_This
    bookmarklet_version = GLOBALS['wp_press_this'].version

    if not Php.empty(locals(),  'ua' ) and preg_match( '/\bMSIE (\d)/', a, matches ) and int(matches[1]) <= 8:
      url = wp_json_encode( admin_url( 'press-this.php' ) )

      link = ('javascript:var d=document,w=window,e=w.getSelection,k=d.getSelection,x=d.selection,' +
        's=(e?e():(k)?k():(x?x.createRange().text:0)),f=' + url + ',l=d.location,e=encodeURIComponent,' +
        # revert to wp.4.6.1 for now.  not yet implemented 4.7.1 WP_Press_This
        #'u=f+"?u="+e(l.href)+"&t="+e(d.title)+"&s="+e(s)+"&v=' + WP_Press_This.VERSION + '";' +
        'u=f+"?u="+e(l.href)+"&t="+e(d.title)+"&s="+e(s)+"&v=' + bookmarklet_version + '";' +
        'a=function(){if(!w.open(u,"t","toolbar=0,resizable=1,scrollbars=1,status=1,width=600,height=700"))l.href=u;};' +
        'if(/Firefox/.test(navigator.userAgent))setTimeout(a,0);else a();void(0)')

  if Php.empty(locals(),  'link' ):
    src = file_get_contents( ABSPATH + 'wp-admin/js/bookmarklet.min.js' )

    if src:
      # revert to wp.4.6.1 for now.  not yet implemented 4.7.1 WP_Press_This
      #url = wp_json_encode( admin_url( 'press-this.php' ) + '?v=' + WP_Press_This::VERSION )
      url = wp_json_encode( admin_url( 'press-this.php' ) + '?v=' + bookmarklet_version )
      link = 'javascript:' + Php.str_replace( 'window.pt_url', url, src )

  link = Php.str_replace( array( "\r", "\n", "\t" ),  '', link )

  # Filters the Press This bookmarklet link.
  # @param string link The Press This bookmarklet link.
  return WiPg.apply_filters( 'shortcut_link', link )


def home_url( path = '', scheme = None ):
  ''' Retrieves the URL for the current site where the front end is accessible.
  Returns the 'home' option with the appropriate protocol. The protocol will be 'https'
  if is_ssl() evaluates to true; otherwise, it will be the same as the 'home' option.
  If `$scheme` is 'http' or 'https', is_ssl() is overridden.
  @param  string      path   Optional. Path relative to the home URL. Default empty.
  @param  string|None scheme Optional. Scheme to give the home URL context. Accepts
                              'http', 'https', 'relative', 'rest', or None. Default None.
  @return string Home URL link with optional path appended.
  '''
  return get_home_url( None, path, scheme )


def get_home_url( blog_id = None, path = '', scheme = None ):
  ''' Retrieves the URL for a given site where the front end is accessible.
  Returns the 'home' option with the appropriate protocol. The protocol will be 'https'
  if is_ssl() evaluates to true; otherwise, it will be the same as the 'home' option.
  If `$scheme` is 'http' or 'https', is_ssl() is overridden.
  @global string pagenow
  @param  int         blog_id Optional. Site ID. Default None (current site).
  @param  string      path    Optional. Path relative to the home URL. Default empty.
  @param  string|None scheme  Optional. Scheme to give the home URL context. Accepts
                               'http', 'https', 'relative', 'rest', or None. Default None.
  @return string Home URL link with optional path appended.
  '''
  #global pagenow

  orig_scheme = scheme

  if Php.empty(locals(),  'blog_id' ) or not WpC.WB.Wj.is_multisite():
    url = WiO.get_option( 'home' )
    print('get_home_url url=', url)
  else:
    switch_to_blog( blog_id )
    url = WiO.get_option( 'home' )
    restore_current_blog()

  if not Php.in_array( scheme, array( 'http', 'https', 'relative' ) ):
    if WpC.WB.Wj.is_ssl() and not is_admin() and 'wp-login.php' != WpC.WB.Wj.pagenow:
      scheme = 'https'
    else:
      scheme = Php.parse_url( url, Php.PHP_URL_SCHEME )

  url = set_url_scheme( url, scheme )

  if path and Php.is_string( path ):
    url += '/' + Php.ltrim( path, '/' )

  # Filters the home URL.
  # @param string      url         The complete home URL including scheme and path.
  # @param string      path        Path relative to the home URL. Blank string if no path is specified.
  # @param string|None orig_scheme Scheme to give the home URL context. Accepts 'http', 'https',
  #                                 'relative', 'rest', or None.
  # @param int|None    blog_id     Site ID, or None for the current site.
  return WiPg.apply_filters( 'home_url', url, path, orig_scheme, blog_id )


def site_url( path = '', scheme = None ):
  ''' Retrieves the URL for the current site where WordPress application files
  (e.g. wp-blog-header.php or the wp-admin/ folder) are accessible.
  Returns the 'site_url' option with the appropriate protocol, 'https' if
  is_ssl() and 'http' otherwise. If scheme is 'http' or 'https', is_ssl() is
  overridden.
  @param string path   Optional. Path relative to the site URL. Default empty.
  @param string scheme Optional. Scheme to give the site URL context. See set_url_scheme().
  @return string Site URL link with optional path appended.
  '''
  return get_site_url( None, path, scheme )


def get_site_url( blog_id = None, path = '', scheme = None ):
  ''' Retrieves the URL for a given site where WordPress application files
  (e.g. wp-blog-header.php or the wp-admin/ folder) are accessible.
  Returns the 'site_url' option with the appropriate protocol, 'https' if
  is_ssl() and 'http' otherwise. If `scheme` is 'http' or 'https',
  `is_ssl()` is overridden.
  @param int    blog_id Optional. Site ID. Default None (current site).
  @param string path    Optional. Path relative to the site URL. Default empty.
  @param string scheme  Optional. Scheme to give the site URL context. Accepts
                         'http', 'https', 'login', 'login_post', 'admin', or
                         'relative'. Default None.
  @return string Site URL link with optional path appended.
  '''
  if Php.empty(locals(),  'blog_id' ) or not WpC.WB.Wj.is_multisite():
    url = WiO.get_option( 'siteurl' )
  else:
    switch_to_blog( blog_id )
    url = WiO.get_option( 'siteurl' )
    restore_current_blog()

  url = set_url_scheme( url, scheme )

  if path and Php.is_string( path ):
    url += '/' + Php.ltrim( path, '/' )

  # Filters the site URL.
  # @param string      url     The complete site URL including scheme and path.
  # @param string      path    Path relative to the site URL. Blank string if no path is specified.
  # @param string|None scheme  Scheme to give the site URL context. Accepts 'http', 'https', 'login',
  #                             'login_post', 'admin', 'relative' or None.
  # @param int|None    blog_id Site ID, or None for the current site.
  return WiPg.apply_filters( 'site_url', url, path, scheme, blog_id )


def admin_url( path = '', scheme = 'admin' ):
  ''' Retrieves the URL to the admin area for the current site.
  @param string path   Optional path relative to the admin URL.
  @param string scheme The scheme to use. Default is 'admin', which obeys force_ssl_admin() and is_ssl().
                        'http' or 'https' can be passed to force those schemes.
  @return string Admin URL link with optional path appended.
  '''
  return get_admin_url( None, path, scheme )


def get_admin_url( blog_id = None, path = '', scheme = 'admin' ):
  ''' Retrieves the URL to the admin area for a given site.
  @param int    blog_id Optional. Site ID. Default None (current site).
  @param string path    Optional. Path relative to the admin URL. Default empty.
  @param string scheme  Optional. The scheme to use. Accepts 'http' or 'https',
                         to force those schemes. Default 'admin', which obeys
                         force_ssl_admin() and is_ssl().
  @return string Admin URL link with optional path appended.
  '''
  url = get_site_url(blog_id, 'wp-admin/', scheme)

  if path and Php.is_string( path ):
    url += Php.ltrim( path, '/' )

  # Filters the admin area URL.
  # @param string   url     The complete admin area URL including scheme and path.
  # @param string   path    Path relative to the admin area URL. Blank string if no path is specified.
  # @param int|None blog_id Site ID, or None for the current site.
  return WiPg.apply_filters( 'admin_url', url, path, blog_id )


def includes_url( path = '', scheme = None ):
  ''' Retrieves the URL to the includes directory.
  @param string path   Optional. Path relative to the includes URL. Default empty.
  @param string scheme Optional. Scheme to give the includes URL context. Accepts
                        'http', 'https', or 'relative'. Default None.
  @return string Includes URL link with optional path appended.
  '''
  url = site_url( '/' + WPINC + '/', scheme )

  if path and Php.is_string( path ):
    url += Php.ltrim(path, '/')

  # Filters the URL to the includes directory.
  # @param string url  The complete URL to the includes directory including scheme and path.
  # @param string path Path relative to the URL to the wp-includes directory. Blank string
  #                     if no path is specified.
  return WiPg.apply_filters( 'includes_url', url, path )


def content_url( path = '' ):
  ''' Retrieves the URL to the content directory.
  @param string path Optional. Path relative to the content URL. Default empty.
  @return string Content URL link with optional path appended.
  '''
  url = set_url_scheme( WP_CONTENT_URL )

  if path and Php.is_string( path ):
    url += '/' + Php.ltrim(path, '/')

  # Filters the URL to the content directory.
  # @param string url  The complete URL to the content directory including scheme and path.
  # @param string path Path relative to the URL to the content directory. Blank string
  #                     if no path is specified.
  return WiPg.apply_filters( 'content_url', url, path)


def plugins_url( path = '', plugin = '' ):
  ''' Retrieves a URL within the plugins or mu-plugins directory.
  Defaults to the plugins directory URL if no arguments are supplied.
  @param  string path   Optional. Extra path appended to the end of the URL, including
                         the relative directory if plugin is supplied. Default empty.
  @param  string plugin Optional. A full path to a file inside a plugin or mu-plugin.
                         The URL will be relative to its directory. Default empty.
                         Typically this is done by passing `__FILE__` as the argument.
  @return string Plugins URL link with optional paths appended.
  '''

  path = wp_normalize_path( path )
  plugin = wp_normalize_path( plugin )
  mu_plugin_dir = wp_normalize_path( WPMU_PLUGIN_DIR )

  if not Php.empty(locals(), 'plugin') and 0 == Php.strpos(plugin, mu_plugin_dir):
    url = WPMU_PLUGIN_URL
  else:
    url = WP_PLUGIN_URL


  url = set_url_scheme( url )

  if not Php.empty(locals(), 'plugin') and Php.is_string(plugin):
    folder = dirname(plugin_basename(plugin))
    if '.' != folder:
      url += '/' + Php.ltrim(folder, '/')

  if path and Php.is_string( path ):
    url += '/' + Php.ltrim(path, '/')

  # Filters the URL to the plugins directory.
  # @param string url    The complete URL to the plugins directory including scheme and path.
  # @param string path   Path relative to the URL to the plugins directory. Blank string
  #                       if no path is specified.
  # @param string plugin The plugin file path to be relative to. Blank string if no plugin
  #                       is specified.
  return WiPg.apply_filters( 'plugins_url', url, path, plugin )


def network_site_url( path = '', scheme = None ):
  ''' Retrieves the site URL for the current network.
  Returns the site URL with the appropriate protocol, 'https' if
  is_ssl() and 'http' otherwise. If scheme is 'http' or 'https', is_ssl() is
  overridden.
  @see set_url_scheme()
  @param string path   Optional. Path relative to the site URL. Default empty.
  @param string scheme Optional. Scheme to give the site URL context. Accepts
                        'http', 'https', or 'relative'. Default None.
  @return string Site URL link with optional path appended.
  '''
  if not WpC.WB.Wj.is_multisite():
    return site_url(path, scheme)

  current_network = get_network()

  if 'relative' == scheme:
    url = current_network.path
  else:
    url = set_url_scheme( 'http://' + current_network.domain + current_network.path, scheme )

  if path and Php.is_string( path ):
    url += Php.ltrim( path, '/' )

  # Filters the network site URL.
  # @param string      url    The complete network site URL including scheme and path.
  # @param string      path   Path relative to the network site URL. Blank string if
  #                            no path is specified.
  # @param string|None scheme Scheme to give the URL context. Accepts 'http', 'https',
  #                            'relative' or None.
  return WiPg.apply_filters( 'network_site_url', url, path, scheme )


def network_home_url( path = '', scheme = None ):
  ''' Retrieves the home URL for the current network.
  Returns the home URL with the appropriate protocol, 'https' is_ssl()
  and 'http' otherwise. If `scheme` is 'http' or 'https', `is_ssl()` is
  overridden.
  @param  string path   Optional. Path relative to the home URL. Default empty.
  @param  string scheme Optional. Scheme to give the home URL context. Accepts
                         'http', 'https', or 'relative'. Default None.
  @return string Home URL link with optional path appended.
  '''
  if not WpC.WB.Wj.is_multisite():
    return home_url(path, scheme)

  current_network = get_network()
  orig_scheme = scheme

  if not Php.in_array( scheme, array( 'http', 'https', 'relative' ) ):
    scheme = 'https' if WpC.WB.Wj.is_ssl() and not is_admin() else 'http'

  if 'relative' == scheme:
    url = current_network.path
  else:
    url = set_url_scheme( 'http://' + current_network.domain + current_network.path, scheme )

  if path and Php.is_string( path ):
    url += Php.ltrim( path, '/' )

  # Filters the network home URL.
  # @param string      url         The complete network home URL including scheme and path.
  # @param string      path        Path relative to the network home URL. Blank string
  #                                 if no path is specified.
  # @param string|None orig_scheme Scheme to give the URL context. Accepts 'http', 'https',
  #                                 'relative' or None.
  return WiPg.apply_filters( 'network_home_url', url, path, orig_scheme)


def network_admin_url( path = '', scheme = 'admin' ):
  ''' Retrieves the URL to the admin area for the network.
  @param string path   Optional path relative to the admin URL. Default empty.
  @param string scheme Optional. The scheme to use. Default is 'admin', which obeys force_ssl_admin()
                        and is_ssl(). 'http' or 'https' can be passed to force those schemes.
  @return string Admin URL link with optional path appended.
  '''
  if not WpC.WB.Wj.is_multisite():
    return admin_url( path, scheme )

  url = network_site_url('wp-admin/network/', scheme)

  if path and Php.is_string( path ):
    url += Php.ltrim(path, '/')

  # Filters the network admin URL.
  # @param string url  The complete network admin URL including scheme and path.
  # @param string path Path relative to the network admin URL. Blank string if
  #                     no path is specified.
  return WiPg.apply_filters( 'network_admin_url', url, path )


def user_admin_url( path = '', scheme = 'admin' ):
  ''' Retrieves the URL to the admin area for the current user.
  @param string path   Optional. Path relative to the admin URL. Default empty.
  @param string scheme Optional. The scheme to use. Default is 'admin', which obeys force_ssl_admin()
                        and is_ssl(). 'http' or 'https' can be passed to force those schemes.
  @return string Admin URL link with optional path appended.
  '''
  url = network_site_url('wp-admin/user/', scheme)

  if path and Php.is_string( path ):
    url += Php.ltrim(path, '/')

  # Filters the user admin URL for the current user.
  # @param string url  The complete URL including scheme and path.
  # @param string path Path relative to the URL. Blank string if
  #                     no path is specified.
  return WiPg.apply_filters( 'user_admin_url', url, path )


def self_admin_url( path = '', scheme = 'admin' ):
  ''' Retrieves the URL to the admin area for either the current site or the network depending on context.
  @param string path   Optional. Path relative to the admin URL. Default empty.
  @param string scheme Optional. The scheme to use. Default is 'admin', which obeys force_ssl_admin()
                        and is_ssl(). 'http' or 'https' can be passed to force those schemes.
  @return string Admin URL link with optional path appended.
  '''
  if is_network_admin():
    return network_admin_url(path, scheme)
  elif is_user_admin():
    return user_admin_url(path, scheme)
  else:
    return admin_url(path, scheme)


def set_url_scheme( url, scheme = None ):
  ''' Sets the scheme for a URL.
  @since 4.4.0 The 'rest' scheme was added.
  @param string      url    Absolute URL that includes a scheme
  @param string|None scheme Optional. Scheme to give url. Currently 'http', 'https', 'login',
                             'login_post', 'admin', 'relative', 'rest', 'rpc', or None. Default None.
  @return string url URL with chosen scheme.
  '''
  orig_scheme = scheme

  if not scheme:
    scheme = 'https' if WpC.WB.Wj.is_ssl() else 'http'
  elif scheme == 'admin' or scheme == 'login' or scheme == 'login_post' or scheme == 'rpc':
    scheme = WpC.WB.Wj.is_ssl() or 'https' if force_ssl_admin() else 'http'
  elif scheme != 'http' and scheme != 'https' and scheme != 'relative':
    scheme = 'https' if WpC.WB.Wj.is_ssl() else 'http'

  url = Php.trim( url )
  if Php.substr( url, 0, 2 ) == '//':
    url = 'http:' + url

  if 'relative' == scheme:
    url = Php.ltrim( Php.preg_replace( '#^\w+://[^/]*#', '', url ) )
    if url != '' and url[0] == '/':
      url = '/' + Php.ltrim(url , "/ \t\n\r\0\x0B" )
  else:
    url = Php.preg_replace( '#^\w+://#', scheme + '://', url )

  # Filters the resulting URL after setting the scheme.
  # @param string      url         The complete URL including scheme and path.
  # @param string      scheme      Scheme applied to the URL. One of 'http', 'https', or 'relative'.
  # @param string|None orig_scheme Scheme requested for the URL. One of 'http', 'https', 'login',
  #                                 'login_post', 'admin', 'relative', 'rest', 'rpc', or None.
  return WiPg.apply_filters( 'set_url_scheme', url, scheme, orig_scheme )


def get_dashboard_url( user_id = 0, path = '', scheme = 'admin' ):
  ''' Retrieves the URL to the user's dashboard.
  If a user does not belong to any site, the global user dashboard is used. If the user
  belongs to the current site, the dashboard for the current site is returned. If the user
  cannot edit the current site, the dashboard to the user's primary site is returned.
  @param int    user_id Optional. User ID. Defaults to current user.
  @param string path    Optional path relative to the dashboard. Use only paths known to
                         both site and user admins. Default empty.
  @param string scheme  The scheme to use. Default is 'admin', which obeys force_ssl_admin()
                         and is_ssl(). 'http' or 'https' can be passed to force those schemes.
  @return string Dashboard URL link with optional path appended.
  '''
  user_id = int(user_id) if user_id else get_current_user_id()

  blogs = get_blogs_of_user( user_id )
  if not is_super_admin() and Php.empty(locals(), 'blogs'):
    url = user_admin_url( path, scheme )
  elif not WpC.WB.Wj.is_multisite():
    url = admin_url( path, scheme )
  else:
    current_blog = WpC.WB.Wj.get_current_blog_id()
    if current_blog  and ( is_super_admin( user_id ) or Php.in_array( current_blog, array_keys( blogs ) ) ):
      url = admin_url( path, scheme )
    else:
      active = get_active_blog_for_user( user_id )
      if active:
        url = get_admin_url( active.blog_id, path, scheme )
      else:
        url = user_admin_url( path, scheme )

  # Filters the dashboard URL for a user.
  # @param string url     The complete URL including scheme and path.
  # @param int    user_id The user ID.
  # @param string path    Path relative to the URL. Blank string if no path is specified.
  # @param string scheme  Scheme to give the URL context. Accepts 'http', 'https', 'login',
  #                        'login_post', 'admin', 'relative' or None.
  return WiPg.apply_filters( 'user_dashboard_url', url, user_id, path, scheme)


def get_edit_profile_url( user_id = 0, scheme = 'admin' ):
  ''' Retrieves the URL to the user's profile editor.
  @param int    user_id Optional. User ID. Defaults to current user.
  @param string scheme  Optional. The scheme to use. Default is 'admin', which obeys force_ssl_admin()
                         and is_ssl(). 'http' or 'https' can be passed to force those schemes.
  @return string Dashboard URL link with optional path appended.
  '''
  user_id = int(user_id) if user_id else get_current_user_id()

  if is_user_admin():
    url = user_admin_url( 'profile.php', scheme )
  elif is_network_admin():
    url = network_admin_url( 'profile.php', scheme )
  else:
    url = get_dashboard_url( user_id, 'profile.php', scheme )

  # Filters the URL for a user's profile editor.
  # @param string url     The complete URL including scheme and path.
  # @param int    user_id The user ID.
  # @param string scheme  Scheme to give the URL context. Accepts 'http', 'https', 'login',
  #                        'login_post', 'admin', 'relative' or None.
  return WiPg.apply_filters( 'edit_profile_url', url, user_id, scheme)


def wp_get_canonical_url( post = None ):
  ''' Returns the canonical URL for a post.
  When the post is the same as the current requested page the function will handle the
  pagination arguments too.
  @param int|WP_Post post Optional. Post ID or object. Default is global `post`.
  @return string|False The canonical URL, or False if the post does not exist or has not
                       been published yet.
  '''
  post = WiP.get_post( post )

  if not post:
    return False

  if 'publish' != post.post_status:
    return False

  canonical_url = get_permalink( post )

  # If a canonical is being generated for the current page, make sure it has pagination if needed.
  if post.ID == get_queried_object_id():
    page = get_query_var( 'page', 0 )
    if page >= 2:
      if '' == WiO.get_option( 'permalink_structure' ):
        canonical_url = add_query_arg( 'page', page, canonical_url )
      else:
        canonical_url = WiF.trailingslashit( canonical_url ) + user_trailingslashit( page, 'single_paged' )

    cpage = get_query_var( 'cpage', 0 )
    if cpage:
      canonical_url = get_comments_pagenum_link( cpage )

  # Filters the canonical URL for a post.
  # @param string  string The post's canonical URL.
  # @param WP_Post post   Post object.
  return WiPg.apply_filters( 'get_canonical_url', canonical_url, post )


def rel_canonical():
  ''' Outputs rel=canonical for singular queries.
  @since 4.6.0 Adjusted to use wp_get_canonical_url().
  '''
  if not Php.is_singular():
    return

  Id = get_queried_object_id()

  if 0 == Id:
    return

  url = wp_get_canonical_url( Id )

  if not Php.empty(locals(),  'url' ):
    Php.echo( '<link rel="canonical" href="' + esc_url( url ) + '" />' + "\n")


def wp_get_shortlink( Id = 0, context = 'post', allow_slugs = True ):
  ''' Returns a shortlink for a post, page, attachment, or site.
  This function exists to provide a shortlink tag that all themes and plugins can target.
  A plugin must hook in to provide the actual shortlinks. Default shortlink support is
  limited to providing ?p= style links for posts. Plugins can short-circuit this function
  via the {@see 'pre_get_shortlink'} filter or filter the output via the {@see 'get_shortlink'}
  filter.
  @param int    Id          Optional. A post or site Id. Default is 0, which means the current post or site.
  @param string context     Optional. Whether the Id is a 'site' Id, 'post' Id, or 'media' Id. If 'post',
                             the post_type of the post is consulted. If 'query', the current query is consulted
                             to determine the Id and context. Default 'post'.
  @param bool   allow_slugs Optional. Whether to allow post slugs in the shortlink. It is up to the plugin how
                             and whether to honor this. Default True.
  @return string A shortlink or an empty string if no shortlink exists for the requested resource or if shortlinks
                 are not enabled.
  '''
  # Filters whether to preempt generating a shortlink for the given post.
  # Passing a truthy value to the filter will effectively short-circuit the
  # shortlink-generation process, returning that value instead.
  # @param bool|string return      Short-circuit return value. Either False or a URL string.
  # @param int         Id          Post ID, or 0 for the current post.
  # @param string      context     The context for the link. One of 'post' or 'query',
  # @param bool        allow_slugs Whether to allow post slugs in the shortlink.
  shortlink = WiPg.apply_filters( 'pre_get_shortlink', False, Id, context, allow_slugs )

  if False is not shortlink:
    return shortlink

  post_id = 0
  if 'query' == context and Php.is_singular():
    post_id = get_queried_object_id()
    post = WiP.get_post( post_id )
  elif 'post' == context:
    post = WiP.get_post( Id )
    if not Php.empty(post, 'ID' ):
      post_id = post.ID

  shortlink = ''

  # Return p= link for all public post types.
  if not Php.empty(locals(),  'post_id' ):
    post_type = WiP.get_post_type_object( post.post_type )

    if 'page' == post.post_type and post.ID == WiO.get_option( 'page_on_front' ) and 'page' == WiO.get_option( 'show_on_front' ):
      shortlink = home_url( '/' )
    elif post_type.public:
      shortlink = home_url( '?p=' + post_id )

  # Filters the shortlink for a post.
  # @param string shortlink   Shortlink URL.
  # @param int    Id          Post ID, or 0 for the current post.
  # @param string context     The context for the link. One of 'post' or 'query',
  # @param bool   allow_slugs Whether to allow post slugs in the shortlink. Not used by default.
  return WiPg.apply_filters( 'get_shortlink', shortlink, Id, context, allow_slugs )


def wp_shortlink_wp_head():
  ''' Injects rel=shortlink into the head if a shortlink is defined for the current page.
  Attached to the {@see 'wp_head'} action.
  '''
  shortlink = wp_get_shortlink( 0, 'query' )

  if Php.empty(locals(),  'shortlink' ):
    return

  Php.echo( "<link rel='shortlink' href='" + esc_url( shortlink ) + "' />\n")


def wp_shortlink_header():
  ''' Sends a Link: rel=shortlink header if a shortlink is defined for the current page.
  Attached to the {@see 'wp'} action.
  '''
  if headers_sent():
    return

  shortlink = wp_get_shortlink(0, 'query')

  if Php.empty(locals(), 'shortlink'):
    return

  header('Link: <' + shortlink + '>; rel=shortlink', False)


def the_shortlink( text = '', title = '', before = '', after = '' ):
  ''' Displays the shortlink for a post.
  Must be called from inside "The Loop"
  Call like the_shortlink( __( 'Shortlinkage FTW' ) )
  @param string text   Optional The link text or HTML to be displayed. Defaults to 'This is the short link.'
  @param string title  Optional The tooltip for the link. Must be sanitized. Defaults to the sanitized post title.
  @param string before Optional HTML to display before the link. Default empty.
  @param string after  Optional HTML to display after the link. Default empty.
  '''
  post = WiP.get_post()

  if Php.empty(locals(),  'text' ):
    text = __('This is the short link.')

  if Php.empty(locals(),  'title' ):
    title = the_title_attribute( array( ('echo', False),) )

  shortlink = wp_get_shortlink( post.ID )

  if not Php.empty(locals(),  'shortlink' ):
    link = '<a rel="shortlink" href="' + esc_url( shortlink ) + '" title="' + title + '">' + text + '</a>'

    # Filters the short link anchor tag for a post.
    # @param string link      Shortlink anchor tag.
    # @param string shortlink Shortlink URL.
    # @param string text      Shortlink's text.
    # @param string title     Shortlink's title attribute.
    link = WiPg.apply_filters( 'the_shortlink', link, shortlink, text, title )
    Php.echo( before, link, after)


def get_avatar_url( id_or_email, args = None ):
  ''' Retrieves the avatar URL.
  @param mixed id_or_email The Gravatar to retrieve a URL for. Accepts a user_id, gravatar md5 hash,
                            user email, WP_User object, WP_Post object, or WP_Comment object.
  @param array args {
      Optional. Arguments to return instead of the default arguments.
      @type int    size           Height and width of the avatar in pixels. Default 96.
      @type string default        URL for the default image or a default type. Accepts '404' (return
                                   a 404 instead of a default image), 'retro' (8bit), 'monsterid' (monster),
                                   'wavatar' (cartoon face), 'indenticon' (the "quilt"), 'mystery', 'mm',
                                   or 'mysteryman' (The Oyster Man), 'blank' (transparent GIF), or
                                   'gravatar_default' (the Gravatar logo). Default is the value of the
                                   'avatar_default' option, with a fallback of 'mystery'.
      @type bool   force_default  Whether to always show the default image, never the Gravatar. Default False.
      @type string rating         What rating to display avatars up to. Accepts 'G', 'PG', 'R', 'X', and are
                                   judged in that order. Default is the value of the 'avatar_rating' option.
      @type string scheme         URL scheme to use. See set_url_scheme() for accepted values.
                                   Default None.
      @type array  processed_args When the function returns, the value will be the processed/sanitized args
                                   plus a "found_avatar" guess. Pass as a reference. Default None.
  }
  @return False|string The URL of the avatar we found, or False if we couldn't find an avatar.
  '''
  args = get_avatar_data( id_or_email, args )
  return args['url']


def get_avatar_data( id_or_email, args = None ):
  ''' Retrieves default data about the avatar.
  @param mixed id_or_email The Gravatar to retrieve. Accepts a user_id, gravatar md5 hash,
                             user email, WP_User object, WP_Post object, or WP_Comment object.
  @param array args {
      Optional. Arguments to return instead of the default arguments.
      @type int    size           Height and width of the avatar image file in pixels. Default 96.
      @type int    height         Display height of the avatar in pixels. Defaults to size.
      @type int    width          Display width of the avatar in pixels. Defaults to size.
      @type string default        URL for the default image or a default type. Accepts '404' (return
                                   a 404 instead of a default image), 'retro' (8bit), 'monsterid' (monster),
                                   'wavatar' (cartoon face), 'indenticon' (the "quilt"), 'mystery', 'mm',
                                   or 'mysteryman' (The Oyster Man), 'blank' (transparent GIF), or
                                   'gravatar_default' (the Gravatar logo). Default is the value of the
                                   'avatar_default' option, with a fallback of 'mystery'.
      @type bool   force_default  Whether to always show the default image, never the Gravatar. Default False.
      @type string rating         What rating to display avatars up to. Accepts 'G', 'PG', 'R', 'X', and are
                                   judged in that order. Default is the value of the 'avatar_rating' option.
      @type string scheme         URL scheme to use. See set_url_scheme() for accepted values.
                                   Default None.
      @type array  processed_args When the function returns, the value will be the processed/sanitized args
                                   plus a "found_avatar" guess. Pass as a reference. Default None.
      @type string extra_attr     HTML attributes to insert in the IMG element. Is not sanitized. Default empty.
  }
  @return array processed_args {
      Along with the arguments passed in `args`, this will contain a couple of extra arguments.
      @type bool   found_avatar True if we were able to find an avatar for this user,
                                 False or not set if we couldn't.
      @type string url          The URL of the avatar we found.
  }
  '''
  args = wp_parse_args( args, array(
    ('size'          , 96),
    ('height'        , None),
    ('width'         , None),
    ('default'       , WiO.get_option( 'avatar_default', 'mystery' )),
    ('force_default' , False),
    ('rating'        , WiO.get_option( 'avatar_rating' )),
    ('scheme'        , None),
    ('processed_args', None), # if used, should be a reference
    ('extra_attr'    , ''),
  ) )

  if is_numeric( args['size'] ):
    args['size'] = absint( args['size'] )
    if not args['size']:
      args['size'] = 96
  else:
    args['size'] = 96

  if is_numeric( args['height'] ):
    args['height'] = absint( args['height'] )
    if not args['height']:
      args['height'] = args['size']
  else:
    args['height'] = args['size']

  if is_numeric( args['width'] ):
    args['width'] = absint( args['width'] )
    if not args['width']:
      args['width'] = args['size']
  else:
    args['width'] = args['size']

  if Php.empty( args, 'default' ):
    args['default'] = WiO.get_option( 'avatar_default', 'mystery' )

  if args['default'] in ('mm', 'mystery', 'mysteryman'):
    args['default'] = 'mm'
  if args['default'] == 'gravatar_default':
    args['default'] = False

  args['force_default'] = bool( args['force_default'] )

  args['rating'] = strtolower( args['rating'] )

  args['found_avatar'] = False

  # Filters whether to retrieve the avatar URL early.
  # Passing a non-None value in the 'url' member of the return array will
  # effectively short circuit get_avatar_data(), passing the value through
  # the {@see 'get_avatar_data'} filter and returning early.
  # @param array  args        Arguments passed to get_avatar_data(), after processing.
  # @param mixed  id_or_email The Gravatar to retrieve. Accepts a user_id, gravatar md5 hash,
  #                            user email, WP_User object, WP_Post object, or WP_Comment object.
  args = WiPg.apply_filters( 'pre_get_avatar_data', args, id_or_email )

  if Php.isset( args, 'url' ) and not is_null( args['url'] ):
    # This filter is documented in wp-includes/link-template.php
    return WiPg.apply_filters( 'get_avatar_data', args, id_or_email )

  email_hash = ''
  user = email = False

  if Php.is_object( id_or_email ) and Php.isset( id_or_email, 'comment_ID' ):
    id_or_email = get_comment( id_or_email )

  import wp.i.cls.user as WcU
  # Process the user identifier.
  if is_numeric( id_or_email ):
    user = WiPgbl.get_user_by( 'id', absint( id_or_email ) )
  elif Php.is_string( id_or_email ):
    if Php.strpos( id_or_email, '@md5.gravatar.com' ):
      # md5 hash
      #list( email_hash ) = Php.explode( '@', id_or_email )
      email_hash = Php.explode( '@', id_or_email )[0]
    else:
      # email address
      email = id_or_email
  elif isinstance(id_or_email, WcU.WP_User):
    # User Object
    user = id_or_email
  elif isinstance(id_or_email, WiP.WP_Post):
    # Post Object
    user = WiPgbl.get_user_by( 'id', int(id_or_email.post_author) )
  elif isinstance(id_or_email, WP_Comment):
    # Filters the list of allowed comment types for retrieving avatars.
    # @param array types An array of content types. Default only contains 'comment'.
    allowed_comment_types = WiPg.apply_filters( 'get_avatar_comment_types', array( 'comment',) )
    if not Php.empty( id_or_email, 'comment_type' ) and not Php.in_array( id_or_email.comment_type, Php.Array( allowed_comment_types )):
      args['url'] = False
      # This filter is documented in wp-includes/link-template.php
      return WiPg.apply_filters( 'get_avatar_data', args, id_or_email )

    if not Php.empty( id_or_email, 'user_id' ):
      user = WiPgbl.get_user_by( 'id', int(id_or_email.user_id) )
    if ( not user or WpC.WB.Wj.is_wp_error( user ) ) and not Php.empty( id_or_email, 'comment_author_email' ):
      email = id_or_email.comment_author_email

  if not email_hash:
    if user:
      email = user.user_email

    if email:
      email_hash = md5( strtolower( Php.trim( email ) ) )

  if email_hash:
    args['found_avatar'] = True
    gravatar_server = hexdec( email_hash[0] ) % 3
  else:
    gravatar_server = rand( 0, 2 )

  url_args = array(
    ('s', args['size']),
    ('d', args['default']),
    ('f', 'y' if args['force_default'] else False),
    ('r', args['rating']),
  )

  if WpC.WB.Wj.is_ssl():
    url = 'https://secure.gravatar.com/avatar/' + email_hash
  else:
    url = Php.sprintf( 'http://%d.gravatar.com/avatar/%s', gravatar_server, email_hash )

  url = add_query_arg(
    rawurlencode_deep( array_filter( url_args ) ),
    set_url_scheme( url, args['scheme'] )
  )

  # Filters the avatar URL.
  # @param string url         The URL of the avatar.
  # @param mixed  id_or_email The Gravatar to retrieve. Accepts a user_id, gravatar md5 hash,
  #                            user email, WP_User object, WP_Post object, or WP_Comment object.
  # @param array  args        Arguments passed to get_avatar_data(), after processing.
  args['url'] = WiPg.apply_filters( 'get_avatar_url', url, id_or_email, args )

  # Filters the avatar data.
  # @param array  args        Arguments passed to get_avatar_data(), after processing.
  # @param mixed  id_or_email The Gravatar to retrieve. Accepts a user_id, gravatar md5 hash,
  #                            user email, WP_User object, WP_Post object, or WP_Comment object.
  return WiPg.apply_filters( 'get_avatar_data', args, id_or_email )


def get_theme_file_uri( File = '' ):
  ''' Retrieves the URL of a file in the theme.
  Searches in the stylesheet directory before the template directory so themes
  which inherit from a parent theme can just override one file.
  @param string File Optional. File to search for in the stylesheet directory
  @return string The URL of the file.
  '''
  File = Php.ltrim( File, '/' )
  
  if Php.empty(locals(), 'File' ):
    url = get_stylesheet_directory_uri()
  elif Php.file_exists( get_stylesheet_directory() + '/' + File ):
    url = get_stylesheet_directory_uri() + '/' + File
  else:
    url = get_template_directory_uri() + '/' + File
  
  # Filters the URL to a file in the theme.
  # @param string url  The file URL.
  # @param string File The requested file to search for.
  return WiPg.apply_filters( 'theme_file_uri', url, File )
  

def get_parent_theme_file_uri( File = '' ):
  '''
  Retrieves the URL of a file in the parent theme.
  @param string File Optional. File to return the URL for in the template directory.
  @return string The URL of the file.
  '''
  File = Php.ltrim( File, '/' )
  
  if Php.empty(locals(), 'File' ):
    url = get_template_directory_uri()
  else:
    url = get_template_directory_uri() + '/' + File
  
  # Filters the URL to a file in the parent theme.
  # @param string url  The file URL.
  # @param string File The requested file to search for.
  return WiPg.apply_filters( 'parent_theme_file_uri', url, File )
  

def get_theme_file_path( File = '' ):
  ''' Retrieves the path of a file in the theme.
  Searches in the stylesheet directory before the template directory so themes
  which inherit from a parent theme can just override one file.
  @param string File Optional. File to search for in the stylesheet directory
  @return string The path of the file.
  '''
  File = Php.ltrim( File, '/' )
  
  if Php.empty(locals(), 'File' ):
    path = get_stylesheet_directory()
  elif file_exists( get_stylesheet_directory() + '/' + File ):
    path = get_stylesheet_directory() + '/' + File
  else:
    path = get_template_directory() + '/' + File
  
  # Filters the path to a file in the theme.
  # @param string path The file path.
  # @param string File The requested file to search for.
  return WiPg.apply_filters( 'theme_file_path', path, File )
  

def get_parent_theme_file_path( File = '' ):
  ''' Retrieves the path of a file in the parent theme.
  @param string File Optional. File to return the path for in the template
                                directory.
  @return string The path of the file.
  '''
  File = Php.ltrim( File, '/' )
  
  if Php.empty(locals(), 'File' ):
    path = get_template_directory()
  else:
    path = get_template_directory() + '/' + File
  
  # Filters the path to a file in the parent theme.
  # @param string path The file path.
  # @param string File The requested file to search for.
  return WiPg.apply_filters( 'parent_theme_file_path', path, File )
  

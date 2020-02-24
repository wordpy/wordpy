import wp.conf      as WpC

# General template tags that can go anywhere in a template.
# @package WordPress
# @subpackage Template

def get_header( name = None ):
  ''' Load header template.
  Includes the header template for a theme or if a name is specified then a
  specialised header will be included.
  For the parameter, if the file is called "header-special.php" then specify
  "special".
  @param string name The name of the specialised header.
  '''
  # Fires before the header template file is loaded.
  # The hook allows a specific header template file to be used in place of the
  # default header template file. If your file is called header-new.php,
  # you would specify the filename in the hook as get_header( 'new' ).
  # @since 2.8.0 name parameter added.
  # @param string|None name Name of the specific header file to use. None for the default header.
  do_action( 'get_header', name )

  templates = array()
  name = (string) name
  if '' != name:
    templates[None] = "header-{}.php".format(name)

  templates[None] = 'header.php'

  locate_template( templates, true )


def get_footer( name = None ):
  ''' Load footer template.
  Includes the footer template for a theme or if a name is specified then a
  specialised footer will be included.
  For the parameter, if the file is called "footer-special.php" then specify
  "special".
  @param string name The name of the specialised footer.
  '''
  # Fires before the footer template file is loaded.
  # The hook allows a specific footer template file to be used in place of the
  # default footer template file. If your file is called footer-new.php,
  # you would specify the filename in the hook as get_footer( 'new' ).
  # @since 2.8.0 name parameter added.
  # @param string|None name Name of the specific footer file to use. None for the default footer.
  do_action( 'get_footer', name )

  templates = array()
  name = (string) name
  if '' != name:
    templates[None] = "footer-{}.php".format(name)

  templates[None]    = 'footer.php'

  locate_template( templates, true )


def get_sidebar( name = None ):
  ''' Load sidebar template.
  Includes the sidebar template for a theme or if a name is specified then a
  specialised sidebar will be included.
  For the parameter, if the file is called "sidebar-special.php" then specify
  "special".
  @param string name The name of the specialised sidebar.
  '''
  # Fires before the sidebar template file is loaded.
  # The hook allows a specific sidebar template file to be used in place of the
  # default sidebar template file. If your file is called sidebar-new.php,
  # you would specify the filename in the hook as get_sidebar( 'new' ).
  # @since 2.8.0 name parameter added.
  # @param string|None name Name of the specific sidebar file to use. None for the default sidebar.
  do_action( 'get_sidebar', name )

  templates = array()
  name = (string) name
  if '' != name:
    templates[None] = "sidebar-{}.php".format(name)

  templates[None] = 'sidebar.php'

  locate_template( templates, true )


def get_template_part( slug, name = None ):
  ''' Load a template part into a template
  Makes it easy for a theme to reuse sections of code in a easy to overload way
  for child themes.
  Includes the named template part for a theme or if a name is specified then a
  specialised part will be included. If the theme contains no {slug}.php file
  then no template will be included.
  The template is included using require, not require_once, so you may include the
  same template part multiple times.
  For the name parameter, if the file is called "{slug}-special.php" then specify
  "special".
  @param string slug The slug name for the generic template.
  @param string name The name of the specialised template.
  '''
  # Fires before the specified template part file is loaded.
  # The dynamic portion of the hook name, `slug`, refers to the slug name
  # for the generic template part.
  # @param string slug The slug name for the generic template.
  # @param string|None name The name of the specialized template.
  do_action( "get_template_part_"+ slug, slug, name )

  templates = array()
  name = (string) name
  if '' != name:
    templates[None] = "{}-{}.php".format(slug, name)

  templates[None] = slug +".php"

  locate_template(templates, true, False)


def get_search_form( echo = true ):
  ''' Display search form.
  Will first attempt to locate the searchform.php file in either the child or
  the parent, then load it. If it doesn't exist, then the default search form
  will be displayed. The default search form is HTML, which will be displayed.
  There is a filter applied to the search form HTML in order to edit or replace
  it. The filter is {@see 'get_search_form'}.
  This function is primarily used by themes which want to hardcode the search
  form into the sidebar and also by the search widget in WordPress.
  There is also an action that is called whenever the function is run called,
  {@see 'pre_get_search_form'}. This can be useful for outputting JavaScript that the
  search relies on or various formatting that applies to the beginning of the
  search. To give a few examples of what it can be used for.
  @param bool echo Default to echo and not return the form.
  @return string|void String when echo is False.
  '''
  # Fires before the search form is retrieved, at the start of get_search_form().
  # @since 2.7.0 as 'get_search_form' action.
  # @link https://core.trac.wordpress.org/ticket/19321
  do_action( 'pre_get_search_form' )

  Format = current_theme_supports( 'html5', 'search-form' ) ? 'html5' : 'xhtml'

  # Filters the HTML format of the search form.
  # @param string Format The type of markup to use in the search form.
  #                       Accepts 'html5', 'xhtml'.
  Format = apply_filters( 'search_form_format', Format )

  search_form_template = locate_template( 'searchform.php' )
  if '' != search_form_template:
    ob_start()
    require( search_form_template )
    form = ob_get_clean()
  else:
    if 'html5' == Format:
      form = '<form role="search" method="get" class="search-form" action="' . esc_url( home_url( '/' ) ) . '">
        <label>
          <span class="screen-reader-text">' . _x( 'Search for:', 'label' ) . '</span>
          <input type="search" class="search-field" placeholder="' . esc_attr_x( 'Search &hellip;', 'placeholder' ) . '" value="' . get_search_query() . '" name="s" />
        </label>
        <input type="submit" class="search-submit" value="'. esc_attr_x( 'Search', 'submit button' ) .'" />
      </form>'
    else:
      form = '<form role="search" method="get" id="searchform" class="searchform" action="' . esc_url( home_url( '/' ) ) . '">
        <div>
          <label class="screen-reader-text" for="s">' . _x( 'Search for:', 'label' ) . '</label>
          <input type="text" value="' . get_search_query() . '" name="s" id="s" />
          <input type="submit" id="searchsubmit" value="'. esc_attr_x( 'Search', 'submit button' ) .'" />
        </div>
      </form>'

  # Filters the HTML output of the search form.
  # @param string form The search form HTML output.
  result = apply_filters( 'get_search_form', form )

  if None === result:
    result = form

  if echo:
    echo result
  else:
    return result


def wp_loginout(redirect = '', echo = true):
  ''' Display the Log In/Out link.
  Displays a link, which allows users to navigate to the Log In page to log in
  or log out depending on whether they are currently logged in.
  @param string redirect Optional path to redirect to on login/logout.
  @param bool   echo     Default to echo and not return the link.
  @return string|void String when retrieving.
  '''
  if ! is_user_logged_in():
    link = '<a href="' . esc_url( wp_login_url(redirect) ) . '">' . __('Log in') . '</a>'
  else:
    link = '<a href="' . esc_url( wp_logout_url(redirect) ) . '">' . __('Log out') . '</a>'

  if echo:
    # Filters the HTML output for the Log In/Log Out link.
    # @param string link The HTML link content.
    echo apply_filters( 'loginout', link )
  else:
    # This filter is documented in wp-includes/general-template.php
    return apply_filters( 'loginout', link )


def wp_logout_url(redirect = ''):
  ''' Retrieves the logout URL.
  Returns the URL that allows the user to log out of the site.
  @param string redirect Path to redirect to on logout.
  @return string The logout URL. Note: HTML-encoded via esc_html() in wp_nonce_url().
  '''
  args = array( ('action', 'logout'), )
  if !Php.empty(locals(), 'redirect'):
    args['redirect_to'] = urlencode( redirect )

  logout_url = add_query_arg(args, site_url('wp-login.php', 'login'))
  logout_url = wp_nonce_url( logout_url, 'log-out' )

  # Filters the logout URL.
  # @param string logout_url The HTML-encoded logout URL.
  # @param string redirect   Path to redirect to on logout.
  return apply_filters( 'logout_url', logout_url, redirect )


def wp_login_url(redirect = '', force_reauth = False):
  ''' Retrieves the login URL.
  @param string redirect     Path to redirect to on log in.
  @param bool   force_reauth Whether to force reauthorization, even if a cookie is present.
                              Default False.
  @return string The login URL. Not HTML-encoded.
  '''
  login_url = site_url('wp-login.php', 'login')

  if !Php.empty(locals(), 'redirect'):
    login_url = add_query_arg('redirect_to', urlencode(redirect), login_url)

  if force_reauth:
    login_url = add_query_arg('reauth', '1', login_url)

  # Filters the login URL.
  # @since 4.2.0 The `force_reauth` parameter was added.
  # @param string login_url    The login URL. Not HTML-encoded.
  # @param string redirect     The path to redirect to on login, if supplied.
  # @param bool   force_reauth Whether to force reauthorization, even if a cookie is present.
  return apply_filters( 'login_url', login_url, redirect, force_reauth )


def wp_registration_url():
  ''' Returns the URL that allows the user to register on the site.
  @return string User registration URL.
  '''
  # Filters the user registration URL.
  # @param string register The user registration URL.
  return apply_filters( 'register_url', site_url( 'wp-login.php?action=register', 'login' ) )


def wp_login_form( args = array() ):
  ''' Provides a simple login form for use anywhere within WordPress.
  The login format HTML is echoed by default. Pass a False value for `echo` to return it instead.
  @param array args {
      Optional. Array of options to control the form output. Default empty array.
      @type bool   echo           Whether to display the login form or return the form HTML code.
                                   Default true (echo).
      @type string redirect       URL to redirect to. Must be absolute, as in "https://example.com/mypage/".
                                   Default is to redirect back to the request URI.
      @type string form_id        ID attribute value for the form. Default 'loginform'.
      @type string label_username Label for the username or email address field. Default 'Username or Email Address'.
      @type string label_password Label for the password field. Default 'Password'.
      @type string label_remember Label for the remember field. Default 'Remember Me'.
      @type string label_log_in   Label for the submit button. Default 'Log In'.
      @type string id_username    ID attribute value for the username field. Default 'user_login'.
      @type string id_password    ID attribute value for the password field. Default 'user_pass'.
      @type string id_remember    ID attribute value for the remember field. Default 'rememberme'.
      @type string id_submit      ID attribute value for the submit button. Default 'wp-submit'.
      @type bool   remember       Whether to display the "rememberme" checkbox in the form.
      @type string value_username Default value for the username field. Default empty.
      @type bool   value_remember Whether the "Remember Me" checkbox should be checked by default.
                                   Default False (unchecked).
  }
  @return string|void String when retrieving.
  '''
  defaults = array(
    ('echo', true),
    # Default 'redirect' value takes the user back to the request URI.
    ('redirect', ( is_ssl() ? 'https://' : 'http://' ) . _SERVER['HTTP_HOST'] . _SERVER['REQUEST_URI'),
    ('form_id', 'loginform'),
    ('label_username', __( 'Username or Email Address' )),
    ('label_password', __( 'Password' )),
    ('label_remember', __( 'Remember Me' )),
    ('label_log_in', __( 'Log In' )),
    ('id_username', 'user_login'),
    ('id_password', 'user_pass'),
    ('id_remember', 'rememberme'),
    ('id_submit', 'wp-submit'),
    ('remember', true),
    ('value_username', ''),
    # Set 'value_remember' to true to default the "Remember me" checkbox to checked.
    ('value_remember', False),
  )

  # Filters the default login form output arguments.
  # @see wp_login_form()
  # @param array defaults An array of default login form arguments.
  args = wp_parse_args( args, apply_filters( 'login_form_defaults', defaults ) )

  # Filters content to display at the top of the login form.
  # The filter evaluates just following the opening form tag element.
  # @param string content Content to display. Default empty.
  # @param array  args    Array of login form arguments.
  login_form_top = apply_filters( 'login_form_top', '', args )

  # Filters content to display in the middle of the login form.
  # The filter evaluates just following the location where the 'login-password'
  # field is displayed.
  # @param string content Content to display. Default empty.
  # @param array  args    Array of login form arguments.
  login_form_middle = apply_filters( 'login_form_middle', '', args )

  # Filters content to display at the bottom of the login form.
  # The filter evaluates just preceding the closing form tag element.
  # @param string content Content to display. Default empty.
  # @param array  args    Array of login form arguments.
  login_form_bottom = apply_filters( 'login_form_bottom', '', args )

  form = '
    <form name="' . args['form_id'] . '" id="' . args['form_id'] . '" action="' . esc_url( site_url( 'wp-login.php', 'login_post' ) ) . '" method="post">
      ' . login_form_top . '
      <p class="login-username">
        <label for="' . esc_attr( args['id_username'] ) . '">' . esc_html( args['label_username'] ) . '</label>
        <input type="text" name="log" id="' . esc_attr( args['id_username'] ) . '" class="input" value="' . esc_attr( args['value_username'] ) . '" size="20" />
      </p>
      <p class="login-password">
        <label for="' . esc_attr( args['id_password'] ) . '">' . esc_html( args['label_password'] ) . '</label>
        <input type="password" name="pwd" id="' . esc_attr( args['id_password'] ) . '" class="input" value="" size="20" />
      </p>
      ' . login_form_middle . '
      ' . ( args['remember'] ? '<p class="login-remember"><label><input name="rememberme" type="checkbox" id="' . esc_attr( args['id_remember'] ) . '" value="forever"' . ( args['value_remember'] ? ' checked="checked"' : '' ) . ' /> ' . esc_html( args['label_remember'] ) . '</label></p>' : '' ) . '
      <p class="login-submit">
        <input type="submit" name="wp-submit" id="' . esc_attr( args['id_submit'] ) . '" class="button button-primary" value="' . esc_attr( args['label_log_in'] ) . '" />
        <input type="hidden" name="redirect_to" value="' . esc_url( args['redirect'] ) . '" />
      </p>
      ' . login_form_bottom . '
    </form>'

  if args['echo']:
    echo form
  else:
    return form


def wp_lostpassword_url( redirect = '' ):
  ''' Returns the URL that allows the user to retrieve the lost password
  @param string redirect Path to redirect to on login.
  @return string Lost password URL.
  '''
  args = array( ('action', 'lostpassword') )
  if !Php.empty(locals(), 'redirect'):
    args['redirect_to'] = redirect

  lostpassword_url = add_query_arg( args, network_site_url('wp-login.php', 'login') )

  # Filters the Lost Password URL.
  # @param string lostpassword_url The lost password page URL.
  # @param string redirect         The path to redirect to on login.
  return apply_filters( 'lostpassword_url', lostpassword_url, redirect )


def wp_register( before = '<li>', after = '</li>', echo = true ):
  ''' Display the Registration or Admin link.
  Display a link which allows the user to navigate to the registration page if
  not logged in and registration is enabled or to the dashboard if logged in.
  @param string before Text to output before the link. Default `<li>`.
  @param string after  Text to output after the link. Default `</li>`.
  @param bool   echo   Default to echo and not return the link.
  @return string|void String when retrieving.
  '''
  if ! is_user_logged_in():
    if get_option('users_can_register'):
      link = before . '<a href="' . esc_url( wp_registration_url() ) . '">' . __('Register') . '</a>' . after
    else:
      link = ''
  elif current_user_can( 'read' ):
    link = before . '<a href="' . admin_url() . '">' . __('Site Admin') . '</a>' . after
  else:
    link = ''

  # Filters the HTML link to the Registration or Admin page.
  # Users are sent to the admin page if logged-in, or the registration page
  # if enabled and logged-out.
  # @param string link The HTML code for the link to the Registration or Admin page.
  link = apply_filters( 'register', link )

  if echo:
    echo link
  else:
    return link


def wp_meta():
  ''' Theme container function for the 'wp_meta' action.
  The {@see 'wp_meta'} action can have several purposes, depending on how you use it,
  but one purpose might have been to allow for theme switching.
  @link https://core.trac.wordpress.org/ticket/1458 Explanation of 'wp_meta' action.
  '''
  # Fires before displaying echoed content in the sidebar.
  do_action( 'wp_meta' )


def bloginfo( show = '' ):
  ''' Displays information about the current site.
  @see get_bloginfo() For possible `show` values
  @param string show Optional. Site information to display. Default empty.
  '''
  echo get_bloginfo( show, 'display' )


def get_bloginfo( show = '', filter = 'raw' ):
  ''' Retrieves information about the current site.
  Possible values for `show` include:
  - 'name' - Site title (set in Settings > General)
  - 'description' - Site tagline (set in Settings > General)
  - 'wpurl' - The WordPress address (URL) (set in Settings > General)
  - 'url' - The Site address (URL) (set in Settings > General)
  - 'admin_email' - Admin email (set in Settings > General)
  - 'charset' - The "Encoding for pages and feeds"  (set in Settings > Reading)
  - 'version' - The current WordPress version
  - 'html_type' - The content-type (default: "text/html"). Themes and plugins
    can override the default value using the {@see 'pre_option_html_type'} filter
  - 'text_direction' - The text direction determined by the site's language. is_rtl()
    should be used instead
  - 'language' - Language code for the current site
  - 'stylesheet_url' - URL to the stylesheet for the active theme. An active child theme
    will take precedence over this value
  - 'stylesheet_directory' - Directory path for the active theme.  An active child theme
    will take precedence over this value
  - 'template_url' / 'template_directory' - URL of the active theme's directory. An active
    child theme will NOT take precedence over this value
  - 'pingback_url' - The pingback XML-RPC file URL (xmlrpc.php)
  - 'atom_url' - The Atom feed URL (/feed/atom)
  - 'rdf_url' - The RDF/RSS 1.0 feed URL (/feed/rfd)
  - 'rss_url' - The RSS 0.92 feed URL (/feed/rss)
  - 'rss2_url' - The RSS 2.0 feed URL (/feed)
  - 'comments_atom_url' - The comments Atom feed URL (/comments/feed)
  - 'comments_rss2_url' - The comments RSS 2.0 feed URL (/comments/feed)
  Some `show` values are deprecated and will be removed in future versions.
  These options will trigger the _deprecated_argument() function.
  Deprecated arguments include:
  - 'siteurl' - Use 'url' instead
  - 'home' - Use 'url' instead
  @global string wp_version
  @param string show   Optional. Site info to retrieve. Default empty (site name).
  @param string filter Optional. How to filter what is retrieved. Default 'raw'.
  @return string Mostly string values, might be empty.
  '''
  #switch( show ) {
  if   show in ('home', 'siteurl'): # both DEPRECATED
    _deprecated_argument( __FUNCTION__, '2.2.0', sprintf(
      # translators: 1: 'siteurl'/'home' argument, 2: bloginfo() function name, 3: 'url' argument
      __( 'The %1$s option is deprecated for the family of %2$s functions. Use the %3$s option instead.' ),
      '<code>' . show . '</code>',
      '<code>bloginfo()</code>',
      '<code>url</code>'
    ) )
  elif show == 'url' :
    output = home_url()
  elif show == 'wpurl' :
    output = site_url()
  elif show == 'description':
    output = get_option('blogdescription')
  elif show == 'rdf_url':
    output = get_feed_link('rdf')
  elif show == 'rss_url':
    output = get_feed_link('rss')
  elif show == 'rss2_url':
    output = get_feed_link('rss2')
  elif show == 'atom_url':
    output = get_feed_link('atom')
  elif show == 'comments_atom_url':
    output = get_feed_link('comments_atom')
  elif show == 'comments_rss2_url':
    output = get_feed_link('comments_rss2')
  elif show == 'pingback_url':
    output = site_url( 'xmlrpc.php' )
  elif show == 'stylesheet_url':
    output = get_stylesheet_uri()
  elif show == 'stylesheet_directory':
    output = get_stylesheet_directory_uri()
  elif show in ('template_directory', 'template_url':
    output = get_template_directory_uri()
  elif show == 'admin_email':
    output = get_option('admin_email')
  elif show == 'charset':
    output = get_option('blog_charset')
    if '' == output:
      output = 'UTF-8'
  elif show == 'html_type' :
    output = get_option('html_type')
  elif show == 'version':
    global wp_version
    output = wp_version
  elif show == 'language':
    # translators: Translate this to the correct language tag for your locale,
    # see https://www.w3.org/International/articles/language-tags/ for reference.
    # Do not translate into your own language.
    output = __( 'html_lang_attribute' )
    if 'html_lang_attribute' === output || preg_match( '/[^a-zA-Z0-9-]/', output ):
      output = get_locale()
      output = str_replace( '_', '-', output )
  elif show == 'text_direction':
    _deprecated_argument( __FUNCTION__, '2.2.0', sprintf(
      # translators: 1: 'text_direction' argument, 2: bloginfo() function name, 3: is_rtl() function name
      __( 'The %1$s option is deprecated for the family of %2$s functions. Use the %3$s function instead.' ),
      '<code>' . show . '</code>',
      '<code>bloginfo()</code>',
      '<code>is_rtl()</code>'
    ) )
    if function_exists( 'is_rtl' ):
      output = is_rtl() ? 'rtl' : 'ltr'
    else:
      output = 'ltr'
  #if show == 'name':
  else:
    output = get_option('blogname')

  url = true
  if (strpos(show, 'url') === False &&
    strpos(show, 'directory') === False &&
    strpos(show, 'home') === False):
    url = False

  if 'display' == filter:
    if url:
      # Filters the URL returned by get_bloginfo().
      # @param mixed output The URL returned by bloginfo().
      # @param mixed show   Type of information requested.
      output = apply_filters( 'bloginfo_url', output, show )
    else:
      # Filters the site information returned by get_bloginfo().
      # @param mixed output The requested non-URL site information.
      # @param mixed show   Type of information requested.
      output = apply_filters( 'bloginfo', output, show )

  return output


def get_site_icon_url( size = 512, url = '', blog_id = 0 ):
  ''' Returns the Site Icon URL.
  @param int    size    Optional. Size of the site icon. Default 512 (pixels).
  @param string url     Optional. Fallback url if no site icon is found. Default empty.
  @param int    blog_id Optional. ID of the blog to get the site icon for. Default current blog.
  @return string Site Icon URL.
  '''
  switched_blog = False
  if is_multisite() and Php.empty(locals(), 'blog_id') and int(blog_id) != WpC.WB.Wj.get_current_blog_id():
    switch_to_blog( blog_id )
    switched_blog = True

  site_icon_id = get_option( 'site_icon' )

  if site_icon_id:
    if size >= 512:
      size_data = 'full'
    else:
      size_data = array( size, size )
    url = wp_get_attachment_image_url( site_icon_id, size_data )

  if switched_blog:
    restore_current_blog()

  # Filters the site icon URL.
  # @param string url     Site icon URL.
  # @param int    size    Size of the site icon.
  # @param int    blog_id ID of the blog to get the site icon for.
  return apply_filters( 'get_site_icon_url', url, size, blog_id )


def site_icon_url( size = 512, url = '', blog_id = 0 ):
  ''' Displays the Site Icon URL.
  @param int    size    Optional. Size of the site icon. Default 512 (pixels).
  @param string url     Optional. Fallback url if no site icon is found. Default empty.
  @param int    blog_id Optional. ID of the blog to get the site icon for. Default current blog.
  '''
  echo esc_url( get_site_icon_url( size, url, blog_id ) )


def has_site_icon( blog_id = 0 ):
  ''' Whether the site has a Site Icon.
  @param int blog_id Optional. ID of the blog in question. Default current blog.
  @return bool Whether the site has a site icon or not.
  '''
  return (bool) get_site_icon_url( 512, '', blog_id )


def has_custom_logo( blog_id = 0 ):
  ''' Determines whether the site has a custom logo.
  @param int blog_id Optional. ID of the blog in question. Default is the ID of the current blog.
  @return bool Whether the site has a custom logo or not.
  '''
  switched_blog = False
  if is_multisite() and Php.empty(locals(), 'blog_id') and int(blog_id) != WpC.WB.Wj.get_current_blog_id():
    switch_to_blog( blog_id )
    switched_blog = True

  custom_logo_id = get_theme_mod( 'custom_logo' )

  if switched_blog:
    restore_current_blog()

  return (bool) custom_logo_id


def get_custom_logo( blog_id = 0 ):
  ''' Returns a custom logo, linked to home.
  @param int blog_id Optional. ID of the blog in question. Default is the ID of the current blog.
  @return string Custom logo markup.
  '''
  html = ''
  switched_blog = False

  if is_multisite() and Php.empty(locals(), 'blog_id') and int(blog_id) != WpC.WB.Wj.get_current_blog_id():
    switch_to_blog( blog_id )
    switched_blog = True

  custom_logo_id = get_theme_mod( 'custom_logo' )

  # We have a logo. Logo is go.
  if custom_logo_id:
    html = sprintf( '<a href="%1$s" class="custom-logo-link" rel="home" itemprop="url">%2$s</a>',
      esc_url( home_url( '/' ) ),
      wp_get_attachment_image( custom_logo_id, 'full', False, array(
        ('class'   , 'custom-logo'),
        ('itemprop', 'logo'),
      ) )
    )

  # If no logo is set but we're in the Customizer, leave a placeholder (needed for the live preview).
  elif is_customize_preview():
    html = sprintf( '<a href="%1$s" class="custom-logo-link" style="display:none;"><img class="custom-logo"/></a>',
      esc_url( home_url( '/' ) )
    )

  if switched_blog:
    restore_current_blog()

  # Filters the custom logo output.
  # @since 4.6.0 Added the `blog_id` parameter.
  # @param string html    Custom logo HTML output.
  # @param int    blog_id ID of the blog to get the custom logo for.
  return apply_filters( 'get_custom_logo', html, blog_id )


def the_custom_logo( blog_id = 0 ):
  ''' Displays a custom logo, linked to home.
  @param int blog_id Optional. ID of the blog in question. Default is the ID of the current blog.
  '''
  echo get_custom_logo( blog_id )


def wp_get_document_title():
  ''' Returns document title for the current page.
  @global int page  Page number of a single post.
  @global int paged Page number of a list of posts.
  @return string Tag with the document title.
  '''

  # Filters the document title before it is generated.
  # Passing a non-empty value will short-circuit wp_get_document_title(),
  # returning that value instead.
  # @param string title The document title. Default empty string.
  title = apply_filters( 'pre_get_document_title', '' )
  if ! Php.empty(locals(), 'title' ):
    return title

  global page, paged

  title = array(
    ('title', ''),
  )

  # If it's a 404 page, use a "Page not found" title.
  if is_404():
    title['title'] = __( 'Page not found' )

  # If it's a search, use a dynamic search results title.
  elif is_search():
    # translators: %s: search phrase
    title['title'] = sprintf( __( 'Search Results for &#8220;%s&#8221;' ), get_search_query() )

  # If on the front page, use the site title.
  elif is_front_page():
    title['title'] = get_bloginfo( 'name', 'display' )

  # If on a post type archive, use the post type archive title.
  elif is_post_type_archive():
    title['title'] = post_type_archive_title( '', False )

  # If on a taxonomy archive, use the term title.
  elif is_tax():
    title['title'] = single_term_title( '', False )

  # If we're on the blog page that is not the homepage or
  # a single post of any post type, use the post title.
  elif is_home() || is_singular():
    title['title'] = single_post_title( '', False )

  # If on a category or tag archive, use the term title.
  elif is_category() || is_tag():
    title['title'] = single_term_title( '', False )

  # If on an author archive, use the author's display name.
  elif is_author() && author = get_queried_object():
    title['title'] = author.display_name

  # If it's a date archive, use the date as the title.
  elif is_year():
    title['title'] = get_the_date( _x( 'Y', 'yearly archives date format' ) )

  elif is_month():
    title['title'] = get_the_date( _x( 'F Y', 'monthly archives date format' ) )

  elif is_day():
    title['title'] = get_the_date()

  # Add a page number if necessary.
  if ( paged >= 2 || page >= 2 ) && ! is_404():
    title['page'] = sprintf( __( 'Page %s' ), max( paged, page ) )

  # Append the description or site title to give context.
  if is_front_page():
    title['tagline'] = get_bloginfo( 'description', 'display' )
  else:
    title['site'] = get_bloginfo( 'name', 'display' )

  # Filters the separator for the document title.
  # @param string sep Document title separator. Default '-'.
  sep = apply_filters( 'document_title_separator', '-' )

  # Filters the parts of the document title.
  # @param array title {
  #     The document title parts.
  #     @type string title   Title of the viewed page.
  #     @type string page    Optional. Page number if paginated.
  #     @type string tagline Optional. Site description when on home page.
  #     @type string site    Optional. Site title when not on home page.
  # }
  title = apply_filters( 'document_title_parts', title )

  title = implode( " "+ sep +" ", array_filter( title ) )
  title = wptexturize( title )
  title = convert_chars( title )
  title = esc_html( title )
  title = capital_P_dangit( title )

  return title


def _wp_render_title_tag():
  ''' Displays title tag with content.
  @ignore
  @since 4.4.0 Improved title output replaced `wp_title()`.
  @access private
  '''
  if ! current_theme_supports( 'title-tag' ):
    return

  echo '<title>' . wp_get_document_title() . '</title>' . "\n"


def wp_title( sep = '&raquo;', display = true, seplocation = '' ):
  ''' Display or retrieve page title for all areas of blog.
  By default, the page title will display the separator before the page title,
  so that the blog title will be before the page title. This is not good for
  title display, since the blog title shows up on most tabs and not what is
  important, which is the page that the user is looking at.
  There are also SEO benefits to having the blog title after or to the 'right'
  of the page title. However, it is mostly common sense to have the blog title
  to the right with most browsers supporting tabs. You can achieve this by
  using the seplocation parameter and setting the value to 'right'. This change
  was introduced around 2.5.0, in case backward compatibility of themes is
  important.
  @global WP_Locale wp_locale
  @param string sep         Optional, default is '&raquo;'. How to separate the various items
                             within the page title.
  @param bool   display     Optional, default is true. Whether to display or retrieve title.
  @param string seplocation Optional. Direction to display title, 'right'.
  @return string|None String on retrieve, None when displaying.
  '''
  global wp_locale

  m        = get_query_var( 'm' )
  year     = get_query_var( 'year' )
  monthnum = get_query_var( 'monthnum' )
  day      = get_query_var( 'day' )
  search   = get_query_var( 's' )
  title    = ''

  t_sep = '%WP_TITLE_SEP%'; # Temporary separator, for accurate flipping, if necessary

  # If there is a post
  if is_single() || ( is_home() && ! is_front_page() ) || ( is_page() && ! is_front_page() ):
    title = single_post_title( '', False )

  # If there's a post type archive
  if is_post_type_archive():
    post_type = get_query_var( 'post_type' )
    if is_array( post_type ):
      post_type = reset( post_type )
    post_type_object = get_post_type_object( post_type )
    if ! post_type_object.has_archive:
      title = post_type_archive_title( '', False )

  # If there's a category or tag
  if is_category() || is_tag():
    title = single_term_title( '', False )

  # If there's a taxonomy
  if is_tax():
    term = get_queried_object()
    if term:
      tax   = get_taxonomy( term.taxonomy )
      title = single_term_title( tax.labels.name . t_sep, False )

  # If there's an author
  if is_author() && ! is_post_type_archive():
    author = get_queried_object()
    if author:
      title = author.display_name

  # Post type archives with has_archive should override terms.
  if is_post_type_archive() && post_type_object.has_archive:
    title = post_type_archive_title( '', False )

  # If there's a month
  if is_archive() && ! Php.empty(locals(), 'm' ):
    my_year  = substr( m, 0, 4 )
    my_month = wp_locale.get_month( substr( m, 4, 2 ) )
    my_day   = intval( substr( m, 6, 2 ) )
    title    = my_year . ( my_month ? t_sep . my_month : '' ) . ( my_day ? t_sep . my_day : '' )

  # If there's a year
  if is_archive() && ! Php.empty(locals(), 'year' ):
    title = year
    if ! Php.empty(locals(), 'monthnum' ):
      title .= t_sep . wp_locale.get_month( monthnum )
    if ! Php.empty(locals(), 'day' ):
      title .= t_sep . zeroise( day, 2 )

  # If it's a search
  if is_search():
    # translators: 1: separator, 2: search phrase
    title = sprintf( __( 'Search Results %1$s %2$s' ), t_sep, strip_tags( search ) )

  # If it's a 404 page
  if is_404():
    title = __( 'Page not found' )

  prefix = ''
  if ! Php.empty(locals(), 'title' ):
    prefix = " sep "

  # Filters the parts of the page title.
  # @param array title_array Parts of the page title.
  title_array = apply_filters( 'wp_title_parts', explode( t_sep, title ) )

  # Determines position of the separator and direction of the breadcrumb
  if 'right' == seplocation:   # sep on right, so reverse the order
    title_array = array_reverse( title_array )
    title       = implode( " "+ sep +" ", title_array ) . prefix
  else:
    title = prefix . implode( " "+ sep +" ", title_array )

  # Filters the text of the page title.
  # @param string title Page title.
  # @param string sep Title separator.
  # @param string seplocation Location of the separator (left or right).
  title = apply_filters( 'wp_title', title, sep, seplocation )

  # Send it out
  if display:
    echo title
  else:
    return title


def single_post_title( prefix = '', display = true ):
  ''' Display or retrieve page title for post.
  This is optimized for single.php template file for displaying the post title.
  It does not support placing the separator after the title, but by leaving the
  prefix parameter empty, you can set the title separator manually. The prefix
  does not automatically place a space between the prefix, so if there should
  be a space, the parameter value will need to have it at the end.
  @param string prefix  Optional. What to display before the title.
  @param bool   display Optional, default is true. Whether to display or retrieve title.
  @return string|void Title when retrieving.
  '''
  _post = get_queried_object()

  if !Php.isset(_post, 'post_title'):
    return

  # Filters the page title for a single post.
  # @param string _post_title The single post page title.
  # @param object _post       The current queried object as returned by get_queried_object().
  title = apply_filters( 'single_post_title', _post.post_title, _post )
  if display:
    echo prefix . title
  else:
    return prefix . title


def post_type_archive_title( prefix = '', display = true ):
  ''' Display or retrieve title for a post type archive.
  This is optimized for archive.php and archive-{post_type}.php template files
  for displaying the title of the post type.
  @param string prefix  Optional. What to display before the title.
  @param bool   display Optional, default is true. Whether to display or retrieve title.
  @return string|void Title when retrieving, None when displaying or failure.
  '''
  if ! is_post_type_archive():
    return

  post_type = get_query_var( 'post_type' )
  if is_array( post_type ):
    post_type = reset( post_type )

  post_type_obj = get_post_type_object( post_type )

  # Filters the post type archive title.
  # @param string post_type_name Post type 'name' label.
  # @param string post_type      Post type.
  title = apply_filters( 'post_type_archive_title', post_type_obj.labels.name, post_type )

  if display:
    echo prefix . title
  else:
    return prefix . title


def single_cat_title( prefix = '', display = true ):
  ''' Display or retrieve page title for category archive.
  Useful for category template files for displaying the category page title.
  The prefix does not automatically place a space between the prefix, so if
  there should be a space, the parameter value will need to have it at the end.
  @param string prefix  Optional. What to display before the title.
  @param bool   display Optional, default is true. Whether to display or retrieve title.
  @return string|void Title when retrieving.
  '''
  return single_term_title( prefix, display )


def single_tag_title( prefix = '', display = true ):
  ''' Display or retrieve page title for tag post archive.
  Useful for tag template files for displaying the tag page title. The prefix
  does not automatically place a space between the prefix, so if there should
  be a space, the parameter value will need to have it at the end.
  @param string prefix  Optional. What to display before the title.
  @param bool   display Optional, default is true. Whether to display or retrieve title.
  @return string|void Title when retrieving.
  '''
  return single_term_title( prefix, display )


def single_term_title( prefix = '', display = true ):
  ''' Display or retrieve page title for taxonomy term archive.
  Useful for taxonomy term template files for displaying the taxonomy term page title.
  The prefix does not automatically place a space between the prefix, so if there should
  be a space, the parameter value will need to have it at the end.
  @param string prefix  Optional. What to display before the title.
  @param bool   display Optional, default is true. Whether to display or retrieve title.
  @return string|void Title when retrieving.
  '''
  term = get_queried_object()

  if !term:
    return

  if is_category():
    # Filters the category archive page title.
    # @param string term_name Category name for archive being displayed.
    term_name = apply_filters( 'single_cat_title', term.name )
  elif is_tag():
    # Filters the tag archive page title.
    # @param string term_name Tag name for archive being displayed.
    term_name = apply_filters( 'single_tag_title', term.name )
  elif is_tax():
    # Filters the custom taxonomy archive page title.
    # @param string term_name Term name for archive being displayed.
    term_name = apply_filters( 'single_term_title', term.name )
  else:
    return

  if Php.empty(locals(), 'term_name' ):
    return

  if display:
    echo prefix . term_name
  else:
    return prefix . term_name


def single_month_title(prefix = '', display = true ):
  ''' Display or retrieve page title for post archive based on date.
  Useful for when the template only needs to display the month and year,
  if either are available. The prefix does not automatically place a space
  between the prefix, so if there should be a space, the parameter value
  will need to have it at the end.
  @global WP_Locale wp_locale
  @param string prefix  Optional. What to display before the title.
  @param bool   display Optional, default is true. Whether to display or retrieve title.
  @return string|void Title when retrieving.
  '''
  global wp_locale

  m = get_query_var('m')
  year = get_query_var('year')
  monthnum = get_query_var('monthnum')

  if not Php.empty(locals(), 'monthnum') && not Php.empty(locals(), 'year'):
    my_year = year
    my_month = wp_locale.get_month(monthnum)
  elif not Php.empty(locals(), 'm'):
    my_year = substr(m, 0, 4)
    my_month = wp_locale.get_month(substr(m, 4, 2))

  if Php.empty(locals(), 'my_month'):
    return False

  result = prefix . my_month . prefix . my_year

  if not display:
    return result
  echo result


def the_archive_title( before = '', after = '' ):
  ''' Display the archive title based on the queried object.
  @see get_the_archive_title()
  @param string before Optional. Content to prepend to the title. Default empty.
  @param string after  Optional. Content to append to the title. Default empty.
  '''
  title = get_the_archive_title()

  if ! Php.empty(locals(), 'title' ):
    echo before . title . after


def get_the_archive_title():
  ''' Retrieve the archive title based on the queried object.
  @return string Archive title.
  '''
  if is_category():
    # translators: Category archive title. 1: Category name */
    title = sprintf( __( 'Category: %s' ), single_cat_title( '', False ) )
  elif is_tag():
    # translators: Tag archive title. 1: Tag name */
    title = sprintf( __( 'Tag: %s' ), single_tag_title( '', False ) )
  elif is_author():
    # translators: Author archive title. 1: Author name */
    title = sprintf( __( 'Author: %s' ), '<span class="vcard">' . get_the_author() . '</span>' )
  elif is_year():
    # translators: Yearly archive title. 1: Year */
    title = sprintf( __( 'Year: %s' ), get_the_date( _x( 'Y', 'yearly archives date format' ) ) )
  elif is_month():
    # translators: Monthly archive title. 1: Month name and year */
    title = sprintf( __( 'Month: %s' ), get_the_date( _x( 'F Y', 'monthly archives date format' ) ) )
  elif is_day():
    # translators: Daily archive title. 1: Date */
    title = sprintf( __( 'Day: %s' ), get_the_date( _x( 'F j, Y', 'daily archives date format' ) ) )
  elif is_tax( 'post_format' ):
    if is_tax( 'post_format', 'post-format-aside' ):
      title = _x( 'Asides', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-gallery' ):
      title = _x( 'Galleries', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-image' ):
      title = _x( 'Images', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-video' ):
      title = _x( 'Videos', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-quote' ):
      title = _x( 'Quotes', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-link' ):
      title = _x( 'Links', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-status' ):
      title = _x( 'Statuses', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-audio' ):
      title = _x( 'Audio', 'post format archive title' )
    elif is_tax( 'post_format', 'post-format-chat' ):
      title = _x( 'Chats', 'post format archive title' )
  elif is_post_type_archive():
    # translators: Post type archive title. 1: Post type name */
    title = sprintf( __( 'Archives: %s' ), post_type_archive_title( '', False ) )
  elif is_tax():
    tax = get_taxonomy( get_queried_object().taxonomy )
    # translators: Taxonomy term archive title. 1: Taxonomy singular name, 2: Current taxonomy term */
    title = sprintf( __( '%1$s: %2$s' ), tax.labels.singular_name, single_term_title( '', False ) )
  else:
    title = __( 'Archives' )

  # Filters the archive title.
  # @param string title Archive title to be displayed.
  return apply_filters( 'get_the_archive_title', title )


def the_archive_description( before = '', after = '' ):
  ''' Display category, tag, term, or author description.
  @see get_the_archive_description()
  @param string before Optional. Content to prepend to the description. Default empty.
  @param string after  Optional. Content to append to the description. Default empty.
  '''
  description = get_the_archive_description()
  if description:
    echo before . description . after


def get_the_archive_description():
  ''' Retrieve category, tag, term, or author description.
  @since 4.7.0 Added support for author archives.
  @see term_description()
  @return string Archive description.
  '''
  if is_author():
    description = get_the_author_meta( 'description' )
  else:
    description = term_description()
  # Filters the archive description.
  # @param string description Archive description to be displayed.
  return apply_filters( 'get_the_archive_description', description )


def get_archives_link(url, text, Format = 'html', before = '', after = ''):
  ''' Retrieve archive link content based on predefined or custom code.
  The format can be one of four styles. The 'link' for head element, 'option'
  for use in the select element, 'html' for use in list (either ol or ul HTML
  elements). Custom content is also supported using the before and after
  parameters.
  The 'link' format uses the `<link>` HTML element with the **archives**
  relationship. The before and after parameters are not used. The text
  parameter is used to describe the link.
  The 'option' format uses the option HTML element for use in select element.
  The value is the url parameter and the before and after parameters are used
  between the text description.
  The 'html' format, which is the default, uses the li HTML element for use in
  the list HTML elements. The before parameter is before the link and the after
  parameter is after the closing link.
  The custom format uses the before parameter before the link ('a' HTML
  element) and the after parameter after the closing link tag. If the above
  three values for the format are not used, then custom format is assumed.
  @param string url    URL to archive.
  @param string text   Archive text description.
  @param string Format Optional, default is 'html'. Can be 'link', 'option', 'html', or custom.
  @param string before Optional. Content to prepend to the description. Default empty.
  @param string after  Optional. Content to append to the description. Default empty.
  @return string HTML link content for archive.
  '''
  text = wptexturize(text)
  url = esc_url(url)

  if 'link' == Format:
    link_html = "\t<link rel='archives' title='" . esc_attr( text ) . "' href='url' />\n"
  elif 'option' == Format:
    link_html = "\t<option value='{}'>{} {} {}</option>\n".format(url, before, text, after)
  elif 'html' == Format:
    link_html = "\t<li>{}<a href='{}'>{}</a>{}</li>\n".format(before, url, text, after)
  else: # custom
    link_html = "\t{}<a href='{}'>{}</a>{}\n".format(before, url, text, after)

  # Filters the archive link content.
  # @since 4.5.0 Added the `url`, `text`, `Format`, `before`, and `after` parameters.
  # @param string link_html The archive HTML link content.
  # @param string url       URL to archive.
  # @param string text      Archive text description.
  # @param string Format    Link format. Can be 'link', 'option', 'html', or custom.
  # @param string before    Content to prepend to the description.
  # @param string after     Content to append to the description.
  return apply_filters( 'get_archives_link', link_html, url, text, Format, before, after )


def wp_get_archives( args = '' ):
  ''' Display archive links based on type and format.
  @since 4.4.0 post_type arg was added.
  @see get_archives_link()
  @global wpdb      wpdb
  @global WP_Locale wp_locale
  @param string|array args {
      Default archive links arguments. Optional.
      @type string     Type            Type of archive to retrieve. Accepts 'daily', 'weekly', 'monthly',
                                        'yearly', 'postbypost', or 'alpha'. Both 'postbypost' and 'alpha'
                                        display the same archive link list as well as post titles instead
                                        of displaying dates. The difference between the two is that 'alpha'
                                        will order by post title and 'postbypost' will order by post date.
                                        Default 'monthly'.
      @type string|int limit           Number of links to limit the query to. Default empty (no limit).
      @type string     Format          Format each link should take using the before and after args.
                                        Accepts 'link' (`<link>` tag), 'option' (`<option>` tag), 'html'
                                        (`<li>` tag), or a custom format, which generates a link anchor
                                        with before preceding and after succeeding. Default 'html'.
      @type string     before          Markup to prepend to the beginning of each link. Default empty.
      @type string     after           Markup to append to the end of each link. Default empty.
      @type bool       show_post_count Whether to display the post count alongside the link. Default False.
      @type bool|int   echo            Whether to echo or return the links list. Default 1|true to echo.
      @type string     order           Whether to use ascending or descending order. Accepts 'ASC', or 'DESC'.
                                        Default 'DESC'.
      @type string     post_type       Post type. Default 'post'.
  }
  @return string|void String when retrieving.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  global wp_locale

  defaults = array(
    ('type'     , 'monthly'), ('limit'          , ''     ),
    ('format'   , 'html'   ), ('before'         , ''     ),
    ('after'    , ''       ), ('show_post_count', False  ),
    ('echo'     , 1        ), ('order'          , 'DESC' ),
    ('post_type', 'post'   ),
  )

  r = wp_parse_args( args, defaults )

  post_type_object = get_post_type_object( r['post_type'] )
  if ! is_post_type_viewable( post_type_object ):
    return
  r['post_type'] = post_type_object.name

  if '' == r['type']:
    r['type'] = 'monthly'

  if ! Php.Php.empty( r, 'limit' ):
    r['limit'] = absint( r['limit'] )
    r['limit'] = ' LIMIT ' . r['limit']

  order = strtoupper( r['order'] )
  if order != 'ASC':
    order = 'DESC'

  # this is what will separate dates on weekly archive links
  archive_week_separator = '&#8211;'

  sql_where = wpdb.prepare( "WHERE post_type = %s AND post_status = 'publish'", r['post_type'] )

  # Filters the SQL WHERE clause for retrieving archives.
  # @param string sql_where Portion of SQL query containing the WHERE clause.
  # @param array  r         An array of default arguments.
  where = apply_filters( 'getarchives_where', sql_where, r )

  # Filters the SQL JOIN clause for retrieving archives.
  # @param string sql_join Portion of SQL query containing JOIN clause.
  # @param array  r        An array of default arguments.
  join = apply_filters( 'getarchives_join', '', r )

  output = ''

  last_changed = wp_cache_get_last_changed( 'posts' )
  if ! last_changed:
    last_changed = microtime()
    wp_cache_set( 'last_changed', last_changed, 'posts' )

  limit = r['limit']

  if 'monthly' == r['type']:
    query = "SELECT YEAR(post_date) AS `year`, MONTH(post_date) AS `month`, count(ID) as posts FROM {} {} {} GROUP BY YEAR(post_date), MONTH(post_date) ORDER BY post_date {} {}".format(wpdb.posts, join, where, order, limit)
    key = md5( query )
    key = "wp_get_archives:{}:{}".format(key, last_changed)
    if ! results = wp_cache_get( key, 'posts' ):
      results = wpdb.get_results( query )
      wp_cache_set( key, results, 'posts' )
    if results:
      after = r['after']
      for result in Php.Array( results ):
        url = get_month_link( result.year, result.month )
        if 'post' != r['post_type']:
          url = add_query_arg( 'post_type', r['post_type'], url )
        # translators: 1: month name, 2: 4-digit year
        text = sprintf( __( '%1$s %2$d' ), wp_locale.get_month( result.month ), result.year )
        if r['show_post_count']:
          r['after'] = '&nbsp;(' . result.posts . ')' . after
        output .= get_archives_link( url, text, r['format'], r['before'], r['after'] )
  elif 'yearly' == r['type']:
    query = "SELECT YEAR(post_date) AS `year`, count(ID) as posts FROM {} {} {} GROUP BY YEAR(post_date) ORDER BY post_date {} {}".format(wpdb.posts, join, where, order, limit)
    key = md5( query )
    key = "wp_get_archives:{}:{}".format(key, last_changed)
    if ! results = wp_cache_get( key, 'posts' ):
      results = wpdb.get_results( query )
      wp_cache_set( key, results, 'posts' )
    if results:
      after = r['after']
      for result in Php.Array( results ):
        url = get_year_link( result.year )
        if 'post' != r['post_type']:
          url = add_query_arg( 'post_type', r['post_type'], url )
        text = sprintf( '%d', result.year )
        if r['show_post_count']:
          r['after'] = '&nbsp;(' . result.posts . ')' . after
        output .= get_archives_link( url, text, r['format'], r['before'], r['after'] )

  elif 'daily' == r['type']:
    query = "SELECT YEAR(post_date) AS `year`, MONTH(post_date) AS `month`, DAYOFMONTH(post_date) AS `dayofmonth`, count(ID) as posts FROM {} {} {} GROUP BY YEAR(post_date), MONTH(post_date), DAYOFMONTH(post_date) ORDER BY post_date {} {}".format(wpdb.posts, join, where, order, limit)
    key = md5( query )
    key = "wp_get_archives:{}:{}".format(key, last_changed)
    if ! results = wp_cache_get( key, 'posts' ):
      results = wpdb.get_results( query )
      wp_cache_set( key, results, 'posts' )
    if results:
      after = r['after']
      for result in Php.Array( results ):
        url  = get_day_link( result.year, result.month, result.dayofmonth )
        if 'post' != r['post_type']:
          url = add_query_arg( 'post_type', r['post_type'], url )
        date = sprintf( '%1$d-%2$02d-%3$02d 00:00:00', result.year, result.month, result.dayofmonth )
        text = mysql2date( get_option( 'date_format' ), date )
        if r['show_post_count']:
          r['after'] = '&nbsp;(' . result.posts . ')' . after
        output .= get_archives_link( url, text, r['format'], r['before'], r['after'] )

  elif 'weekly' == r['type']:
    week = _wp_mysql_week( '`post_date`' )
    query = "SELECT DISTINCT {} AS `week`, YEAR( `post_date` ) AS `yr`, DATE_FORMAT( `post_date`, '%Y-%m-%d' ) AS `yyyymmdd`, count( `ID` ) AS `posts` FROM `{}` {} {} GROUP BY {}, YEAR( `post_date` ) ORDER BY `post_date` {} {}".format(week, wpdb.posts, join, where, week, order, limit)
    key = md5( query )
    key = "wp_get_archives:{}:{}".format(key, last_changed)
    if ! results = wp_cache_get( key, 'posts' ):
      results = wpdb.get_results( query )
      wp_cache_set( key, results, 'posts' )
    arc_w_last = ''
    if results:
      after = r['after']
      for result in Php.Array( results ):
        if result.week != arc_w_last:
          arc_year       = result.yr
          arc_w_last     = result.week
          arc_week       = get_weekstartend( result.yyyymmdd, get_option( 'start_of_week' ) )
          arc_week_start = date_i18n( get_option( 'date_format' ), arc_week['start'] )
          arc_week_end   = date_i18n( get_option( 'date_format' ), arc_week['end'] )
          url            = add_query_arg( array( ('m', arc_year),('w', result.week), ), home_url( '/' ) )
          if 'post' != r['post_type']:
            url = add_query_arg( 'post_type', r['post_type'], url )
          text           = arc_week_start . archive_week_separator . arc_week_end
          if r['show_post_count']:
            r['after'] = '&nbsp;(' . result.posts . ')' . after
          output .= get_archives_link( url, text, r['format'], r['before'], r['after'] )

  elif ( 'postbypost' == r['type'] ) || ('alpha' == r['type'] ):
    orderby = ( 'alpha' == r['type'] ) ? 'post_title ASC ' : 'post_date DESC, ID DESC '
    query = "SELECT * FROM {} {} {} ORDER BY {} {}".format(wpdb.posts, join, where, orderby, limit)
    key = md5( query )
    key = "wp_get_archives:{}:{}".format(key, last_changed)
    if ! results = wp_cache_get( key, 'posts' ):
      results = wpdb.get_results( query )
      wp_cache_set( key, results, 'posts' )
    if results:
      for result in Php.Array( results ):
        if result.post_date != '0000-00-00 00:00:00':
          url = get_permalink( result )
          if result.post_title:
            #* This filter is documented in wp-includes/post-template.php
            text = strip_tags( apply_filters( 'the_title', result.post_title, result.ID ) )
          else:
            text = result.ID
          output .= get_archives_link( url, text, r['format'], r['before'], r['after'] )

  if r['echo']:
    echo output
  else:
    return output


def calendar_week_mod(num):
  ''' Get number of days since the start of the week.
  @param int num Number of day.
  @return int Days since the start of the week.
  '''
  base = 7
  return (num - base*floor(num/base))


def get_calendar( initial = true, echo = true ):
  ''' Display calendar with days that have posts as links.
  The calendar is cached, which will be retrieved, if it exists. If there are
  no posts for the month, then it will not be displayed.
  @global wpdb      wpdb
  @global int       m
  @global int       monthnum
  @global int       year
  @global WP_Locale wp_locale
  @global array     posts
  @param bool initial Optional, default is true. Use initial calendar names.
  @param bool echo    Optional, default is true. Set to False for return.
  @return string|void String when retrieving.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  global m, monthnum, year, wp_locale, posts

  key = md5( m . monthnum . year )
  cache = wp_cache_get( 'get_calendar', 'calendar' )

  if cache && is_array( cache ) && Php.isset( cache, key ):
    #* This filter is documented in wp-includes/general-template.php
    output = apply_filters( 'get_calendar', cache[ key ] )

    if echo:
      echo output
      return

    return output

  if ! is_array( cache ):
    cache = array()

  # Quick check. If we have no posts at all, abort!
  if ! posts:
    gotsome = wpdb.get_var("SELECT 1 as test FROM {} WHERE post_type = 'post' AND post_status = 'publish' LIMIT 1".format(wpdb.posts))
    if ! gotsome:
      cache[ key ] = ''
      wp_cache_set( 'get_calendar', cache, 'calendar' )
      return

  if Php.isset( _GET, 'w' ):
    w = (int) _GET['w']
  # week_begins = 0 stands for Sunday
  week_begins = (int) get_option( 'start_of_week' )
  ts = current_time( 'timestamp' )

  # Let's figure out when we are
  if ! Php.empty(locals(), 'monthnum' ) && ! Php.empty(locals(), 'year' ):
    thismonth = zeroise( intval( monthnum ), 2 )
    thisyear = (int) year
  elif ! Php.empty(locals(), 'w' ):
    # We need to get the month from MySQL
    thisyear = (int) substr( m, 0, 4 )
    #it seems MySQL's weeks disagree with PHP's
    d = ( ( w - 1 ) * 7 ) + 6
    thismonth = wpdb.get_var("SELECT DATE_FORMAT((DATE_ADD('{}0101', INTERVAL {} DAY) ), '%m')".format(thisyear, d))
  elif ! Php.empty(locals(), 'm' ):
    thisyear = (int) substr( m, 0, 4 )
    if strlen( m ) < 6:
      thismonth = '01'
    else:
      thismonth = zeroise( (int) substr( m, 4, 2 ), 2 )
  else:
    thisyear = gmdate( 'Y', ts )
    thismonth = gmdate( 'm', ts )

  unixmonth = mktime( 0, 0 , 0, thismonth, 1, thisyear )
  last_day = date( 't', unixmonth )

  # Get the next and previous month and year with at least one post
  previous = wpdb.get_row("SELECT MONTH(post_date) AS month, YEAR(post_date) AS year
    FROM {}
    WHERE post_date < '{}-{}-01'
    AND post_type = 'post' AND post_status = 'publish'
      ORDER BY post_date DESC
      LIMIT 1".format(wpdb.posts, thisyear, thismonth))
  next = wpdb.get_row("SELECT MONTH(post_date) AS month, YEAR(post_date) AS year
    FROM {}
    WHERE post_date > '{}-{}-{} 23:59:59'
    AND post_type = 'post' AND post_status = 'publish'
      ORDER BY post_date ASC
      LIMIT 1".format(wpdb.posts, thisyear, thismonth, last_day))

  # translators: Calendar caption: 1: month name, 2: 4-digit year
  calendar_caption = _x('%1$s %2$s', 'calendar caption')
  calendar_output = '<table id="wp-calendar">
  <caption>' . sprintf(
    calendar_caption,
    wp_locale.get_month( thismonth ),
    date( 'Y', unixmonth )
  ) . '</caption>
  <thead>
  <tr>'

  myweek = array()

  for ( wdcount = 0; wdcount <= 6; wdcount++ ) {
    myweek[None] = wp_locale.get_weekday( ( wdcount + week_begins ) % 7 )

  for wd in myweek:
    day_name = initial ? wp_locale.get_weekday_initial( wd ) : wp_locale.get_weekday_abbrev( wd )
    wd = esc_attr( wd )
    calendar_output .= "\n\t\t<th scope=\"col\" title=\"{}\">{}</th>".format(wd, day_name)

  calendar_output .= '
  </tr>
  </thead>

  <tfoot>
  <tr>'

  if previous:
    calendar_output .= "\n\t\t".'<td colspan="3" id="prev"><a href="' . get_month_link( previous.year, previous.month ) . '">&laquo; ' .
      wp_locale.get_month_abbrev( wp_locale.get_month( previous.month ) ) .
    '</a></td>'
  else:
    calendar_output .= "\n\t\t".'<td colspan="3" id="prev" class="pad">&nbsp;</td>'

  calendar_output .= "\n\t\t".'<td class="pad">&nbsp;</td>'

  if next:
    calendar_output .= "\n\t\t".'<td colspan="3" id="next"><a href="' . get_month_link( next.year, next.month ) . '">' .
      wp_locale.get_month_abbrev( wp_locale.get_month( next.month ) ) .
    ' &raquo;</a></td>'
  else:
    calendar_output .= "\n\t\t".'<td colspan="3" id="next" class="pad">&nbsp;</td>'

  calendar_output .= '
  </tr>
  </tfoot>

  <tbody>
  <tr>'

  daywithpost = array()

  # Get days with posts
  dayswithposts = wpdb.get_results("SELECT DISTINCT DAYOFMONTH(post_date)
    FROM {} WHERE post_date >= '{}-{}-01 00:00:00'
    AND post_type = 'post' AND post_status = 'publish'
    AND post_date <= '{}-{}-{} 23:59:59'".format(wpdb.posts, thisyear, thismonth, thisyear, thismonth, last_day), ARRAY_N)
  if dayswithposts:
    for daywith in Php.Array( dayswithposts ):
      daywithpost[None] = daywith[0]

  # See how much we should pad in the beginning
  pad = calendar_week_mod( date( 'w', unixmonth ) - week_begins )
  if 0 != pad:
    calendar_output .= "\n\t\t".'<td colspan="'. esc_attr( pad ) .'" class="pad">&nbsp;</td>'

  newrow = False
  daysinmonth = (int) date( 't', unixmonth )

  for ( day = 1; day <= daysinmonth; ++day ) {
    if Php.Php.isset(locals(), 'newrow') && newrow:
      calendar_output .= "\n\t</tr>\n\t<tr>\n\t\t"
    newrow = False

    if ( day == gmdate( 'j', ts ) &&
      thismonth == gmdate( 'm', ts ) &&
      thisyear == gmdate( 'Y', ts ) ):
      calendar_output .= '<td id="today">'
    else:
      calendar_output .= '<td>'

    if in_array( day, daywithpost ):
      # any posts today?
      date_format = date( _x( 'F j, Y', 'daily archives date format' ), strtotime( "{}-{}-{}".format(thisyear, thismonth, day) ) )
      # translators: Post calendar label. 1: Date
      label = sprintf( __( 'Posts published on %s' ), date_format )
      calendar_output .= sprintf(
        '<a href="%s" aria-label="%s">%s</a>',
        get_day_link( thisyear, thismonth, day ),
        esc_attr( label ),
        day
      )
    else:
      calendar_output .= day
    calendar_output .= '</td>'

    if 6 == calendar_week_mod( date( 'w', mktime(0, 0 , 0, thismonth, day, thisyear ) ) - week_begins ):
      newrow = true

  pad = 7 - calendar_week_mod( date( 'w', mktime( 0, 0 , 0, thismonth, day, thisyear ) ) - week_begins )
  if pad != 0 && pad != 7:
    calendar_output .= "\n\t\t".'<td class="pad" colspan="'. esc_attr( pad ) .'">&nbsp;</td>'

  calendar_output .= "\n\t</tr>\n\t</tbody>\n\t</table>"

  cache[ key ] = calendar_output
  wp_cache_set( 'get_calendar', cache, 'calendar' )

  if echo:
    # Filters the HTML calendar output.
    # @param string calendar_output HTML output of the calendar.
    echo apply_filters( 'get_calendar', calendar_output )
    return

  #* This filter is documented in wp-includes/general-template.php
  return apply_filters( 'get_calendar', calendar_output )


def delete_get_calendar_cache():
  ''' Purge the cached results of get_calendar.
  @see get_calendar
  '''
  wp_cache_delete( 'get_calendar', 'calendar' )


def allowed_tags():
  ''' Display all of the allowed tags in HTML format with attributes.
  This is useful for displaying in the comment area, which elements and
  attributes are supported. As well as any plugins which want to display it.
  @global array allowedtags
  @return string HTML allowed tags entity encoded.
  '''
  global allowedtags
  allowed = ''
  for tag, attributes in Php.Array(allowedtags).items():
    allowed .= '<'.tag
    if 0 < count(attributes):
      for attribute, limits in attributes.items():
        allowed .= ' '.attribute.'=""'
    allowed .= '> '

  return htmlentities( allowed )


#**** Date/Time tags *****

def the_date_xml():
  ''' Outputs the date in iso8601 format for xml files.
  '''
  echo mysql2date( 'Y-m-d', get_post().post_date, False )


def the_date( d = '', before = '', after = '', echo = true ):
  ''' Display or Retrieve the date the current post was written (once per date)
  Will only output the date if the current post's date is different from the
  previous one output.
  i.e. Only one date listing will show per day worth of posts shown in the loop, even if the
  function is called several times for each post.
  HTML output can be filtered with 'the_date'.
  Date string output can be filtered with 'get_the_date'.
  @global string|int|bool currentday
  @global string|int|bool previousday
  @param string d      Optional. PHP date format defaults to the date_format option if not specified.
  @param string before Optional. Output before the date.
  @param string after  Optional. Output after the date.
  @param bool   echo   Optional, default is display. Whether to echo the date or return it.
  @return string|void String if retrieving.
  '''
  global currentday, previousday

  if is_new_day():
    the_date = before . get_the_date( d ) . after
    previousday = currentday

    # Filters the date a post was published for display.
    # @param string the_date The formatted date string.
    # @param string d        PHP date format. Defaults to 'date_format' option
    #                         if not specified.
    # @param string before   HTML output before the date.
    # @param string after    HTML output after the date.
    the_date = apply_filters( 'the_date', the_date, d, before, after )

    if echo:
      echo the_date
    else:
      return the_date


def get_the_date( d = '', post = None ):
  ''' Retrieve the date on which the post was written.
  Unlike the_date() this function will always return the date.
  Modify output with the {@see 'get_the_date'} filter.
  @param  string      d    Optional. PHP date format defaults to the date_format option if not specified.
  @param  int|WP_Post post Optional. Post ID or WP_Post object. Default current post.
  @return False|string Date the current post was written. False on failure.
  '''
  post = get_post( post )

  if ! post:
    return False

  if '' == d:
    the_date = mysql2date( get_option( 'date_format' ), post.post_date )
  else:
    the_date = mysql2date( d, post.post_date )

  # Filters the date a post was published.
  # @param string      the_date The formatted date.
  # @param string      d        PHP date format. Defaults to 'date_format' option
  #                              if not specified.
  # @param int|WP_Post post     The post object or ID.
  return apply_filters( 'get_the_date', the_date, d, post )


def the_modified_date( d = '', before = '', after = '', echo = true ):
  ''' Display the date on which the post was last modified.
  @param string d      Optional. PHP date format defaults to the date_format option if not specified.
  @param string before Optional. Output before the date.
  @param string after  Optional. Output after the date.
  @param bool   echo   Optional, default is display. Whether to echo the date or return it.
  @return string|void String if retrieving.
  '''
  the_modified_date = before . get_the_modified_date(d) . after

  # Filters the date a post was last modified for display.
  # @param string the_modified_date The last modified date.
  # @param string d                 PHP date format. Defaults to 'date_format' option
  #                                  if not specified.
  # @param string before            HTML output before the date.
  # @param string after             HTML output after the date.
  the_modified_date = apply_filters( 'the_modified_date', the_modified_date, d, before, after )

  if echo:
    echo the_modified_date
  else:
    return the_modified_date



def get_the_modified_date( d = '', post = None ):
  ''' Retrieve the date on which the post was last modified.
  @since 4.6.0 Added the `post` parameter.
  @param string      d    Optional. PHP date format defaults to the date_format option if not specified.
  @param int|WP_Post post Optional. Post ID or WP_Post object. Default current post.
  @return False|string Date the current post was modified. False on failure.
  '''
  post = get_post( post )

  if ! post:
    # For backward compatibility, failures go through the filter below.
    the_time = False
  elif Php.empty(locals(), 'd' ):
    the_time = get_post_modified_time( get_option( 'date_format' ), False, post, true )
  else:
    the_time = get_post_modified_time( d, False, post, true )

  # Filters the date a post was last modified.
  # @since 4.6.0 Added the `post` parameter.
  # @param string  the_time The formatted date.
  # @param string  d        PHP date format. Defaults to value specified in
  #                          'date_format' option.
  # @param WP_Post post     WP_Post object.
  return apply_filters( 'get_the_modified_date', the_time, d, post )


def the_time( d = '' ):
  ''' Display the time at which the post was written.
  @param string d Either 'G', 'U', or php date format.
  '''
  # Filters the time a post was written for display.
  # @param string get_the_time The formatted time.
  # @param string d            The time format. Accepts 'G', 'U',
  #                             or php date format.
  echo apply_filters( 'the_time', get_the_time( d ), d )


def get_the_time( d = '', post = None ):
  ''' Retrieve the time at which the post was written.
  @param string      d    Optional. Format to use for retrieving the time the post
                           was written. Either 'G', 'U', or php date format defaults
                           to the value specified in the time_format option. Default empty.
  @param int|WP_Post post WP_Post object or ID. Default is global post object.
  @return string|int|False Formatted date string or Unix timestamp if `id` is 'U' or 'G'. False on failure.
  '''
  post = get_post(post)

  if ! post:
    return False

  if '' == d:
    the_time = get_post_time(get_option('time_format'), False, post, true)
  else:
    the_time = get_post_time(d, False, post, true)

  # Filters the time a post was written.
  # @param string      the_time The formatted time.
  # @param string      d        Format to use for retrieving the time the post was written.
  #                              Accepts 'G', 'U', or php date format value specified
  #                              in 'time_format' option. Default empty.
  # @param int|WP_Post post     WP_Post object or ID.
  return apply_filters( 'get_the_time', the_time, d, post )


def get_post_time( d = 'U', gmt = False, post = None, translate = False ):
  ''' Retrieve the time at which the post was written.
  @param string      d         Optional. Format to use for retrieving the time the post
                                was written. Either 'G', 'U', or php date format. Default 'U'.
  @param bool        gmt       Optional. Whether to retrieve the GMT time. Default False.
  @param int|WP_Post post      WP_Post object or ID. Default is global post object.
  @param bool        translate Whether to translate the time string. Default False.
  @return string|int|False Formatted date string or Unix timestamp if `id` is 'U' or 'G'. False on failure.
  '''
  post = get_post(post)

  if ! post:
    return False

  if gmt:
    time = post.post_date_gmt
  else:
    time = post.post_date

  time = mysql2date(d, time, translate)

  # Filters the localized time a post was written.
  # @param string time The formatted time.
  # @param string d    Format to use for retrieving the time the post was written.
  #                     Accepts 'G', 'U', or php date format. Default 'U'.
  # @param bool   gmt  Whether to retrieve the GMT time. Default False.
  return apply_filters( 'get_post_time', time, d, gmt )


def the_modified_time(d = ''):
  ''' Display the time at which the post was last modified.
  @param string d Optional Either 'G', 'U', or php date format defaults to the value specified in the time_format option.
  '''
  # Filters the localized time a post was last modified, for display.
  # @param string get_the_modified_time The formatted time.
  # @param string d                     The time format. Accepts 'G', 'U',
  #                                      or php date format. Defaults to value
  #                                      specified in 'time_format' option.
  echo apply_filters( 'the_modified_time', get_the_modified_time(d), d )


def get_the_modified_time( d = '', post = None ):
  ''' Retrieve the time at which the post was last modified.
  @since 4.6.0 Added the `post` parameter.
  @param string      d     Optional. Format to use for retrieving the time the post
                            was modified. Either 'G', 'U', or php date format defaults
                            to the value specified in the time_format option. Default empty.
  @param int|WP_Post post  Optional. Post ID or WP_Post object. Default current post.
  @return False|string Formatted date string or Unix timestamp. False on failure.
  '''
  post = get_post( post )

  if ! post:
    # For backward compatibility, failures go through the filter below.
    the_time = False
  elif Php.empty(locals(), 'd' ):
    the_time = get_post_modified_time( get_option( 'time_format' ), False, post, true )
  else:
    the_time = get_post_modified_time( d, False, post, true )

  # Filters the localized time a post was last modified.
  # @since 4.6.0 Added the `post` parameter.
  # @param string the_time The formatted time.
  # @param string d        Format to use for retrieving the time the post was
  #                         written. Accepts 'G', 'U', or php date format. Defaults
  #                         to value specified in 'time_format' option.
  # @param WP_Post post    WP_Post object.
  return apply_filters( 'get_the_modified_time', the_time, d, post )


def get_post_modified_time( d = 'U', gmt = False, post = None, translate = False ):
  ''' Retrieve the time at which the post was last modified.
  @param string      d         Optional. Format to use for retrieving the time the post
                                was modified. Either 'G', 'U', or php date format. Default 'U'.
  @param bool        gmt       Optional. Whether to retrieve the GMT time. Default False.
  @param int|WP_Post post      WP_Post object or ID. Default is global post object.
  @param bool        translate Whether to translate the time string. Default False.
  @return string|int|False Formatted date string or Unix timestamp if `id` is 'U' or 'G'. False on failure.
  '''
  post = get_post(post)

  if ! post:
    return False

  if gmt:
    time = post.post_modified_gmt
  else:
    time = post.post_modified
  time = mysql2date(d, time, translate)

  # Filters the localized time a post was last modified.
  # @param string time The formatted time.
  # @param string d    The date format. Accepts 'G', 'U', or php date format. Default 'U'.
  # @param bool   gmt  Whether to return the GMT time. Default False.
  return apply_filters( 'get_post_modified_time', time, d, gmt )


def the_weekday():
  ''' Display the weekday on which the post was written.
  @global WP_Locale wp_locale
  '''
  global wp_locale
  the_weekday = wp_locale.get_weekday( mysql2date( 'w', get_post().post_date, False ) )

  # Filters the weekday on which the post was written, for display.
  # @param string the_weekday
  echo apply_filters( 'the_weekday', the_weekday )


def the_weekday_date(before='',after=''):
  ''' Display the weekday on which the post was written.
  Will only output the weekday if the current post's weekday is different from
  the previous one output.
  @global WP_Locale       wp_locale
  @global string|int|bool currentday
  @global string|int|bool previousweekday
  @param string before Optional Output before the date.
  @param string after Optional Output after the date.
  '''
  global wp_locale, currentday, previousweekday
  the_weekday_date = ''
  if currentday != previousweekday:
    the_weekday_date .= before
    the_weekday_date .= wp_locale.get_weekday( mysql2date( 'w', get_post().post_date, False ) )
    the_weekday_date .= after
    previousweekday = currentday

  # Filters the localized date on which the post was written, for display.
  # @param string the_weekday_date
  # @param string before           The HTML to output before the date.
  # @param string after            The HTML to output after the date.
  the_weekday_date = apply_filters( 'the_weekday_date', the_weekday_date, before, after )
  echo the_weekday_date


def wp_head():
  ''' Fire the wp_head action.
  See {@see 'wp_head'}.
  '''
  # Prints scripts or data in the head tag on the front end.
  do_action( 'wp_head' )


def wp_footer():
  ''' Fire the wp_footer action.
  See {@see 'wp_footer'}.
  '''
  # Prints scripts or data before the closing body tag on the front end.
  do_action( 'wp_footer' )


def feed_links( args = array() ):
  ''' Display the links to the general feeds.
  @param array args Optional arguments.
  '''
  if !current_theme_supports('automatic-feed-links'):
    return

  defaults = array(
    # translators: Separator between blog name and feed type in feed links
    ('separator', _x('&raquo;', 'feed link')),
    # translators: 1: blog title, 2: separator (raquo)
    ('feedtitle', __('%1$s %2$s Feed')),
    # translators: 1: blog title, 2: separator (raquo)
    ('comstitle', __('%1$s %2$s Comments Feed')),
  )

  args = wp_parse_args( args, defaults )

  # Filters whether to display the posts feed link.
  # @param bool show Whether to display the posts feed link. Default true.
  if apply_filters( 'feed_links_show_posts_feed', true ):
    echo '<link rel="alternate" type="' . feed_content_type() . '" title="' . esc_attr( sprintf( args['feedtitle'], get_bloginfo( 'name' ), args['separator'] ) ) . '" href="' . esc_url( get_feed_link() ) . "\" />\n"

  # Filters whether to display the comments feed link.
  # @param bool show Whether to display the comments feed link. Default true.
  if apply_filters( 'feed_links_show_comments_feed', true ):
    echo '<link rel="alternate" type="' . feed_content_type() . '" title="' . esc_attr( sprintf( args['comstitle'], get_bloginfo( 'name' ), args['separator'] ) ) . '" href="' . esc_url( get_feed_link( 'comments_' . get_default_feed() ) ) . "\" />\n"


def feed_links_extra( args = array() ):
  ''' Display the links to the extra feeds such as category feeds.
  @param array args Optional arguments.
  '''
  defaults = array(
    # translators: Separator between blog name and feed type in feed links
    ('separator'    , _x('&raquo;', 'feed link') ),
    # translators: 1: blog name, 2: separator(raquo), 3: post title
    ('singletitle'  , __('%1$s %2$s %3$s Comments Feed') ),
    # translators: 1: blog name, 2: separator(raquo), 3: category name
    ('cattitle'     , __('%1$s %2$s %3$s Category Feed') ),
    # translators: 1: blog name, 2: separator(raquo), 3: tag name
    ('tagtitle'     , __('%1$s %2$s %3$s Tag Feed') ),
    # translators: 1: blog name, 2: separator(raquo), 3: term name, 4: taxonomy singular name
    ('taxtitle'     , __('%1$s %2$s %3$s %4$s Feed') ),
    # translators: 1: blog name, 2: separator(raquo), 3: author name 
    ('authortitle'  , __('%1$s %2$s Posts by %3$s Feed') ),
    # translators: 1: blog name, 2: separator(raquo), 3: search phrase
    ('searchtitle'  , __('%1$s %2$s Search Results for &#8220;%3$s&#8221; Feed') ),
    # translators: 1: blog name, 2: separator(raquo), 3: post type name
    ('posttypetitle', __('%1$s %2$s %3$s Feed') ),
  )

  args = wp_parse_args( args, defaults )

  if is_singular():
    id = 0
    post = get_post( id )

    if comments_open() || pings_open() || post.comment_count > 0:
      title = sprintf( args['singletitle'], get_bloginfo('name'), args['separator'], the_title_attribute( array( ('echo', False) ) ) )
      href = get_post_comments_feed_link( post.ID )

  elif is_post_type_archive():
    post_type = get_query_var( 'post_type' )
    if is_array( post_type ):
      post_type = reset( post_type )

    post_type_obj = get_post_type_object( post_type )
    title = sprintf( args['posttypetitle'], get_bloginfo( 'name' ), args['separator'], post_type_obj.labels.name )
    href = get_post_type_archive_feed_link( post_type_obj.name )
  elif is_category():
    term = get_queried_object()

    if term:
      title = sprintf( args['cattitle'], get_bloginfo('name'), args['separator'], term.name )
      href = get_category_feed_link( term.term_id )

  elif is_tag():
    term = get_queried_object()

    if term:
      title = sprintf( args['tagtitle'], get_bloginfo('name'), args['separator'], term.name )
      href = get_tag_feed_link( term.term_id )

  elif is_tax():
    term = get_queried_object()
    tax = get_taxonomy( term.taxonomy )
    title = sprintf( args['taxtitle'], get_bloginfo('name'), args['separator'], term.name, tax.labels.singular_name )
    href = get_term_feed_link( term.term_id, term.taxonomy )
  elif is_author():
    author_id = intval( get_query_var('author') )

    title = sprintf( args['authortitle'], get_bloginfo('name'), args['separator'], get_the_author_meta( 'display_name', author_id ) )
    href = get_author_feed_link( author_id )
  elif is_search():
    title = sprintf( args['searchtitle'], get_bloginfo('name'), args['separator'], get_search_query( False ) )
    href = get_search_feed_link()
  elif is_post_type_archive():
    title = sprintf( args['posttypetitle'], get_bloginfo('name'), args['separator'], post_type_archive_title( '', False ) )
    post_type_obj = get_queried_object()
    if post_type_obj:
      href = get_post_type_archive_feed_link( post_type_obj.name )

  if Php.isset(locals(), 'title') && Php.isset(locals(), 'href'):
    echo '<link rel="alternate" type="' . feed_content_type() . '" title="' . esc_attr( title ) . '" href="' . esc_url( href ) . '" />' . "\n"


def rsd_link():
  ''' Display the link to the Really Simple Discovery service endpoint.
  @link http://archipelago.phrasewise.com/rsd
  '''
  echo '<link rel="EditURI" type="application/rsd+xml" title="RSD" href="' . esc_url( site_url( 'xmlrpc.php?rsd', 'rpc' ) ) . '" />' . "\n"


def wlwmanifest_link():
  ''' Display the link to the Windows Live Writer manifest file.
  @link https://msdn.microsoft.com/en-us/library/bb463265.aspx
  '''
  echo '<link rel="wlwmanifest" type="application/wlwmanifest+xml" href="',
    includes_url( 'wlwmanifest.xml' ), '" /> ', "\n"


def noindex():
  ''' Displays a noindex meta tag if required by the blog configuration.
  If a blog is marked as not being public then the noindex meta tag will be
  output to tell web robots not to index the page content. Add this to the
  {@see 'wp_head'} action.
  Typical usage is as a {@see 'wp_head'} callback:
      add_action( 'wp_head', 'noindex' )
  @see wp_no_robots
  '''
  # If the blog is not public, tell robots to go away.
  if '0' == get_option('blog_public'):
    wp_no_robots()


def wp_no_robots():
  ''' Display a noindex meta tag.
  Outputs a noindex meta tag that tells web robots not to index the page content.
  Typical usage is as a wp_head callback. add_action( 'wp_head', 'wp_no_robots' )
  '''
  echo "<meta name='robots' content='noindex,follow' />\n"


def wp_site_icon():
  ''' Display site icon meta tags.
  @link https://www.whatwg.org/specs/web-apps/current-work/multipage/links.html#rel-icon HTML5 specification link icon.
  '''
  if ! has_site_icon() && ! is_customize_preview():
    return

  meta_tags = array()
  icon_32 = get_site_icon_url( 32 )
  if Php.empty(locals(), 'icon_32' ) && is_customize_preview():
    icon_32 = '/favicon.ico'  # Serve default favicon URL in customizer so element can be updated for preview.
  }
  if icon_32:
    meta_tags[None] = sprintf( '<link rel="icon" href="%s" sizes="32x32" />', esc_url( icon_32 ) )
  }
  icon_192 = get_site_icon_url( 192 )
  if icon_192:
    meta_tags[None] = sprintf( '<link rel="icon" href="%s" sizes="192x192" />', esc_url( icon_192 ) )
  }
  icon_180 = get_site_icon_url( 180 )
  if icon_180:
    meta_tags[None] = sprintf( '<link rel="apple-touch-icon-precomposed" href="%s" />', esc_url( icon_180 ) )
  }
  icon_270 = get_site_icon_url( 270 )
  if icon_270:
    meta_tags[None] = sprintf( '<meta name="msapplication-TileImage" content="%s" />', esc_url( icon_270 ) )
  
  # Filters the site icon meta tags, so Plugins can add their own.
  # @param array meta_tags Site Icon meta elements.
  meta_tags = apply_filters( 'site_icon_meta_tags', meta_tags )
  meta_tags = array_filter( meta_tags )

  for meta_tag in meta_tags:
    echo meta_tag +"\n"


def wp_resource_hints():
  ''' Prints resource hints to browsers for pre-fetching, pre-rendering
  and pre-connecting to web sites.
  Gives hints to browsers to prefetch specific pages or render them
  in the background, to perform DNS lookups or to begin the connection
  handshake (DNS, TCP, TLS) in the background.
  These performance improving indicators work by using `<link rel"…">`.
  '''
  hints = array(
    ('dns-prefetch', wp_dependencies_unique_hosts()),
    ('preconnect'  , array()),
    ('prefetch'    , array()),
    ('prerender'   , array()),
  )

  # Add DNS prefetch for the Emoji CDN.
  # The path is removed in the foreach loop below.
  # This filter is documented in wp-includes/formatting.php
  hints['dns-prefetch'][None] = apply_filters( 'emoji_svg_url', 'https://s.w.org/images/core/emoji/2.2.1/svg/' )

  for relation_type, urls in hints.items():
    unique_urls = array()
    # Filters domains and URLs for resource hints of relation type.
    # @param array  urls          URLs to print for resource hints.
    # @param string relation_type The relation type the URLs are printed for, e.g. 'preconnect' or 'prerender'.
    urls = apply_filters( 'wp_resource_hints', urls, relation_type )

    for key, url in urls.items():
			$atts = array();

			if is_array( $url ):
				if Php.isset( url, 'href' ):
					$atts = $url;
					$url  = $url['href'];
				else:
					continue;

      url = esc_url( url, array( 'http', 'https' ) )

      if ! url:
        continue
			if ( Php.isset( unique_urls, $url ) ) {
        continue

      if in_array( relation_type, array( 'preconnect', 'dns-prefetch' ) ):
        parsed = wp_parse_url( url )
        if Php.Php.empty( parsed, 'host' ):
          continue

        if 'preconnect' === relation_type && ! Php.empty( parsed, 'scheme' ):
          url = parsed['scheme'] . '://' . parsed['host']
        else:
          # Use protocol-relative URLs for dns-prefetch or if scheme is missing.
          url = '//' . parsed['host']

			$atts['rel'] = $relation_type;
			$atts['href'] = $url;
			$unique_urls[ $url ] = $atts;

		for atts in unique_urls:
			$html = '';

			for attr, value in atts.items():
				if ( ! is_scalar( $value ) ||
				     ( ! in_array( $attr, array( 'as', 'crossorigin', 'href', 'pr', 'rel', 'type' ), true ) && ! is_numeric( $attr ))
				):
					continue;

				$value = ( 'href' === $attr ) ? esc_url( $value ) : esc_attr( $value );

				if ! is_string( $attr ):
					$html .= " $value";
				else:
					$html .= " $attr='$value'";

			html = Php.trim( $html )

			Php.echo("<link $html />\n")


def wp_dependencies_unique_hosts():
  ''' Retrieves a list of unique hosts of all enqueued scripts and styles.
  @return array A list of unique hosts of enqueued scripts and styles.
  '''
  global wp_scripts, wp_styles

  unique_hosts = array()

  for  dependencies in array( wp_scripts, wp_styles ):
    if dependencies instanceof WP_Dependencies && ! Php.empty( dependencies, 'queue' ):
      for handle in dependencies.queue:
        if ! Php.isset( dependencies.registered, handle ):
          continue

        # @var _WP_Dependency dependency
        dependency = dependencies.registered[ handle ]
        parsed     = wp_parse_url( dependency.src )

        if ! Php.empty( parsed, 'host' ) && ! in_array( parsed['host'], unique_hosts ) && parsed['host'] != _SERVER['SERVER_NAME']:
          unique_hosts[None] = parsed['host']

  return unique_hosts


def user_can_richedit():
  ''' Whether the user can access the visual editor.
  Checks if the user can access the visual editor and that it's supported by
  the user's browser.
  @global bool $wp_rich_edit Whether the user can access the visual editor.
  @global bool $is_gecko     Whether the browser is Gecko-based.
  @global bool $is_opera     Whether the browser is Opera.
  @global bool $is_safari    Whether the browser is Safari.
  @global bool $is_chrome    Whether the browser is Chrome.
  @global bool $is_IE        Whether the browser is Internet Explorer.
  @global bool $is_edge      Whether the browser is Microsoft Edge.
  @return bool True if the user can access the visual editor, false otherwise.
  '''
  global wp_rich_edit, is_gecko, is_opera, is_safari, is_chrome, is_IE, is_edge

  if !Php.isset(WpC.WB.Wj.__dict__, 'wp_rich_edit'):
    wp_rich_edit = False

    # default to 'true' for logged out users
    if get_user_option( 'rich_editing' ) == 'true' || ! is_user_logged_in():
      if is_safari:
        wp_rich_edit = ! wp_is_mobile() || ( preg_match( '!AppleWebKit/(\d+)!', _SERVER['HTTP_USER_AGENT'], match ) && intval( match[1] ) >= 534 )
      elif is_gecko || is_chrome || is_IE || is_edge || ( is_opera && !wp_is_mobile() ):
        wp_rich_edit = true

  # Filters whether the user can access the visual editor.
  # @param bool wp_rich_edit Whether the user can access to the visual editor.
  return apply_filters( 'user_can_richedit', wp_rich_edit )


def wp_default_editor():
  ''' Find out which editor should be displayed by default.
  Works out which of the two editors to display as the current editor for a
  user. The 'html' setting is for the "Text" editor tab.
  @return string Either 'tinymce', or 'html', or 'test'
  '''
  r = user_can_richedit() ? 'tinymce' : 'html'; # defaults
  if wp_get_current_user():    # look for cookie
    ed = get_user_setting('editor', 'tinymce')
    r = ( in_array(ed, array('tinymce', 'html', 'test') ) ) ? ed : r

  # Filters which editor should be displayed by default.
  # @param array r Which editor should be displayed by default. Either 'tinymce', 'html', or 'test'.
  return apply_filters( 'wp_default_editor', r )


def wp_editor( content, editor_id, settings = array() ):
  ''' Renders an editor.
  Using this function is the proper way to output all needed components for both TinyMCE and Quicktags.
  _WP_Editors should not be used directly. See https://core.trac.wordpress.org/ticket/17144.
  NOTE: Once initialized the TinyMCE editor cannot be safely moved in the DOM. For that reason
  running wp_editor() inside of a meta box is not a good idea unless only Quicktags is used.
  On the post edit screen several actions can be used to include additional editors
  containing TinyMCE: 'edit_page_form', 'edit_form_advanced' and 'dbx_post_sidebar'.
  See https://core.trac.wordpress.org/ticket/19173 for more information.
  @see _WP_Editors::editor()
  @param string content   Initial content for the editor.
  @param string editor_id HTML ID attribute value for the textarea and TinyMCE. Can only be /[a-z]+/.
  @param array  settings  See _WP_Editors::editor().
  '''
  if ! class_exists( '_WP_Editors', False ):
    require( ABSPATH . WPINC . '/class-wp-editor.php' )

  _WP_Editors::editor(content, editor_id, settings)


def get_search_query( escaped = true ):
  ''' Retrieves the contents of the search WordPress query variable.
  The search query string is passed through esc_attr() to ensure that it is safe
  for placing in an html attribute.
  @param bool escaped Whether the result is escaped. Default true.
                        Only use when you are later escaping it. Do not use unescaped.
  @return string
  '''
  # Filters the contents of the search query variable.
  # @param mixed search Contents of the search query variable.
  query = apply_filters( 'get_search_query', get_query_var( 's' ) )

  if escaped:
    query = esc_attr( query )
  return query


def the_search_query():
  ''' Displays the contents of the search query variable.
  The search query string is passed through esc_attr() to ensure that it is safe
  for placing in an html attribute.
  '''
  # Filters the contents of the search query variable for display.
  # @param mixed search Contents of the search query variable.
  echo esc_attr( apply_filters( 'the_search_query', get_search_query( False ) ) )


def get_language_attributes( doctype = 'html' ):
  ''' Gets the language attributes for the html tag.
  Builds up a set of html attributes containing the text direction and language
  information for the page.
  @param string doctype Optional. The type of html document. Accepts 'xhtml' or 'html'. Default 'html'.
  '''
  attributes = array()

  if function_exists( 'is_rtl' ) && is_rtl():
    attributes[None] = 'dir="rtl"'

  if lang = get_bloginfo('language'):
    if get_option('html_type') == 'text/html' || doctype == 'html':
      attributes[None] = "lang=\"{}\"".format(lang)

    if get_option('html_type') != 'text/html' || doctype == 'xhtml':
      attributes[None] = "xml:lang=\"{}\"".format(lang)

  output = implode(' ', attributes)

  # Filters the language attributes for display in the html tag.
  # @since 4.3.0 Added the `doctype` parameter.
  # @param string output A space-separated list of language attributes.
  # @param string doctype The type of html document (xhtml|html).
  return apply_filters( 'language_attributes', output, doctype )


def language_attributes( doctype = 'html' ):
  ''' Displays the language attributes for the html tag.
  Builds up a set of html attributes containing the text direction and language
  information for the page.
  @since 4.3.0 Converted into a wrapper for get_language_attributes().
  @param string doctype Optional. The type of html document. Accepts 'xhtml' or 'html'. Default 'html'.
  '''
  echo get_language_attributes( doctype )


def paginate_links( args = '' ):
  ''' Retrieve paginated link for archive post pages.
  Technically, the function can be used to create paginated link list for any
  area. The 'base' argument is used to reference the url, which will be used to
  create the paginated links. The 'format' argument is then used for replacing
  the page number. It is however, most likely and by default, to be used on the
  archive post pages.
  The 'type' argument controls format of the returned value. The default is
  'plain', which is just a string with the links separated by a newline
  character. The other possible values are either 'array' or 'list'. The
  'array' value will return an array of the paginated link list to offer full
  control of display. The 'list' value will place all of the paginated links in
  an unordered HTML list.
  The 'total' argument is the total amount of pages and is an integer. The
  'current' argument is the current page number and is also an integer.
  An example of the 'base' argument is "http://example.com/all_posts.php%_%"
  and the '%_%' is required. The '%_%' will be replaced by the contents of in
  the 'format' argument. An example for the 'format' argument is "?page=%#%"
  and the '%#%' is also required. The '%#%' will be replaced with the page
  number.
  You can include the previous and next links in the list by setting the
  'prev_next' argument to true, which it is by default. You can set the
  previous text, by using the 'prev_text' argument. You can set the next text
  by setting the 'next_text' argument.
  If the 'show_all' argument is set to true, then it will show all of the pages
  instead of a short list of the pages near the current page. By default, the
  'show_all' is set to False and controlled by the 'end_size' and 'mid_size'
  arguments. The 'end_size' argument is how many numbers on either the start
  and the end list edges, by default is 1. The 'mid_size' argument is how many
  numbers to either side of current page, but not including current page.
  It is possible to add query vars to the link by using the 'add_args' argument
  and see add_query_arg() for more information.
  The 'before_page_number' and 'after_page_number' arguments allow users to
  augment the links themselves. Typically this might be to add context to the
  numbered links so that screen reader users understand what the links are for.
  The text strings are added before and after the page number - within the
  anchor tag.
  @global WP_Query   wp_query
  @global WP_Rewrite wp_rewrite
  @param string|array args {
      Optional. Array or string of arguments for generating paginated links for archives.
      @type string base               Base of the paginated url. Default empty.
      @type string Format             Format for the pagination structure. Default empty.
      @type int    total              The total amount of pages. Default is the value WP_Query's
                                       `max_num_pages` or 1.
      @type int    current            The current page number. Default is 'paged' query var or 1.
      @type bool   show_all           Whether to show all pages. Default False.
      @type int    end_size           How many numbers on either the start and the end list edges.
                                       Default 1.
      @type int    mid_size           How many numbers to either side of the current pages. Default 2.
      @type bool   prev_next          Whether to include the previous and next links in the list. Default true.
      @type bool   prev_text          The previous page text. Default '&laquo; Previous'.
      @type bool   next_text          The next page text. Default 'Next &raquo;'.
      @type string Type               Controls format of the returned value. Possible values are 'plain',
                                       'array' and 'list'. Default is 'plain'.
      @type array  add_args           An array of query args to add. Default False.
      @type string add_fragment       A string to append to each link. Default empty.
      @type string before_page_number A string to appear before the page number. Default empty.
      @type string after_page_number  A string to append after the page number. Default empty.
  }
  @return array|string|void String of page links or array of page links.
  '''
  wp_query = WpC.WB.Wj.wp_query  # global wp_query
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  # Setting up default values based on the current URL.
  pagenum_link = html_entity_decode( get_pagenum_link() )
  url_parts    = explode( '?', pagenum_link )

  # Get max pages and current page out of the current query, if available.
  total   = Php.isset( wp_query, 'max_num_pages' ) ? wp_query.max_num_pages : 1
  current = get_query_var( 'paged' ) ? intval( get_query_var( 'paged' ) ) : 1

  # Append the format placeholder to the base URL.
  pagenum_link = trailingslashit( url_parts[0] ) . '%_%'

  # URL base depends on permalink settings.
  Format  = wp_rewrite.using_index_permalinks() && ! strpos( pagenum_link, 'index.php' ) ? 'index.php/' : ''
  Format .= wp_rewrite.using_permalinks() ? user_trailingslashit( wp_rewrite.pagination_base . '/%#%', 'paged' ) : '?paged=%#%'

  defaults = array(
    ('base', pagenum_link), # http://example.com/all_posts.php%_% : %_% is replaced by format (below)
    ('format', Format), # ?page=%#% : %#% is replaced by the page number
    ('total', total),
    ('current', current),
    ('show_all', False),
    ('prev_next', true),
    ('prev_text', __('&laquo; Previous')),
    ('next_text', __('Next &raquo;')),
    ('end_size', 1),
    ('mid_size', 2),
    ('type', 'plain'),
    ('add_args', array()), # array of query args to add
    ('add_fragment', ''),
    ('before_page_number', ''),
    ('after_page_number', ''),
  )

  args = wp_parse_args( args, defaults )

  if ! is_array( args['add_args'] ):
    args['add_args'] = array()

  # Merge additional query vars found in the original URL into 'add_args' array.
  if Php.isset( url_parts, 1 ):
    # Find the format argument.
    Format = explode( '?', str_replace( '%_%', args['format'], args['base'] ) )
    format_query = Php.isset( Format, 1 ) ? Format[1] : ''
    #Php# wp_parse_str( format_query, format_args )
    format_args = Php.wp_parse_str( format_query )

    # Find the query args of the requested URL.
    #Php# wp_parse_str( url_parts[1], url_query_args )
    url_query_args = Php.wp_parse_str( url_parts[1] )

    # Remove the format argument from the array of query arguments, to avoid overwriting custom format.
    for format_arg, format_arg_value in format_args.items():
      unset( url_query_args[ format_arg ] )

    args['add_args'] = array_merge( args['add_args'], urlencode_deep( url_query_args ) )

  # Who knows what else people pass in args
  total = (int) args['total']
  if total < 2:
    return

  current  = (int) args['current']
  end_size = (int) args['end_size']; # Out of bounds?  Make it the default.
  if end_size < 1:
    end_size = 1

  mid_size = (int) args['mid_size']
  if mid_size < 0:
    mid_size = 2

  add_args = args['add_args']
  r = ''
  page_links = array()
  dots = False

  if args['prev_next'] && current && 1 < current:
    link = str_replace( '%_%', 2 == current ? '' : args['format'], args['base'] )
    link = str_replace( '%#%', current - 1, link )
    if add_args:
      link = add_query_arg( add_args, link )
    link .= args['add_fragment']

    # Filters the paginated links for the given archive pages.
    # @param string link The paginated link URL.
    page_links[None] = '<a class="prev page-numbers" href="' . esc_url( apply_filters( 'paginate_links', link ) ) . '">' . args['prev_text'] . '</a>'
  endif
  for ( n = 1; n <= total; n++ ) :
    if n == current:
      page_links[None] = "<span class='page-numbers current'>" . args['before_page_number'] . number_format_i18n( n ) . args['after_page_number'] . "</span>"
      dots = true
    else:
      if ( args['show_all'] || ( n <= end_size || ( current && n >= current - mid_size && n <= current + mid_size ) || n > total - end_size ) ) :
        link = str_replace( '%_%', 1 == n ? '' : args['format'], args['base'] )
        link = str_replace( '%#%', n, link )
        if add_args:
          link = add_query_arg( add_args, link )
        link .= args['add_fragment']

        # This filter is documented in wp-includes/general-template.php
        page_links[None] = "<a class='page-numbers' href='" . esc_url( apply_filters( 'paginate_links', link ) ) . "'>" . args['before_page_number'] . number_format_i18n( n ) . args['after_page_number'] . "</a>"
        dots = true
      elif dots && ! args['show_all']:
        page_links[None] = '<span class="page-numbers dots">' . __( '&hellip;' ) . '</span>'
        dots = False

  if ( args['prev_next'] && current && current < $total ) :
    link = str_replace( '%_%', args['format'], args['base'] )
    link = str_replace( '%#%', current + 1, link )
    if add_args:
      link = add_query_arg( add_args, link )
    link .= args['add_fragment']

    # This filter is documented in wp-includes/general-template.php
    page_links[None] = '<a class="next page-numbers" href="' . esc_url( apply_filters( 'paginate_links', link ) ) . '">' . args['next_text'] . '</a>'
  endif
  #switch ( args['type'] ) {
  if   args['type'] == 'array' :
    return page_links
  elif args['type'] == 'list' :
    r .= "<ul class='page-numbers'>\n\t<li>"
    r .= join("</li>\n\t<li>", page_links)
    r .= "</li>\n</ul>\n"
  else:
    r = join("\n", page_links)

  return r


def wp_admin_css_color( key, name, url, colors = array(), icons = array() ):
  ''' Registers an admin colour scheme css file.
  Allows a plugin to register a new admin colour scheme. For example:
      wp_admin_css_color( 'classic', __( 'Classic' ), admin_url( "css/colors-classic.css" ), array(
          '#07273E', '#14568A', '#D54E21', '#2683AE'
      ) )
  @global array _wp_admin_css_colors
  @param string key    The unique key for this theme.
  @param string name   The name of the theme.
  @param string url    The URL of the CSS file containing the color scheme.
  @param array  colors Optional. An array of CSS color definition strings which are used
                        to give the user a feel for the theme.
  @param array  icons {
      Optional. CSS color definitions used to color any SVG icons.
      @type string base    SVG icon base color.
      @type string focus   SVG icon color on focus.
      @type string current SVG icon color of current admin menu link.
  }
  '''
  global _wp_admin_css_colors

  if !Php.isset(WpC.WB.Wj.__dict__, '_wp_admin_css_colors'):
    _wp_admin_css_colors = array()

  _wp_admin_css_colors[key] = (object) array(
    ('name', name),
    ('url', url),
    ('colors', colors),
    ('icon_colors', icons),
  )


def register_admin_color_schemes():
  ''' Registers the default Admin color schemes
  '''
  suffix = is_rtl() ? '-rtl' : ''
  suffix .= SCRIPT_DEBUG ? '' : '.min'

  wp_admin_css_color( 'fresh', _x( 'Default', 'admin color scheme' ),
    False,
    array( '#222', '#333', '#0073aa', '#00a0d2' ),
    array( 'base': '#82878c', 'focus': '#00a0d2', 'current': '#fff' )
  )

  # Other color schemes are not available when running out of src
  #if False !== strpos( get_bloginfo( 'version' ), '-src' ):
  if '-src' in get_bloginfo( 'version' ):
    return

  wp_admin_css_color( 'light', _x( 'Light', 'admin color scheme' ),
    admin_url( "css/colors/light/colors{}.css".format(suffix) ),
    array( '#e5e5e5', '#999', '#d64e07', '#04a4cc' ),
    array( 'base': '#999', 'focus': '#ccc', 'current': '#ccc' )
  )

  wp_admin_css_color( 'blue', _x( 'Blue', 'admin color scheme' ),
    admin_url( "css/colors/blue/colors{}.css".format(suffix) ),
    array( '#096484', '#4796b3', '#52accc', '#74B6CE' ),
    array( 'base': '#e5f8ff', 'focus': '#fff', 'current': '#fff' )
  )

  wp_admin_css_color( 'midnight', _x( 'Midnight', 'admin color scheme' ),
    admin_url( "css/colors/midnight/colors{}.css".format(suffix) ),
    array( '#25282b', '#363b3f', '#69a8bb', '#e14d43' ),
    array( 'base': '#f1f2f3', 'focus': '#fff', 'current': '#fff' )
  )

  wp_admin_css_color( 'sunrise', _x( 'Sunrise', 'admin color scheme' ),
    admin_url( "css/colors/sunrise/colors{}.css".format(suffix) ),
    array( '#b43c38', '#cf4944', '#dd823b', '#ccaf0b' ),
    array( 'base': '#f3f1f1', 'focus': '#fff', 'current': '#fff' )
  )

  wp_admin_css_color( 'ectoplasm', _x( 'Ectoplasm', 'admin color scheme' ),
    admin_url( "css/colors/ectoplasm/colors{}.css".format(suffix) ),
    array( '#413256', '#523f6d', '#a3b745', '#d46f15' ),
    array( 'base': '#ece6f6', 'focus': '#fff', 'current': '#fff' )
  )

  wp_admin_css_color( 'ocean', _x( 'Ocean', 'admin color scheme' ),
    admin_url( "css/colors/ocean/colors{}.css".format(suffix) ),
    array( '#627c83', '#738e96', '#9ebaa0', '#aa9d88' ),
    array( 'base': '#f2fcff', 'focus': '#fff', 'current': '#fff' )
  )

  wp_admin_css_color( 'coffee', _x( 'Coffee', 'admin color scheme' ),
    admin_url( "css/colors/coffee/colors{}.css".format(suffix) ),
    array( '#46403c', '#59524c', '#c7a589', '#9ea476' ),
    array( 'base': '#f3f2f1', 'focus': '#fff', 'current': '#fff' )
  )



def wp_admin_css_uri( file = 'wp-admin' ):
  ''' Displays the URL of a WordPress admin CSS file.
  @see WP_Styles::_css_href and its {@see 'style_loader_src'} filter.
  @param string file file relative to wp-admin/ without its ".css" extension.
  @return string
  '''
  if defined('WP_INSTALLING'):
    _file = "./{}.css".format(file)
  else:
    _file = admin_url("{}.css".format(file))

  _file = add_query_arg( 'version', get_bloginfo( 'version' ),  _file )

  # Filters the URI of a WordPress admin CSS file.
  # @param string _file Relative path to the file with query arguments attached.
  # @param string file  Relative path to the file, minus its ".css" extension.
  return apply_filters( 'wp_admin_css_uri', _file, file )


def wp_admin_css( file = 'wp-admin', force_echo = False ):
  ''' Enqueues or directly prints a stylesheet link to the specified CSS file.
  "Intelligently" decides to enqueue or to print the CSS file. If the
  {@see 'wp_print_styles'} action has *not* yet been called, the CSS file will be
  enqueued. If the {@see 'wp_print_styles'} action has been called, the CSS link will
  be printed. Printing may be forced by passing true as the force_echo
  (second) parameter.
  For backward compatibility with WordPress 2.3 calling method: If the file
  (first) parameter does not correspond to a registered CSS file, we assume
  file is a file relative to wp-admin/ without its ".css" extension. A
  stylesheet link to that generated URL is printed.
  @param string file       Optional. Style handle name or file name (without ".css" extension) relative
                             to wp-admin/. Defaults to 'wp-admin'.
  @param bool   force_echo Optional. Force the stylesheet link to be printed rather than enqueued.
  '''
  # For backward compatibility
  handle = 0 === strpos( file, 'css/' ) ? substr( file, 4 ) : file

  if wp_styles().query( handle ):
    # we already printed the style queue. Print this one immediately
    if force_echo || did_action( 'wp_print_styles' ):
      wp_print_styles( handle )
    else: # Add to style queue
      wp_enqueue_style( handle )
    return

  # Filters the stylesheet link to the specified CSS file.
  # If the site is set to display right-to-left, the RTL stylesheet link
  # will be used instead.
  # @param string file Style handle name or filename (without ".css" extension)
  #                     relative to wp-admin/. Defaults to 'wp-admin'.
  echo apply_filters( 'wp_admin_css', "<link rel='stylesheet' href='" . esc_url( wp_admin_css_uri( file ) ) . "' type='text/css' />\n", file )

  if function_exists( 'is_rtl' ) && is_rtl():
    # This filter is documented in wp-includes/general-template.php
    echo apply_filters( 'wp_admin_css', "<link rel='stylesheet' href='" . esc_url( wp_admin_css_uri( "file-rtl" ) ) . "' type='text/css' />\n", "file-rtl" )


def add_thickbox():
  ''' Enqueues the default ThickBox js and css.
  If any of the settings need to be changed, this can be done with another js
  file similar to media-upload.js. That file should
  require array('thickbox') to ensure it is loaded after.
  '''
  wp_enqueue_script( 'thickbox' )
  wp_enqueue_style( 'thickbox' )

  if is_network_admin():
    add_action( 'admin_head', '_thickbox_path_admin_subfolder' )


def wp_generator():
  ''' Displays the XHTML generator that is generated on the wp_head hook.
  See {@see 'wp_head'}.
  '''
  # Filters the output of the XHTML generator tag.
  # @param string generator_type The XHTML generator.
  the_generator( apply_filters( 'wp_generator_type', 'xhtml' ) )


def the_generator( Type ):
  ''' Display the generator XML or Comment for RSS, ATOM, etc.
  Returns the correct generator type for the requested output format. Allows
  for a plugin to filter generators overall the {@see 'the_generator'} filter.
  @param string Type The type of generator to output - (html|xhtml|atom|rss2|rdf|comment|export).
  '''
  # Filters the output of the XHTML generator tag for display.
  # @param string generator_type The generator output.
  # @param string Type           The type of generator to output. Accepts 'html',
  #                               'xhtml', 'atom', 'rss2', 'rdf', 'comment', 'export'.
  echo apply_filters( 'the_generator', get_the_generator(Type), Type ) . "\n"


def get_the_generator( Type = '' ):
  ''' Creates the generator XML or Comment for RSS, ATOM, etc.
  Returns the correct generator type for the requested output format. Allows
  for a plugin to filter generators on an individual basis using the
  {@see 'get_the_generator_'+ Type} filter.
  @param string Type The type of generator to return - (html|xhtml|atom|rss2|rdf|comment|export).
  @return string|void The HTML content for the generator.
  '''
  if Php.empty(locals(), 'Type' ):

    current_filter = current_filter()
    if Php.empty(locals(), 'current_filter' ):
      return

    # switch ( current_filter ) {
    if   current_filter in ('rss2_head', 'commentsrss2_head'):
      Type = 'rss2'
    elif current_filter in ('rss_head', 'opml_head'):
      Type = 'comment'
    elif current_filter == 'rdf_header':
      Type = 'rdf'
    elif current_filter in ('atom_head', 'comments_atom_head', 'app_head'):
      Type = 'atom'

  #switch ( Type ) {
  if   type == 'html':
    gen = '<meta name="generator" content="WordPress ' . get_bloginfo( 'version' ) . '">'
  elif Type == 'xhtml':
    gen = '<meta name="generator" content="WordPress ' . get_bloginfo( 'version' ) . '" />'
  elif Type == 'atom':
    gen = '<generator uri="https://wordpress.org/" version="' . get_bloginfo_rss( 'version' ) . '">WordPress</generator>'
  elif Type == 'rss2':
    gen = '<generator>https://wordpress.org/?v=' . get_bloginfo_rss( 'version' ) . '</generator>'
  elif Type == 'rdf':
    gen = '<admin:generatorAgent rdf:resource="https://wordpress.org/?v=' . get_bloginfo_rss( 'version' ) . '" />'
  elif Type == 'comment':
    gen = '<!-- generator="WordPress/' . get_bloginfo( 'version' ) . '" -.'
  elif Type == 'export':
    gen = '<!-- generator="WordPress/' . get_bloginfo_rss('version') . '" created="'. date('Y-m-d H:i') . '" -->'

  # Filters the HTML for the retrieved generator type.
  # The dynamic portion of the hook name, `Type`, refers to the generator type.
  # @param string gen  The HTML markup output to wp_head().
  # @param string Type The type of generator. Accepts 'html', 'xhtml', 'atom',
  #                     'rss2', 'rdf', 'comment', 'export'.
  return apply_filters( "get_the_generator_"+ Type, gen, Type )


def checked( checked, current = true, echo = true ):
  ''' Outputs the html checked attribute.
  Compares the first two arguments and if identical marks as checked
  @param mixed checked One of the values to compare
  @param mixed current (true) The other value to compare if not just true
  @param bool  echo    Whether to echo or just return the string
  @return string html attribute or empty string
  '''
  return __checked_selected_helper( checked, current, echo, 'checked' )


def selected( selected, current = true, echo = true ):
  ''' Outputs the html selected attribute.
  Compares the first two arguments and if identical marks as selected
  @param mixed selected One of the values to compare
  @param mixed current  (true) The other value to compare if not just true
  @param bool  echo     Whether to echo or just return the string
  @return string html attribute or empty string
  '''
  return __checked_selected_helper( selected, current, echo, 'selected' )


def disabled( disabled, current = true, echo = true ):
  ''' Outputs the html disabled attribute.
  Compares the first two arguments and if identical marks as disabled
  @param mixed disabled One of the values to compare
  @param mixed current  (true) The other value to compare if not just true
  @param bool  echo     Whether to echo or just return the string
  @return string html attribute or empty string
  '''
  return __checked_selected_helper( disabled, current, echo, 'disabled' )


def __checked_selected_helper( helper, current, echo, Type ):
  ''' Private helper function for checked, selected, and disabled.
  Compares the first two arguments and if identical marks as Type
  @access private
  @param mixed  helper  One of the values to compare
  @param mixed  current (true) The other value to compare if not just true
  @param bool   echo    Whether to echo or just return the string
  @param string Type    The type of checked|selected|disabled we are doing
  @return string html attribute or empty string
  '''
  if (string) helper === (string) current:
    result = " {}='{}'".format(Type, Type)
  else:
    result = ''

  if echo:
    echo result

  return result


def wp_heartbeat_settings( settings ):
  ''' Default settings for heartbeat
  Outputs the nonce used in the heartbeat XHR
  @param array settings
  @return array settings
  '''
  if ! is_admin():
    settings['ajaxurl'] = admin_url( 'admin-ajax.php', 'relative' )

  if is_user_logged_in():
    settings['nonce'] = wp_create_nonce( 'heartbeat-nonce' )

  return settings


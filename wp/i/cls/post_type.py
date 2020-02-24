import pyx.php     as Php
import wp.i.format as WiF
import wp.i.func   as WiFc
import wp.i.option as WiO
array = Php.array

''' Post API: WP_Post_Type class
@package WordPress  @subpackage Post
'''

#def InitPostTypesGlobals(self):
#  "global var==>self.var, except: var=self.var=same Obj,mutable array"
#  #global post_type_meta_caps, _wp_post_type_features, wp
#  #global wp_rewrite
#  #post_type_meta_caps   = self.post_type_meta_caps
#  #_wp_post_type_features= self._wp_post_type_features
#  #wp                    = self.wp
#  #wp_rewrite            = self.wp_rewrite
#  pass


class WP_Post_Type(Php.stdClass):
  ''' Core class used for interacting with post types.
  @see register_post_type()
  '''

  # Add Wj, since in wp.i.default_filters, WB.Wj was not initialized yet
  #def __init__(self, post_type, args = array()):
  def __init__( self, post_type, args = array(), Wj=None ):
    ''' Constructor.
    Will populate object properties from provided arguments and assign other
    default properties based on that information.
    @see register_post_type()
    @param string       post_type Post type key.
    @param array|string args     Optional. Array or string of arguments for
                                 registering a post type. Default empty array.
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    self.Wj = Wj
    #print("\n WP_Post_Type.init: post_type={}, args={}".format(post_type,args))
    # Post type key.
    # @var string name   @access public
    "self.name"
    # Name of the post type shown in the menu. Usually plural.
    # @var string label   @access public
    "self.label"
    # Labels object for this post type.
    # If not set, post labels are inherited for non-hierarchical types
    # and page labels for hierarchical ones. * @see get_post_type_labels()
    # @var object labels   @access public
    "self.labels"
    # A short descriptive summary of what the post type is.
    # Default empty.
    # @access public   @var string description
    self.description = ''
    # Whether a post type is intended for use publicly either via the admin interface or by front-end users.
    # While the default settings of exclude_from_search, publicly_queryable, show_ui, and show_in_nav_menus
    # are inherited from public, each does not rely on this relationship and controls a very specific intention.
    # Default False.
    # @access public   @var bool public
    self.public = False
    # Whether the post type is hierarchical (e.g. page).
    # Default False.
    # @var bool hierarchical   @access public
    self.hierarchical = False
    # Whether to exclude posts with this post type from front end search
    # results.
    # Default is the opposite value of public.
    # @var bool exclude_from_search * @access public
    self.exclude_from_search = None
    # Whether queries can be performed on the front end for the post type as part of `parse_request()`.
    # Endpoints would include:
    # - `?post_type={post_type_key}`
    # - `?{post_type_key}={single_post_slug}`
    # - `?{post_type_query_var}={single_post_slug}`
    # Default is the value of public.
    # @var bool publicly_queryable * @access public
    self.publicly_queryable = None
    # Whether to generate and allow a UI for managing this post type in the admin.
    # Default is the value of public.
    # @var bool show_ui   @access public
    self.show_ui = None
    # Where to show the post type in the admin menu.
    # To work, show_ui must be True. If True, the post type is shown in its own top level menu. If False, no menu is
    # shown. If a string of an existing top level menu (eg. 'tools.php' or 'edit.php?post_type=page'), the post type
    # will be placed as a sub-menu of that.
    # Default is the value of show_ui.
    # @var bool show_in_menu   @access public
    self.show_in_menu = None
    # Makes this post type available for selection in navigation menus.
    # Default is the value public.
    # @var bool show_in_nav_menus   @access public
    self.show_in_nav_menus = None
    # Makes this post type available via the admin bar.
    # Default is the value of show_in_menu.
    # @var bool show_in_admin_bar   @access public
    self.show_in_admin_bar = None
    # The position in the menu order the post type should appear.
    # To work, show_in_menu must be True. Default None (at the bottom).
    # @var int menu_position   @access public
    self.menu_position = None
    # The URL to the icon to be used for this menu.
    # Pass a base64-encoded SVG using a data URI, which will be colored to match the color scheme.
    # This should begin with 'data:image/svg+xml;base64,'. Pass the name of a Dashicons helper class
    # to use a font icon, e.g. 'dashicons-chart-pie'. Pass 'none' to leave div.wp-menu-image empty
    # so an icon can be added via CSS.
    # Defaults to use the posts icon.
    # @var string menu_icon   @access public
    self.menu_icon = None
    # The string to use to build the read, edit, and delete capabilities.
    # May be passed as an array to allow for alternative plurals when using
    # this argument as a base to construct the capabilities, e.g.
    # array( 'story', 'stories' ). Default 'post'.
    # @var string capability_type   @access public
    self.capability_type = 'post'
    # Whether to use the internal default meta capability handling.
    # Default False.
    # @var bool map_meta_cap   @access public
    self.map_meta_cap = False
    # Provide a callback function that sets up the meta boxes for the edit form.
    # Do `remove_meta_box()` and `add_meta_box()` calls in the callback. Default None.
    # @var string register_meta_box_cb   @access public
    self.register_meta_box_cb = None
    # An array of taxonomy identifiers that will be registered for the post type.
    # Taxonomies can be registered later with `register_taxonomy()` or `register_taxonomy_for_object_type()`.
    # Default empty array.
    # @var array taxonomies   @access public
    self.taxonomies = array()
    # Whether there should be post type archives, or if a string, the archive slug to use.
    # Will generate the proper rewrite rules if rewrite is enabled. Default False.
    # @var bool|string has_archive   @access public
    self.has_archive = False
    # Sets the query_var key for this post type.
    # Defaults to post_type key. If False, a post type cannot be loaded at `?{query_var}={post_slug}`.
    # If specified as a string, the query `?{query_var_string}={post_slug}` will be valid.
    # @var string|bool query_var   @access public
    "self.query_var"
    # Whether to allow this post type to be exported.
    # Default True.
    # @var bool can_export   @access public
    self.can_export = True
    # Whether to delete posts of this type when deleting a user.
    # If True, posts of this type belonging to the user will be moved to trash when then user is deleted.
    # If False, posts of this type belonging to the user will *not* be trashed or deleted.
    # If not set (the default), posts are trashed if post_type_supports( 'author' ).
    # Otherwise posts are not trashed or deleted. Default None.
    # @var bool delete_with_user   @access public
    self.delete_with_user = None
    # Whether this post type is a native or "built-in" post_type.
    # Default False.
    # @var bool _builtin   @access public
    self._builtin = False
    # URL segment to use for edit link of this post type.
    # Default 'post.php?post=%d'.
    # @var string _edit_link   @access public
    self._edit_link = 'post.php?post=%d'
    # Post type capabilities.
    # @var object cap   @access public
    "self.cap"
    # Triggers the handling of rewrites for this post type.
    # Defaults to True, using post_type as slug.
    # @var array|False rewrite   @access public
    "self.rewrite"
    # The features supported by the post type.
    # @var array|bool supports   @access public
    "self.supports"

    self.name = post_type
    self.set_props( args )


  def set_props(self, args):
    ''' Sets post type properties.
    @param array|str args arguments for registering a post type.
    '''
    import wp.i.post    as WpP
    args      = WiFc.wp_parse_args( args )

    # Filters the arguments for registering a post type.
    # @param array  args      Array of arguments for registering a post type.
    # @param string post_type Post type key.
    #args = apply_filters( 'register_post_type_args', args, self.name )

    #has_edit_link = bool( args['_edit_link']) #err: '_edit_link' not in args!
    #has_edit_link = bool( args.get('_edit_link', None) )
    has_edit_link  = not Php.empty( args, '_edit_link' )

    # Args prefixed with an underscore are reserved for internal use.
    defaults = array(
      ('labels'              , array()),
      ('description'         , ''),
      ('public'              , False),
      ('hierarchical'        , False),
      ('exclude_from_search' , None),
      ('publicly_queryable'  , None),
      ('show_ui'             , None),
      ('show_in_menu'        , None),
      ('show_in_nav_menus'   , None),
      ('show_in_admin_bar'   , None),
      ('menu_position'       , None),
      ('menu_icon'           , None),
      ('capability_type'     , 'post'),
      ('capabilities'        , array()),
      ('map_meta_cap'        , None),
      ('supports'            , array()),
      ('register_meta_box_cb', None),
      ('taxonomies'          , array()),
      ('has_archive'         , False),
      ('rewrite'             , True),
      ('query_var'           , True),
      ('can_export'          , True),
      ('delete_with_user'    , None),
      ('_builtin'            , False),
      ('_edit_link'          , 'post.php?post=%d'),
    )

    args = Php.array_merge( defaults, args )
    args['name'] = self.name

    # If not set, default to the setting for public.
    if None == args['publicly_queryable']:
      args['publicly_queryable'] = args['public']

    # If not set, default to the setting for public.
    if None == args['show_ui']:
      args['show_ui'] = args['public']

    # If not set, default to the setting for show_ui.
    if None == args['show_in_menu'] or not args['show_ui']:
      args['show_in_menu'] = args['show_ui']

    # If not set, default to the whether the full UI is shown.
    if None == args['show_in_admin_bar']:
      args['show_in_admin_bar'] = bool(args['show_in_menu'])

    # If not set, default to the setting for public.
    if None == args['show_in_nav_menus']:
      args['show_in_nav_menus'] = args['public']

    # If not set, default to True if public, False if publi:
    if None == args['exclude_from_search']:
      args['exclude_from_search'] = not args['public']

    # Back compat with quirky handling in version 3.0. #14122.
    if (Php.empty( args, 'capabilities' ) and None is args['map_meta_cap'] and
            Php.in_array(args['capability_type'], array( 'post', 'page' ) )):
      args['map_meta_cap'] = True

    # If not set, default to False.
    if None == args['map_meta_cap']:
      args['map_meta_cap'] = False

    # If there's no specified edit link and no UI, remove the edit link.
    if not args['show_ui'] and not has_edit_link:
      args['_edit_link'] = ''

    #args['cap']=WpP.get_post_type_capabilities(Php.Object(args))
    args['cap']= WpP.get_post_type_capabilities(Php.Object(args), Wj=self.Wj)
    del args['capabilities']

    if Php.is_array( args['capability_type'] ):
      args['capability_type'] = args['capability_type'][0]

    if False != args['query_var']:
      if True == args['query_var']:
        args['query_var'] = self.name
      else:
        args['query_var'] = WiF.sanitize_title_with_dashes( args['query_var'] )

    if False != args['rewrite'] and (
         self.Wj.is_admin() or '' != WiO.get_option( 'permalink_structure' ) ):
      if  not Php.is_array( args['rewrite'] ):
        args['rewrite'] = array()
      if Php.empty( args['rewrite'], 'slug' ):
        args['rewrite']['slug'] = self.name
      if not Php.isset( args['rewrite'], 'with_front' ):
        args['rewrite']['with_front'] = True
      if not Php.isset( args['rewrite'], 'pages' ):
        args['rewrite']['pages'] = True
      if not Php.isset( args['rewrite'], 'feeds' ) or not args['has_archive']:
        args['rewrite']['feeds'] = bool(args['has_archive'])
      if not Php.isset( args['rewrite'], 'ep_mask' ):
        if Php.isset( args, 'permalink_epmask' ):
          args['rewrite']['ep_mask'] = args['permalink_epmask']
        else:
          args['rewrite']['ep_mask'] = EP_PERMALINK

    for property_name, property_value in args.items():
      setattr(self, property_name, property_value)

    self.labels = WpP.get_post_type_labels( self )
    #print('\n VT self.lables =', self.labels, type(self.labels))

    self.label  = self.labels.name


  def add_supports(self):
    ''' Sets the features support for the post type.
    '''
    import wp.i.post    as WpP
    if not Php.empty(self, 'supports'):
      #WpP.add_post_type_support(self.name, self.supports )
      WpP.add_post_type_support( self.name, self.supports , Wj=self.Wj)
      del self.supports
    elif False != self.supports:
      # Add default features
      #WpP.add_post_type_support(self.name, array('title','editor') )
      WpP.add_post_type_support( self.name, array('title','editor'), Wj=self.Wj)


  def add_rewrite_rules(self):
    ''' Adds the necessary rewrite rules for the post type.
    @global WP_Rewrite wp_rewrite WordPress Rewrite Component.
    @global WP         wp         Current WordPress environment instance.
    '''
    wp_rewrite = self.Wj.wp_rewrite  # global wp_rewrite
    wp = self.Wj.wp  # global wp
    if False != self.query_var and wp and is_post_type_viewable( self ):
      wp.add_query_var( self.query_var )

    if ( False != self.rewrite and ( self.Wj.is_admin() or
         '' != WiO.get_option( 'permalink_structure' ) ) ):

      if self.hierarchical:
        add_rewrite_tag( "%"+ self.name +"%", '(.+?)'  , self.query_var +"="
                 if self.query_var else "post_type="+ self.name +"&pagename=" )
      else:
        add_rewrite_tag( "%"+ self.name +"%", '([^/]+)', self.query_var +"="
                 if self.query_var else "post_type="+ self.name +"&name=" )

      if self.has_archive:
        archive_slug = self.rewrite['slug'] if self.has_archive == True else \
                       self.has_archive
        if self.rewrite['with_front']:
          archive_slug = substr( wp_rewrite.front, 1 ) + archive_slug
        else:
          archive_slug = wp_rewrite.root + archive_slug

        add_rewrite_rule( archive_slug +"/?$", "index.php?post_type="+ self.name, 'top' )
        if self.rewrite['feeds'] and wp_rewrite.feeds:
          feeds = '(' + trim( implode( '|', wp_rewrite.feeds ) ) + ')'
          add_rewrite_rule( archive_slug +"/feed/"+ feeds +"/?$", "index.php?post_type=" + self.name +'&feed=$matches[1]', 'top' )
          add_rewrite_rule( archive_slug +"/"+ feeds +"/?$", "index.php?post_type="+ self.name +'&feed=$matches[1]', 'top' )

        if self.rewrite['pages']:
          add_rewrite_rule( archive_slug +"/"+ wp_rewrite.pagination_base +"/([0-9]{1,})/?$", "index.php?post_type="+ self.name +'&paged=$matches[1]', 'top' )

      permastruct_args         = self.rewrite
      permastruct_args['feed'] = permastruct_args['feeds']
      add_permastruct( self.name, self.rewrite['slug'] +"/%"+ self.name +"%", permastruct_args )


  def register_meta_boxes(self):
    "Registers the post type meta box if a custom callback was specified."
    pass
    #if self.register_meta_box_cb:
    #  add_action('add_meta_boxes_'+self.name, self.register_meta_box_cb, 10,1)

  def add_hooks(self):
    " Adds the future post hook action for the post type. "
    pass
    #add_action( 'future_' + self.name, '_future_post_hook', 5, 2 )

  def register_taxonomies(self):
    " Registers the taxonomies for the post type. "
    for taxonomy in self.taxonomies:
      register_taxonomy_for_object_type( taxonomy, self.name )

  def remove_supports(self):
    ''' Removes the features support for the post type.
    @global array _wp_post_type_features Post type features.
    '''
    # global _wp_post_type_features
    _wp_post_type_features = self.Wj._wp_post_type_features
    del _wp_post_type_features[ self.name ]


  def remove_rewrite_rules(self):
    ''' Removes any rewrite rules, permastructs, and rules for the post type.
    @global WP_Rewrite wp_rewrite          WordPress rewrite component.
    @global WP         wp                  Current WordPress environment instance.
    @global array      post_type_meta_caps Used to remove meta capabilities.
    '''
    wp = self.Wj.wp  # global wp
    post_type_meta_caps = self.Wj.post_type_meta_caps # global post_type_meta_caps
    wp_rewrite = self.Wj.wp_rewrite  # global wp_rewrite

    # Remove query var.
    if False != self.query_var:
      wp.remove_query_var( self.query_var )

    # Remove any rewrite rules, permastructs, and rules.
    if False != self.rewrite:
      remove_rewrite_tag( "%"+ self.name +"%" )
      remove_permastruct( self.name )
      for regex, query in wp_rewrite.extra_rules_top.items():
        if False != strpos( query, "index.php?post_type="+ self.name ):
          del wp_rewrite.extra_rules_top[ regex ]

    # Remove registered custom meta capabilities.
    for cap in self.cap:
      del post_type_meta_caps[ cap ]


  def unregister_meta_boxes(self):
    " Unregisters the post type meta box if a custom callback was specified."
    if self.register_meta_box_cb:
      remove_action( 'add_meta_boxes_' + self.name, self.register_meta_box_cb, 10 )

  def unregister_taxonomies(self):
    " Removes the post type from all taxonomies. "
    for taxonomy in get_object_taxonomies( self.name ):
      unregister_taxonomy_for_object_type( taxonomy, self.name )

  def remove_hooks(self):
    " Removes the future post hook action for the post type. "
    remove_action( 'future_' + self.name, '_future_post_hook', 5 )


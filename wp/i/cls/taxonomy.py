import pyx.php     as Php
import wp.i.format as WiF
import wp.i.func   as WiFc
import wp.i.option as WiO
import wp.i.plugin as WiPg
array = Php.array
# wp = WcTx.wp  = self.wp   # init in WiTx
# Wj = WcTx.Wj  = self      # init in WiTx

# Taxonomy API: WP_Taxonomy class
# @package WordPress
# @subpackage Taxonomy
# @since 4.7.0


class WP_Taxonomy(Php.stdClass):
  " Core class used for interacting with taxonomies. "
  " Added to inherit (Php.stdClass) to class WP_Taxonomy: "
  # Add Wj, since in wp.i.default_filters, WB.Wj was not initialized yet
  #def __init__(self, taxonomy, object_type, args = array() ):
  def __init__( self, taxonomy, object_type, args = array(), Wj=None ):
    ''' Constructor.
    @access public
    @global WP wp WP instance.
    @param string    taxonomy    Taxonomy key, must not exceed 32 characters.
    @param array|str object_type Name of the object type for the taxonomy obj
    @param array|str args        Optional. Array or query string of arguments
                              for registering a taxonomy. Default empty array.
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    self.Wj = Wj

    # Taxonomy key.
    # @access public @var string
    #self.name

    # Name of the taxonomy shown in the menu. Usually plural.
    # @access public @var string
    #self.label

    # An array of labels for this taxonomy.
    # @access public @var object
    self.labels = array()

    # A short descriptive summary of what the taxonomy is for.
    # @access public @var string
    self.description = ''

    # Whether a taxonomy is intended for use publicly either via the admin
    #   interface or by front-end users.
    # @access public @var bool
    self.public = True

    # Whether the taxonomy is publicly queryable.
    # @access public @var bool
    self.publicly_queryable = True

    # Whether the taxonomy is hierarchical.
    # @access public @var bool
    self.hierarchical = False

    # Whether to generate and allow a UI for managing terms in this taxonomy
    #   in the admin.
    # @access public @var bool
    self.show_ui = True

    # Whether to show the taxonomy in the admin menu.
    # If True, the taxonomy is shown as a submenu of the object type menu.
    # If False, no menu is shown.
    # @access public @var bool
    self.show_in_menu = True

    # Whether the taxonomy is available for selection in navigation menus.
    # @access public @var bool
    self.show_in_nav_menus = True

    # Whether to list the taxonomy in the tag cloud widget controls.
    # @access public @var bool
    self.show_tagcloud = True

    # Whether to show the taxonomy in the quick/bulk edit panel.
    # @access public @var bool
    self.show_in_quick_edit = True

    # Whether to display a column for the taxonomy on its post type listing
    #   screens.
    # @access public @var bool
    self.show_admin_column = False

    # The callback function for the meta box display.
    # @access public @var bool|callable
    self.meta_box_cb = None

    # An array of object types this taxonomy is registered for.
    # @access public @var array
    self.object_type = None

    # Capabilities for this taxonomy.
    # @access public @var array
    #self.cap

    # Rewrites information for this taxonomy.
    # @access public @var array|False
    #self.rewrite

    # Query var string for this taxonomy.
    # @access public @var string|False
    #self.query_var

    # Function that will be called when the count is updated.
    # @access public @var callable
    #self.update_count_callback

    # Whether it is a built-in taxonomy.
    # @access public @var bool
    #self._builtin

    self.name = taxonomy
    self.set_props( object_type, args )


  def set_props( self, object_type, args ):
    ''' Sets taxonomy properties.
    @access public
    @param array|str object_type Name of the object type for the taxonomy obj
    @param array|str args        Array or query string of arguments for
                                 registering a taxonomy.
    '''
    Wj = self.Wj
    import wp.i.taxonomy as WiTx
    args = WiFc.wp_parse_args( args )

    # Filters the arguments for registering a taxonomy.
    # @param array args        Array of arguments for registering a taxonomy.
    # @param str   taxonomy    Taxonomy key.
    # @param array object_type Array of names of object types for the taxonomy
    args = WiPg.apply_filters( 'register_taxonomy_args', args, self.name,
                               Php.Array(object_type), Wj=self.Wj )

    defaults = array(
      ('labels'               , array()),
      ('description'          , ''),
      ('public'               , True),
      ('publicly_queryable'   , None),
      ('hierarchical'         , False),
      ('show_ui'              , None),
      ('show_in_menu'         , None),
      ('show_in_nav_menus'    , None),
      ('show_tagcloud'        , None),
      ('show_in_quick_edit'   , None),
      ('show_admin_column'    , False),
      ('meta_box_cb'          , None),
      ('capabilities'         , array()),
      ('rewrite'              , True),
      ('query_var'            , self.name),
      ('update_count_callback', ''),
      ('_builtin'             , False),
    )

    args = Php.array_merge( defaults, args )

    # If not set, default to the setting for public.
    if None is args['publicly_queryable']:
      args['publicly_queryable'] = args['public']

    if False is not args['query_var'] and (
                  Wj.is_admin() or False is not args['publicly_queryable'] ):
      if True is args['query_var']:
        args['query_var'] = self.name
      else:
        args['query_var'] = WiF.sanitize_title_with_dashes( args['query_var'])
    else:
      # Force query_var to False for non-public taxonomies.
      args['query_var'] = False

    if False is not args['rewrite'] and (
            Wj.is_admin() or '' != WiO.get_option( 'permalink_structure' ) ):
      args['rewrite'] = WiFc.wp_parse_args( args['rewrite'], array(
        ('with_front'  , True),
        ('hierarchical', False),
        ('ep_mask'     , 'EP_NONE'),
      ) )

      if Php.empty( args['rewrite'], 'slug' ):
        args['rewrite']['slug'] = WiF.sanitize_title_with_dashes( self.name )

    # If not set, default to the setting for public.
    if None is args['show_ui']:
      args['show_ui'] = args['public']

    # If not set, default to the setting for show_ui.
    if None is args['show_in_menu'] or not args['show_ui']:
      args['show_in_menu'] = args['show_ui']

    # If not set, default to the setting for public.
    if None is args['show_in_nav_menus']:
      args['show_in_nav_menus'] = args['public']

    # If not set, default to the setting for show_ui.
    if None is args['show_tagcloud']:
      args['show_tagcloud'] = args['show_ui']

    # If not set, default to the setting for show_ui.
    if None is args['show_in_quick_edit']:
      args['show_in_quick_edit'] = args['show_ui']

    default_caps = array(
      ('manage_terms', 'manage_categories'),
      ('edit_terms'  , 'manage_categories'),
      ('delete_terms', 'manage_categories'),
      ('assign_terms', 'edit_posts'       ),
    )

    args['cap'] = Php.Object(
                      Php.array_merge( default_caps, args['capabilities'] ))
    Php.unset( args, 'capabilities' )

    args['object_type'] = Php.array_unique( Php.Array(object_type) )

    # If not set, use the default meta box
    if None is args['meta_box_cb']:
      if args['hierarchical']:
        args['meta_box_cb'] = 'post_categories_meta_box'
      else:
        args['meta_box_cb'] = 'post_tags_meta_box'

    for property_name, property_value in args.items():
      setattr(self, property_name, property_value)

    self.labels = WiTx.get_taxonomy_labels( self )  # pass self.Wj
    self.label = self.labels.name


  def add_rewrite_rules(self):
    ''' Adds the necessary rewrite rules for the taxonomy.
    @access public
    @global WP wp Current WordPress environment instance.
    '''
    # @var WP wp
    wp = self.Wj.wp  # global wp

    # Non-publicly queryable taxonomies should not register query vars,
    #    except in the admin.
    if False is not self.query_var and wp:
      wp.add_query_var( self.query_var )

    if False is not self.rewrite and (
             self.Wj.is_admin() or '' != WiO.get_option( 'permalink_structure' ) ):
      if self.hierarchical and self.rewrite['hierarchical']:
        tag = '(.+?)'
      else:
        tag = '([^/]+)'

      add_rewrite_tag( "%{}%".format(self.name), tag, self.query_var + "="
                if self.query_var else "taxonomy={}&term=".format(self.name) )
      add_permastruct( self.name, "{}/%{}%".format(self.rewrite['slug'],
                self.name), self.rewrite )


  def remove_rewrite_rules(self):
    ''' Removes any rewrite rules, permastructs, and rules for the taxonomy.
    @access public
    @global WP wp Current WordPress environment instance.
    '''
    # @var WP wp
    wp = self.Wj.wp  # global wp

    # Remove query var.
    if False is not self.query_var:
      wp.remove_query_var( self.query_var )

    # Remove rewrite tags and permastructs.
    if False is not self.rewrite:
      remove_rewrite_tag( "%{}%".format(self.name) )
      remove_permastruct( self.name )


  def add_hooks(self):
    ''' Registers the ajax callback for the meta box.
    @access public
    '''
    WiPg.add_filter( 'wp_ajax_add-' + self.name,
                     '_wp_ajax_add_hierarchical_term', Wj=self.Wj )


  def remove_hooks(self):
    ''' Removes the ajax callback for the meta box.
    @access public
    '''
    WiPg.remove_filter( 'wp_ajax_add-' + self.name,
                        '_wp_ajax_add_hierarchical_term' )


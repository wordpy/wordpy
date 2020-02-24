# Fixed all &value pass by reference

import pyx.php     as Php
import wp.conf     as WpC
import wp.i.cls.error       as WcE  # WP_Error
import wp.i.cls.meta_query  as WcMQ
import wp.i.cls.taxonomy    as WcTx
import wp.i.cls.term        as WcT
import wp.i.cls.term_query  as WcTQ
import wp.i.cache  as WiCa
import wp.i.format as WiF
import wp.i.func   as WiFc
import wp.i.l10n   as WiTr
import wp.i.meta   as WiM
import wp.i.option as WiO
import wp.i.plugin as WiPg
import wp.i.wpdb   as WpDb
array = Php.array

#wpdb set in Web.WpBlogCls
#    for Module in (WpT, WiM, WiU, WiO, WpTx):
#      Module.wpdb = self.Wj.wpdb

# Core Taxonomy API
# @package WordPress  @subpackage Taxonomy
# Taxonomy Registration
#   PyMySQL convert all obj including int to formatted and quoted string. 
#     use only %s or %(name)s as placeholder.  Don't use %d.

#def InitTaxonomyGlobals(self):
#  "global var==>self.var, except: var=self.var=same Obj,mutable array"
#  #global wp_taxonomies, Wj, wp, wp_rewrite
#  #if not Php.is_array( wp_taxonomies ):
#  if not Php.is_array(getattr(self, 'wp_taxonomies', None)):
#    self.wp_taxonomies = array()
#  #wp_taxonomies = self.wp_taxonomies
#  #wp_rewrite    = self.wp_rewrite
#  #wp = WcTx.wp  = self.wp
#  #Wj = WcTx.Wj  = self


__, _x, _n_noop = WiTr.__, WiTr._x, WiTr._n_noop

#def apply_filters(tag, *values):
#  return values[0]

def current_theme_supports( Format ):
  return {'post-formats': True}.get(Format, False)


#def create_initial_taxonomies():
def  create_initial_taxonomies(self):
  ''' Creates the initial taxonomies.
  This function fires twice: in wp-settings.php before plugins are loaded (for
  backward compatibility reasons), and again on the {@see 'init'} action. We must
  avoid registering rewrite rules before the {@see 'init'} action.
  @global WP_Rewrite wp_rewrite The WordPress rewrite class.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wp_rewrite = self.wp_rewrite   #= WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  #if not WiPg.did_action( 'init' ):
  if not WiPg.did_action( 'init', Wj=self ):
    rewrite = array(('category'   , False),
                    ('post_tag'   , False),
                    ('post_format', False),)
  else:
    # Filters the post formats rewrite base.
    # @param string context Context of the rewrite base. Default 'type'.
    post_format_base = WiPg.apply_filters( 'post_format_rewrite_base', 'type')
    rewrite = array(
      ('category', array(
        ('hierarchical', True),
        ('slug', WiO.get_option('category_base') \
                 if WiO.get_option('category_base') else 'category'),
        ('with_front', not WiO.get_option('category_base') or \
                       wp_rewrite.using_index_permalinks()),
        ('ep_mask', EP_CATEGORIES),
      )),
      ('post_tag', array(
        ('hierarchical', False),
        ('slug', WiO.get_option('tag_base') \
                 if WiO.get_option('tag_base') else 'tag'),
        ('with_front', not WiO.get_option('tag_base') or \
                       wp_rewrite.using_index_permalinks()),
        ('ep_mask', EP_TAGS),
      )),
      ('post_format', array(('slug',post_format_base))
                             if post_format_base else False),
    )

  register_taxonomy( 'category', 'post', array(
    ('hierarchical', True),
    ('query_var', 'category_name'),
    ('rewrite', rewrite['category']),
    ('public', True),
    ('show_ui', True),
    ('show_admin_column', True),
    ('_builtin', True),
    ('capabilities', array(
      ('manage_terms', 'manage_categories'),
      ('edit_terms'  , 'edit_categories'),
      ('delete_terms', 'delete_categories'),
      ('assign_terms', 'assign_categories'),
    )),
    ('show_in_rest', True),
    ('rest_base', 'categories'),
    ('rest_controller_class', 'WP_REST_Terms_Controller'),
  ), Wj=self )  # Added Wj=self

  register_taxonomy( 'post_tag', 'post', array(
    ('hierarchical', False),
    ('query_var', 'tag'),
    ('rewrite', rewrite['post_tag']),
    ('public', True),
    ('show_ui', True),
    ('show_admin_column', True),
    ('_builtin', True),
    ('capabilities', array(
      ('manage_terms', 'manage_post_tags'),
      ('edit_terms'  , 'edit_post_tags'),
      ('delete_terms', 'delete_post_tags'),
      ('assign_terms', 'assign_post_tags'),
    )),
    ('show_in_rest', True),
    ('rest_base', 'tags'),
    ('rest_controller_class', 'WP_REST_Terms_Controller'),
  ), Wj=self )  # Added Wj=self

  register_taxonomy( 'nav_menu', 'nav_menu_item', array(
    ('public', False),
    ('hierarchical', False),
    ('labels', array(
      ('name', __( 'Navigation Menus' )),
      ('singular_name', __( 'Navigation Menu' )),
    )),
    ('query_var', False),
    ('rewrite', False),
    ('show_ui', False),
    ('_builtin', True),
    ('show_in_nav_menus', False),
  ), Wj=self )  # Added Wj=self

  register_taxonomy( 'link_category', 'link', array(
    ('hierarchical', False),
    ('labels', array(
      ('name', __( 'Link Categories' )),
      ('singular_name', __( 'Link Category' )),
      ('search_items', __( 'Search Link Categories' )),
      ('popular_items', None),
      ('all_items', __( 'All Link Categories' )),
      ('edit_item', __( 'Edit Link Category' )),
      ('update_item', __( 'Update Link Category' )),
      ('add_new_item', __( 'Add New Link Category' )),
      ('new_item_name', __( 'New Link Category Name' )),
      ('separate_items_with_commas', None),
      ('add_or_remove_items', None),
      ('choose_from_most_used', None),
    )),
    ('capabilities', array(
      ('manage_terms', 'manage_links'),
      ('edit_terms'  , 'manage_links'),
      ('delete_terms', 'manage_links'),
      ('assign_terms', 'manage_links'),
    )),
    ('query_var', False),
    ('rewrite', False),
    ('public', False),
    ('show_ui', True),
    ('_builtin', True),
  ), Wj=self )  # Added Wj=self

  register_taxonomy( 'post_format', 'post', array(
    ('public', True),
    ('hierarchical', False),
    ('labels', array(
      ('name', _x( 'Format', 'post format' )),
      ('singular_name', _x( 'Format', 'post format' )),
    )),
    ('query_var', True),
    ('rewrite', rewrite['post_format']),
    ('show_ui', False),
    ('_builtin', True),
    ('show_in_nav_menus', current_theme_supports( 'post-formats' )),
  ), Wj=self )  # Added Wj=self


def get_taxonomies( args = array(), output = 'names', operator = 'and' ):
  ''' Retrieves a list of registered taxonomy names or objects.
  @global array  wp_taxonomies The registered taxonomies.
  @param array  args     Optional. An array of `key : value` arguments to match against the taxonomy objects.
                          Default empty array.
  @param string output   Optional. The type of output to return in the array. Accepts either taxonomy 'names'
                          or 'objects'. Default 'names'.
  @param string operator Optional. The logical operation to perform. Accepts 'and' or 'or'. 'or' means only
                          one element from the array needs to match; 'and' means all elements must match.
                          Default 'and'.
  @return array A list of taxonomy names or objects.
  '''
  wp_taxonomies = WpC.WB.Wj.wp_taxonomies  # global wp_taxonomies
  field = 'name' if 'names' == output else False
  return WiFc.wp_filter_object_list(wp_taxonomies, args, operator, field)


def get_object_taxonomies( Obj, output = 'names' ):
  ''' Return the names or objects of the taxonomies which are registered for
  the requested object or object type, such as a post object or post type name
      Example: taxonomies = get_object_taxonomies( 'post' )
      results: Array( 'category', 'post_tag' )
  @global array  wp_taxonomies The registered taxonomies.
  @param array|string|WP_Post object Name of the type of taxonomy object,
                              or an object (row from posts)
  @param str output Optional. type of output to return in the array. Accepts
                        either taxonomy 'names' or 'objects'. Default 'names'.
  NOTE: All calling functions implies output= 'name', except output= 'objects'
        in wp-includes/class-wp-xmlrpc-server.php.
  @return array The names of all taxonomy of object_type.
  '''
  wp_taxonomies = WpC.WB.Wj.wp_taxonomies  # global wp_taxonomies
  if Php.is_object(Obj):
    if Obj.post_type == 'attachment':
      return get_attachment_taxonomies(Obj, output)
    Obj = Obj.post_type

  Obj = Php.Array( Obj )

  taxonomies = array()

  for tax_name, tax_obj in Php.Array(wp_taxonomies).items():
    if Php.array_intersect(Obj, Php.Array( tax_obj.object_type )):
      if 'names' == output:
        taxonomies[None] = tax_name
      else:
        taxonomies[ tax_name ] = tax_obj

  return taxonomies

def get_taxonomy( taxonomy ):
  ''' Retrieves the taxonomy object of taxonomy.
  The get_taxonomy function will first check that the parameter string given
  is a taxonomy object and if it is, it will return it.
  @global array  wp_taxonomies The registered taxonomies.
  @param string taxonomy Name of taxonomy object to return.
  @return WP_Taxonomy|False The Taxonomy Object or False if taxonomy doesn't exist.
  '''
  wp_taxonomies = WpC.WB.Wj.wp_taxonomies  # global wp_taxonomies
  if not taxonomy_exists( taxonomy ):
    return False
  return wp_taxonomies[taxonomy]


def taxonomy_exists( taxonomy ):
  ''' Checks that the taxonomy name exists.
  Formerly is_taxonomy(), introduced in 2.3.0.
  @global array  wp_taxonomies The registered taxonomies.
  @param string taxonomy Name of taxonomy object.
  @return bool Whether the taxonomy exists.
  '''
  wp_taxonomies = WpC.WB.Wj.wp_taxonomies  # global wp_taxonomies
  return Php.isset(wp_taxonomies, taxonomy)


def is_taxonomy_hierarchical(taxonomy):
  ''' Whether the taxonomy object is hierarchical.
  Checks to make sure that the taxonomy is an object first. Then Gets the
  object, and finally returns the hierarchical value in the object.
  A False return value might also mean that the taxonomy does not exist.
  @param string taxonomy Name of taxonomy object.
  @return bool Whether the taxonomy is hierarchical.
  '''
  if not taxonomy_exists(taxonomy):
    return False

  taxonomy = get_taxonomy(taxonomy)
  return taxonomy.hierarchical


# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
#def register_taxonomy(taxonomy, object_type, args = array() ):
def register_taxonomy( taxonomy, object_type, args = array(), Wj=None ):
  ''' Creates or modifies a taxonomy object.
  Note: Do not use before the {@see 'init'} hook.
  A simple function for creating or modifying a taxonomy object based on the
  parameters given. The function will accept an array (third optional
  parameter), along with strings for the taxonomy name and another string for
  the object type.
  @since 4.2.0 Introduced `show_in_quick_edit` argument.
  @since 4.4.0 The `show_ui` argument is now enforced on the term editing screen.
  @since 4.4.0 The `public` argument now controls whether the taxonomy can be queried on the front end.
  @since 4.5.0 Introduced `publicly_queryable` argument.
  @since 4.7.0 Introduced `show_in_rest`, 'rest_base' and 'rest_controller_class'
               arguments to register the Taxonomy in REST API.
  @global array  wp_taxonomies Registered taxonomies.
  @global WP    wp            WP instance.
  @param string       taxonomy    Taxonomy key, must not exceed 32 characters.
  @param array|string object_type Object type or array of object types with which the taxonomy should be associated.
  @param array|string args        {
    Optional. Array or query string of arguments for registering a taxonomy.
  @type array         labels                An array of labels for this taxonomy. By default, Tag labels are
                                             used for non-hierarchical taxonomies, and Category labels are used
                                             for hierarchical taxonomies. See accepted values in
                                             get_taxonomy_labels(). Default empty array.
    @type string        description           A short descriptive summary of what the taxonomy is for. Default empty.
    @type bool          public                Whether a taxonomy is intended for use publicly either via
                                               the admin interface or by front-end users. The default settings
                                               of `publicly_queryable`, `show_ui`, and `show_in_nav_menus`
                                               are inherited from `public`.
    @type bool          publicly_queryable    Whether the taxonomy is publicly queryable.
                                               If not set, the default is inherited from `public`
    @type bool          hierarchical          Whether the taxonomy is hierarchical. Default False.
    @type bool          show_ui               Whether to generate and allow a UI for managing terms in this taxonomy in
                                               the admin. If not set, the default is inherited from `public`
                                               (default True).
    @type bool          show_in_menu          Whether to show the taxonomy in the admin menu. If True, the taxonomy is
                                               shown as a submenu of the object type menu. If False, no menu is shown.
                                               `show_ui` must be True. If not set, default is inherited from `show_ui`
                                               (default True).
    @type bool          show_in_nav_menus     Makes this taxonomy available for selection in navigation menus. If not
                                               set, the default is inherited from `public` (default True).
    @type bool          show_in_rest          Whether to include the taxonomy in the REST API.
    @type string        rest_base             To change the base url of REST API route. Default is $taxonomy.
    @type string        rest_controller_class REST API Controller class name. Default is 'WP_REST_Terms_Controller'.
    @type bool          show_tagcloud         Whether to list the taxonomy in the Tag Cloud Widget controls. If not set,
                                               the default is inherited from `show_ui` (default True).
    @type bool          show_in_quick_edit    Whether to show the taxonomy in the quick/bulk edit panel. It not set,
                                               the default is inherited from `show_ui` (default True).
    @type bool          show_admin_column     Whether to display a column for the taxonomy on its post type listing
                                               screens. Default False.
    @type bool|callable meta_box_cb           Provide a callback function for the meta box display. If not set,
                                               post_categories_meta_box() is used for hierarchical taxonomies, and
                                               post_tags_meta_box() is used for non-hierarchical. If False, no meta
                                               box is shown.
    @type array         capabilities {
        Array of capabilities for this taxonomy.
  
        @type string manage_terms Default 'manage_categories'.
        @type string edit_terms   Default 'manage_categories'.
        @type string delete_terms Default 'manage_categories'.
        @type string assign_terms Default 'edit_posts'.
    }
    @type bool|array    rewrite {
        Triggers the handling of rewrites for this taxonomy. Default True, using taxonomy as slug. To prevent
        rewrite, set to False. To specify rewrite rules, an array can be passed with any of these keys:
  
        @type string slug         Customize the permastruct slug. Default `taxonomy` key.
        @type bool   with_front   Should the permastruct be prepended with WP_Rewrite::front. Default True.
        @type bool   hierarchical Either hierarchical rewrite tag or not. Default False.
        @type int    ep_mask      Assign an endpoint mask. Default `EP_NONE`.
    }
    @type string        query_var    Sets the query var key for this taxonomy. Default `taxonomy` key. If
                                      False, a taxonomy cannot be loaded at `?{query_var}={term_slug}`. If a
                                      string, the query `?{query_var}={term_slug}` will be valid.
    @type callable      update_count_Works much like a hook, in that it will be called when the count is
                                      updated. Default _update_post_term_count() for taxonomies attached
                                      to post types, which confirms that the objects are published before
                                      counting them. Default _update_generic_term_count() for taxonomies
                                      attached to other object types, such as users.
    @type bool          _builtin     This taxonomy is a "built-in" taxonomy. INTERNAL USE ONLY!
                                      Default False.
  }
  @return WP_Error|void WP_Error, if errors.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_taxonomies = Wj.wp_taxonomies  # global wp_taxonomies

  # Move to the top
  #if not Php.is_array( wp_taxonomies ):
  #  wp_taxonomies = array()

  args = WiFc.wp_parse_args( args )

  if Php.empty( taxonomy ) or Php.strlen( taxonomy ) > 32:
    WiFc._doing_it_wrong( register_taxonomy.__name__,    # __FUNCTION__,
         __( 'Taxonomy names must be between 1 and 32 characters in length.' ),
            '4.2.0' )
    return WcE.WP_Error( 'taxonomy_length_invalid', __(
            'Taxonomy names must be between 1 and 32 characters in length.' ) )
  
  #taxonomy_object = WcTx.WP_Taxonomy(taxonomy, object_type, args )
  taxonomy_object = WcTx.WP_Taxonomy( taxonomy, object_type, args, Wj=Wj )
  taxonomy_object.add_rewrite_rules()
  
  wp_taxonomies[ taxonomy ] = taxonomy_object
  
  taxonomy_object.add_hooks()

  #### Comment out old wp.4.6.1 below: ###
  ## Filters the arguments for registering a taxonomy.
  ## @param array  args        Array of arguments for registering a taxonomy.
  ## @param string taxonomy    Taxonomy key.
  ## @param array  object_type Array of names of object types for the taxonomy.
  #args = WiPg.apply_filters( 'register_taxonomy_args', args, taxonomy,
  #                            Php.Array( object_type ))

  #defaults = array(
  #  ('labels'               , array()  ),
  #  ('description'          , ''       ),
  #  ('public'               , True     ),
  #  ('publicly_queryable'   , None     ),
  #  ('hierarchical'         , False    ),
  #  ('show_ui'              , None     ),
  #  ('show_in_menu'         , None     ),
  #  ('show_in_nav_menus'    , None     ),
  #  ('show_tagcloud'        , None     ),
  #  ('show_in_quick_edit'   , None     ),
  #  ('show_admin_column'    , False    ),
  #  ('meta_box_cb'          , None     ),
  #  ('capabilities'         , array()  ),
  #  ('rewrite'              , True     ),
  #  ('query_var'            , taxonomy ),
  #  ('update_count_callback', ''       ),
  #  ('_builtin'             , False    ),
  #)
  #args = Php.array_merge( defaults, args )

  #if not taxonomy or len( taxonomy ) > 32:    # if empty( taxonomy ) or ...
  #  #WiFc._doing_it_wrong( register_taxonomy.__name__,    # __FUNCTION__,
  #      __( 'Taxonomy names must be between 1 and 32 characters in length.' ),
  #         '4.2.0' )
  #  print( register_taxonomy, __( 'Taxonomy names must be between 1 and 32 characters in length.' ), '4.2.0' )
  #  return WcE.WP_Error( 'taxonomy_length_invalid', __( 'Taxonomy names must be between 1 and 32 characters in length.' ) )

  ## If not set, default to the setting for public.
  #if None == args['publicly_queryable']:
  #  args['publicly_queryable'] = args['public']

  ## Non-publicly queryable taxonomies should not register query vars, except in the admin.
  ##if ( false !== $args['query_var'] && ( is_admin() || false !== $args['publicly_queryable'] ) && ! empty( $wp ) ) {
  #if False != args['query_var'] and ( Wj.is_admin() or False != args['publicly_queryable'] ) and not Php.empty({**globals(), **locals()}, 'wp'): #getattr(Wj, 'wp', None):
  #  if True == args['query_var']:
  #    args['query_var'] = taxonomy
  #  else:
  #    args['query_var'] = WiF.sanitize_title_with_dashes( args['query_var'] )
  #  #wp.add_query_var( args['query_var'] )
  #  Wj.wp.add_query_var( args['query_var'] )
  #else:
  #  # Force query_var to False for non-public taxonomies.
  #  args['query_var'] = False

  #if False != args['rewrite'] and ( Wj.is_admin() or \
  #      '' != WiO.get_option( 'permalink_structure' ) ):
  #  args['rewrite'] = WiFc.wp_parse_args( args['rewrite'], array(
  #    ('with_front', True),
  #    ('hierarchical', False),
  #    ('ep_mask', 'EP_NONE'),
  #  ) )

  #  if Php.empty( args['rewrite'], 'slug'):
  #    args['rewrite']['slug'] = WiF.sanitize_title_with_dashes( taxonomy )

  #  if args['hierarchical'] and args['rewrite']['hierarchical']:
  #    tag = '(.+?)'
  #  else:
  #    tag = '([^/]+)'

  #  add_rewrite_tag( "%"+ taxonomy +"%", tag, args['query_var'] +"="  if args['query_var'] else "taxonomy="+ taxonomy +"&term=" )
  #  add_permastruct( taxonomy, args['rewrite']['slug'] +"/%"+ taxonomy +"%", args['rewrite'] )

  ## If not set, default to the setting for public.
  #if None == args['show_ui']:
  #  args['show_ui'] = args['public']

  ## If not set, default to the setting for show_ui.
  #if None == args['show_in_menu' ] or not args['show_ui']:
  #  args['show_in_menu' ] = args['show_ui']

  ## If not set, default to the setting for public.
  #if None == args['show_in_nav_menus']:
  #  args['show_in_nav_menus'] = args['public']

  ## If not set, default to the setting for show_ui.
  #if None == args['show_tagcloud']:
  #  args['show_tagcloud'] = args['show_ui']

  ## If not set, default to the setting for show_ui.
  #if None == args['show_in_quick_edit']:
  #  args['show_in_quick_edit'] = args['show_ui']

  #default_caps = array(
  #  ('manage_terms', 'manage_categories'),
  #  ('edit_terms'  , 'manage_categories'),
  #  ('delete_terms', 'manage_categories'),
  #  ('assign_terms', 'edit_posts'       ),
  #)
  #args['cap'] = Php.Object(Php.array_merge(default_caps, args['capabilities']))
  #del args['capabilities']

  #args['name'] = taxonomy
  #args['object_type'] = Php.array_unique( Php.Array( object_type ))

  #args['labels'] = get_taxonomy_labels( Php.Object( args ))
  #args['label'] = args['labels'].name
  #print("WiT.register_taxonomy : args['label'] =", args['label'],)

  ## If not set, use the default meta box
  #if None == args['meta_box_cb']:
  #  if args['hierarchical']:
  #    args['meta_box_cb'] = 'post_categories_meta_box'
  #  else:
  #    args['meta_box_cb'] = 'post_tags_meta_box'

  ##wp_taxonomies[ taxonomy ]= (object) args
  #wp_taxonomies[ taxonomy ] = Php.Object(args)  #= Php.Object(args)

  ## Register callback handling for meta box.
  ##add_filter( 'wp_ajax_add-' + taxonomy, '_wp_ajax_add_hierarchical_term' )

  # Fires after a taxonomy is registered.
  # @param string       taxonomy    Taxonomy slug.
  # @param array|string object_type Object type or array of object types.
  # @param array        args        Array of taxonomy registration arguments.
  WiPg.do_action( 'registered_taxonomy', taxonomy, object_type,
                  Php.Array(taxonomy_object), Wj=Wj )  #Added Wj=Wj


def unregister_taxonomy( taxonomy ):
  ''' Unregisters a taxonomy.
  Can not be used to unregister built-in taxonomies.
  @global WP    wp            Current WordPress environment instance.
  @global array  wp_taxonomies List of taxonomies.
  @param string taxonomy Taxonomy name.
  @return bool|WP_Error True on success, WP_Error on failure or if the taxonomy doesn't exist.
  '''
  if not taxonomy_exists( taxonomy ):
    return WcE.WP_Error( 'invalid_taxonomy', __( 'Invalid taxonomy.' ) )

  #taxonomy_args = get_taxonomy( taxonomy )
  taxonomy_object = get_taxonomy( taxonomy )

  # Do not allow unregistering internal taxonomies.
  #if taxonomy_args._builtin:
  if taxonomy_object._builtin:
    return WcE.WP_Error( 'invalid_taxonomy', __( 'Unregistering a built-in taxonomy is not allowed' ) )

  wp = WpC.WB.Wj.wp  # global wp
  wp_taxonomies = WpC.WB.Wj.wp_taxonomies  # global wp_taxonomies

  ## Remove query var.
  #if False != taxonomy_args.query_var:
  #  wp.remove_query_var( taxonomy_args.query_var )
  ## Remove rewrite tags and permastructs.
  #if False != taxonomy_args.rewrite:
  #  remove_rewrite_tag( "%taxonomy%" )
  #  remove_permastruct( taxonomy )
  ## Unregister callback handling for meta box.
  #remove_filter( 'wp_ajax_add-' + taxonomy, '_wp_ajax_add_hierarchical_term' )

  taxonomy_object.remove_rewrite_rules()
  taxonomy_object.remove_hooks()

  # Remove the taxonomy.
  Php.unset(wp_taxonomies, taxonomy )

  # Fires after a taxonomy is unregistered.
  # @param string taxonomy Taxonomy name.
  WiPg.do_action( 'unregistered_taxonomy', taxonomy )

  return True


def get_taxonomy_labels( tax ):
  ''' Builds an object with all taxonomy labels out of a taxonomy object
  Accepted keys of the label array in the taxonomy object:
  - name - general name for the taxonomy, usually plural. The same as and overridden by tax.label. Default is Tags/Categories
  - singular_name - name for one object of this taxonomy. Default is Tag/Category
  - search_items - Default is Search Tags/Search Categories
  - popular_items - This string isn't used on hierarchical taxonomies. Default is Popular Tags
  - all_items - Default is All Tags/All Categories
  - parent_item - This string isn't used on non-hierarchical taxonomies. In hierarchical ones the default is Parent Category
  - parent_item_colon - The same as `parent_item`, but with colon `:` in the end
  - edit_item - Default is Edit Tag/Edit Category
  - view_item - Default is View Tag/View Category
  - update_item - Default is Update Tag/Update Category
  - add_new_item - Default is Add New Tag/Add New Category
  - new_item_name - Default is New Tag Name/New Category Name
  - separate_items_with_commas - This string isn't used on hierarchical taxonomies. Default is "Separate tags with commas", used in the meta box.
  - add_or_remove_items - This string isn't used on hierarchical taxonomies. Default is "Add or remove tags", used in the meta box when JavaScript is disabled.
  - choose_from_most_used - This string isn't used on hierarchical taxonomies. Default is "Choose from the most used tags", used in the meta box.
  - not_found - Default is "No tags found"/"No categories found", used in the meta box and taxonomy list table.
  - no_terms - Default is "No tags"/"No categories", used in the posts and media list tables.
  - items_list_navigation - String for the table pagination hidden heading.
  - items_list - String for the table hidden heading.
  
  Above, the first default value is for non-hierarchical taxonomies (like tags) and the second one is for hierarchical taxonomies (like categories).
  @todo Better documentation for the labels array.
  @since 4.3.0 Added the `no_terms` label.
  @since 4.4.0 Added the `items_list_navigation` and `items_list` labels.
  @param WP_Taxonomy tax Taxonomy object.
  @return object object with all the labels as member variables.
  '''
  import wp.i.post as WiP
  tax.labels = Php.Array( tax.labels )

  if Php.isset(tax, 'helps'
              ) and Php.empty(tax.labels, 'separate_items_with_commas'):
    tax.labels['separate_items_with_commas'] = tax.helps
  if Php.isset(tax, 'no_tagcloud' ) and Php.empty(tax.labels, 'not_found'):
    tax.labels['not_found'] = tax.no_tagcloud

  nohier_vs_hier_defaults = array(
    ('name', array( _x( 'Tags', 'taxonomy general name' ),
                _x( 'Categories', 'taxonomy general name' ) )),
    ('singular_name', array( _x( 'Tag', 'taxonomy singular name' ),
                         _x( 'Category', 'taxonomy singular name' ) )),
    ('search_items', array( __( 'Search Tags' ), __( 'Search Categories' ) )),
    ('popular_items', array( __( 'Popular Tags' ), None )),
    ('all_items', array( __( 'All Tags' ), __( 'All Categories' ) )),
    ('parent_item', array( None, __( 'Parent Category' ) )),
    ('parent_item_colon', array( None, __( 'Parent Category:' ) )),
    ('edit_item', array( __( 'Edit Tag' ), __( 'Edit Category' ) )),
    ('view_item', array( __( 'View Tag' ), __( 'View Category' ) )),
    ('update_item', array( __( 'Update Tag' ), __( 'Update Category' ) )),
    ('add_new_item', array( __( 'Add New Tag' ), __( 'Add New Category' ) )),
    ('new_item_name', array( __( 'New Tag Name' ), __( 'New Category Name' ) )),
    ('separate_items_with_commas', array( __( 'Separate tags with commas' ),None)),
    ('add_or_remove_items', array( __( 'Add or remove tags' ), None )),
    ('choose_from_most_used', array( __( 'Choose from the most used tags' ),None)),
    ('not_found', array( __( 'No tags found.' ), __( 'No categories found.' ) )),
    ('no_terms', array( __( 'No tags' ), __( 'No categories' ) )),
    ('items_list_navigation', array( __( 'Tags list navigation' ),
                                __( 'Categories list navigation' ) )),
    ('items_list', array( __( 'Tags list' ), __( 'Categories list' ) )),
  )
  nohier_vs_hier_defaults['menu_name'] = nohier_vs_hier_defaults['name']

  labels = WiP._get_custom_object_labels( tax, nohier_vs_hier_defaults )
  # print("WiT labels=", labels)

  taxonomy = tax.name
  default_labels = Php.clone(labels)
  #print("WiT default_labels=", default_labels)

  # Filters the labels of a specific taxonomy.
  # dynamic portion of the hook name, `taxonomy`, refers to the taxonomy slug.
  # @see get_taxonomy_labels() for the full list of taxonomy labels.
  # @param object labels Object with labels for the taxonomy as member var.
  #labels= WiPg.apply_filters( "taxonomy_labels_"+ taxonomy, labels) #Added Wj
  labels = WiPg.apply_filters( "taxonomy_labels_"+ taxonomy, labels, Wj=tax.Wj )

  # Ensure that the filtered labels contain all required default values.
  labels = Php.Object( Php.array_merge( Php.Array(default_labels), Php.Array( labels )))
  #print("WiT Object labels=", labels)

  return labels


def register_taxonomy_for_object_type( taxonomy, object_type):
  ''' Add an already registered taxonomy to an object type.
  @global array  wp_taxonomies The registered taxonomies.
  @param string taxonomy    Name of taxonomy object.
  @param string object_type Name of the object type.
  @return bool True if successful, False if not.
  '''
  wp_taxonomies = WpC.WB.Wj.wp_taxonomies  # global wp_taxonomies

  if not Php.isset(wp_taxonomies, taxonomy):
    return False

  if not get_post_type_object(object_type):
    return False

  if object_type not in wp_taxonomies[taxonomy].object_type:
    wp_taxonomies[taxonomy].object_type[None] = object_type

  # Filters out empties.
  wp_taxonomies[ taxonomy ].object_type = \
        Php.array_filter( wp_taxonomies[ taxonomy ].object_type )

  return True


def unregister_taxonomy_for_object_type( taxonomy, object_type ):
  ''' Remove an already registered taxonomy from an object type.
  @global array  wp_taxonomies The registered taxonomies.
  @param string taxonomy    Name of taxonomy object.
  @param string object_type Name of the object type.
  @return bool True if successful, False if not.
  '''
  wp_taxonomies = WpC.WB.Wj.wp_taxonomies  # global wp_taxonomies

  if not Php.isset(wp_taxonomies, taxonomy):
    return False

  if not get_post_type_object( object_type ):
    return False

  key = Php.array_search( object_type, wp_taxonomies[ taxonomy ].object_type, True )
  if False == key:
    return False

  del wp_taxonomies[ taxonomy ].object_type[ key ]
  return True


#
# Term API
#

def get_objects_in_term( term_ids, taxonomies, args = array() ):
  ''' Retrieve object_ids of valid taxonomy and term.
  The strings of taxonomies must exist before this function will continue. On
  failure of finding a valid taxonomy, it will return an WP_Error class, kind
  of like Exceptions in PHP 5, except you can't catch them. Even so, you can
  still test for the WP_Error class and get the error message.
  The terms aren't checked the same as taxonomies, but still need to exist
  for object_ids to be returned.
  It is possible to change the order that object_ids is returned by either
  using PHP sort family functions or using the database by using args with
  either ASC or DESC array. The value should be in the key named 'order'.
  @global wpdb wpdb WordPress database abstraction object.
  @param int|array    term_ids   Term id or array of term ids of terms that will be used.
  @param string|array taxonomies String of taxonomy name or Array of string values of taxonomy names.
  @param array|string args       Change the order of the object_ids, either ASC or DESC.
  @return WP_Error|array If the taxonomy does not exist, then WP_Error will be returned. On success.
   the array can be empty meaning that there are no object_ids found or it will return the object_ids found.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if not Php.is_array( term_ids):
    term_ids = array( term_ids )
  if not Php.is_array( taxonomies):
    taxonomies = array( taxonomies )
  for taxonomy in Php.Array(taxonomies):
    if not taxonomy_exists( taxonomy ):
      return WcE.WP_Error( 'invalid_taxonomy', __( 'Invalid taxonomy.' ) )

  defaults = array(( 'order', 'ASC'),)
  args = WiFc.wp_parse_args( args, defaults )

  order = 'DESC' if 'desc' == args['order'].lower() else 'ASC'

  term_ids = Php.array_map(Php.intval, term_ids )

  taxonomies = "'"+ Php.implode( "', '", Php.array_map( WiF.esc_sql, taxonomies ) )+ "'"
  term_ids = "'"+ Php.implode( "', '", term_ids )+ "'"

  object_ids = wpdb.get_col("SELECT tr.object_id FROM {} AS tr "
      "INNER JOIN {} AS tt ON tr.term_taxonomy_id = tt.term_taxonomy_id WHERE "
      "tt.taxonomy IN ({}) AND tt.term_id IN ({}) ORDER BY tr.object_id {}"
      .format(wpdb.term_relationships, wpdb.term_taxonomy,
              taxonomies, term_ids, order))

  if not object_id:
    return array()
  return object_ids


def get_tax_sql( tax_query, primary_table, primary_id_column ):
  ''' Given a taxonomy query, generates SQL to be appended to a main query.
  @see WP_Tax_Query
  @param array  tax_query         A compact tax query
  @param string primary_table
  @param string primary_id_column
  @return array
  '''
  tax_query_obj = WP_Tax_Query( tax_query )
  return tax_query_obj.get_sql( primary_table, primary_id_column )


def get_term( term, taxonomy = '', output = WpDb.OBJECT, filter = 'raw' ):
  ''' Get all Term data from database by Term ID.
  The usage of the get_term function is to apply filters to a term object. It
  is possible to get a term object from the database before applying the
  filters.
  term ID must be part of taxonomy, to get from the database. Failure, might
  be able to be captured by the hooks. Failure would be the same value as wpdb
  returns for the get_row method.
  There are two hooks, one is specifically for each term, named 'get_term', and
  the second is for the taxonomy name, 'term_$taxonomy'. Both hooks gets the
  term object, and the taxonomy name as parameters. Both hooks are expected to
  return a Term object.
  {@see 'get_term'} hook - Takes two parameters the term Object and the taxonomy name.
  Must return term object. Used in get_term() as a catch-all filter for every
  term.
  {@see 'get_$taxonomy'} hook - Takes two parameters the term Object and the taxonomy
  name. Must return term object. taxonomy will be the taxonomy name, so for
  example, if 'category', it would be 'get_category' as the filter name. Useful
  for custom taxonomies or plugging into default taxonomies.
  @global wpdb wpdb WordPress database abstraction object.
  @see sanitize_term_field() The context param lists the available values for get_term_by() filter param.
  @param int|WP_Term|object term If integer, term data will be fetched from the database, or from the cache if
                                  available. If stdClass object (as in the results of a database query), will apply
                                  filters and return a `WP_Term` object corresponding to the `term` data. If `WP_Term`,
                                  will return `term`.
  @param string     taxonomy Optional. Taxonomy name that term is part of.
  @param string     output   Optional. The required return type. One of OBJECT, ARRAY_A, or ARRAY_N, which correspond to
                             a WP_Term object, an associative array, or a numeric array, respectively. Default OBJECT.
  @param string     filter   Optional, default is raw or no WordPress defined filter will applied.
  @return array|WP_Term|WP_Error|None Object of the type specified by `output` on success. When `output` is 'OBJECT',
                                      a WP_Term instance is returned. If taxonomy does not exist, a WP_Error is
                                      returned. Returns None for miscellaneous failure.
  '''
  if not term:  # if empty( term ):
    return WcE.WP_Error( 'invalid_term', __( 'Empty Term' ) )

  if taxonomy and not taxonomy_exists( taxonomy ):
    return WcE.WP_Error( 'invalid_taxonomy', __( 'Invalid taxonomy.' ) )

  if isinstance(term, WcT.WP_Term):
    _term = term
  elif Php.is_object( term ):
    if Php.empty(term, 'filter') or 'raw' == term.filter:
      _term = sanitize_term( term, taxonomy, 'raw' )
      _term = WcT.WP_Term( _term )
    else:
      _term = WcT.WP_Term.get_instance( term.term_id )
  else:
    _term = WcT.WP_Term.get_instance( term, taxonomy )

  if WpC.WB.Wj.is_wp_error( _term ):
    return _term
  elif not _term:
    return None

  # Filters a term.
  # @param int|WP_Term _term    Term object or ID.
  # @param string      taxonomy The taxonomy slug.
  _term = WiPg.apply_filters( 'get_term', _term, taxonomy )

  # Filters a taxonomy.
  # The dynamic portion of the filter name, `taxonomy`, refers
  # to the taxonomy slug.
  # @param int|WP_Term _term    Term object or ID.
  # @param string      taxonomy The taxonomy slug.
  _term = WiPg.apply_filters( "get_"+ taxonomy, _term, taxonomy )

  # Bail if a filter callback has changed the type of the `_term` object.
  if not isinstance(_term, WcT.WP_Term ):
    return _term

  # Sanitize term, according to the specified filter.
  _term.filter( filter )

  if output == WpDb.ARRAY_A:
    return _term.to_array()
  elif output == WpDb.ARRAY_N:
    return Php.array_values( _term.to_array() )

  return _term


def get_term_by( field, value, taxonomy = '', output = WpDb.OBJECT, filter = 'raw' ):
  '''
  Get all Term data from database by Term field and data.
  Warning: value is not escaped for 'name' field. You must do it yourself, if
  required.
  The default field is 'id', therefore it is possible to also use None for
  field, but not recommended that you do so.
  If value does not exist, the return value will be False. If taxonomy exists
  and field and value combinations exist, the Term will be returned.
  This function will always return the first term that matches the `$field`-
  `$value`-`$taxonomy` combination specified in the parameters. If your query
  is likely to match more than one term (as is likely to be the case when
  `field` is 'name', for example), consider using get_terms() instead; that
  way, you will get all matching terms, and can provide your own logic for
  deciding which one was intended.
  @todo Better formatting for DocBlock.
  @since 4.4.0 `taxonomy` is optional if `field` is 'term_taxonomy_id'. Converted to return
               a WP_Term object if `output` is `OBJECT`.
  @global wpdb wpdb WordPress database abstraction object.
  @see sanitize_term_field() The context param lists the available values for get_term_by() filter param.
  @param string     field    Either 'slug', 'name', 'id' (term_id), or 'term_taxonomy_id'
  @param string|int value    Search for this term value
  @param string     taxonomy Taxonomy name. Optional, if `field` is 'term_taxonomy_id'.
  @param string     output   Optional. The required return type. One of OBJECT, ARRAY_A, or ARRAY_N, which correspond to
                             a WP_Term object, an associative array, or a numeric array, respectively. Default OBJECT.
  @param string     filter   Optional, default is raw or no WordPress defined filter will applied.
  @return WP_Term|array|false WP_Term instance (or array) on success. Will return false if `$taxonomy` does not exist
                             or `term` was not found.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  # 'term_taxonomy_id' lookups don't require taxonomy checks.
  if 'term_taxonomy_id' != field and not taxonomy_exists( taxonomy ):
    return False

  tax_clause = wpdb.prepare( "AND tt.taxonomy = %s", taxonomy )

  if 'slug' == field:
    _field = 't.slug'
    value = WiF.sanitize_title(value)
    if not value:  # if empty(value):
      return False
  elif 'name' == field:
    # Assume already escaped
    value = WiF.wp_unslash(value)
    _field = 't.name'
  elif 'term_taxonomy_id' == field:
    value = int(value)
    _field = 'tt.term_taxonomy_id'

    # No `taxonomy` clause when searching by 'term_taxonomy_id'.
    tax_clause = ''
  else:
    term = get_term( int(value), taxonomy, output, filter )
    if WpC.WB.Wj.is_wp_error( term ) or Php.is_null( term ):
      term = False
    return term

  term = wpdb.get_row( wpdb.prepare( "SELECT t.*, tt.* FROM {} AS t "
         " INNER JOIN {} AS tt ON t.term_id = tt.term_id WHERE {} = %s"
         .format(wpdb.terms, wpdb.term_taxonomy, _field), value )
         + " {} LIMIT 1".format( tax_clause) )
  if not term:
    return False
  print("wpdb.get_term_by term=", term)
  print("wpdb.get_term_by term.term_id=", term.term_id)

  # In the case of 'term_taxonomy_id', override the provided `taxonomy` with whatever we find in the db.
  if 'term_taxonomy_id' == field:
    taxonomy = term.taxonomy

  WiCa.wp_cache_add( term.term_id, term, 'terms' )

  return get_term( term, taxonomy, output, filter )


def get_term_children( term_id, taxonomy ):
  ''' Merge all term children into a single array of their IDs.
  This recursive function will merge all of the children of term into the same
  array of term IDs. Only useful for taxonomies which are hierarchical.
  Will return an empty array if term does not exist in taxonomy.
  @param string term_id  ID of Term to get children.
  @param string taxonomy Taxonomy Name.
  @return array|WP_Error List of Term IDs. WP_Error returned if `taxonomy` does not exist.
  '''
  if not taxonomy_exists(taxonomy):
    return WcE.WP_Error('invalid_taxonomy', __('Invalid taxonomy.'))

  term_id = int( term_id )

  terms = _get_term_hierarchy(taxonomy)

  if not Php.isset(terms, term_id):
    return array()

  children = terms[term_id]

  for child in Php.Array( terms[term_id] ):
    if term_id == child:
      continue

    if Php.isset(terms, child):
      children = Php.array_merge(children, get_term_children(child, taxonomy))

  return children


def get_term_field( field, term, taxonomy = '', context = 'display' ):
  ''' Get sanitized Term field.
  The function is for contextual reasons and for simplicity of usage.
  @see sanitize_term_field()
  @param string      field    Term field to fetch.
  @param int|WP_Term term     Term ID or object.
  @param string      taxonomy Optional. Taxonomy Name. Default empty.
  @param string      context  Optional, default is display. Look at sanitize_term_field() for available options.
  @return string|int|None|WP_Error Will return an empty string if term is not an object or if field is not set in term.
  '''
  term = get_term( term, taxonomy )
  if WpC.WB.Wj.is_wp_error(term):
    return term

  if not Php.is_object(term):
    return ''

  if not Php.isset(term, field):
    return ''

  return sanitize_term_field( field, getattr(term, field),
                              term.term_id, term.taxonomy, context )


def get_term_to_edit( Id, taxonomy ):
  ''' Sanitizes Term for editing.
  Return value is sanitize_term() and usage is for sanitizing the term for
  editing. Function is for contextual and simplicity.
  @param int|object id       Term ID or object.
  @param string     taxonomy Taxonomy name.
  @return string|int|None|WP_Error Will return empty string if term is not an object.
  '''
  term = get_term( Id, taxonomy )

  if WpC.WB.Wj.is_wp_error(term):
    return term

  if not Php.is_object(term):
    return ''

  return sanitize_term(term, taxonomy, 'edit')


def get_terms( args = array(), deprecated = '' ):
  ''' Retrieve the terms in a given taxonomy or list of taxonomies.
  
  You can fully inject any customizations to the query before it is sent, as
  well as control the output with a filter.
  
  The {@see 'get_terms'} filter will be called when the cache has the term and will
  pass the found term along with the array of taxonomies and array of args.
  This filter is also called before the array of terms is passed and will pass
  the array of terms, along with the taxonomies and args.
  
  The {@see 'list_terms_exclusions'} filter passes the compiled exclusions along with
  the args.
  
  The {@see 'get_terms_orderby'} filter passes the `ORDER BY` clause for the query
  along with the args array.
  
  Since 4.5.0, taxonomies should be passed via the 'taxonomy' argument in the `args` array:
  
      terms = get_terms( array(
          ('taxonomy'  , 'post_tag'),
          ('hide_empty', False     ),
      ) )
  @since 4.2.0 Introduced 'name' and 'childless' parameters.
  @since 4.4.0 Introduced the ability to pass 'term_id' as an alias of 'id' for the `orderby` parameter.
               Introduced the 'meta_query' and 'update_term_meta_cache' parameters. Converted to return
               a list of WP_Term objects.
  @since 4.5.0 Changed the function signature so that the `args` array can be provided as the first parameter.
               Introduced 'meta_key' and 'meta_value' parameters. Introduced the ability to order results by metadata.
  
  @internal The `deprecated` parameter is parsed for backward compatibility only.
  
  @global wpdb  wpdb WordPress database abstraction object.
  @global array wp_filter
  
  @param array|string args {
      Optional. Array or string of arguments to get terms.
  
      @type string|array taxonomy               Taxonomy name, or array of taxonomies, to which results should
                                                 be limited.
      @type string       orderby                Field(s) to order terms by. Accepts term fields ('name', 'slug',
                                                 'term_group', 'term_id', 'id', 'description'), 'count' for term
                                                 taxonomy count, 'include' to match the 'order' of the include param,
                                                 'meta_value', 'meta_value_num', the value of `meta_key`, the array
                                                 keys of `meta_query`, or 'none' to omit the ORDER BY clause.
                                                 Defaults to 'name'.
      @type string       order                  Whether to order terms in ascending or descending order.
                                                 Accepts 'ASC' (ascending) or 'DESC' (descending).
                                                 Default 'ASC'.
      @type bool|int     hide_empty             Whether to hide terms not assigned to any posts. Accepts
                                                 1|True or 0|False. Default 1|True.
      @type array|string include                Array or comma/space-separated string of term ids to include.
                                                 Default empty array.
      @type array|string exclude                Array or comma/space-separated string of term ids to exclude.
                                                 If include is non-empty, exclude is ignored.
                                                 Default empty array.
      @type array|string exclude_tree           Array or comma/space-separated string of term ids to exclude
                                                 along with all of their descendant terms. If include is
                                                 non-empty, exclude_tree is ignored. Default empty array.
      @type int|string   number                 Maximum number of terms to return. Accepts ''|0 (all) or any
                                                 positive number. Default ''|0 (all).
      @type int          offset                 The number by which to offset the terms query. Default empty.
      @type string       fields                 Term fields to query for. Accepts 'all' (returns an array of complete
                                                 term objects), 'ids' (returns an array of ids), 'id:parent' (returns
                                                 an associative array with ids as keys, parent term IDs as values),
                                                 'names' (returns an array of term names), 'count' (returns the number
                                                 of matching terms), 'id:name' (returns an associative array with ids
                                                 as keys, term names as values), or 'id:slug' (returns an associative
                                                 array with ids as keys, term slugs as values). Default 'all'.
      @type string|array name                   Optional. Name or array of names to return term(s) for. Default empty.
      @type string|array slug                   Optional. Slug or array of slugs to return term(s) for. Default empty.
      @type bool         hierarchical           Whether to include terms that have non-empty descendants (even
                                                 if hide_empty is set to True). Default True.
      @type string       search                 Search criteria to match terms. Will be SQL-formatted with
                                                 wildcards before and after. Default empty.
      @type string       name__like             Retrieve terms with criteria by which a term is LIKE name__like.
                                                 Default empty.
      @type string       description__like      Retrieve terms where the description is LIKE description__like.
                                                 Default empty.
      @type bool         pad_counts             Whether to pad the quantity of a term's children in the quantity
                                                 of each term's "count" object variable. Default False.
      @type string       get                    Whether to return terms regardless of ancestry or whether the terms
                                                 are empty. Accepts 'all' or empty (disabled). Default empty.
      @type int          child_of               Term ID to retrieve child terms of. If multiple taxonomies
                                                 are passed, child_of is ignored. Default 0.
      @type int|string   parent                 Parent term ID to retrieve direct-child terms of. Default empty.
      @type bool         childless              True to limit results to terms that have no children. This parameter
                                                 has no effect on non-hierarchical taxonomies. Default False.
      @type string       cache_domain           Unique cache key to be produced when this query is stored in an
                                                 object cache. Default is 'core'.
      @type bool         update_term_meta_cache Whether to prime meta caches for matched terms. Default True.
      @type array        meta_query             Meta query clauses to limit retrieved terms by.
                                                 See `WP_Meta_Query`. Default empty.
      @type string       meta_key               Limit terms to those matching a specific metadata key. Can be used in
                                                 conjunction with `meta_value`.
      @type string       meta_value             Limit terms to those matching a specific metadata value. Usually used
                                                 in conjunction with `meta_key`.
  }
  @param array deprecated Argument array, when using the legacy function parameter format. If present, this
                           parameter will be interpreted as `args`, and the first function parameter will
                           be parsed as a taxonomy or array of taxonomies.
  @return array|int|WP_Error List of WP_Term instances and their children. Will return WP_Error, if any of taxonomies
                             do not exist.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  term_query = WcTQ.WP_Term_Query()

  # Legacy argument format (taxonomy, args) takes precedence.
  # We detect legacy argument format by checking if
  # (a) a second non-empty parameter is passed, or
  # (b) the first parameter shares no keys with the default array (ie, it's a list of taxonomies)
  _args = WiFc.wp_parse_args( args )
  key_intersect  = Php.array_intersect_key( term_query.query_var_defaults,
                                            Php.Array( _args ))
  do_legacy_args = deprecated or not key_intersect  #empty( key_intersect )

  if do_legacy_args:
    taxonomies = Php.Array( args )
    args = WiFc.wp_parse_args( deprecated )
    args['taxonomy'] = taxonomies
    print('WiT.get_terms do_legacy_args:', args)
  else:
    args = WiFc.wp_parse_args( args )
    if Php.isset(args, 'taxonomy') and None is not args['taxonomy']:
      args['taxonomy'] = Php.Array( args['taxonomy'] )
    print('WiT.get_terms not do_legacy_args:', args)

  if not Php.empty(args, 'taxonomy'):
    for taxonomy in args['taxonomy']:
      if not taxonomy_exists( taxonomy ):
        print('WiT.get_terms invalid_taxonomy:', taxonomy)
        return WcE.WP_Error( 'invalid_taxonomy', __( 'Invalid taxonomy.' ) )

  terms = term_query.query( args )

  # Count queries are not filtered, for legacy reasons.
  if not Php.is_array( terms ):
    return terms

  # Filters the found terms.
  # @param array         terms      Array of found terms.
  # @param array         taxonomies An array of taxonomies.
  # @param array         args       An array of get_terms() arguments.
  # @param WP_Term_Query term_query The WP_Term_Query object.
  return WiPg.apply_filters( 'get_terms', terms,
                             term_query.query_vars['taxonomy'], 
                             term_query.query_vars, term_query )


def add_term_meta( term_id, meta_key, meta_value, unique = False ):
  ''' Adds metadata to a term.
  @param int    term_id    Term ID.
  @param string meta_key   Metadata name.
  @param mixed  meta_value Metadata value.
  @param bool   unique     Optional. Whether to bail if an entry with the same key is found for the term.
                            Default False.
  @return int|WP_Error|bool Meta ID on success. WP_Error when term_id is ambiguous between taxonomies.
                            False on failure.
  '''
  # Bail if term meta table is not installed.
  if int( WiO.get_option( 'db_version' )) < 34370:
    return False

  if wp_term_is_shared( term_id ):
    return WcE.WP_Error( 'ambiguous_term_id', __( 'Term meta cannot be added to terms that are shared between taxonomies.'), term_id )

  added = add_metadata( 'term', term_id, meta_key, meta_value, unique )

  # Bust term query cache.
  if added:
    WiCa.wp_cache_set( 'last_changed', Php.microtime(), 'terms' )
  return added


def delete_term_meta( term_id, meta_key, meta_value = '' ):
  ''' Removes metadata matching criteria from a term.
  @param int    term_id    Term ID.
  @param string meta_key   Metadata name.
  @param mixed  meta_value Optional. Metadata value. If provided, rows will only be removed that match the value.
  @return bool True on success, False on failure.
  '''
  # Bail if term meta table is not installed.
  if int( WiO.get_option( 'db_version' )) < 34370:
    return False

  deleted = delete_metadata( 'term', term_id, meta_key, meta_value )

  # Bust term query cache.
  if deleted:
    WiCa.wp_cache_set( 'last_changed', Php.microtime(), 'terms' )

  return deleted


def get_term_meta( term_id, key = '', single = False ):
  ''' Retrieves metadata for a term.
  @param int    term_id Term ID.
  @param string key     Optional. The meta key to retrieve. If no key is provided, fetches all metadata for the term.
  @param bool   single  Whether to return a single value. If False, an array of all values matching the
                         `term_id`/`key` pair will be returned. Default: False.
  @return mixed If `single` is False, an array of metadata values. If `single` is True, a single metadata value.
  '''
  # Bail if term meta table is not installed.
  if int( WiO.get_option( 'db_version' )) < 34370:
    return False

  return get_metadata( 'term', term_id, key, single )


def update_term_meta( term_id, meta_key, meta_value, prev_value = '' ):
  ''' Updates term metadata.
  Use the `prev_value` parameter to differentiate between meta fields with the same key and term ID.
  If the meta field for the term does not exist, it will be added.
  @param int    term_id    Term ID.
  @param string meta_key   Metadata key.
  @param mixed  meta_value Metadata value.
  @param mixed  prev_value Optional. Previous value to check before removing.
  @return int|WP_Error|bool Meta ID if the key didn't previously exist. True on successful update.
                            WP_Error when term_id is ambiguous between taxonomies. False on failure.
  '''
  # Bail if term meta table is not installed.
  if int( WiO.get_option( 'db_version' )) < 34370:
    return False

  if wp_term_is_shared( term_id ):
    return WcE.WP_Error( 'ambiguous_term_id', __( 'Term meta cannot be added to terms that are shared between taxonomies.'), term_id )

  updated = update_metadata( 'term', term_id, meta_key, meta_value, prev_value )

  # Bust term query cache.
  if updated:
    WiCa.wp_cache_set( 'last_changed', Php.microtime(), 'terms' )

  return updated
#'''

def update_termmeta_cache( term_ids ):
  ''' Updates metadata cache for list of term IDs.
  Performs SQL query to retrieve all metadata for the terms matching `term_ids` and stores them in the cache.
  Subsequent calls to `get_term_meta()` will not need to query the database.
  @param array term_ids List of term IDs.
  @return array|False Returns False if there is nothing to update. Returns an array of metadata on success.
  '''
  # Bail if term meta table is not installed.
  if int( WiO.get_option( 'db_version' )) < 34370:
    return

  return WiM.update_meta_cache( 'term', term_ids )

#'''
def term_exists( term, taxonomy = '', parent = None ):
  ''' Check if Term exists.
  Formerly is_term(), introduced in 2.3.0.
  @global wpdb wpdb WordPress database abstraction object.
  @param int|string term     The term to check. Accepts term ID, slug, or name.
  @param string     taxonomy The taxonomy name to use
  @param int        parent   Optional. ID of parent term under which to confine the exists search.
  @return mixed Returns None if the term does not exist. Returns the term ID
                if no taxonomy is specified and the term ID exists. Returns
                an array of the term ID and the term taxonomy ID the taxonomy
                is specified and the pairing exists.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  select = "SELECT term_id FROM {} as t WHERE ".format(wpdb.terms)
  tax_select = ("SELECT tt.term_id, tt.term_taxonomy_id FROM {} AS t "
                "INNER JOIN {} as tt ON tt.term_id = t.term_id WHERE "
                .format(wpdb.terms, wpdb.term_taxonomy) )

  if Php.is_int(term):
    if 0 == term:
      return 0
    where = 't.term_id = %s'  # PyMySQL %d->%s
    if taxonomy:   # if not empty(taxonomy):
      return wpdb.get_row( wpdb.prepare( tax_select + where +
                      " AND tt.taxonomy = %s", term, taxonomy ), WpDb.ARRAY_A )
    else:
      return wpdb.get_var( wpdb.prepare( select + where, term ) )

  term = Php.trim( WiF.wp_unslash( term ) )
  slug = WiF.sanitize_title( term )

  where = 't.slug = %s'
  else_where = 't.name = %s'
  where_fields = array(slug)
  else_where_fields = array(term)
  orderby = 'ORDER BY t.term_id ASC'
  limit = 'LIMIT 1'
  if taxonomy:   # if not empty(taxonomy):
    if Php.is_numeric( parent ):
      parent = int(parent)
      where_fields[None] = parent
      else_where_fields[None] = parent
      where += ' AND tt.parent = %s'  # PyMySQL %d->%s
      else_where += ' AND tt.parent = %s'  # PyMySQL %d->%s

    where_fields[None] = taxonomy
    else_where_fields[None] = taxonomy

    result = wpdb.get_row( wpdb.prepare("SELECT tt.term_id, "
        "tt.term_taxonomy_id FROM {} AS t INNER JOIN {} as tt "
        "ON tt.term_id = t.term_id WHERE {} AND tt.taxonomy = %s {} "
        .format(wpdb.terms, wpdb.term_taxonomy, where, orderby, limit),
        where_fields), WpDb.ARRAY_A)
    if result:
      return result

    return wpdb.get_row( wpdb.prepare("SELECT tt.term_id, tt.term_taxonomy_id "
           "FROM {} AS t INNER JOIN {} as tt ON tt.term_id = t.term_id "
           "WHERE {} AND tt.taxonomy = %s {} {}"
           .format(wpdb.terms, wpdb.term_taxonomy, else_where, orderby, limit),
           else_where_fields), WpDb.ARRAY_A)

  result = wpdb.get_var( wpdb.prepare("SELECT term_id FROM {} as t WHERE "
           "{} {} {}".format(wpdb.terms, where, orderby, limit), where_fields))
  if result:
    return result

  return wpdb.get_var(wpdb.prepare("SELECT term_id FROM {} as t WHERE {} {} {}"
          .format(wpdb.terms, else_where, orderby, limit), else_where_fields) )


def term_is_ancestor_of( term1, term2, taxonomy ):
  ''' Check if a term is an ancestor of another term.
  You can use either an id or the term object for both parameters.
  @param int|object term1    ID or object to check if this is the parent term.
  @param int|object term2    The child term.
  @param string     taxonomy Taxonomy name that term1 and `term2` belong to.
  @return bool Whether `term2` is a child of `term1`.
  '''
  if not Php.isset(term1, 'term_id'):
    term1 = get_term( term1, taxonomy )
  if not Php.isset(term2, 'parent'):
    term2 = get_term( term2, taxonomy )

  if Php.empty(term1, 'term_id') or Php.empty(term2, 'parent'):
    return False
  if term2.parent == term1.term_id:
    return True

  return term_is_ancestor_of( term1, get_term( term2.parent, taxonomy ), taxonomy )
#'''

def sanitize_term(term, taxonomy, context = 'display'):
  ''' Sanitize Term all fields.
  Relies on sanitize_term_field() to sanitize the term. The difference is that
  this function will sanitize <strong>all</strong> fields. The context is based
  on sanitize_term_field().
  The term is expected to be either an array or an object.
  @param array|object term     The term to check.
  @param string       taxonomy The taxonomy name to use.
  @param string       context  Optional. Context in which to sanitize the term. Accepts 'edit', 'db',
                                'display', 'attribute', or 'js'. Default 'display'.
  @return array|object Term with all fields sanitized.
  '''
  fields = array( 'term_id', 'name', 'description', 'slug', 'count', 'parent', 'term_group', 'term_taxonomy_id', 'object_id' )

  do_object = Php.is_object( term )

  #term_id = do_object ? term->term_id : (isset(term['term_id']) ? term['term_id'] : 0)
  term_id = term.term_id if do_object else term.get('term_id', 0)

  for field in Php.Array( fields ):   #= .values():
    if do_object:
      if Php.isset(term, field):
        setattr(term, field, sanitize_term_field(field, getattr(term, field),
                term_id, taxonomy, context))
    else:
      if Php.isset(term, field):
        term[field] = sanitize_term_field(field, term[field], term_id,
                                          taxonomy, context)
  if do_object:
    term.filter = context
  else:
    term['filter'] = context

  return term


def sanitize_term_field(field, value, term_id, taxonomy, context):
  ''' Cleanse the field value in the term based on the context.
  Passing a term field value through the function should be assumed to have
  cleansed the value for whatever context the term field is going to be used.
  If no context or an unsupported context is given, then default filters will
  be applied.
  There are enough filters for each context to support a custom filtering
  without creating your own filter function. Simply create a function that
  hooks into the filter you need.
  @param string field    Term field to sanitize.
  @param string value    Search for this term value.
  @param int    term_id  Term ID.
  @param string taxonomy Taxonomy Name.
  @param string context  Context in which to sanitize the term field. Accepts
                          'edit', 'db', 'display', 'attribute', or 'js'.
  @return mixed Sanitized field.
  '''
  int_fields = ( 'parent', 'term_id', 'count', 'term_group', 'term_taxonomy_id', 'object_id' )
  if field in int_fields:   # if Php.in_array( field, int_fields):
    # py> int('') => ValueError: invalid literal for int() with base 10: ''
    #php> (int)'' => int(0)
    value = Php.intval(value)   # int(value)  #can't use py: int('')
    if value < 0:
      value = 0

  if 'raw' == context:
    return value

  if 'edit' == context:
    # Filters a term field to edit before it is sanitized.
    # The dynamic portion of the filter name, `field`, refers to term field.
    # @param mixed value     Value of the term field.
    # @param int   term_id   Term ID.
    # @param string taxonomy Taxonomy slug.
    value = WiPg.apply_filters( "edit_term_"+ field, value, term_id, taxonomy )

    # Filters the taxonomy field to edit before it is sanitized.
    # The dynamic portions of the filter name, `taxonomy` and `field`, refer
    # to the taxonomy slug and taxonomy field, respectively.
    # @param mixed value   Value of the taxonomy field to edit.
    # @param int   term_id Term ID.
    value = WiPg.apply_filters( "edit_"+ taxonomy +"_"+ field, value, term_id )

    if 'description' == field:
      value = esc_html(value); # textarea_escaped
    else:
      value = esc_attr(value)

  elif 'db' == context:
    # Filters a term field value before it is sanitized.
    # The dynamic portion of the filter name, `field`, refers to term field.
    # @param mixed  value    Value of the term field.
    # @param string taxonomy Taxonomy slug.
    value = WiPg.apply_filters( "pre_term_"+ field, value, taxonomy )

    # Filters a taxonomy field before it is sanitized.
    # The dynamic portions of the filter name, `taxonomy` and `field`, refer
    # to the taxonomy slug and field name, respectively.
    # @param mixed value Value of the taxonomy field.
    value = WiPg.apply_filters( "pre_"+ taxonomy +"_"+ field, value )

    # Back compat filters
    if 'slug' == field:
      # Filters the category nicename before it is sanitized.
      # Use the {@see 'pre_$taxonomy_$field'} hook instead.
      # @param string value The category nicename.
      value = WiPg.apply_filters( 'pre_category_nicename', value )

  elif 'rss' == context:
    # Filters the term field for use in RSS.
    # The dynamic portion of the filter name, `field`, refers to term field.
    # @param mixed  value    Value of the term field.
    # @param string taxonomy Taxonomy slug.
    value = WiPg.apply_filters( "term_"+ field +"_rss", value, taxonomy )

    # Filters the taxonomy field for use in RSS.
    # The dynamic portions of the hook name, `taxonomy`, and `field`, refer
    # to the taxonomy slug and field name, respectively.
    # @param mixed value Value of the taxonomy field.
    value = WiPg.apply_filters( taxonomy +"_"+ field +"_"+ rss, value )
  
  else:
    # Use display filters by default.

    # Filters the term field sanitized for display.
    # The dynamic portion of filter name, `field`, refers to term field name.
    # @param mixed  value    Value of the term field.
    # @param int    term_id  Term ID.
    # @param string taxonomy Taxonomy slug.
    # @param string context  Context to retrieve the term field value.
    value = WiPg.apply_filters( "term_"+ field, value, term_id, taxonomy,context)

    # Filters the taxonomy field sanitized for display.
    # The dynamic portions of the filter name, `taxonomy`, and `field`, refer
    # to the taxonomy slug and taxonomy field, respectively.
    # @param mixed  value   Value of the taxonomy field.
    # @param int    term_id Term ID.
    # @param string context Context to retrieve the taxonomy field value.
    value = WiPg.apply_filters( taxonomy +"_"+ field, value, term_id, context )

  if 'attribute' == context:
    value = esc_attr(value)
  elif 'js' == context:
    value = esc_js(value)
  return value
#'''

def wp_count_terms( taxonomy, args = array() ):
  ''' Count how many terms are in Taxonomy.
  Default args is 'hide_empty' which can be 'hide_empty=True' or array('hide_empty' : True).
  @param string       taxonomy Taxonomy name.
  @param array|string args     Optional. Array of arguments that get passed to get_terms().
                               Default empty array.
  @return array|int|WP_Error Number of terms in that taxonomy or WP_Error if the taxonomy does not exist.
  '''
  defaults = array(('hide_empty', False),)
  args = WiFc.wp_parse_args(args, defaults)

  # backward compatibility
  if Php.isset(args, 'ignore_empty'):
    args['hide_empty'] = args['ignore_empty']
    del args['ignore_empty']

  args['fields'] = 'count'

  return get_terms(taxonomy, args)


def wp_delete_object_term_relationships( object_id, taxonomies ):
  ''' Will unlink the object from the taxonomy or taxonomies.
  Will remove all relationships between the object and any terms in
  a particular taxonomy or taxonomies. Does not remove the term or
  taxonomy itself.
  @param int          object_id  The term Object Id that refers to the term.
  @param string|array taxonomies List of Taxonomy Names or single Taxonomy name.
  '''
  object_id = int(object_id)

  if not Php.is_array(taxonomies):
    taxonomies = array(taxonomies)

  for taxonomy in Php.Array(taxonomies):
    term_ids = wp_get_object_terms(
               object_id, taxonomy, array(( 'fields', 'ids' ),))
    term_ids = Php.array_map( Php.intval, term_ids )
    wp_remove_object_terms( object_id, term_ids, taxonomy )


def wp_delete_term( term, taxonomy, args = array() ):
  ''' Removes a term from the database.
  If the term is a parent of other terms, then the children will be updated to
  that term's parent.
  Metadata associated with the term will be deleted.
  @global wpdb wpdb WordPress database abstraction object.
  @param int          term     Term ID.
  @param string       taxonomy Taxonomy Name.
  @param array|string args {
      Optional. Array of arguments to override the default term ID. Default empty array.
      @type int  default       The term ID to make the default term. This will only override
                                the terms found if there is only one term found. Any other and
                                the found terms are used.
      @type bool force_default Optional. Whether to force the supplied term as default to be
                                assigned even if the object was not going to be term-less.
                                Default False.
  }
  @return bool|int|WP_Error True on success, False if term does not exist. Zero on attempted
                            deletion of default Category. WP_Error if the taxonomy does not exist.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  term = int(term)

  ids = term_exists(term, taxonomy)
  if not ids:
    return False
  if WpC.WB.Wj.is_wp_error( ids ):
    return ids

  tt_id = ids['term_taxonomy_id']

  defaults = array()

  if 'category' == taxonomy:
    defaults['default'] = WiO.get_option( 'default_category' )
    if defaults['default'] == term:
      return 0  # Don't delete the default category

  args = WiFc.wp_parse_args(args, defaults)

  if Php.isset(args, 'default'):
    default = int(args['default'])
    if not term_exists( default, taxonomy ):
      del locals()['default']    # unset( default )

  if Php.isset(args, 'force_default'):
    force_default = args['force_default']

  # Fires when deleting a term, before any modifications are made to posts or terms.
  # @param int    term     Term ID.
  # @param string taxonomy Taxonomy Name.
  WiPg.do_action( 'pre_delete_term', term, taxonomy )

  # Update children to point to new parent
  if is_taxonomy_hierarchical(taxonomy):
    term_obj = get_term(term, taxonomy)
    if WpC.WB.Wj.is_wp_error( term_obj ):
      return term_obj
    parent = term_obj.parent

    edit_ids = wpdb.get_results( "SELECT term_id, term_taxonomy_id FROM {} "
               "WHERE `parent` = ".format(wpdb.term_taxonomy)
               + str(term_obj.term_id) )     #Orig# + int(term_obj.term_id) )
    edit_tt_ids = WiFc.wp_list_pluck( edit_ids, 'term_taxonomy_id' )

    # Fires immediately before a term to delete's children are reassigned a parent.
    # @param array edit_tt_ids An array of term taxonomy IDs for the given term.
    WiPg.do_action( 'edit_term_taxonomies', edit_tt_ids )

    wpdb.update( wpdb.term_taxonomy, Php.compact(locals(), 'parent' ),
           array( ('parent', term_obj.term_id)), + Php.compact(locals(), 'taxonomy' ) )

    # Clean the cache for all child terms.
    edit_term_ids = WiFc.wp_list_pluck( edit_ids, 'term_id' )
    clean_term_cache( edit_term_ids, taxonomy )

    # Fires immediately after a term to delete's children are reassigned a parent.
    # @param array edit_tt_ids An array of term taxonomy IDs for the given term.
    WiPg.do_action( 'edited_term_taxonomies', edit_tt_ids )

  # Get the term before deleting it or its term relationships so we can pass to actions below.
  deleted_term = get_term( term, taxonomy )

  object_ids = Php.Array( wpdb.get_col( wpdb.prepare( "SELECT object_id FROM {} WHERE term_taxonomy_id = %s".format(wpdb.term_relationships), tt_id ) ))  # PyMySQL %d->%s

  for object_id in object_ids:
    terms = wp_get_object_terms( object_id, taxonomy,
              array(('fields', 'ids'), ('orderby', 'none')) )
    if 1 == len(terms) and Php.isset(locals(), 'default'):
      terms = array(default)  # array(default)
    else:
      #Since array_diff takes list, default, terms and term are lists.
      terms = Php.array_diff(terms, array(term))
      if (Php.isset(locals(), 'default'      ) and
          Php.isset(locals(), 'force_default') and force_default):
        terms = Php.array_merge(terms, array(default))
    terms = Php.array_map(Php.intval, terms)
    wp_set_object_terms( object_id, terms, taxonomy )

  # Clean the relationship caches for all object types using this term.
  tax_object = get_taxonomy( taxonomy )
  for object_type in tax_object.object_type:
    clean_object_term_cache( object_ids, object_type )

  term_meta_ids = wpdb.get_col( wpdb.prepare( "SELECT meta_id FROM {} WHERE "
              "term_id = %s ".format(wpdb.termmeta), term ) )  # PyMySQL %d->%s
  for mid in term_meta_ids:
    delete_metadata_by_mid( 'term', mid )

  # Fires immediately before a term taxonomy ID is deleted.
  # @param int tt_id Term taxonomy ID.
  WiPg.do_action( 'delete_term_taxonomy', tt_id )
  wpdb.delete( wpdb.term_taxonomy, array( ('term_taxonomy_id', tt_id),) )

  # Fires immediately after a term taxonomy ID is deleted.
  # @param int tt_id Term taxonomy ID.
  WiPg.do_action( 'deleted_term_taxonomy', tt_id )

  # Delete the term if no taxonomies use it.
  if not wpdb.get_var( wpdb.prepare( "SELECT COUNT(*) FROM {} WHERE "
          "term_id = %s".format(wpdb.term_taxonomy), term) ):  # PyMySQL %d->%s
    wpdb.delete( wpdb.terms, array( ('term_id', term),) )

  clean_term_cache(term, taxonomy)

  # Fires after a term is deleted from the database and the cache is cleaned.
  # @param int     term         Term ID.
  # @param int     tt_id        Term taxonomy ID.
  # @param string  taxonomy     Taxonomy slug.
  # @param mixed   deleted_term Copy of the already-deleted term, in the form specified
  #                              by the parent function. WP_Error otherwise.
  # @param array   object_ids   List of term object IDs.
  WiPg.do_action( 'delete_term', term, tt_id, taxonomy, deleted_term, object_ids )

  # Fires after a term in a specific taxonomy is deleted.
  # The dynamic portion of the hook name, `taxonomy`, refers to the specific
  # taxonomy the term belonged to.
  # @param int     term         Term ID.
  # @param int     tt_id        Term taxonomy ID.
  # @param mixed   deleted_term Copy of the already-deleted term, in the form specified
  #                              by the parent function. WP_Error otherwise.
  # @param array   object_ids   List of term object IDs.
  WiPg.do_action( "delete_"+ taxonomy, term, tt_id, deleted_term, object_ids )

  return True


def wp_delete_category( cat_ID ):
  ''' Deletes one existing category.
  @param int cat_ID
  @return bool|int|WP_Error Returns True if completes delete action; False if term doesn't exist
  Zero on attempted deletion of default Category; WP_Error object is also a possibility.
  '''
  return wp_delete_term( cat_ID, 'category' )

#'''

def wp_get_object_terms(object_ids, taxonomies, args = array()):
  ''' Retrieves the terms associated with the given object(s), in the supplied taxonomies.
  @since 4.4.0 Introduced `meta_query` and `update_term_meta_cache` arguments. When `fields` is 'all' or
  @since 4.7.0 Refactored to use WP_Term_Query, and to support any WP_Term_Query arguments.
               'all_with_object_id', an array of `WP_Term` objects will be returned.
  @global wpdb wpdb WordPress database abstraction object.
  @param int|array    object_ids The ID(s) of the object(s) to retrieve.
  @param string|array taxonomies The taxonomies to retrieve terms from.
  @param array|string args       See WP_Term_Query::__construct() for supported arguments.
  @return array|WP_Error The requested term data or empty array if no terms found.
                         WP_Error if any of the taxonomies don't exist.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  #if empty(object_ids) or empty(taxonomies):
  if not object_ids or not taxonomies:
    return array()

  if not Php.is_array(taxonomies):
    taxonomies = array(taxonomies)

  for taxonomy in taxonomies:
    if not taxonomy_exists(taxonomy):
      return WcE.WP_Error('invalid_taxonomy', __('Invalid taxonomy.'))

  if not Php.is_array(object_ids):
    object_ids = array(object_ids)
  object_ids = Php.array_map(Php.intval, object_ids)

  args = WiFc.wp_parse_args( args )
  
  args['taxonomy'] = taxonomies
  args['object_ids'] = object_ids
  
  terms = get_terms( args )


  # Filters the terms for a given object or objects.
  # @param array terms      An array of terms for the given object or objects.
  # @param array object_ids Array of object IDs for which `terms` were retrieved.
  # @param array taxonomies Array of taxonomies from which `terms` were retrieved.
  # @param array args       An array of arguments for retrieving terms for the given
  #                         object(s). See wp_get_object_terms() for details.
  #terms = WiPg.apply_filters('get_object_terms', terms, object_id_array, taxonomy_array, args )
  terms = WiPg.apply_filters( 'get_object_terms', terms, object_ids, taxonomies, args )
  object_ids = Php.implode( ',', object_ids )
  taxonomies = Php.implode( ',', taxonomies )

  # Filters the terms for a given object or objects.
  # The `taxonomies` parameter passed to this filter is formatted as a SQL fragment. The
  # {@see 'get_object_terms'} filter is recommended as an alternative.
  # @param array     terms      An array of terms for the given object or objects.
  # @param int|array object_ids Object ID or array of IDs.
  # @param string    taxonomies SQL-formatted (comma-separated and quoted) list of taxonomy names.
  # @param array     args       An array of arguments for retrieving terms for the given object(s).
  #                              See wp_get_object_terms() for details.
  return WiPg.apply_filters( 'wp_get_object_terms', terms, object_ids, taxonomies, args )


#'''
def wp_insert_term( term, taxonomy, args = array() ):
  ''' Add a new term to the database.
  A non-existent term is inserted in the following sequence:
  1. The term is added to the term table, then related to the taxonomy.
  2. If everything is correct, several actions are fired.
  3. The 'term_id_filter' is evaluated.
  4. The term cache is cleaned.
  5. Several more actions are fired.
  6. An array is returned containing the term_id and term_taxonomy_id.
  If the 'slug' argument is not empty, then it is checked to see if the term
  is invalid. If it is not a valid, existing term, it is added and the term_id
  is given.
  If the taxonomy is hierarchical, and the 'parent' argument is not empty,
  the term is inserted and the term_id will be given.
  Error handling:
  If taxonomy does not exist or term is empty,
  a WP_Error object will be returned.
  If the term already exists on the same hierarchical level,
  or the term slug and name are not unique, a WP_Error object will be returned.
  @global wpdb wpdb WordPress database abstraction object.
  @param string       term     The term to add or update.
  @param string       taxonomy The taxonomy to which to add the term.
  @param array|string args {
      Optional. Array or string of arguments for inserting a term.
      @type string alias_of    Slug of the term to make this term an alias of.
                                Default empty string. Accepts a term slug.
      @type string description The term description. Default empty string.
      @type int    parent      The id of the parent term. Default 0.
      @type string slug        The term slug to use. Default empty string.
  }
  @return array|WP_Error An array containing `term_id`, `term_taxonomy_id`,
                         and `slug` (added by VT).  WP_Error otherwise.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if not taxonomy_exists(taxonomy):
    return WcE.WP_Error('invalid_taxonomy', __('Invalid taxonomy.'))
  # Filters a term before it is sanitized and inserted into the database.
  # @param string term     The term to add or update.
  # @param string taxonomy Taxonomy slug.
  term = WiPg.apply_filters( 'pre_insert_term', term, taxonomy )
  if WpC.WB.Wj.is_wp_error( term ):
    return term
  if Php.is_int( term ) and 0 == term:
    return WcE.WP_Error( 'invalid_term_id', __('Invalid term ID') )
  if '' == Php.trim( term ):
    return WcE.WP_Error( 'empty_term_name', __( 'A name is required for this term.' ) )
  defaults = array(('alias_of', ''), ('description', ''), ('parent', 0),
                   ('slug', ''),)
  args = WiFc.wp_parse_args( args, defaults )

  if args['parent'] > 0 and not term_exists( int(args['parent']) ):
    return WcE.WP_Error( 'missing_parent', __( 'Parent term does not exist.' ) )

  args['name'] = term
  args['taxonomy'] = taxonomy

  # Coerce None description to strings, to avoid database errors.
  args['description'] = str(args['description'])

  args = sanitize_term(args, taxonomy, 'db')

  # expected_slashed (name)
  name = WiF.wp_unslash( args['name'] )
  description = WiF.wp_unslash( args['description'] )
  parent = int(args['parent'])

  slug_provided = not Php.empty(args, 'slug')
  if not slug_provided:
    slug = WiF.sanitize_title( name )
  else:
    slug = args['slug']

  term_group = 0
  if args['alias_of']:
    alias = get_term_by( 'slug', args['alias_of'], taxonomy )
    if not Php.empty(alias, 'term_group'):
      # The alias we want is already in a group, so let's use that one.
      term_group = alias.term_group
    elif not Php.empty(alias, 'term_id'):
      # The alias is not in a group, so we create a new one
      # and add the alias to it.
      term_group = wpdb.get_var("SELECT MAX(term_group) FROM "+ wpdb.terms) + 1

      wp_update_term( alias.term_id, taxonomy, array(
        ('term_group', term_group),
      ) )

  # Prevent the creation of terms with duplicate names at the same level of a taxonomy hierarchy,
  # unless a unique slug has been explicitly provided.
  name_matches = get_terms( taxonomy, array(
    ('name', name),
    ('hide_empty', False),
  ) )

  #The `name` match in `get_terms()` doesn't differentiate accented characters,
  # so we do a stricter comparison here.
  name_match = None
  if name_matches:
    for _match in name_matches:
      if Php.strtolower( name ) == Php.strtolower( _match.name ):
        name_match = _match
        break

  if name_match:
    slug_match = get_term_by( 'slug', slug, taxonomy )
    if not slug_provided or name_match.slug == slug or slug_match:
      if is_taxonomy_hierarchical( taxonomy ):
        siblings = get_terms( taxonomy,
                              array(('get', 'all'), ('parent', parent),) )
        existing_term = None
        if name_match.slug == slug and Php.in_array( name,
                                      WiFc.wp_list_pluck( siblings, 'name' )):
          existing_term = name_match
        elif slug_match and Php.in_array(slug,
                                      WiFc.wp_list_pluck( siblings, 'slug' )):
          existing_term = slug_match

        if existing_term:
          return WcE.WP_Error( 'term_exists', __(
            'A term with the name provided already exists with this parent.' ),
            existing_term.term_id )
      else:
        return WcE.WP_Error( 'term_exists', __(
            'A term with the name provided already exists in this taxonomy.' ),
            name_match.term_id )

  slug = wp_unique_term_slug( slug, Php.Object( args ))

  data = Php.compact(locals(), 'name', 'slug', 'term_group' )
  
  # Filters term data before it is inserted into the database.
  # @param array  data     Term data to be inserted.
  # @param string taxonomy Taxonomy slug.
  # @param array  args     Arguments passed to wp_insert_term().
  data = WiPg.apply_filters( 'wp_insert_term_data', data, taxonomy, args );
  
  if False is wpdb.insert( wpdb.terms, data ):
    return WcE.WP_Error( 'db_insert_error', __(
                 'Could not insert term into the database' ), wpdb.last_error )

  term_id = int(wpdb.insert_id)

  # Seems unreachable, However, Is used in the case that a term name is provided, which sanitizes to an empty string.
  if not slug: # if Php.empty(locals(), slug):
    slug = WiF.sanitize_title(slug, term_id)

    # This action is documented in wp-includes/taxonomy.php
    WiPg.do_action( 'edit_terms', term_id, taxonomy )
    wpdb.update( wpdb.terms, Php.compact(locals(), 'slug' ), Php.compact(locals(), 'term_id' ) )

    # This action is documented in wp-includes/taxonomy.php
    WiPg.do_action( 'edited_terms', term_id, taxonomy )

  tt_id = wpdb.get_var( wpdb.prepare( "SELECT tt.term_taxonomy_id FROM {} "
         "AS tt INNER JOIN {} AS t ON tt.term_id = t.term_id "
         "WHERE tt.taxonomy = %s AND t.term_id = %s".format(wpdb.term_taxonomy,
         wpdb.terms), taxonomy, term_id ) )  # PyMySQL %d->%s

  if tt_id:     # if not empty(locals(), tt_id):
    return array(('term_id', term_id), ('term_taxonomy_id', tt_id),)
  #wpdb.insert( wpdb.term_taxonomy, { **Php.compact(locals(), 'term_id', 'taxonomy',
  #                                   'description', 'parent'), 'count' : 0 } )
  wpdb.insert( wpdb.term_taxonomy, Php.compact(locals(), 'term_id', 'taxonomy',
             'description', 'parent') + array(('count', 0) )) #+ = array_plus()
  tt_id = int(wpdb.insert_id)

  # Sanity check: if we just created a term with the same parent + taxonomy + slug but a higher term_id than
  # an existing term, then we have unwittingly created a duplicate term. Delete the dupe, and use the term_id
  # and term_taxonomy_id of the older term instead. Then return out of the function so that the "create" hooks
  # are not fired.
  duplicate_term = wpdb.get_row( wpdb.prepare(
        "SELECT t.term_id, tt.term_taxonomy_id FROM {} t INNER JOIN {} tt "
        "ON ( tt.term_id = t.term_id ) WHERE t.slug = %s AND tt.parent = %s "
        "AND tt.taxonomy = %s AND t.term_id < %s AND tt.term_taxonomy_id != %s"
        .format(wpdb.terms, wpdb.term_taxonomy), slug, parent, taxonomy,
        term_id, tt_id ) )  # PyMySQL %d->%s
  if duplicate_term:
    wpdb.delete( wpdb.terms, array(('term_id', term_id)) )
    wpdb.delete( wpdb.term_taxonomy, array(('term_taxonomy_id', tt_id)) )

    term_id = int(duplicate_term.term_id)
    tt_id   = int(duplicate_term.term_taxonomy_id)

    clean_term_cache( term_id, taxonomy )
    return array(('term_id', term_id), ('term_taxonomy_id', tt_id), #) #Orig
                  ('slug',slug),)   #VT Added slug!!

  # Fires immediately after a new term is created, before the term cache is cleaned.
  # @param int    term_id  Term ID.
  # @param int    tt_id    Term taxonomy ID.
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( "create_term", term_id, tt_id, taxonomy )

  # Fires after a new term is created for a specific taxonomy.
  # The dynamic portion of the hook name, `taxonomy`, refers
  # to the slug of the taxonomy the term was created for.
  # @param int term_id Term ID.
  # @param int tt_id   Term taxonomy ID.
  WiPg.do_action( "create_"+ taxonomy, term_id, tt_id )

  # Filters the term ID after a new term is created.
  # @param int term_id Term ID.
  # @param int tt_id   Taxonomy term ID.
  term_id = WiPg.apply_filters( 'term_id_filter', term_id, tt_id )

  clean_term_cache(term_id, taxonomy)

  # Fires after a new term is created, and after the term cache has been cleaned.
  # @param int    term_id  Term ID.
  # @param int    tt_id    Term taxonomy ID.
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( 'created_term', term_id, tt_id, taxonomy )

  # Fires after a new term in a specific taxonomy is created, and after the term
  # cache has been cleaned.
  # The dynamic portion of the hook name, `taxonomy`, refers to the taxonomy slug.
  # @param int term_id Term ID.
  # @param int tt_id   Term taxonomy ID.
  WiPg.do_action( "created_"+ taxonomy, term_id, tt_id )

  return array(('term_id', term_id), ('term_taxonomy_id', tt_id), #]) #Orig
               ('slug', slug), ('name', name),)   #VT Added slug & name


def wp_set_object_terms( object_id, terms, taxonomy, append = False ):
  ''' Create Term and Taxonomy Relationships.
  Relates an object (post, link etc) to a term and taxonomy type. Creates the
  term and taxonomy relationship if it doesn't already exist. Creates a term if
  it doesn't exist (using the slug).
  A relationship means that the term is grouped in or belongs to the taxonomy.
  A term has no meaning until it is given context by defining which taxonomy it
  exists under.
  @global wpdb wpdb The WordPress database abstraction object.
  @param int              object_id The object to relate to.
  @param array|int|string terms     A single term slug, single term id, or array of either term slugs or ids.
                                     Will replace all existing related terms in this taxonomy.
  @param string           taxonomy  The context in which to relate the term to the object.
  @param bool             append    Optional. If False will delete difference of terms. Default False.
  @return array|WP_Error Term taxonomy IDs of the affected terms.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  object_id = int(object_id)

  if not taxonomy_exists(taxonomy):
    return WcE.WP_Error('invalid_taxonomy', __('Invalid taxonomy.'))

  if not Php.is_array(terms):
    terms = array(terms)

  if not append:
    old_tt_ids =  wp_get_object_terms(object_id, taxonomy,
                             array(('fields', 'tt_ids'), ('orderby', 'none')) )
  else:
    old_tt_ids = array()

  tt_ids     = array()
  term_ids   = array()
  new_tt_ids = array()

  for term in Php.Array( terms ):
    if not len(Php.trim(term)):
      continue

    term_info = term_exists(term, taxonomy)
    if not term_info:
      # Skip if a non-existent term ID is passed.
      if Php.is_int(term):
        continue
      term_info = wp_insert_term(term, taxonomy)

    if WpC.WB.Wj.is_wp_error(term_info):
      return term_info
    term_ids[None] = term_info['term_id']
    tt_id = term_info['term_taxonomy_id']
    tt_ids[None] = tt_id

    if wpdb.get_var( wpdb.prepare( "SELECT term_taxonomy_id FROM {} WHERE "
                     "object_id = %s AND term_taxonomy_id = %s".format(
                wpdb.term_relationships), object_id, tt_id )): #PyMySQL %d->%s
      continue

    # Fires immediately before an object-term relationship is added.
    # @param int object_id Object ID.
    # @param int tt_id     Term taxonomy ID.
    # @param str taxonomy  Taxonomy slug.
    WiPg.do_action( 'add_term_relationship', object_id, tt_id, taxonomy )
    wpdb.insert( wpdb.term_relationships,
                 array(('object_id', object_id),('term_taxonomy_id', tt_id)) )

    # Fires immediately after an object-term relationship is added.
    # @param int object_id Object ID.
    # @param int tt_id     Term taxonomy ID.
    # @param str taxonomy  Taxonomy slug.
    WiPg.do_action( 'added_term_relationship', object_id, tt_id, taxonomy )
    new_tt_ids[None] = tt_id

  if new_tt_ids:
    wp_update_term_count( new_tt_ids, taxonomy )

  if not append:
    delete_tt_ids = Php.array_diff( old_tt_ids, tt_ids )

    if delete_tt_ids:
      in_delete_tt_ids = "'" + Php.implode( "', '", delete_tt_ids ) + "'"
      delete_term_ids = wpdb.get_col( wpdb.prepare( "SELECT tt.term_id FROM "
          "{} AS tt WHERE tt.taxonomy = %s AND tt.term_taxonomy_id IN ({})"
          .format(wpdb.term_taxonomy, in_delete_tt_ids), taxonomy ) )
      delete_term_ids = Php.array_map( Php.intval, delete_term_ids )

      remove = wp_remove_object_terms( object_id, delete_term_ids, taxonomy )
      if WpC.WB.Wj.is_wp_error( remove ):
        return remove

  t = get_taxonomy(taxonomy)
  #if ( ! $append && isset($t->sort) && $t->sort ) {
  if not append and getattr(t, 'sort', None):
    values = array()
    term_order = 0
    final_tt_ids = wp_get_object_terms(object_id, taxonomy,
                                       array(('fields', 'tt_ids')) )
    for tt_id in tt_ids:
      if Php.in_array(tt_id, final_tt_ids):
        term_order += 1            # PyMySQL %d->%s
        values[None] = wpdb.prepare( "(%s, %s, %s)",object_id,tt_id,term_order)
    if values:
      if False == wpdb.query( "INSERT INTO {} (object_id, term_taxonomy_id, "
          "term_order) VALUES ".format(wpdb.term_relationships) + 
          Php.Join( ',', values ) + " ON DUPLICATE KEY UPDATE term_order = "
          "VALUES(term_order)" ):
        return WcE.WP_Error( 'db_insert_error', __(
          'Could not insert term relationship into the database' ),
          wpdb.last_error )

  WiCa.wp_cache_delete( object_id, taxonomy + '_relationships' )

  # Fires after an object's terms have been set.
  # @param int    object_id  Object ID.
  # @param array  terms      An array of object terms.
  # @param array  tt_ids     An array of term taxonomy IDs.
  # @param string taxonomy   Taxonomy slug.
  # @param bool   append     Whether to append new terms to the old terms.
  # @param array  old_tt_ids Old array of term taxonomy IDs.
  WiPg.do_action( 'set_object_terms', object_id, terms, tt_ids, taxonomy,
                  append, old_tt_ids )
  return tt_ids


def wp_add_object_terms( object_id, terms, taxonomy ):
  ''' Add term(s) associated with a given object.
  @param int              object_id The ID of the object to which the terms will be added.
  @param array|int|string terms     The slug(s) or ID(s) of the term(s) to add.
  @param array|string     taxonomy  Taxonomy name.
  @return array|WP_Error Term taxonomy IDs of the affected terms.
  '''
  return wp_set_object_terms( object_id, terms, taxonomy, True )


def wp_remove_object_terms( object_id, terms, taxonomy ):
  ''' Remove term(s) associated with a given object.
  @global wpdb wpdb WordPress database abstraction object.
  @param int              object_id The ID of the object from which the terms will be removed.
  @param array|int|string terms     The slug(s) or ID(s) of the term(s) to remove.
  @param array|string     taxonomy  Taxonomy name.
  @return bool|WP_Error True on success, False or WP_Error on failure.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  object_id = int(object_id)

  if not taxonomy_exists( taxonomy ):
    return WcE.WP_Error( 'invalid_taxonomy', __( 'Invalid taxonomy.' ) )

  if not Php.is_array( terms ):
    terms = array( terms )

  tt_ids = array()

  for term in Php.Array(terms):
    if not len( Php.trim( term ) ):
      continue

    term_info = term_exists( term, taxonomy )
    if not term_info:
      # Skip if a non-existent term ID is passed.
      if Php.is_int( term ):
        continue

    if WpC.WB.Wj.is_wp_error( term_info ):
      return term_info

    tt_ids[None] = term_info['term_taxonomy_id']

  if tt_ids:
    in_tt_ids = "'" + Php.implode( "', '", tt_ids ) + "'"

    # Fires immediately before an object-term relationship is deleted.
    # @param int   object_id Object ID.
    # @param array tt_ids    An array of term taxonomy IDs.
    # @param string taxonomy  Taxonomy slug.
    WiPg.do_action( 'delete_term_relationships', object_id, tt_ids, taxonomy )
    deleted = wpdb.query( wpdb.prepare( "DELETE FROM {} WHERE object_id = %s "
              "AND term_taxonomy_id IN ({})".format(wpdb.term_relationships,
              in_tt_ids), object_id ) )  # PyMySQL %d->%s

    WiCa.wp_cache_delete( object_id, taxonomy + '_relationships' )

    # Fires immediately after an object-term relationship is deleted.
    # @param int   object_id Object ID.
    # @param array tt_ids    An array of term taxonomy IDs.
    WiPg.do_action( 'deleted_term_relationships', object_id, tt_ids )

    wp_update_term_count( tt_ids, taxonomy )

    return bool(deleted)

  return False


def wp_unique_term_slug( slug, term ):
  ''' Will make slug unique, if it isn't already.
  The `slug` has to be unique global to every taxonomy, meaning that one
  taxonomy term can't have a matching slug with another taxonomy term. Each
  slug has to be globally unique for every taxonomy.
  The way this works is that if the taxonomy that the term belongs to is
  hierarchical and has a parent, it will append that parent to the slug.
  If that still doesn't return an unique slug, then it try to append a number
  until it finds a number that is truly unique.
  The only purpose for `term` is for appending a parent, if one exists.
  @global wpdb wpdb WordPress database abstraction object.
  @param string slug The string that will be tried for a unique slug.
  @param object term The term object that the `slug` will belong to.
  @return string Will return a True unique slug.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  needs_suffix = True
  original_slug = slug

  # As of 4.1, duplicate slugs are allowed as long as they're in different taxonomies.
  if (not term_exists( slug ) or int( WiO.get_option( 'db_version' )) >= 30133      and not get_term_by( 'slug', slug, term.taxonomy )):
    needs_suffix = False

  # If the taxonomy supports hierarchy and the term has a parent, make the slug unique
  # by incorporating parent slugs.
  parent_suffix = ''
  if (needs_suffix and is_taxonomy_hierarchical( term.taxonomy ) and
      not Php.empty(term, 'parent')):
    the_parent = term.parent
    while ( the_parent ):    # not empty(locals(), the_parent):
      parent_term = get_term(the_parent, term.taxonomy)
      if WpC.WB.Wj.is_wp_error(parent_term) or not parent_term: #empty(parent_term):
        break
      parent_suffix += '-' + parent_term.slug
      if not term_exists( slug + parent_suffix ):
        break

      if Php.empty(parent_term, 'parent'):
        break
      the_parent = parent_term.parent

  # If we didn't get a unique slug, try appending a number to make it unique.

  # Filters whether the proposed unique term slug is bad.
  # @param bool   needs_suffix Whether the slug needs to be made unique with a suffix.
  # @param string slug         The slug.
  # @param object term         Term object.
  if WiPg.apply_filters( 'wp_unique_term_slug_is_bad_slug', needs_suffix, slug, term ):
    if parent_suffix:
      slug += parent_suffix
    else:
      if not Php.empty(term, 'term_id'):
        query = wpdb.prepare(
                "SELECT slug FROM {} WHERE slug = %s AND term_id != %s"
                .format(wpdb.terms), slug, term.term_id )  # PyMySQL %d->%s
      else:
        query = wpdb.prepare( "SELECT slug FROM {} WHERE slug = %s"
                              .format(wpdb.terms), slug )

      if wpdb.get_var( query ):
        num = 2
        # do {
        while True:
          alt_slug = slug +"-"+ str(num)
          num += 1
          slug_check = wpdb.get_var( wpdb.prepare(
                       "SELECT slug FROM {} WHERE slug = %s"
                       .format(wpdb.terms), alt_slug ) )
          if not slug_check:
            break
        # } while ( slug_check );
        slug = alt_slug

  # Filters the unique term slug.
  # @param string slug          Unique term slug.
  # @param object term          Term object.
  # @param string original_slug Slug originally passed to the function for testing.
  return WiPg.apply_filters( 'wp_unique_term_slug', slug, term, original_slug )


def wp_update_term( term_id, taxonomy, args = array() ):
  ''' Update term based on arguments provided.
  The args will indiscriminately override all values with the same field name.
  Care must be taken to not override important information need to update or
  update will fail (or perhaps create a new term, neither would be acceptable).
  Defaults will set 'alias_of', 'description', 'parent', and 'slug' if not
  defined in args already.
  'alias_of' will create a term group, if it doesn't already exist, and update
  it for the term.
  If the 'slug' argument in args is missing, then the 'name' in args will be
  used. It should also be noted that if you set 'slug' and it isn't unique then
  a WP_Error will be passed back. If you don't pass any slug, then a unique one
  will be created for you.
  For what can be overrode in `args`, check the term scheme can contain and stay
  away from the term keys.
  @global wpdb wpdb WordPress database abstraction object.
  @param int          term_id  The ID of the term
  @param string       taxonomy The context in which to relate the term to the object.
  @param array|string args     Optional. Array of get_terms() arguments. Default empty array.
  @return array|WP_Error Returns Term ID and Taxonomy Term ID
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if not taxonomy_exists( taxonomy ):
    return WcE.WP_Error( 'invalid_taxonomy', __( 'Invalid taxonomy.' ) )

  term_id = int(term_id)

  # First, get all of the original args
  term = get_term( term_id, taxonomy )

  if WpC.WB.Wj.is_wp_error( term ):
    return term

  if not term:
    return WcE.WP_Error( 'invalid_term', __( 'Empty Term' ) )

  term = Php.Array( term.data )

  # Escape data pulled from DB.
  term = wp_slash( term )

  # Merge old and new args with new args overwriting old ones.
  args = Php.array_merge(term, args)

  defaults = array(('alias_of', ''), ('description', ''), ('parent', 0),
                   ('slug', ''))
  args = WiFc.wp_parse_args(args, defaults)
  args = sanitize_term(args, taxonomy, 'db')
  parsed_args = args

  # expected_slashed (name)
  name = WiF.wp_unslash( args['name'] )
  description = WiF.wp_unslash( args['description'] )

  parsed_args['name'] = name
  parsed_args['description'] = description

  if '' == Php.trim(name):
    return WcE.WP_Error('empty_term_name', __('A name is required for this term'))

  if parsed_args['parent'] > 0 and not term_exists( int(parsed_args['parent']) ):
    return WcE.WP_Error( 'missing_parent', __( 'Parent term does not exist.' ) )

  empty_slug = False
  if Php.empty( args, 'slug' ):
    empty_slug = True
    slug = WiF.sanitize_title(name)
  else:
    slug = args['slug']

  parsed_args['slug'] = slug

  #term_group = isset(parsed_args['term_group']) ? parsed_args['term_group']:0
  term_group = getattr(parsed_args, 'term_group', 0)
  if args['alias_of']:
    alias = get_term_by( 'slug', args['alias_of'], taxonomy )
    if not Php.empty(alias, 'term_group'):
      # The alias we want is already in a group, so let's use that one.
      term_group = alias.term_group
    elif not Php.empty(alias, 'term_id'):
      # The alias is not in a group, so we create a new one
      # and add the alias to it.
      term_group = wpdb.get_var("SELECT MAX(term_group) FROM "+ wpdb.terms) +1

      wp_update_term( alias.term_id, taxonomy, array(
        ('term_group', term_group),
      ) )

    parsed_args['term_group'] = term_group

  # Filters the term parent.
  # Hook to this filter to see if it will cause a hierarchy loop.
  # @param int    parent      ID of the parent term.
  # @param int    term_id     Term ID.
  # @param string taxonomy    Taxonomy slug.
  # @param array  parsed_args An array of potentially altered update arguments for the given term.
  # @param array  args        An array of update arguments for the given term.
  parent = WiPg.apply_filters( 'wp_update_term_parent', args['parent'], term_id, taxonomy, parsed_args, args )

  # Check for duplicate slug
  duplicate = get_term_by( 'slug', slug, taxonomy )
  if duplicate and duplicate.term_id != term_id:
    # If an empty slug was passed or the parent changed, reset the slug to something unique.
    # Otherwise, bail.
    if empty_slug or ( parent != term['parent']):
      slug = wp_unique_term_slug(slug, Php.Object( args ))
    else:
      # translators: 1: Taxonomy term slug */
      return WcE.WP_Error('duplicate_term_slug', sprintf(__('The slug &#8220;%s&#8221; is already in use by another term'), slug))

  tt_id = int(wpdb.get_var( wpdb.prepare( "SELECT tt.term_taxonomy_id FROM {} "
         "AS tt INNER JOIN {} AS t ON tt.term_id = t.term_id "
         "WHERE tt.taxonomy = %s AND t.term_id = %s".format(wpdb.term_taxonomy,
         wpdb.terms), taxonomy, term_id) ))  # PyMySQL %d->%s

  # Check whether this is a shared term that needs splitting.
  _term_id = _split_shared_term( term_id, tt_id )
  if not WpC.WB.Wj.is_wp_error( _term_id ):
    term_id = _term_id

  # Fires immediately before the given terms are edited.
  # @param int    term_id  Term ID.
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( 'edit_terms', term_id, taxonomy )

  data = Php.compact(locals(), 'name', 'slug', 'term_group' )

  # Filters term data before it is updated in the database.
  # @param array  $data     Term data to be updated.
  # @param int    $term_id  Term ID.
  # @param string $taxonomy Taxonomy slug.
  # @param array  $args     Arguments passed to wp_update_term().
  data = WiPg.apply_filters( 'wp_update_term_data', data, term_id, taxonomy,
                              args )
  wpdb.update(wpdb.terms, data, Php.compact(locals(), 'term_id' ) )
  if not slug:   # if empty(slug):
    slug = WiF.sanitize_title(name, term_id)
    wpdb.update( wpdb.terms, Php.compact(locals(), 'slug' ), Php.compact(locals(), 'term_id' ) )

  # Fires immediately after the given terms are edited.
  # @param int    term_id  Term ID
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( 'edited_terms', term_id, taxonomy )

  # Fires immediate before a term-taxonomy relationship is updated.
  # @param int    tt_id    Term taxonomy ID.
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( 'edit_term_taxonomy', tt_id, taxonomy )

  wpdb.update( wpdb.term_taxonomy, Php.compact(locals(), 'term_id', 'taxonomy', 'description', 'parent' ), array( ('term_taxonomy_id', tt_id) ) )

  # Fires immediately after a term-taxonomy relationship is updated.
  # @param int    tt_id    Term taxonomy ID.
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( 'edited_term_taxonomy', tt_id, taxonomy )

  # Fires after a term has been updated, but before the term cache has been cleaned.
  # @param int    term_id  Term ID.
  # @param int    tt_id    Term taxonomy ID.
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( "edit_term", term_id, tt_id, taxonomy )

  # Fires after a term in a specific taxonomy has been updated, but before the term
  # cache has been cleaned.
  # The dynamic portion of the hook name, `taxonomy`, refers to the taxonomy slug.
  # @param int term_id Term ID.
  # @param int tt_id   Term taxonomy ID.
  WiPg.do_action( "edit_taxonomy", term_id, tt_id )

  # This filter is documented in wp-includes/taxonomy.php
  term_id = WiPg.apply_filters( 'term_id_filter', term_id, tt_id )

  clean_term_cache(term_id, taxonomy)

  # Fires after a term has been updated, and the term cache has been cleaned.
  # @param int    term_id  Term ID.
  # @param int    tt_id    Term taxonomy ID.
  # @param string taxonomy Taxonomy slug.
  WiPg.do_action( "edited_term", term_id, tt_id, taxonomy )

  # Fires after a term for a specific taxonomy has been updated, and the term
  # cache has been cleaned.
  # The dynamic portion of the hook name, `taxonomy`, refers to the taxonomy slug.
  # @param int term_id Term ID.
  # @param int tt_id   Term taxonomy ID.
  WiPg.do_action( "edited_"+ taxonomy, term_id, tt_id )

  return array(('term_id', term_id), ('term_taxonomy_id', tt_id),)


@Php.static_vars(_defer = False)
def wp_defer_term_counting(defer=None):
  ''' Enable or disable term counting.
  @staticvar bool _defer
  @param bool defer Optional. Enable if True, disable if False.
  @return bool Whether term counting is enabled or disabled.
  '''
  #static _defer = False  # static_vars above

  if Php.is_bool(defer):
    wp_defer_term_counting._defer = defer
    # flush any deferred counts
    if not defer:
      wp_update_term_count( None, None, True )

  return wp_defer_term_counting._defer


@Php.static_vars(_deferred = array())
def wp_update_term_count( terms, taxonomy, do_deferred = False ):
  ''' Updates the amount of terms in taxonomy.
  If there is a taxonomy callback applied, then it will be called for updating
  the count.
  The default action is to count what the amount of terms have the relationship
  of term ID. Once that is done, then update the database.
  @staticvar array _deferred
  @param int|array terms       The term_taxonomy_id of the terms.
  @param string    taxonomy    The context of the term.
  @param bool      do_deferred Whether to flush the deferred term counts too. Default False.
  @return bool If no terms will return False, and if successful will return True.
  '''
  #static _deferred = array()  # static_vars above

  if do_deferred:
    for tax in Php.Array( Php.array_keys( wp_update_term_count._deferred )):
      wp_update_term_count_now( wp_update_term_count._deferred[tax], tax )
      del wp_update_term_count._deferred[tax]

  if not terms:    # if empty(locals(), terms):
    return False

  if not Php.is_array(terms):
    terms = array(terms)

  if wp_defer_term_counting():
    if not Php.isset(wp_update_term_count._deferred, taxonomy):
      wp_update_term_count._deferred[taxonomy] = array()
    wp_update_term_count._deferred[taxonomy] = Php.array_unique(
            Php.array_merge(wp_update_term_count._deferred[taxonomy], terms) )
    return True
  return wp_update_term_count_now( terms, taxonomy )


def wp_update_term_count_now( terms, taxonomy ):
  ''' Perform term count update immediately.
  @param array  terms    The term_taxonomy_id of terms to update.
  @param string taxonomy The context of the term.
  @return True Always True when complete.
  '''
  import wp.i.post as WiP
  terms = Php.array_map(Php.intval, terms)

  taxonomy = get_taxonomy(taxonomy)
  if not Php.empty(taxonomy, 'update_count_callback'):
    Php.call_user_func(taxonomy.update_count_callback, terms, taxonomy)
  else:
    object_types = Php.Array( taxonomy.object_type )
    #for &object_type in object_types:
    #for  i, object_type in enumerate(object_types):
    for   k, object_type in object_types.items():
      if 0 == Php.strpos( object_type, 'attachment:' ):
        #list( $object_type ) = explode( ':', $object_type );
        object_types[k] = Php.explode( ':', object_type )[0]

    if object_types == Php.array_filter( object_types, WiP.post_type_exists ):
      # Only post types are attached to this taxonomy
      _update_post_term_count( terms, taxonomy )
    else:
      # Default count updater
      _update_generic_term_count( terms, taxonomy )

  clean_term_cache(terms, '', False)

  return True


#
# Cache
#

def clean_object_term_cache(object_ids, object_type):
  ''' Removes the taxonomy relationship to terms from the cache.
  Will remove the entire taxonomy relationship containing term `object_id`. The
  term IDs have to exist within the taxonomy `object_type` for the deletion to
  take place.
  @global bool _wp_suspend_cache_invalidation
  @see get_object_taxonomies() for more on object_type.
  @param int|array    object_ids  Single or list of term object ID(s).
  @param array|string object_type The taxonomy object type.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global _wp_suspend_cache_invalidation
  #_wp_suspend_cache_invalidation = WpC.WB.Wj._wp_suspend_cache_invalidation

  #if globals().get('_wp_suspend_cache_invalidation', None):
  if not Php.empty(WpC.WB.Wj.__dict__, '_wp_suspend_cache_invalidation'):
    return

  if not Php.is_array(object_ids):
    object_ids = array(object_ids)

  taxonomies = get_object_taxonomies( object_type )

  for Id in object_ids:
    for taxonomy in taxonomies:
      WiCa.wp_cache_delete(Id, taxonomy +"_relationships")

  # Fires after the object term cache has been cleaned.
  # @param array  object_ids An array of object IDs.
  # @param string objet_type Object type.
  WiPg.do_action( 'clean_object_term_cache', object_ids, object_type )


def clean_term_cache(ids, taxonomy = '', clean_taxonomy = True):
  ''' Will remove all of the term ids from the cache.
  @global wpdb wpdb WordPress database abstraction object.
  @global bool _wp_suspend_cache_invalidation
  @param int|array ids            Single or list of Term IDs.
  @param string    taxonomy       Optional. Can be empty and will assume `tt_ids`, else will use for context.
                                   Default empty.
  @param bool      clean_taxonomy Optional. Whether to clean taxonomy wide caches (True), or just individual
                                   term object caches (False). Default True.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wpdb = WpC.WB.Wj.wpdb  # global wpdb, _wp_suspend_cache_invalidation

  #if globals().get('_wp_suspend_cache_invalidation', None):
  if not Php.empty(WpC.WB.Wj.__dict__, '_wp_suspend_cache_invalidation'):
    return

  if not Php.is_array(ids):
    ids = array()

  taxonomies = array()
  # If no taxonomy, assume tt_ids.
  if not taxonomy:   # if empty(taxonomy):
    tt_ids = Php.array_map(Php.intval, ids)
    tt_ids = Php.implode(', ', tt_ids)
    terms = wpdb.get_results("SELECT term_id, taxonomy FROM {} WHERE "
                 "term_taxonomy_id IN ({})".format(wpdb.term_taxonomy, tt_ids))
    ids = array()
    for term in Php.Array(terms):
      taxonomies[None] = term.taxonomy
      ids[None] = term.term_id
      WiCa.wp_cache_delete( term.term_id, 'terms' )
    taxonomies = Php.array_unique(taxonomies)
  else:
    taxonomies = array(taxonomy)
    for taxonomy in taxonomies:
      for Id in ids:
        WiCa.wp_cache_delete( Id, 'terms' )

  for taxonomy in taxonomies:
    if clean_taxonomy:
      WiCa.wp_cache_delete('all_ids', taxonomy)
      WiCa.wp_cache_delete('get', taxonomy)
      WiO.delete_option(taxonomy +"_children")
      # Regenerate {taxonomy}_children
      _get_term_hierarchy(taxonomy)

    # Fires once after each taxonomy's term cache has been cleaned.
    # @param array  ids            An array of term IDs.
    # @param string taxonomy       Taxonomy slug.
    # @param bool   clean_taxonomy Whether or not to clean taxonomy-wide caches
    WiPg.do_action( 'clean_term_cache', ids, taxonomy, clean_taxonomy )

  WiCa.wp_cache_set( 'last_changed', Php.microtime(), 'terms' )
#'''


def get_object_term_cache( Id, taxonomy ):
  ''' Retrieves the taxonomy relationship to the term object Id.
  Upstream functions (like get_the_terms() and is_object_in_term()) are
  responsible for populating the object-term relationship cache. The current
  function only fetches relationship data that is already in the cache.
  @param int    Id       Term object ID.
  @param string taxonomy Taxonomy name.
  @return bool|array|WP_Error Array of `WP_Term` objects, if cached.
                   False if cache is empty for `$taxonomy` and `$id`.
                   WP_Error if get_term() returns an error object for any term.
  '''
  import wp.i.cache    as WiCa
  _term_ids = WiCa.wp_cache_get( Id, taxonomy + "_relationships" )
  print("WiTx.get_object_term_cache( Id={}, taxonomy={} ), _term_ids ={}"
        .format(Id, taxonomy, _term_ids))

  # We leave the priming of relationship caches to upstream functions.
  if False is _term_ids:
    return False
  
  # Backward compatibility for if a plugin is putting objects into the cache, rather than IDs.
  term_ids = array()
  for term_id in _term_ids:
    if Php.is_numeric( term_id ):
      term_ids[None] = Php.intval( term_id )
    elif Php.isset( term_id, 'term_id' ):
      term_ids[None] = Php.intval( term_id.term_id )
  
  # Fill the term objects.
  _prime_term_caches( term_ids )
  
  terms = array()
  for term_id in _term_ids:
    term = get_term( term_id, taxonomy )
    if WpC.WB.Wj.is_wp_error( term ):
      return term
    
    terms[None] = term
  
  return terms


def update_object_term_cache(object_ids, object_type):
  ''' Updates the cache for the given term object ID(s).
  Note: Due to performance concerns, great care should be taken to only update
  term caches when necessary. Processing time can increase exponentially depending
  on both the number of passed term IDs and the number of taxonomies those terms
  belong to.
  Caches will only be updated for terms not already cached.
  @param string|array object_ids  Comma-separated list or array of term object IDs.
  @param array|string object_type The taxonomy object type.
  @return void|False False if all of the terms in `object_ids` are already cached.
  '''
  if not object_ids:   # if Php.empty(locals(), 'object_ids')
    return

  if not Php.is_array(object_ids):
    object_ids = Php.explode(',', object_ids)

  object_ids = Php.array_map(Php.intval, object_ids)

  taxonomies = get_object_taxonomies(object_type)

  ids = array()
  for Id in Php.Array(object_ids):
    for taxonomy in taxonomies:
      if False == WiCa.wp_cache_get(Id, taxonomy +"_relationships"):
        ids[None] = Id
        break

  if not ids:    # if Php.empty(locals(), 'ids'):
    return False

  terms = wp_get_object_terms( ids, taxonomies, array(
    ('fields', 'all_with_object_id'),
    ('orderby', 'name'),
    ('update_term_meta_cache', False),
  ) )

  object_terms = array()
  for term in Php.Array(terms):
    object_terms[term.object_id][term.taxonomy][None] = term.term_id

  for Id in ids:
    for taxonomy in taxonomies:
      #if   not Php.isset(object_terms[Id], taxonomy):
      #  if not Php.isset(object_terms, Id):
      #    object_terms[Id] = array()
      #  object_terms[Id][taxonomy] = array()
      #Orig php is not good for py, as py will err for a[b][c] if not a[b]
      if not Php.isset(object_terms, Id):
        object_terms[Id] = array()
        if   not Php.isset(object_terms[Id], taxonomy):
          object_terms[Id][taxonomy] = array()

  for Id, value in object_terms.items():
    for taxonomy, terms in value.items():
      WiCa.wp_cache_add( Id, terms, taxonomy +"_relationships" )
#'''


def update_term_cache( terms, taxonomy = '' ):
  ''' Updates Terms to Taxonomy in cache.
  @since 2.3.0
  @param array  terms    List of term objects to change.
  @param string taxonomy Optional. Update Term to this taxonomy in cache. Default empty.
  '''
  for term in Php.Array(terms):
    # Create a copy in case the array was passed by reference.
    _term = Php.clone(term)

    # Object ID should not be cached.
    Php.unset( _term, 'object_id' )

    WiCa.wp_cache_add( term.term_id, _term, 'terms' )
#'''

#
# Private
#

def _get_term_hierarchy( taxonomy ):
  ''' Retrieves children of taxonomy as Term IDs.
  @param string taxonomy Taxonomy name.
  @return array Empty if taxonomy isn't hierarchical or returns children as Term IDs.
  '''
  if not is_taxonomy_hierarchical(taxonomy):
    return array()
  children = WiO.get_option(taxonomy +"_children")

  if Php.is_array(children):
    return children
  children = array()
  terms = get_terms(taxonomy,
          array( ('get', 'all'), ('orderby', 'id'), ('fields', 'id=>parent')) )
  for term_id, parent in terms.items():
    if parent > 0:
      children[parent][None] = term_id
  WiO.update_option(taxonomy +"_children", children)

  return children


#def _get...(term_id, terms, taxonomy, &ancestors = array()): # mutable array()
def _get_term_children( term_id, terms, taxonomy, ancestors=array() ):
  ''' Get the subset of terms that are descendants of term_id.
  If `terms` is an array of objects, then _get_term_children() returns an array of objects.
  If `terms` is an array of IDs, then _get_term_children() returns an array of IDs.
  @param int    term_id   The ancestor term: all returned terms should be descendants of `term_id`.
  @param array  terms     The set of terms - either an array of term objects or term IDs - from which those that
                           are descendants of term_id will be chosen.
  @param string taxonomy  The taxonomy which determines the hierarchy of the terms.
  @param array  ancestors Optional. Term ancestors that have already been identified. Passed by reference, to keep
                           track of found terms when recursing the hierarchy. The array of located ancestors is used
                           to prevent infinite recursion loops. For performance, `term_ids` are used as array keys,
                           with 1 as value. Default empty array.
  @return array|WP_Error The subset of terms that are descendants of term_id.
  '''
  empty_array = array()
  if not terms:    # if Php.empty(locals(), 'terms'):
    return empty_array

  term_list = array()
  has_children = _get_term_hierarchy(taxonomy)

  if 0 != term_id and not Php.isset(has_children, term_id):
    return empty_array

  # Include the term itself in the ancestors array, so we can properly detect when a loop has occurred.
  if not ancestors:    # if Php.empty(locals(), 'ancestors'):
    ancestors[ term_id ] = 1

  for term in Php.Array(terms):
    use_id = False
    if not Php.is_object(term):
      term = get_term(term, taxonomy)
      if WpC.WB.Wj.is_wp_error( term ):
        return term
      use_id = True

    # Don't recurse if we've already identified the term as a child - this indicates a loop.
    if Php.isset(ancestors, term.term_id):
      continue

    if term.parent == term_id:
      if use_id:
        term_list[None] = term.term_id
      else:
        term_list[None] = term

      if not Php.isset(has_children, term.term_id):
        continue

      ancestors[ term.term_id ] = 1

      children = _get_term_children( term.term_id, terms, taxonomy, ancestors)
      if children:
        term_list = Php.array_merge(term_list, children)

  return term_list


#def _pad_term_counts(&terms, taxonomy): #mutable array,no need to return terms
#Calling:  terms = pad_term_counts( terms, taxonomy ):
def _pad_term_counts( terms, taxonomy ):
  ''' Add count of children to parent count.
  Recalculates term counts by including items from child terms. Assumes all
  relevant children are already in the terms argument.
  @global wpdb wpdb WordPress database abstraction object.
  @param array  terms    List of term objects, passed by reference.
  @param string taxonomy Term context.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  # This function only works for hierarchical taxonomies like post categories.
  if not is_taxonomy_hierarchical( taxonomy ):
    return

  term_hier = _get_term_hierarchy(taxonomy)

  if not term_hier:    # if empty(locals(), 'term_hier'):
    return

  term_items = array()
  terms_by_id = array()
  term_ids = array()

  for key, term in Php.Array(terms).items():
    #terms_by_id[term.term_id] = & terms[key]  # mutable array
    terms_by_id[term.term_id] = terms[key]
    term_ids[term.term_taxonomy_id] = term.term_id

  # Get the object and term ids and stick them in a lookup table.
  tax_obj = get_taxonomy(taxonomy)
  object_types = WiF.esc_sql(tax_obj.object_type)
  results = wpdb.get_results("SELECT object_id, term_taxonomy_id FROM {} INNER"
           "JOIN {} ON object_id = ID WHERE term_taxonomy_id IN ("
           .format(wpdb.term_relationships, wpdb.posts) + Php.implode(',',
           Php.array_keys(term_ids)) + ") AND post_type IN ('" +
           Php.implode("', '", object_types) +"') AND post_status = 'publish'")
  for row in results:
    Id = term_ids[row.term_taxonomy_id]
    # $term_items[$id][$row->object_id] = isset($term_items[$id][$row->object_id]) ? ++$term_items[$id][$row->object_id] : 1
    term_items[Id][row.object_id] = term_items[Id].get(row.object_id, 0) + 1

  # Touch every ancestor's lookup row for each post in each term.
  for term_id in term_ids:
    child = term_id
    ancestors = array()
    #while ( !empty( $terms_by_id[$child] ) &&                  #VT Orig
    #        $parent = $terms_by_id[$child]->parent ) {         #VT Orig
    while True:                                                 #VT New
      parent = terms_by_id[child].parent                        #VT New
      if not (not Php.empty(terms_by_id, child) and parent ):   #VT New
        break                                                   #VT New
      ancestors[None] = child
      if not Php.empty(term_items, term_id):
        for item_id, touches in term_items[term_id].items():
          #term_items[parent][item_id] = isset(term_items[parent][item_id]
          #                              ) ? ++term_items[parent][item_id]: 1
          term_items[parent][item_id] = term_items[parent].get(item_id, 0) + 1
      child = parent

      if Php.in_array(parent, ancestors):
        break

  # Transfer the touched cells.
  for Id, items in Php.Array(term_items).items():
    if Php.isset(terms_by_id, Id):
      terms_by_id[Id].count = len(items)

  return terms


def _prime_term_caches( term_ids, update_meta_cache = True ):
  ''' Adds any terms from the given IDs to the cache that do not already exist in cache.
  @global wpdb wpdb WordPress database abstraction object.
  @param array term_ids          Array of term IDs.
  @param bool  update_meta_cache Optional. Whether to update the meta cache. Default True.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  non_cached_ids = _get_non_cached_ids( term_ids, 'terms' )
  if non_cached_ids:    # if not empty(locals(), 'non_cached_ids'):
    fresh_terms = wpdb.get_results( sprintf( "SELECT t.*, tt.* FROM {} AS t "
        "INNER JOIN {} AS tt ON t.term_id = tt.term_id WHERE t.term_id IN (%s)"
        .format(wpdb.terms, wpdb.term_taxonomy),
        Php.Join( ",", Php.array_map( int, non_cached_ids ) ) ) )
    
    update_term_cache( fresh_terms, update_meta_cache )
    
    if update_meta_cache:
      update_termmeta_cache( non_cached_ids )


#
# Default callbacks
#

def _update_post_term_count( terms, taxonomy ):
  ''' Will update term count based on object types of the current taxonomy.
  Private function for the default callback for post_tag and category
  taxonomies.
  @global wpdb wpdb WordPress database abstraction object.
  @param array  terms    List of Term taxonomy IDs.
  @param object taxonomy Current taxonomy object of terms.
  '''
  import wp.i.post as WiP
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  object_types = Php.Array( taxonomy.object_type )

  #foreach ( $object_types as &$object_type )
  #  list( $object_type ) = explode( ':', $object_type );
  #for i,object_type in enumerate(object_types):
  for k, object_type in object_types.items():
    object_types[k] = Php.explode( ':', object_type )[0]

  object_types = Php.array_unique( object_types )

  check_attachments = Php.array_search( 'attachment', object_types )
  if False != check_attachments:
    del object_types[ check_attachments ]
    check_attachments = True

  if object_types:
    object_types = WiF.esc_sql( Php.array_filter( object_types, WiP.post_type_exists ))

  for term in Php.Array(terms):
    count = 0

    # Attachments can be 'inherit' status, we need to base count off the parent's status if so.
    if check_attachments:
      count += int(wpdb.get_var( wpdb.prepare("SELECT COUNT(*) FROM {}, {} p1 "
          "WHERE p1.ID = {}.object_id AND ( post_status = 'publish' "
          "OR ( post_status = 'inherit' AND post_parent > 0 "
          "AND ( SELECT post_status FROM {} WHERE ID = p1.post_parent ) = "
         "'publish' ) ) AND post_type = 'attachment' AND term_taxonomy_id = %s"
          .format(wpdb.term_relationships, wpdb.posts, wpdb.term_relationships,
                  wpdb.posts), term ) ))  # PyMySQL %d->%s

    if object_types:
      count += int(wpdb.get_var( wpdb.prepare( "SELECT COUNT(*) FROM {}, {} "
          "WHERE {}.ID = {}.object_id AND post_status = 'publish' "
          "AND post_type IN ('".format(wpdb.term_relationships, wpdb.posts,
          wpdb.posts, wpdb.term_relationships) + Php.implode("', '", 
          object_types ) + "') AND term_taxonomy_id = %s", term ) ))  # %d->%s

    # This action is documented in wp-includes/taxonomy.php
    WiPg.do_action( 'edit_term_taxonomy', term, taxonomy.name )
    wpdb.update( wpdb.term_taxonomy, Php.compact(locals(), 'count' ),
                 array( ('term_taxonomy_id', term) ) )

    # This action is documented in wp-includes/taxonomy.php
    WiPg.do_action( 'edited_term_taxonomy', term, taxonomy.name )


def _update_generic_term_count( terms, taxonomy ):
  ''' Will update term count based on number of objects.
  Default callback for the 'link_category' taxonomy.
  @global wpdb wpdb WordPress database abstraction object.
  @param array  terms    List of term taxonomy IDs.
  @param object taxonomy Current taxonomy object of terms.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  for term in Php.Array(terms):
    count = wpdb.get_var( wpdb.prepare( "SELECT COUNT(*) FROM {} WHERE "
              "term_taxonomy_id = %s".format(wpdb.term_relationships), term ) )

    # This action is documented in wp-includes/taxonomy.php
    WiPg.do_action( 'edit_term_taxonomy', term, taxonomy.name )
    wpdb.update( wpdb.term_taxonomy, Php.compact(locals(), 'count' ),
                 array( ('term_taxonomy_id', term) ) )

    # This action is documented in wp-includes/taxonomy.php
    WiPg.do_action( 'edited_term_taxonomy', term, taxonomy.name )


def _split_shared_term( term_id, term_taxonomy_id, record = True ):
  ''' Create a new term for a term_taxonomy item that currently shares its term
  with another term_taxonomy.
  @global wpdb wpdb WordPress database abstraction object.
  @param int|object term_id          ID of the shared term, or the shared term object.
  @param int|object term_taxonomy_id ID of the term_taxonomy item to receive a new term, or the term_taxonomy object
                                      (corresponding to a row from the term_taxonomy table).
  @param bool       record           Whether to record data about the split term in the options table. The recording
                                      process has the potential to be resource-intensive, so during batch operations
                                      it can be beneficial to skip inline recording and do it just once, after the
                                      batch is processed. Only set this to `False` if you know what you are doing.
                                      Default: True.
  @return int|WP_Error When the current term does not need to be split (or cannot be split on the current
                       database schema), `term_id` is returned. When the term is successfully split, the
                       new term_id is returned. A WP_Error is returned for miscellaneous errors.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if Php.is_object( term_id ):
    shared_term = term_id
    term_id = int( shared_term.term_id )

  if Php.is_object( term_taxonomy_id ):
    term_taxonomy = term_taxonomy_id
    term_taxonomy_id = int( term_taxonomy.term_taxonomy_id )

  # If there are no shared term_taxonomy rows, there's nothing to do here.
  shared_tt_count = wpdb.get_var( wpdb.prepare( "SELECT COUNT(*) FROM {} tt "
          "WHERE tt.term_id = %s AND tt.term_taxonomy_id != %s"
          .format(wpdb.term_taxonomy), term_id, term_taxonomy_id ) )  # %d->%s

  if not shared_tt_count:
    return term_id

  # Verify that the term_taxonomy_id passed to the function is actually associated with the term_id.
  # If there's a mismatch, it may mean that the term is already split. Return the actual term_id from the db.
  check_term_id = wpdb.get_var( wpdb.prepare( "SELECT term_id FROM {} WHERE "
       "term_taxonomy_id = %s".format(wpdb.term_taxonomy), term_taxonomy_id ) )
  if check_term_id != term_id:
    return check_term_id

  # Pull up data about the currently shared slug, which we'll use to populate the new one.
  if Php.empty(locals(), 'shared_term'):
    shared_term = wpdb.get_row( wpdb.prepare( "SELECT t.* FROM {} t WHERE "
             "t.term_id = %s".format(wpdb.terms), term_id ) )  # PyMySQL %d->%s

  new_term_data = array(
    ('name', shared_term.name),
    ('slug', shared_term.slug),
    ('term_group', shared_term.term_group),
  )

  if False == wpdb.insert( wpdb.terms, new_term_data ):
    return WcE.WP_Error( 'db_insert_error', __( 'Could not split shared term.'
                        ), wpdb.last_error )

  new_term_id = int(wpdb.insert_id)

  # Update the existing term_taxonomy to point to the newly created term.
  wpdb.update( wpdb.term_taxonomy,
    array( ('term_id', new_term_id) ),
    array( ('term_taxonomy_id', term_taxonomy_id) )
  )

  # Reassign child terms to the new parent.
  if Php.empty(locals(), 'term_taxonomy'):
    term_taxonomy = wpdb.get_row( wpdb.prepare( "SELECT * FROM {} WHERE "
        "term_taxonomy_id = %s".format(wpdb.term_taxonomy), term_taxonomy_id ))

  children_tt_ids = wpdb.get_col( wpdb.prepare( "SELECT term_taxonomy_id FROM "
          "{} WHERE parent = %s AND taxonomy = %s".format(wpdb.term_taxonomy),
          term_id, term_taxonomy.taxonomy ) )  # PyMySQL %d->%s
  if children_tt_ids:    # if not Php.empty(locals(), 'children_tt_ids'):
    for child_tt_id in children_tt_ids:
      wpdb.update( wpdb.term_taxonomy,
        array( ('parent', new_term_id) ),
        array( ('term_taxonomy_id', child_tt_id) )
      )
      clean_term_cache( term_id, term_taxonomy.taxonomy )
  else:
    # If the term has no children, we must force its taxonomy cache to be rebuilt separately.
    clean_term_cache( new_term_id, term_taxonomy.taxonomy )

  # Clean the cache for term taxonomies formerly shared with the current term.
  shared_term_taxonomies = wpdb.get_row( wpdb.prepare(
                    "SELECT taxonomy FROM {} WHERE term_id = %s"
                    .format(wpdb.term_taxonomy), term_id ) )  # PyMySQL %d->%s
  if shared_term_taxonomies:
    for shared_term_taxonomy in shared_term_taxonomies:
      clean_term_cache( term_id, shared_term_taxonomy )

  # Keep a record of term_ids that have been split, keyed by old term_id. See wp_get_split_term().
  if record:
    split_term_data = WiO.get_option( '_split_terms', array() )
    if Php.isset(split_term_data, term_id):
      split_term_data[ term_id ] = array()

    split_term_data[ term_id ][ term_taxonomy.taxonomy ] = new_term_id
    WiO.update_option( '_split_terms', split_term_data )

  # If we've just split the final shared term, set the "finished" flag.
  shared_terms_exist = wpdb.get_results(
    '''SELECT tt.term_id, t.*, count(*) as term_tt_count FROM {} tt
     LEFT JOIN {} t ON t.term_id = tt.term_id
     GROUP BY t.term_id
     HAVING term_tt_count > 1
     LIMIT 1'''.format(wpdb.term_taxonomy, wpdb.terms)
  )
  if not shared_terms_exist:
    WiO.update_option( 'finished_splitting_shared_terms', True )

  # Fires after a previously shared taxonomy term is split into two separate terms.
  # @param int    term_id          ID of the formerly shared term.
  # @param int    new_term_id      ID of the new term created for the term_taxonomy_id.
  # @param int    term_taxonomy_id ID for the term_taxonomy row affected by the split.
  # @param string taxonomy         Taxonomy for the split term.
  WiPg.do_action( 'split_shared_term', term_id, new_term_id, term_taxonomy_id, term_taxonomy.taxonomy )

  return new_term_id


def _wp_batch_split_terms():
  ''' Splits a batch of shared taxonomy terms.
  @global wpdb wpdb WordPress database abstraction object.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  lock_name = 'term_split.lock'

  # Try to lock.
  lock_result = wpdb.query( wpdb.prepare( "INSERT IGNORE INTO `{}` "
         "( `option_name`, `option_value`, `autoload` ) VALUES (%s, %s, 'no') "
         "/* LOCK */".format(wpdb.options), lock_name, time() ) )

  if not lock_result:
    lock_result = WiO.get_option( lock_name )

    # Bail if we were unable to create a lock, or if the existing lock is still valid.
    if not lock_result or ( lock_result > ( time() - HOUR_IN_SECONDS ) ):
      wp_schedule_single_event( time() + ( 5 * MINUTE_IN_SECONDS ), 'wp_split_shared_term_batch' )
      return

  # Update the lock, as by this point we've definitely got a lock, just need to fire the actions.
  WiO.update_option( lock_name, time() )

  # Get a list of shared terms (those with more than one associated row in term_taxonomy).
  shared_terms = wpdb.get_results(
    '''SELECT tt.term_id, t.*, count(*) as term_tt_count FROM {} tt
     LEFT JOIN {} t ON t.term_id = tt.term_id
     GROUP BY t.term_id
     HAVING term_tt_count > 1
     LIMIT 10'''.format(wpdb.term_taxonomy, wpdb.terms)
  )

  # No more terms, we're done here.
  if not shared_terms:
    WiO.update_option( 'finished_splitting_shared_terms', True )
    WiO.delete_option( lock_name )
    return

  # Shared terms found? We'll need to run this script again.
  wp_schedule_single_event( time() + ( 2 * MINUTE_IN_SECONDS ), 'wp_split_shared_term_batch' )

  # Rekey shared term array for faster lookups.
  _shared_terms = array()
  for shared_term in shared_terms:
    term_id = int( shared_term.term_id )
    _shared_terms[ term_id ] = shared_term

  shared_terms = _shared_terms

  # Get term taxonomy data for all shared terms.
  shared_term_ids = Php.implode( ',', Php.array_keys( shared_terms ) )
  shared_tts = wpdb.get_results( "SELECT * FROM {} WHERE `term_id` IN ({})"
                                .format(wpdb.term_taxonomy, shared_term_ids) )

  # Split term data recording is slow, so we do it just once, outside the loop.
  split_term_data = WiO.get_option( '_split_terms', array() )
  #skipped_first_term = taxonomies = array()
  skipped_first_term = array()  # bad if a = b = array() as it'll be shared []
  taxonomies = array()
  for shared_tt in shared_tts:
    term_id = int( shared_tt.term_id )

    # Don't split the first tt belonging to a given term_id.
    if not Php.isset(skipped_first_term, term_id):
      skipped_first_term[ term_id ] = 1
      continue

    if not Php.isset(split_term_data, term_id):
      split_term_data[ term_id ] = array()

    # Keep track of taxonomies whose hierarchies need flushing.
    if not Php.isset(taxonomies, shared_tt.taxonomy):
      taxonomies[ shared_tt.taxonomy ] = 1

    # Split the term.
    split_term_data[ term_id ][ shared_tt.taxonomy ] = _split_shared_term( shared_terms[ term_id ], shared_tt, False )

  # Rebuild the cached hierarchy for each affected taxonomy.
  for tax in Php.array_keys( taxonomies ):
    WiO.delete_option( tax +"_children" )
    _get_term_hierarchy( tax )

  WiO.update_option( '_split_terms', split_term_data )

  WiO.delete_option( lock_name )


def _wp_check_for_scheduled_split_terms():
  ''' In order to avoid the _wp_batch_split_terms() job being accidentally removed,
  check that it's still scheduled while we haven't finished splitting terms.
  @ignore
  '''
  if (not WiO.get_option( 'finished_splitting_shared_terms' ) and
      not wp_next_scheduled( 'wp_split_shared_term_batch' )):
    wp_schedule_single_event( time() + MINUTE_IN_SECONDS, 'wp_split_shared_term_batch' )


def _wp_check_split_default_terms( term_id, new_term_id, term_taxonomy_id, taxonomy ):
  ''' Check default categories when a term gets split to see if any of them need to be updated.
  @ignore
  @param int    term_id          ID of the formerly shared term.
  @param int    new_term_id      ID of the new term created for the term_taxonomy_id.
  @param int    term_taxonomy_id ID for the term_taxonomy row affected by the split.
  @param string taxonomy         Taxonomy for the split term.
  '''
  if 'category' != taxonomy:
    return

  for option in ( 'default_category', 'default_link_category', 'default_email_category' ):
    if term_id == WiO.get_option( option, -1 ):
      WiO.update_option( option, new_term_id )


def _wp_check_split_terms_in_menus( term_id, new_term_id, term_taxonomy_id, taxonomy ):
  ''' Check menu items when a term gets split to see if any of them need to be updated.
  @ignore
  @since 4.2.0
  @global wpdb wpdb WordPress database abstraction object.
  @param int    term_id          ID of the formerly shared term.
  @param int    new_term_id      ID of the new term created for the term_taxonomy_id.
  @param int    term_taxonomy_id ID for the term_taxonomy row affected by the split.
  @param string taxonomy         Taxonomy for the split term.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  post_ids = wpdb.get_col( wpdb.prepare(
    '''SELECT m1.post_id
    FROM {} AS m1
      INNER JOIN {} AS m2 ON ( m2.post_id = m1.post_id )
      INNER JOIN {} AS m3 ON ( m3.post_id = m1.post_id )
    WHERE ( m1.meta_key = '_menu_item_type' AND m1.meta_value = 'taxonomy' )
      AND ( m2.meta_key = '_menu_item_object' AND m2.meta_value = '%s' )
      AND ( m3.meta_key = '_menu_item_object_id' AND m3.meta_value = %s )'''
      .format(wpdb.postmeta, wpdb.postmeta, wpdb.postmeta),  # PyMySQL %d->%s
    taxonomy,
    term_id
  ) )

  if post_ids:
    for post_id in post_ids:
      update_post_meta( post_id, '_menu_item_object_id', new_term_id, term_id )


def _wp_check_split_nav_menu_terms( term_id, new_term_id, term_taxonomy_id, taxonomy ):
  ''' If the term being split is a nav_menu, change associations.
  @ignore
  @param int    term_id          ID of the formerly shared term.
  @param int    new_term_id      ID of the new term created for the term_taxonomy_id.
  @param int    term_taxonomy_id ID for the term_taxonomy row affected by the split.
  @param string taxonomy         Taxonomy for the split term.
  '''
  if 'nav_menu' != taxonomy:
    return

  # Update menu locations.
  locations = get_nav_menu_locations()
  for location, menu_id in locations.items():
    if term_id == menu_id:
      locations[ location ] = new_term_id
  set_theme_mod( 'nav_menu_locations', locations )


def wp_get_split_terms( old_term_id ):
  ''' Get data about terms that previously shared a single term_id, but have since been split.
  @param int old_term_id Term ID. This is the old, pre-split term ID.
  @return array Array of new term IDs, keyed by taxonomy.
  '''
  split_terms = WiO.get_option( '_split_terms', array() )

  terms = array()
  if old_term_id in split_terms:
    terms = split_terms[ old_term_id ]

  return terms


def wp_get_split_term( old_term_id, taxonomy ):
  ''' Get the new term ID corresponding to a previously split term.
  @param int    old_term_id Term ID. This is the old, pre-split term ID.
  @param string taxonomy    Taxonomy that the term belongs to.
  @return int|False If a previously split term is found corresponding to the old term_id and taxonomy,
                    the new term_id will be returned. If no previously split term is found matching
                    the parameters, returns False.
  '''
  split_terms = wp_get_split_terms( old_term_id )

  term_id = False
  if Php.isset(split_terms, taxonomy):
    term_id = int(split_terms[ taxonomy ])

  return term_id


def wp_term_is_shared( term_id ):
  ''' Determine whether a term is shared between multiple taxonomies.
  Shared taxonomy terms began to be split in 4.3, but failed cron tasks or other delays in upgrade routines may cause
  shared terms to remain.
  @param int term_id
  @return bool
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb

  if WiO.get_option( 'finished_splitting_shared_terms' ):
    return False

  tt_count = wpdb.get_var( wpdb.prepare( "SELECT COUNT(*) FROM {} WHERE "
      "term_id = %s".format(wpdb.term_taxonomy), term_id ) )  # PyMySQL %d->%s

  return tt_count > 1


def get_term_link( term, taxonomy = '' ):
  ''' Generate a permalink for a taxonomy term archive.
  @global WP_Rewrite wp_rewrite
  @param object|int|string term     The term object, ID, or slug whose link will be retrieved.
  @param string            taxonomy Optional. Taxonomy. Default empty.
  @return string|WP_Error HTML link to taxonomy term archive on success, WP_Error if term does not exist.
  '''
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite

  if not Php.is_object(term):
    if Php.is_int( term ):
      term = get_term( term, taxonomy )
    else:
      term = get_term_by( 'slug', term, taxonomy )

  if not Php.is_object(term):
    term = WcE.WP_Error('invalid_term', __('Empty Term'))

  if WpC.WB.Wj.is_wp_error( term ):
    return term

  taxonomy = term.taxonomy

  termlink = wp_rewrite.get_extra_permastruct(taxonomy)

  slug = term.slug
  t = get_taxonomy(taxonomy)

  if not termlink:   # if Php.empty(locals(), 'termlink'):
    if 'category' == taxonomy:
      termlink = '?cat=' + term.term_id
    elif t.query_var:
      termlink = "?{}={}".format(t.query_var, slug)
    else:
      termlink = "?taxonomy={}&term={}".format(taxonomy, slug)
    termlink = home_url(termlink)
  else:
    if t.rewrite['hierarchical']:
      hierarchical_slugs = array()
      ancestors = get_ancestors( term.term_id, taxonomy, 'taxonomy' )
      for ancestor in Php.Array(ancestors):
        ancestor_term = get_term(ancestor, taxonomy)
        hierarchical_slugs[None] = ancestor_term.slug
      hierarchical_slugs = Php.array_reverse(hierarchical_slugs)
      hierarchical_slugs[None] = slug
      termlink = str_replace("%"+ taxonomy +"%", Php.implode('/', hierarchical_slugs), termlink)
    else:
      termlink = str_replace("%"+ taxonomy +"%", slug, termlink)
    termlink = home_url( user_trailingslashit(termlink, 'category') )
  # Back Compat filters.
  if 'post_tag' == taxonomy:

    # Filters the tag link.
    # @param string termlink Tag link URL.
    # @param int    term_id  Term ID.
    termlink = WiPg.apply_filters( 'tag_link', termlink, term.term_id )
  elif 'category' == taxonomy:

    # Filters the category link.
    # @param string termlink Category link URL.
    # @param int    term_id  Term ID.
    termlink = WiPg.apply_filters( 'category_link', termlink, term.term_id )

  # Filters the term link.
  # @since 2.5.0
  # @param string termlink Term link URL.
  # @param object term     Term object.
  # @param string taxonomy Taxonomy slug.
  return WiPg.apply_filters( 'term_link', termlink, term, taxonomy )


def the_taxonomies( args = array() ):
  ''' Display the taxonomies of a post with available options.
  This function can be used within the loop to display the taxonomies for a
  post without specifying the Post ID. You can also use it outside the Loop to
  display the taxonomies for a specific post.
  @param array args {
      Arguments about which post to use and how to format the output. Shares all of the arguments
      supported by get_the_taxonomies(), in addition to the following.
      @type  int|WP_Post post   Post ID or object to get taxonomies of. Default current post.
      @type  string      before Displays before the taxonomies. Default empty string.
      @type  string      sep    Separates each taxonomy. Default is a space.
      @type  string      after  Displays after the taxonomies. Default empty string.
  } '''
  defaults = array(
    ('post'  , 0  ),
    ('before', '' ),
    ('sep'   , ' '),
    ('after' , '' ),
  )

  r = WiFc.wp_parse_args( args, defaults )

  #echo r['before'] + join( r['sep'], get_the_taxonomies( r['post'], r ) ) + r['after']
  return r['before'] + Php.Join( r['sep'], get_the_taxonomies( r['post'], r ) ) + r['after']


def get_the_taxonomies( post = 0, args = array() ):
  ''' Retrieve all taxonomies associated with a post.
  This function can be used within the loop. It will also return an array of
  the taxonomies with links to the taxonomy and name.
  @param int|WP_Post post Optional. Post ID or WP_Post object. Default is global post.
  @param array args {
      Optional. Arguments about how to format the list of taxonomies. Default empty array.
      @type string template      Template for displaying a taxonomy label and list of terms.
                                  Default is "Label: Terms."
      @type string term_template Template for displaying a single term in the list. Default is the term name
                                  linked to its archive.
  } @return array List of taxonomies.
  '''
  post = get_post( post )

  args = WiFc.wp_parse_args( args, array(
    # translators: %s: taxonomy label, %l:
    #    list of terms formatted as per term_template
    ('template'     , __( '%s: %l.' )),
    ('term_template', '<a href="%1$s">%2$s</a>'),
  ) )

  taxonomies = array()

  if not post:
    return taxonomies

  for taxonomy in get_object_taxonomies( post ):
    t = Php.Array( get_taxonomy( taxonomy ))
    if Php.empty(t, 'label'):
      t['label'] = taxonomy
    if Php.empty(t, 'args'):
      t['args'] = array()
    if Php.empty(t, 'template'):
      t['template'] = args['template']
    if Php.empty(t, 'term_template'):
      t['term_template'] = args['term_template']

    terms = get_object_term_cache( post.ID, taxonomy )
    if False == terms:
      terms = wp_get_object_terms( post.ID, taxonomy, t['args'] )

    links = array()

    for term in terms:
      links[None] = wp_sprintf( t['term_template'], esc_attr( get_term_link( term ) ), term.name )

    if links:
      taxonomies[taxonomy] = wp_sprintf( t['template'], t['label'], links, terms )

  return taxonomies


def get_post_taxonomies( post = 0 ):
  ''' Retrieve all taxonomies of a post with just the names.
  @param int|WP_Post post Optional. Post ID or WP_Post object. Default is global post.
  @return array
  '''
  post = get_post( post )

  return get_object_taxonomies(post)


def is_object_in_term( object_id, taxonomy, terms = None ):
  ''' Determine if the given object is associated with any of the given terms.
  The given terms are checked against the object's terms' term_ids, names and slugs.
  Terms given as integers will only be checked against the object's terms' term_ids.
  If no terms are given, determines if object is associated with any terms in the given taxonomy.
  @param int              object_id ID of the object (post ID, link ID, ...).
  @param string           taxonomy  Single taxonomy name.
  @param int|string|array terms     Optional. Term term_id, name, slug or array of said. Default None.
  @return bool|WP_Error WP_Error on input error.
  '''
  object_id = int(object_id)
  if not object_id:
    return WcE.WP_Error( 'invalid_object', __( 'Invalid object ID' ) )

  object_terms = get_object_term_cache( object_id, taxonomy )
  if False == object_terms:
    object_terms = wp_get_object_terms( object_id, taxonomy,
                                   array( ('update_term_meta_cache', False) ))
    if WpC.WB.Wj.is_wp_error( object_terms ):
      return object_terms
    
    WiCa.wp_cache_set( object_id, WiFc.wp_list_pluck( object_terms, 'term_id' ), taxonomy +"_relationships" )

  if WpC.WB.Wj.is_wp_error( object_terms ):
    return object_terms
  if not object_terms:    # if Php.empty(locals, 'object_terms'):
    return False
  if not terms:    # if Php.empty(locals, 'terms'):
    return not Php.empty(locals(), 'object_terms')
    #return bool(object_terms)

  terms = Php.Array( terms )

  #if ints = Php.array_filter( terms, lambda x: isinstance(x, int)):
  ints = Php.array_filter( terms, Php.is_int )
  if ints:
    strs = Php.array_diff( terms, ints )
  else:
    #strs =& terms
    #[PHP =& Reference assignment op](stackoverflow.com/questions/1768343/)
    strs = terms   # = same mutable array()

  for object_term in object_terms:
    # If term is an int, check against term_ids only.
    if ints and Php.in_array( object_term.term_id, ints ):
      return True

    if strs:
      # Only check numeric strings against term_id, to avoid False matches
      #    due to type juggling.
      numeric_strs = Php.array_map( Php.intval,
                                    Php.array_filter( strs, Php.is_numeric ))
      #if object_term.term_id in numeric_strs:
      if Php.in_array( object_term.term_id, numeric_strs, True ):
        return True

      if Php.in_array( object_term.name, strs ): return True
      if Php.in_array( object_term.slug, strs ): return True

  return False
#'''


def is_object_in_taxonomy( object_type, taxonomy ):
  '''Determine if the given object type is associated with the given taxonomy.
  @param string object_type Object type string.
  @param string taxonomy    Single taxonomy name.
  @return bool True if object is associated with the taxonomy, otherwise False.
  '''
  taxonomies = get_object_taxonomies( object_type )
  if not taxonomies:    # if Php.empty(locals(), 'taxonomies'):
    return False

  return Php.in_array( taxonomy, taxonomies )


def get_ancestors( object_id = 0, object_type = '', resource_type = '' ):
  ''' Get an array of ancestor IDs for a given object.
  @param int    object_id     Optional. The ID of the object. Default 0.
  @param string object_type   Optional. The type of object for which we'll be retrieving
                               ancestors. Accepts a post type or a taxonomy name. Default empty.
  @param string resource_type Optional. Type of resource object_type is. Accepts 'post_type'
                               or 'taxonomy'. Default empty.
  @return array An array of ancestors from lowest to highest in the hierarchy.
  '''
  import wp.i.post as WiP
  object_id = int(object_id)

  ancestors = array()

  if not object_id:    # if Php.empty(locals(), 'object_id'):

    # This filter is documented in wp-includes/taxonomy.php
    return WiPg.apply_filters( 'get_ancestors', ancestors, object_id, object_type, resource_type )

  if not resource_type:
    if is_taxonomy_hierarchical( object_type ):
      resource_type = 'taxonomy'
    elif WiP.post_type_exists( object_type ):
      resource_type = 'post_type'

  if 'taxonomy' == resource_type:
    term = get_term(object_id, object_type)
    while ( not WpC.WB.Wj.is_wp_error(term) and not Php.empty(term, 'parent') and
            not Php.in_array( term.parent, ancestors ) ):
      ancestors[None] = int(term.parent)
      term = get_term(term.parent, object_type)

  elif 'post_type' == resource_type:
    ancestors = get_post_ancestors(object_id)

  # Filters a given object's ancestors.
  # @param array  ancestors     An array of object ancestors.
  # @param int    object_id     Object ID.
  # @param string object_type   Type of object.
  # @param string resource_type Type of resource object_type is.
  return WiPg.apply_filters( 'get_ancestors', ancestors, object_id, object_type, resource_type )


def wp_get_term_taxonomy_parent_id( term_id, taxonomy ):
  ''' Returns the term's parent's term_ID.
  @param int    term_id  Term ID.
  @param string taxonomy Taxonomy name.
  @return int|False False on error.
  '''
  term = get_term( term_id, taxonomy )
  if not term or WpC.WB.Wj.is_wp_error( term ):
    return False
  return int(term.parent)


def wp_check_term_hierarchy_for_loops( parent, term_id, taxonomy ):
  ''' Checks the given subset of the term hierarchy for hierarchy loops.
  Prevents loops from forming and breaks those that it finds.
  Attached to the {@see 'wp_update_term_parent'} filter.
  @param int    parent   `term_id` of the parent for the term we're checking.
  @param int    term_id  The term we're checking.
  @param string taxonomy The taxonomy of the term we're checking.
  @return int The new parent for the term.
  '''
  # Nothing fancy here - bail
  if not parent:
    return 0

  # Can't be its own parent.
  if parent == term_id:
    return 0

  # Now look for larger loops.
  loop = wp_find_hierarchy_loop( 'wp_get_term_taxonomy_parent_id',
                                 term_id, parent, array( taxonomy ) )
  if not loop:
    return parent  # No loop

  # Setting parent to the given value causes a loop.
  if Php.isset(loop, term_id):
    return 0

  # There's a loop, but it doesn't contain term_id. Break the loop.
  for loop_member in Php.array_keys( loop ):
    wp_update_term( loop_member, taxonomy, array( ('parent', 0) ) )

  return parent
#'''


# wp-settings.php:
#create_initial_taxonomies()


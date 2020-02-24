import pyx.php      as Php
import wp.conf      as WpC
import wp.i.cache   as WiCa
import wp.i.format  as WiF
array = Php.array


class WP_User(Php.stdClass):
  ''' Core class used to implement the WP_User object.
  @property string nickname
  @property string description
  @property string user_description
  @property string first_name
  @property string user_firstname
  @property string last_name
  @property string user_lastname
  @property string user_login
  @property string user_pass
  @property string user_nicename
  @property string user_email
  @property string user_url
  @property string user_registered
  @property string user_activation_key
  @property string user_status
  @property int    user_level
  @property string display_name
  @property string spam
  @property string deleted
  @property string locale
  Class variables are shared among class instances
  '''
  def __init__(self, Id = 0, name ='', blog_id =''):
    ''' Retrieves the userdata and passes it to WP_User.Init().
    @global wpdb wpdb  WordPress database abstraction object.
    @param int|string|stdClass|WP_User Id User's ID, a WP_User object,
                        or a user object from the DB.
    @param string name Optional. User's username
    @param int blog_id Optional Site ID, defaults to current site.
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    # php @static = py class var!!   @access private
    self.back_compat_keys = array()    # {}

    self.data   =None#obj  User data container
    self.ID     = 0  #int  user's ID
    self.caps   = array() # The individual capabilities the user has been given
    self.cap_key=None#str  User metadata option name
    self.roles  = array() # The roles the user is part of
    # All caps the user has, including individual and role based
    self.allcaps= array()
    #@access private
    self.Filter =None     #str  filter context applied to user data fields

    if not Php.isset(self, 'back_compat_keys'):
      #prefix = GLOBALS['wpdb'].prefix
      prefix  = WpC.WPfx
      setattr(self, back_compat_keys, array(
          ('user_firstname'  , 'first_name'),
          ('user_lastname'   , 'last_name'),
          ('user_description', 'description'),
          ('user_level'      , prefix +'user_level'),
          (prefix +'usersettings'     , prefix +'user-settings'),
          (prefix +'usersettingstime' , prefix +'user-settings-time'),
      ))
    if isinstance(Id, WP_User ):
      self.Init( Id.data, blog_id)
      return
    #elif isinstance( Id, object):   # None, 1, 'a' all are objects!!
    #elif isclass(Id):               # isclass, not instance of a classt
    elif Php.is_object(Id):
      self.Init( Id, blog_id)
      return

    if Id and not isinstance(Id, int):
      name = Id
      Id = 0

    if Id:
      data = self.get_data_by( 'id', Id )
    else:
      data = self.get_data_by( 'login', name )

    if data:
      self.Init( data, blog_id)
    else:
      self.data = Php.stdClass()


  def Init(self, data, blog_id = ''):
    ''' Sets up object properties, including capabilities.
        @param object data    User DB row object.
        @param int    blog_id Optional. The site ID to initialize for.
    '''
    self.data = data
    self.ID = int(self.data.ID)
    self.for_blog( blog_id )


  @staticmethod
  def get_data_by( field, value ):
    ''' replicate wp-includes/class-wp-user.php: class WP_User
    Return only the main user fields
    @global wpdb wpdb WordPress database abstraction object.
    @param string field The field to query against:
                         'id', 'ID', 'slug', 'email' or 'login'.
    @param string|int value The field value
    @return object|False Raw user object
    '''
    import wp.i.user as WiU
    wpdb = WpC.WB.Wj.wpdb  # global wpdb
    # 'ID' is an alias of 'id'.
    if 'ID' == field:
      field = 'id'

    if 'id' == field:
      # Make sure the value is numeric to avoid casting objects, e.g. to int 1
      if not Php.is_numeric(value):
        return False
      value = int ( value )
      if value < 1:
        return False
    else:
      value = value.strip()

    if not value:
      return False

    if field == 'id':
        user_id = value
        db_field = 'ID'
    elif field == 'slug':
        user_id = WiCa.wp_cache_get(value, 'userslugs')
        db_field = 'user_nicename'
    elif field == 'email':
        user_id = WiCa.wp_cache_get(value, 'useremail')
        db_field = 'user_email'
    elif field == 'login':
        value = WiF.sanitize_user( value )
        user_id = WiCa.wp_cache_get(value, 'userlogins')
        db_field = 'user_login'
    else:
        return False

    if False is not user_id:
      user = WiCa.wp_cache_get( user_id, 'users' )
      if user:
        return user

    user = wpdb.get_row( wpdb.prepare(
      "SELECT * FROM {} WHERE {} = %s".format(wpdb.users, db_field), value ))
    if not user:
      return False

    WiU.update_user_caches( user )
    return user
  # wp> WP_User::get_data_by('ID', 1001) # output: Raw user object

  @staticmethod
  def __call( name, arguments ):
    ''' Makes private/protected methods readable for backward compatibility.
    @param callable name      Method to call.
    @param array    arguments Arguments to pass when calling.
    @return mixed|False Return value of the callback, False otherwise.
    '''
    if '_init_caps' == name:
      return Php.call_user_func_array( array( this, name ), arguments )
    return False

  def __isset(self, key ):
    '''   Magic method for checking the existence of a certain custom field.
    @access public
    @param string key User meta key to check if set.
    @return bool Whether the given user meta key is set.
    '''
    if 'id' == key:
      Php._deprecated_argument( 'WP_User.id', '2.1.0',
        Php.sprintf( # translators: %s: WP_User.ID
          __( 'Use %s instead.' ), '<code>WP_User.ID</code>'))
      key = 'ID'

    if Php.isset( this.data, key ):
      return True

    if Php.isset( getattr(self, back_compat_keys), key ):
      key = getattr(self, back_compat_keys)[ key ]

    return metadata_exists( 'user', this.ID, key )


  def __get(self, key ):
    '''   Magic method for accessing custom fields.
    @access public
    @param string key User meta key to retrieve.
    @return mixed Value of the given user meta key (if set). If `key` is 'id',
                  the user ID.
    '''
    import wp.i.user as WiU
    if 'id' == key:
      Php._deprecated_argument( 'WP_User.id', '2.1.0',
        Php.sprintf( # translators: %s: WP_User.ID
          __( 'Use %s instead.' ), '<code>WP_User.ID</code>'))
      return this.ID

    if Php.isset( this.data, key ):
      value = getattr(this.data, key)
    else:
      if Php.isset( getattr(self, back_compat_keys), key ):
        key = getattr(self, back_compat_keys)[ key ]
      value = WiU.get_user_meta( this.ID, key, True )

    if self.filter:
      value = WiU.sanitize_user_field( key, value, self.ID, self.filter )

    return value


  def __set(self, key, value ):
    '''   Magic method for setting custom user fields.
    This method does not update custom fields in the database. It only stores
    the value on the WP_User instance.
    @access public
    @param string key   User meta key.
    @param mixed  value User meta value.
    '''
    if 'id' == key:
      Php._deprecated_argument( 'WP_User.id', '2.1.0',
        Php.sprintf( # translators: %s: WP_User.ID
          __( 'Use %s instead.' ), '<code>WP_User.ID</code>'))
      self.ID = value
      return

    setattr(this.data, key, value)


  def __unset(self, key ):
    '''   Magic method for unsetting a certain custom field.
    @access public
    @param string key User meta key to unset.
    '''
    if 'id' == key:
      Php._deprecated_argument( 'WP_User.id', '2.1.0',
        Php.sprintf( # translators: %s: WP_User.ID
          __( 'Use %s instead.' ), '<code>WP_User.ID</code>'))

    if Php.isset( self.data, key ):
      Php.unset( this.data, key ) # delattr( this.data, key )

    if Php.isset( getattr(self, back_compat_keys), key ):
      Php.unset(  getattr(self, back_compat_keys), key )


  def exists(self,):
    '''   Determine whether the user exists in the database.
    @access public
    @return bool True if user exists in the database, False if not.
    '''
    return not Php.empty( self, 'ID' )


  def get(self, key ):
    '''   Retrieve the value of a property or meta key.
    Retrieves from the users and usermeta table.
    @param string key Property
    @return mixed
    '''
    return self.__get( key )


  def has_prop(self, key ):
    '''   Determine whether a property or meta key is set
    Consults the users and usermeta tables.
    @param string key Property
    @return bool
    '''
    return self.__isset( key )


  def to_array(self,):
    '''   Return an array representation.
    @return array Array representation.
    '''
    return Php.get_object_vars( self.data )


  def _init_caps( self, cap_key = '' ):
    ''' Set up capability object properties.
      Will set the value for the 'cap_key' property to current database table
      prefix, followed by 'capabilities'. Will then check to see if the
      property matching the 'cap_key' exists and is an array. If so,it will be
      used.
      @param string cap_key Optional capability key
    '''
    wpdb = WpC.WB.Wj.wpdb  # global wpdb
    import wp.i.user as WiU
    if not cap_key:   # if empty
      self.cap_key = wpdb.get_blog_prefix() + 'capabilities'
    else:
      self.cap_key = cap_key

    self.caps = WiU.get_user_meta( self.ID, self.cap_key, True )
    #if not isinstance(self.caps, (dict,array)):
    if not Php.is_array(self.caps):
      self.caps = array()   # array()    # {}
    self.get_role_caps()




  def get_role_caps(self,):
    ''' Retrieve all of the role capabilities and merge with individual caps.
    All of the capabilities of the roles the user belongs to are merged with
    the users individual roles. This also means that the user can be denied
    specific roles that their role might have, but the specific user isn't
    granted permission to.
    @access public
    @return array List of all capabilities for the user.
    '''
    WpRoles = wp_roles()    # = WP_Roles()

    #Filter out caps that are not role names and assign to self.roles
    if Php.is_array( self.caps ):
      self.roles = Php.array_filter( Php.array_keys(self.caps), WpRoles.is_role)
                                   # array( WpRoles, 'is_role' ) )

    #Build allcaps from role caps, overlay user's caps
    self.allcaps = array()
    for role in Php.Array(self.roles):
      the_role = WpRoles.get_role( role )
      self.allcaps = Php.array_merge( Php.Array(self.allcaps),
                                      Php.Array(the_role.capabilities) )

    self.allcaps = Php.array_merge( Php.Array(self.allcaps),
                                    Php.Array(self.caps) )
    return self.allcaps


  def add_role(self, role ):
    ''' Add role to user.
    Updates the user's meta data option with capabilities and roles.
    @access public
    @param string role Role name.
    '''
    import wp.i.user as WiU
    if Php.empty( role ):
      return

    self.caps[role] = True
    WiU.update_user_meta( self.ID, self.cap_key, self.caps )
    self.get_role_caps()
    self.update_user_level_from_caps()

    # Fires immediately after the user has been given a new role.
    # @param int    user_id The user ID.
    # @param string role    The new role.
    WiPg.do_action( 'add_user_role', self.ID, role )


  def remove_role(self, role ):
    ''' Remove role from user.
    @access public
    @param string role Role name.
    '''
    import wp.i.user as WiU
    if not Php.in_array(role, self.roles):
      return
    Php.unset( self.caps, role )
    WiU.update_user_meta( self.ID, self.cap_key, self.caps )
    self.get_role_caps()
    self.update_user_level_from_caps()

    # Fires immediately after a role as been removed from a user.
    # @param int    user_id The user ID.
    # @param string role    The removed role.
    WiPg.do_action( 'remove_user_role', self.ID, role )


  def set_role(self, role ):
    ''' Set the role of the user.
    This will remove the previous roles of the user and assign the user the
    new one. You can set the role to an empty string and it will remove all
    of the roles from the user.
    @access public
    @param string role Role name.
    '''
    import wp.i.user as WiU
    if 1 == Php.count( self.roles ) and role == Php.current( self.roles ):
      return

    for oldrole in Php.Array(self.roles):
      Php.unset( self.caps, oldrole )

    old_roles = self.roles
    if not Php.empty( role ):
      self.caps[role] = True
      self.roles = array( (role, True) )
    else:
      self.roles = False

    WiU.update_user_meta( self.ID, self.cap_key, self.caps )
    self.get_role_caps()
    self.update_user_level_from_caps()

    # Fires after the user's role has changed.
    # @since 3.6.0 Added old_roles to include an array of the user's previous roles.
    # @param int    user_id   The user ID.
    # @param string role      The new role.
    # @param array  old_roles An array of the user's previous roles.
    WiPg.do_action( 'set_user_role', self.ID, role, old_roles )


  @staticmethod
  def level_reduction( Max, item ):
    ''' Choose the maximum level the user has.
    Will compare the level from the item parameter against the Max
    parameter. If the item is incorrect, then just the Max parameter value
    will be returned.
    Used to get the Max level based on the capabilities the user has. This
    is also based on roles, so if the user is assigned the Administrator role
    then the capability 'level_10' will exist and the user will get that
    value.
    @access public
    @param int Max Max level of user.
    @param string item Level capability name.
    @return int Max Level.
    '''
    if preg_match( '/^level_(10|[0-9])$/i', item, matches ):
      level = intval( matches[1] )
      return Php.max( Max, level )
    else:
      return Max



  def update_user_level_from_caps(self):
    ''' Update the maximum user level for the user.
    Updates the 'user_level' user metadata (includes prefix that is the
    database table prefix) with the maximum user level. Gets the value from
    the all of the capabilities that the user has.
    @access public
    @global wpdb wpdb WordPress database abstraction object.
    '''
    import wp.i.user as WiU
    wpdb = WpC.WB.Wj.wpdb  # global wpdb
    self.user_level = array_reduce( Php.array_keys( self.allcaps ), array( this, 'level_reduction' ), 0 )
    WiU.update_user_meta( self.ID, wpdb.get_blog_prefix() + 'user_level', self.user_level )


  def add_cap( cap, grant = True ):
    ''' Add capability and grant or deny access to capability.
    @access public
    @param string cap Capability name.
    @param bool grant Whether to grant capability to user.
    '''
    import wp.i.user as WiU
    self.caps[cap] = grant
    WiU.update_user_meta( self.ID, self.cap_key, self.caps )
    self.get_role_caps()
    self.update_user_level_from_caps()


  def remove_cap(self, cap ):
    ''' Remove capability from user.
    @access public
    @param string cap Capability name.
    '''
    import wp.i.user as WiU
    if not isset( self.caps[ cap ] ):
      return

    Php.unset( self.caps, cap )
    WiU.update_user_meta( self.ID, self.cap_key, self.caps )
    self.get_role_caps()
    self.update_user_level_from_caps()


  def remove_all_caps(self,):
    ''' Remove all of the capabilities of the user.
    @access public
    @global wpdb wpdb WordPress database abstraction object.
    '''
    wpdb = WpC.WB.Wj.wpdb  # global wpdb
    self.caps = array()
    delete_user_meta( self.ID, self.cap_key )
    delete_user_meta( self.ID, wpdb.get_blog_prefix() + 'user_level' )
    self.get_role_caps()


  def has_cap(self, cap ):
    ''' Whether user has capability or role name.
    While checking against particular roles in place of a capability is supported
    in part, this practice is discouraged as it may produce unreliable results.
    @access public
    @see map_meta_cap()
    @param string cap           Capability name.
    @param int    object_id,... Optional. ID of the specific object to check against if `cap` is a "meta" cap.
                                 "Meta" capabilities, e.g. 'edit_post', 'edit_user', etc., are capabilities used
                                 by map_meta_cap() to map to other "primitive" capabilities, e.g. 'edit_posts',
                                 'edit_others_posts', etc. The parameter is accessed via func_get_args() and passed
                                 to map_meta_cap().
    @return bool Whether the current user has the given capability. If `cap` is a meta cap and `object_id` is
                 passed, whether the current user has the given meta capability for the given object.
    '''
    if Php.is_numeric( cap ):
      Php._deprecated_argument( __FUNCTION__, '2.0.0', __('Usage of user levels by plugins and themes is deprecated. Use roles and capabilities instead.') )
      cap = self.translate_level_to_cap( cap )


    args = Php.array_slice( func_get_args(), 1 )
    args = Php.array_merge( array( cap, self.ID ), args )
    caps = Php.call_user_func_array( 'map_meta_cap', args )

    # Multisite super admin has all caps by definition, Unless specifically denied.
    if WpC.WB.Wj.is_multisite() and is_super_admin( self.ID ):
      if Php.in_array('do_not_allow', caps):
        return False
      return True

    # Dynamically filter a user's capabilities.
    # @since 3.7.0 Added the user object.
    # @param array allcaps An array of all the user's capabilities.
    # @param array caps Actual capabilities for meta capability.
    # @param array args Optional parameters passed to has_cap(), typically obj ID
    # @param WP_User user    The user object.
    capabilities = WiPg.apply_filters( 'user_has_cap',
                                       self.allcaps, caps, args, self )

    # Everyone is allowed to exist.
    capabilities['exist'] = True

    # Must have ALL requested caps.
    for cap in Php.Array(caps):
      if Php.empty( capabilities, cap ):
        return False

    return True


  @staticmethod
  def translate_level_to_cap( level ):
    ''' Convert numeric level to level capability name.
    Prepends 'level_' to level number.
    @access public
    @param int level Level number, 1 to 10.
    @return string
    '''
    return 'level_' + level


  def for_blog( self, blog_id = '' ):
    ''' Set the site to operate on. Defaults to the current site.
    @global wpdb wpdb WordPress database abstraction object.
    @param int blog_id Optional. Site ID, defaults to current site.
    '''
    wpdb = WpC.WB.Wj.wpdb  # global wpdb
    if blog_id:
      cap_key = wpdb.get_blog_prefix( blog_id ) + 'capabilities'
    else:
      cap_key = ''
    self._init_caps( cap_key )




def wp_roles():
  '''/fs/web/wp/wp-includes/capabilities.php
  Retrieves the global WP_Roles instance and instantiates it if necessary
  @global WP_Roles wp_roles WP_Roles global instance.
  @return WP_Roles WP_Roles global instance if not already instantiated.

  W = WcU.wp_roles() && W.role_objects["administrator"].capabilities
  '''
  # wp_roles = WpC.WB.Wj.wp_roles  # global wp_roles
  # if wp_roles is None:
  #   wp_roles = WP_Roles()
  # return wp_roles

  #return Php.stdClass( WP_Roles_Arr )
  return  WP_Roles()


class WP_Roles(Php.stdClass):
  ''' wp-includes/class-wp-roles.php
  '''
  def __init__(self):
    self._obj = WP_Roles_Arr
    self.role_objects = WP_Roles_Arr['role_objects']

  def get_role( self, role):
    ''' Retrieve role object by name.
    @access public
    @param string $role Role name.
    @return WP_Role|None WP_Role object if found, None if the role does not exist.
    '''
    #if ( Php.isset( self.role_objects[role] ) ):
    if  ( Php.isset( self.role_objects, role ) ):
      return self.role_objects[role]
    else:
      return None

  def is_role( self, role ):
    ''' Whether role name is currently in the list of available roles.
    @param string $role Role name to look up.
    @return bool
    '''
    return Php.isset( self.role_names, role )


class WP_Role(Php.stdClass):
  ''' wp-includes/class-wp-role.php
  '''
  def __init__(self, role, capabilities):
    self._obj = array( ('name', role), ('capabilities', capabilities) )


WP_Roles_Arr = array(
  ("roles", array(
    ("administrator", array(
      ("name", "Administrator"),
      ("capabilities", array(
        ("switch_themes", True),
        ("edit_themes", True),
        ("activate_plugins", True),
        ("edit_plugins", True),
        ("edit_users", True),
        ("edit_files", True),
        ("manage_options", True),
        ("moderate_comments", True),
        ("manage_categories", True),
        ("manage_links", True),
        ("upload_files", True),
        ("import", True),
        ("unfiltered_html", True),
        ("edit_posts", True),
        ("edit_others_posts", True),
        ("edit_published_posts", True),
        ("publish_posts", True),
        ("edit_pages", True),
        ("read", True),
        ("level_10", True),
        ("level_9", True),
        ("level_8", True),
        ("level_7", True),
        ("level_6", True),
        ("level_5", True),
        ("level_4", True),
        ("level_3", True),
        ("level_2", True),
        ("level_1", True),
        ("level_0", True),
        ("edit_others_pages", True),
        ("edit_published_pages", True),
        ("publish_pages", True),
        ("delete_pages", True),
        ("delete_others_pages", True),
        ("delete_published_pages", True),
        ("delete_posts", True),
        ("delete_others_posts", True),
        ("delete_published_posts", True),
        ("delete_private_posts", True),
        ("edit_private_posts", True),
        ("read_private_posts", True),
        ("delete_private_pages", True),
        ("edit_private_pages", True),
        ("read_private_pages", True),
        ("delete_users", True),
        ("create_users", True),
        ("unfiltered_upload", True),
        ("edit_dashboard", True),
        ("update_plugins", True),
        ("delete_plugins", True),
        ("install_plugins", True),
        ("update_themes", True),
        ("install_themes", True),
        ("update_core", True),
        ("list_users", True),
        ("remove_users", True),
        ("promote_users", True),
        ("edit_theme_options", True),
        ("delete_themes", True),
        ("export", True),
      )),
    )),
    ("editor", array(
      ("name", "Editor"),
      ("capabilities", array(
        ("moderate_comments", True),
        ("manage_categories", True),
        ("manage_links", True),
        ("upload_files", True),
        ("unfiltered_html", True),
        ("edit_posts", True),
        ("edit_others_posts", True),
        ("edit_published_posts", True),
        ("publish_posts", True),
        ("edit_pages", True),
        ("read", True),
        ("level_7", True),
        ("level_6", True),
        ("level_5", True),
        ("level_4", True),
        ("level_3", True),
        ("level_2", True),
        ("level_1", True),
        ("level_0", True),
        ("edit_others_pages", True),
        ("edit_published_pages", True),
        ("publish_pages", True),
        ("delete_pages", True),
        ("delete_others_pages", True),
        ("delete_published_pages", True),
        ("delete_posts", True),
        ("delete_others_posts", True),
        ("delete_published_posts", True),
        ("delete_private_posts", True),
        ("edit_private_posts", True),
        ("read_private_posts", True),
        ("delete_private_pages", True),
        ("edit_private_pages", True),
        ("read_private_pages", True),
      )),
    )),
    ("author", array(
      ("name", "Author"),
      ("capabilities", array(
        ("upload_files", True),
        ("edit_posts", True),
        ("edit_published_posts", True),
        ("publish_posts", True),
        ("read", True),
        ("level_2", True),
        ("level_1", True),
        ("level_0", True),
        ("delete_posts", True),
        ("delete_published_posts", True),
      )),
    )),
    ("contributor", array(
      ("name", "Contributor"),
      ("capabilities", array(
        ("edit_posts", True),
        ("read", True),
        ("level_1", True),
        ("level_0", True),
        ("delete_posts", True),
      )),
    )),
    ("subscriber", array(
      ("name", "Subscriber"),
      ("capabilities", array(
        ("read", True),
        ("level_0", True),
      )),
    )),
    ("bbp_keymaster", array(
      ("name", "Keymaster"),
      ("capabilities", array(
        ("keep_gate", True),
        ("spectate", True),
        ("participate", True),
        ("moderate", True),
        ("throttle", True),
        ("view_trash", True),
        ("publish_forums", True),
        ("edit_forums", True),
        ("edit_others_forums", True),
        ("delete_forums", True),
        ("delete_others_forums", True),
        ("read_private_forums", True),
        ("read_hidden_forums", True),
        ("publish_topics", True),
        ("edit_topics", True),
        ("edit_others_topics", True),
        ("delete_topics", True),
        ("delete_others_topics", True),
        ("read_private_topics", True),
        ("publish_replies", True),
        ("edit_replies", True),
        ("edit_others_replies", True),
        ("delete_replies", True),
        ("delete_others_replies", True),
        ("read_private_replies", True),
        ("manage_topic_tags", True),
        ("edit_topic_tags", True),
        ("delete_topic_tags", True),
        ("assign_topic_tags", True),
      )),
    )),
    ("bbp_moderator", array(
      ("name", "Moderator"),
      ("capabilities", array(
        ("spectate", True),
        ("participate", True),
        ("moderate", True),
        ("throttle", True),
        ("view_trash", True),
        ("publish_forums", True),
        ("edit_forums", True),
        ("read_private_forums", True),
        ("read_hidden_forums", True),
        ("publish_topics", True),
        ("edit_topics", True),
        ("edit_others_topics", True),
        ("delete_topics", True),
        ("delete_others_topics", True),
        ("read_private_topics", True),
        ("publish_replies", True),
        ("edit_replies", True),
        ("edit_others_replies", True),
        ("delete_replies", True),
        ("delete_others_replies", True),
        ("read_private_replies", True),
        ("manage_topic_tags", True),
        ("edit_topic_tags", True),
        ("delete_topic_tags", True),
        ("assign_topic_tags", True),
      )),
    )),
    ("bbp_participant", array(
      ("name", "Participant"),
      ("capabilities", array(
        ("spectate", True),
        ("participate", True),
        ("read_private_forums", True),
        ("publish_topics", True),
        ("edit_topics", True),
        ("publish_replies", True),
        ("edit_replies", True),
        ("assign_topic_tags", True),
      )),
    )),
    ("bbp_spectator", array(
      ("name", "Spectator"),
      ("capabilities", array(
        ("spectate", True),
      )),
    )),
    ("bbp_blocked", array(
      ("name", "Blocked"),
      ("capabilities", array(
        ("spectate", False),
        ("participate", False),
        ("moderate", False),
        ("throttle", False),
        ("view_trash", False),
        ("publish_forums", False),
        ("edit_forums", False),
        ("edit_others_forums", False),
        ("delete_forums", False),
        ("delete_others_forums", False),
        ("read_private_forums", False),
        ("read_hidden_forums", False),
        ("publish_topics", False),
        ("edit_topics", False),
        ("edit_others_topics", False),
        ("delete_topics", False),
        ("delete_others_topics", False),
        ("read_private_topics", False),
        ("publish_replies", False),
        ("edit_replies", False),
        ("edit_others_replies", False),
        ("delete_replies", False),
        ("delete_others_replies", False),
        ("read_private_replies", False),
        ("manage_topic_tags", False),
        ("edit_topic_tags", False),
        ("delete_topic_tags", False),
        ("assign_topic_tags", False),
      )),
    )),
  )),
  ("role_objects", array(
    ("administrator", Php.stdClass(array(  # object(WP_Role)#4030 (2) {
      ("name", "administrator"),
      ("capabilities", array(
        ("switch_themes", True),
        ("edit_themes", True),
        ("activate_plugins", True),
        ("edit_plugins", True),
        ("edit_users", True),
        ("edit_files", True),
        ("manage_options", True),
        ("moderate_comments", True),
        ("manage_categories", True),
        ("manage_links", True),
        ("upload_files", True),
        ("import", True),
        ("unfiltered_html", True),
        ("edit_posts", True),
        ("edit_others_posts", True),
        ("edit_published_posts", True),
        ("publish_posts", True),
        ("edit_pages", True),
        ("read", True),
        ("level_10", True),
        ("level_9", True),
        ("level_8", True),
        ("level_7", True),
        ("level_6", True),
        ("level_5", True),
        ("level_4", True),
        ("level_3", True),
        ("level_2", True),
        ("level_1", True),
        ("level_0", True),
        ("edit_others_pages", True),
        ("edit_published_pages", True),
        ("publish_pages", True),
        ("delete_pages", True),
        ("delete_others_pages", True),
        ("delete_published_pages", True),
        ("delete_posts", True),
        ("delete_others_posts", True),
        ("delete_published_posts", True),
        ("delete_private_posts", True),
        ("edit_private_posts", True),
        ("read_private_posts", True),
        ("delete_private_pages", True),
        ("edit_private_pages", True),
        ("read_private_pages", True),
        ("delete_users", True),
        ("create_users", True),
        ("unfiltered_upload", True),
        ("edit_dashboard", True),
        ("update_plugins", True),
        ("delete_plugins", True),
        ("install_plugins", True),
        ("update_themes", True),
        ("install_themes", True),
        ("update_core", True),
        ("list_users", True),
        ("remove_users", True),
        ("promote_users", True),
        ("edit_theme_options", True),
        ("delete_themes", True),
        ("export", True),
      )),
    ))),
    ("editor", Php.stdClass(array(  # object(WP_Role)#4029 (2) {
      ("name", "editor"),
      ("capabilities", array(
        ("moderate_comments", True),
        ("manage_categories", True),
        ("manage_links", True),
        ("upload_files", True),
        ("unfiltered_html", True),
        ("edit_posts", True),
        ("edit_others_posts", True),
        ("edit_published_posts", True),
        ("publish_posts", True),
        ("edit_pages", True),
        ("read", True),
        ("level_7", True),
        ("level_6", True),
        ("level_5", True),
        ("level_4", True),
        ("level_3", True),
        ("level_2", True),
        ("level_1", True),
        ("level_0", True),
        ("edit_others_pages", True),
        ("edit_published_pages", True),
        ("publish_pages", True),
        ("delete_pages", True),
        ("delete_others_pages", True),
        ("delete_published_pages", True),
        ("delete_posts", True),
        ("delete_others_posts", True),
        ("delete_published_posts", True),
        ("delete_private_posts", True),
        ("edit_private_posts", True),
        ("read_private_posts", True),
        ("delete_private_pages", True),
        ("edit_private_pages", True),
        ("read_private_pages", True),
      )),
    ))),
    ("author", Php.stdClass(array(  # object(WP_Role)#4028 (2) {
      ("name", "author"),
      ("capabilities", array(
        ("upload_files", True),
        ("edit_posts", True),
        ("edit_published_posts", True),
        ("publish_posts", True),
        ("read", True),
        ("level_2", True),
        ("level_1", True),
        ("level_0", True),
        ("delete_posts", True),
        ("delete_published_posts", True),
      )),
    ))),
    ("contributor", Php.stdClass(array(  # object(WP_Role)#4027 (2) {
      ("name", "contributor"),
      ("capabilities", array(
        ("edit_posts", True),
        ("read", True),
        ("level_1", True),
        ("level_0", True),
        ("delete_posts", True),
      )),
    ))),
    ("subscriber", Php.stdClass(array(  # object(WP_Role)#4026 (2) {
      ("name", "subscriber"),
      ("capabilities", array(
        ("read", True),
        ("level_0", True),
      )),
    ))),
    ("bbp_keymaster", Php.stdClass(array(  # object(WP_Role)#4025 (2) {
      ("name", "bbp_keymaster"),
      ("capabilities", array(
        ("keep_gate", True),
        ("spectate", True),
        ("participate", True),
        ("moderate", True),
        ("throttle", True),
        ("view_trash", True),
        ("publish_forums", True),
        ("edit_forums", True),
        ("edit_others_forums", True),
        ("delete_forums", True),
        ("delete_others_forums", True),
        ("read_private_forums", True),
        ("read_hidden_forums", True),
        ("publish_topics", True),
        ("edit_topics", True),
        ("edit_others_topics", True),
        ("delete_topics", True),
        ("delete_others_topics", True),
        ("read_private_topics", True),
        ("publish_replies", True),
        ("edit_replies", True),
        ("edit_others_replies", True),
        ("delete_replies", True),
        ("delete_others_replies", True),
        ("read_private_replies", True),
        ("manage_topic_tags", True),
        ("edit_topic_tags", True),
        ("delete_topic_tags", True),
        ("assign_topic_tags", True),
      )),
    ))),
    ("bbp_moderator", Php.stdClass(array(  # object(WP_Role)#4024 (2) {
      ("name", "bbp_moderator"),
      ("capabilities", array(
        ("spectate", True),
        ("participate", True),
        ("moderate", True),
        ("throttle", True),
        ("view_trash", True),
        ("publish_forums", True),
        ("edit_forums", True),
        ("read_private_forums", True),
        ("read_hidden_forums", True),
        ("publish_topics", True),
        ("edit_topics", True),
        ("edit_others_topics", True),
        ("delete_topics", True),
        ("delete_others_topics", True),
        ("read_private_topics", True),
        ("publish_replies", True),
        ("edit_replies", True),
        ("edit_others_replies", True),
        ("delete_replies", True),
        ("delete_others_replies", True),
        ("read_private_replies", True),
        ("manage_topic_tags", True),
        ("edit_topic_tags", True),
        ("delete_topic_tags", True),
        ("assign_topic_tags", True),
      )),
    ))),
    ("bbp_participant", Php.stdClass(array(  # object(WP_Role)#4023 (2) {
      ("name", "bbp_participant"),
      ("capabilities", array(
        ("spectate", True),
        ("participate", True),
        ("read_private_forums", True),
        ("publish_topics", True),
        ("edit_topics", True),
        ("publish_replies", True),
        ("edit_replies", True),
        ("assign_topic_tags", True),
      )),
    ))),
    ("bbp_spectator", Php.stdClass(array(  # object(WP_Role)#4022 (2) {
      ("name", "bbp_spectator"),
      ("capabilities", array(
        ("spectate", True),
      )),
    ))),
    ("bbp_blocked", Php.stdClass(array(  # object(WP_Role)#4021 (2) {
      ("name", "bbp_blocked"),
      ("capabilities", array(
        ("spectate", False),
        ("participate", False),
        ("moderate", False),
        ("throttle", False),
        ("view_trash", False),
        ("publish_forums", False),
        ("edit_forums", False),
        ("edit_others_forums", False),
        ("delete_forums", False),
        ("delete_others_forums", False),
        ("read_private_forums", False),
        ("read_hidden_forums", False),
        ("publish_topics", False),
        ("edit_topics", False),
        ("edit_others_topics", False),
        ("delete_topics", False),
        ("delete_others_topics", False),
        ("read_private_topics", False),
        ("publish_replies", False),
        ("edit_replies", False),
        ("edit_others_replies", False),
        ("delete_replies", False),
        ("delete_others_replies", False),
        ("read_private_replies", False),
        ("manage_topic_tags", False),
        ("edit_topic_tags", False),
        ("delete_topic_tags", False),
        ("assign_topic_tags", False),
      )),
    ))),
  )),
  ("role_names", array(
    ("administrator", "Administrator"),
    ("editor", "Editor"),
    ("author", "Author"),
    ("contributor", "Contributor"),
    ("subscriber", "Subscriber"),
    ("bbp_keymaster", "Keymaster"),
    ("bbp_moderator", "Moderator"),
    ("bbp_participant", "Participant"),
    ("bbp_spectator", "Spectator"),
    ("bbp_blocked", "Blocked"),
  )),
  ("role_key", "wp_12_user_roles"),
  ("use_db", True),
)




# Translate from Php.array to py array:
# 0,$ s/^  \[/  (/
# 0,$ s/^    \[/    (/
# 0,$ s/^      \[/      (/
# 0,$ s/^        \[/        (/
# 0,$ s/^          \[/          (/
# 0,1230 s/\]=> /, /
# 0,1230 s/ bool(true)/ True),/
# 0,1230 s/ bool(false)/ False),/
# 0,1230 s/ array(\d*) {/ array(/
# 0,1230 s/ string(\d*) \(.*\)/ \1),/
# 0,1230 s/}/)/

# wp> WP_Roles()
# => object(WP_Roles)#4031 (5) {
#   ["roles"]=> array(10) {
#     ["administrator"]=> array(2) {
#       ["name"]=> string(13) "Administrator"
#       ["capabilities"]=> array(61) {
#         ["switch_themes"]=> bool(true)
#         ["edit_themes"]=> bool(true)
#         ["activate_plugins"]=> bool(true)
#         ["edit_plugins"]=> bool(true)
#         ["edit_users"]=> bool(true)
#         ["edit_files"]=> bool(true)
#         ["manage_options"]=> bool(true)
#         ["moderate_comments"]=> bool(true)
#         ["manage_categories"]=> bool(true)
#         ["manage_links"]=> bool(true)
#         ["upload_files"]=> bool(true)
#         ["import"]=> bool(true)
#         ["unfiltered_html"]=> bool(true)
#         ["edit_posts"]=> bool(true)
#         ["edit_others_posts"]=> bool(true)
#         ["edit_published_posts"]=> bool(true)
#         ["publish_posts"]=> bool(true)
#         ["edit_pages"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_10"]=> bool(true)
#         ["level_9"]=> bool(true)
#         ["level_8"]=> bool(true)
#         ["level_7"]=> bool(true)
#         ["level_6"]=> bool(true)
#         ["level_5"]=> bool(true)
#         ["level_4"]=> bool(true)
#         ["level_3"]=> bool(true)
#         ["level_2"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["edit_others_pages"]=> bool(true)
#         ["edit_published_pages"]=> bool(true)
#         ["publish_pages"]=> bool(true)
#         ["delete_pages"]=> bool(true)
#         ["delete_others_pages"]=> bool(true)
#         ["delete_published_pages"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#         ["delete_others_posts"]=> bool(true)
#         ["delete_published_posts"]=> bool(true)
#         ["delete_private_posts"]=> bool(true)
#         ["edit_private_posts"]=> bool(true)
#         ["read_private_posts"]=> bool(true)
#         ["delete_private_pages"]=> bool(true)
#         ["edit_private_pages"]=> bool(true)
#         ["read_private_pages"]=> bool(true)
#         ["delete_users"]=> bool(true)
#         ["create_users"]=> bool(true)
#         ["unfiltered_upload"]=> bool(true)
#         ["edit_dashboard"]=> bool(true)
#         ["update_plugins"]=> bool(true)
#         ["delete_plugins"]=> bool(true)
#         ["install_plugins"]=> bool(true)
#         ["update_themes"]=> bool(true)
#         ["install_themes"]=> bool(true)
#         ["update_core"]=> bool(true)
#         ["list_users"]=> bool(true)
#         ["remove_users"]=> bool(true)
#         ["promote_users"]=> bool(true)
#         ["edit_theme_options"]=> bool(true)
#         ["delete_themes"]=> bool(true)
#         ["export"]=> bool(true)
#       }
#     }
#     ["editor"]=> array(2) {
#       ["name"]=> string(6) "Editor"
#       ["capabilities"]=> array(34) {
#         ["moderate_comments"]=> bool(true)
#         ["manage_categories"]=> bool(true)
#         ["manage_links"]=> bool(true)
#         ["upload_files"]=> bool(true)
#         ["unfiltered_html"]=> bool(true)
#         ["edit_posts"]=> bool(true)
#         ["edit_others_posts"]=> bool(true)
#         ["edit_published_posts"]=> bool(true)
#         ["publish_posts"]=> bool(true)
#         ["edit_pages"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_7"]=> bool(true)
#         ["level_6"]=> bool(true)
#         ["level_5"]=> bool(true)
#         ["level_4"]=> bool(true)
#         ["level_3"]=> bool(true)
#         ["level_2"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["edit_others_pages"]=> bool(true)
#         ["edit_published_pages"]=> bool(true)
#         ["publish_pages"]=> bool(true)
#         ["delete_pages"]=> bool(true)
#         ["delete_others_pages"]=> bool(true)
#         ["delete_published_pages"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#         ["delete_others_posts"]=> bool(true)
#         ["delete_published_posts"]=> bool(true)
#         ["delete_private_posts"]=> bool(true)
#         ["edit_private_posts"]=> bool(true)
#         ["read_private_posts"]=> bool(true)
#         ["delete_private_pages"]=> bool(true)
#         ["edit_private_pages"]=> bool(true)
#         ["read_private_pages"]=> bool(true)
#       }
#     }
#     ["author"]=> array(2) {
#       ["name"]=> string(6) "Author"
#       ["capabilities"]=> array(10) {
#         ["upload_files"]=> bool(true)
#         ["edit_posts"]=> bool(true)
#         ["edit_published_posts"]=> bool(true)
#         ["publish_posts"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_2"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#         ["delete_published_posts"]=> bool(true)
#       }
#     }
#     ["contributor"]=> array(2) {
#       ["name"]=> string(11) "Contributor"
#       ["capabilities"]=> array(5) {
#         ["edit_posts"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#       }
#     }
#     ["subscriber"]=> array(2) {
#       ["name"]=> string(10) "Subscriber"
#       ["capabilities"]=> array(2) {
#         ["read"]=> bool(true)
#         ["level_0"]=> bool(true)
#       }
#     }
#     ["bbp_keymaster"]=> array(2) {
#       ["name"]=> string(9) "Keymaster"
#       ["capabilities"]=> array(29) {
#         ["keep_gate"]=> bool(true)
#         ["spectate"]=> bool(true)
#         ["participate"]=> bool(true)
#         ["moderate"]=> bool(true)
#         ["throttle"]=> bool(true)
#         ["view_trash"]=> bool(true)
#         ["publish_forums"]=> bool(true)
#         ["edit_forums"]=> bool(true)
#         ["edit_others_forums"]=> bool(true)
#         ["delete_forums"]=> bool(true)
#         ["delete_others_forums"]=> bool(true)
#         ["read_private_forums"]=> bool(true)
#         ["read_hidden_forums"]=> bool(true)
#         ["publish_topics"]=> bool(true)
#         ["edit_topics"]=> bool(true)
#         ["edit_others_topics"]=> bool(true)
#         ["delete_topics"]=> bool(true)
#         ["delete_others_topics"]=> bool(true)
#         ["read_private_topics"]=> bool(true)
#         ["publish_replies"]=> bool(true)
#         ["edit_replies"]=> bool(true)
#         ["edit_others_replies"]=> bool(true)
#         ["delete_replies"]=> bool(true)
#         ["delete_others_replies"]=> bool(true)
#         ["read_private_replies"]=> bool(true)
#         ["manage_topic_tags"]=> bool(true)
#         ["edit_topic_tags"]=> bool(true)
#         ["delete_topic_tags"]=> bool(true)
#         ["assign_topic_tags"]=> bool(true)
#       }
#     }
#     ["bbp_moderator"]=> array(2) {
#       ["name"]=> string(9) "Moderator"
#       ["capabilities"]=> array(25) {
#         ["spectate"]=> bool(true)
#         ["participate"]=> bool(true)
#         ["moderate"]=> bool(true)
#         ["throttle"]=> bool(true)
#         ["view_trash"]=> bool(true)
#         ["publish_forums"]=> bool(true)
#         ["edit_forums"]=> bool(true)
#         ["read_private_forums"]=> bool(true)
#         ["read_hidden_forums"]=> bool(true)
#         ["publish_topics"]=> bool(true)
#         ["edit_topics"]=> bool(true)
#         ["edit_others_topics"]=> bool(true)
#         ["delete_topics"]=> bool(true)
#         ["delete_others_topics"]=> bool(true)
#         ["read_private_topics"]=> bool(true)
#         ["publish_replies"]=> bool(true)
#         ["edit_replies"]=> bool(true)
#         ["edit_others_replies"]=> bool(true)
#         ["delete_replies"]=> bool(true)
#         ["delete_others_replies"]=> bool(true)
#         ["read_private_replies"]=> bool(true)
#         ["manage_topic_tags"]=> bool(true)
#         ["edit_topic_tags"]=> bool(true)
#         ["delete_topic_tags"]=> bool(true)
#         ["assign_topic_tags"]=> bool(true)
#       }
#     }
#     ["bbp_participant"]=> array(2) {
#       ["name"]=> string(11) "Participant"
#       ["capabilities"]=> array(8) {
#         ["spectate"]=> bool(true)
#         ["participate"]=> bool(true)
#         ["read_private_forums"]=> bool(true)
#         ["publish_topics"]=> bool(true)
#         ["edit_topics"]=> bool(true)
#         ["publish_replies"]=> bool(true)
#         ["edit_replies"]=> bool(true)
#         ["assign_topic_tags"]=> bool(true)
#       }
#     }
#     ["bbp_spectator"]=> array(2) {
#       ["name"]=> string(9) "Spectator"
#       ["capabilities"]=> array(1) {
#         ["spectate"]=> bool(true)
#       }
#     }
#     ["bbp_blocked"]=> array(2) {
#       ["name"]=> string(7) "Blocked"
#       ["capabilities"]=> array(28) {
#         ["spectate"]=> bool(false)
#         ["participate"]=> bool(false)
#         ["moderate"]=> bool(false)
#         ["throttle"]=> bool(false)
#         ["view_trash"]=> bool(false)
#         ["publish_forums"]=> bool(false)
#         ["edit_forums"]=> bool(false)
#         ["edit_others_forums"]=> bool(false)
#         ["delete_forums"]=> bool(false)
#         ["delete_others_forums"]=> bool(false)
#         ["read_private_forums"]=> bool(false)
#         ["read_hidden_forums"]=> bool(false)
#         ["publish_topics"]=> bool(false)
#         ["edit_topics"]=> bool(false)
#         ["edit_others_topics"]=> bool(false)
#         ["delete_topics"]=> bool(false)
#         ["delete_others_topics"]=> bool(false)
#         ["read_private_topics"]=> bool(false)
#         ["publish_replies"]=> bool(false)
#         ["edit_replies"]=> bool(false)
#         ["edit_others_replies"]=> bool(false)
#         ["delete_replies"]=> bool(false)
#         ["delete_others_replies"]=> bool(false)
#         ["read_private_replies"]=> bool(false)
#         ["manage_topic_tags"]=> bool(false)
#         ["edit_topic_tags"]=> bool(false)
#         ["delete_topic_tags"]=> bool(false)
#         ["assign_topic_tags"]=> bool(false)
#       }
#     }
#   }
#   ["role_objects"]=> array(10) {
#     ["administrator"]=> object(WP_Role)#4030 (2) {
#       ["name"]=> string(13) "administrator"
#       ["capabilities"]=> array(61) {
#         ["switch_themes"]=> bool(true)
#         ["edit_themes"]=> bool(true)
#         ["activate_plugins"]=> bool(true)
#         ["edit_plugins"]=> bool(true)
#         ["edit_users"]=> bool(true)
#         ["edit_files"]=> bool(true)
#         ["manage_options"]=> bool(true)
#         ["moderate_comments"]=> bool(true)
#         ["manage_categories"]=> bool(true)
#         ["manage_links"]=> bool(true)
#         ["upload_files"]=> bool(true)
#         ["import"]=> bool(true)
#         ["unfiltered_html"]=> bool(true)
#         ["edit_posts"]=> bool(true)
#         ["edit_others_posts"]=> bool(true)
#         ["edit_published_posts"]=> bool(true)
#         ["publish_posts"]=> bool(true)
#         ["edit_pages"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_10"]=> bool(true)
#         ["level_9"]=> bool(true)
#         ["level_8"]=> bool(true)
#         ["level_7"]=> bool(true)
#         ["level_6"]=> bool(true)
#         ["level_5"]=> bool(true)
#         ["level_4"]=> bool(true)
#         ["level_3"]=> bool(true)
#         ["level_2"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["edit_others_pages"]=> bool(true)
#         ["edit_published_pages"]=> bool(true)
#         ["publish_pages"]=> bool(true)
#         ["delete_pages"]=> bool(true)
#         ["delete_others_pages"]=> bool(true)
#         ["delete_published_pages"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#         ["delete_others_posts"]=> bool(true)
#         ["delete_published_posts"]=> bool(true)
#         ["delete_private_posts"]=> bool(true)
#         ["edit_private_posts"]=> bool(true)
#         ["read_private_posts"]=> bool(true)
#         ["delete_private_pages"]=> bool(true)
#         ["edit_private_pages"]=> bool(true)
#         ["read_private_pages"]=> bool(true)
#         ["delete_users"]=> bool(true)
#         ["create_users"]=> bool(true)
#         ["unfiltered_upload"]=> bool(true)
#         ["edit_dashboard"]=> bool(true)
#         ["update_plugins"]=> bool(true)
#         ["delete_plugins"]=> bool(true)
#         ["install_plugins"]=> bool(true)
#         ["update_themes"]=> bool(true)
#         ["install_themes"]=> bool(true)
#         ["update_core"]=> bool(true)
#         ["list_users"]=> bool(true)
#         ["remove_users"]=> bool(true)
#         ["promote_users"]=> bool(true)
#         ["edit_theme_options"]=> bool(true)
#         ["delete_themes"]=> bool(true)
#         ["export"]=> bool(true)
#       }
#     }
#     ["editor"]=> object(WP_Role)#4029 (2) {
#       ["name"]=> string(6) "editor"
#       ["capabilities"]=> array(34) {
#         ["moderate_comments"]=> bool(true)
#         ["manage_categories"]=> bool(true)
#         ["manage_links"]=> bool(true)
#         ["upload_files"]=> bool(true)
#         ["unfiltered_html"]=> bool(true)
#         ["edit_posts"]=> bool(true)
#         ["edit_others_posts"]=> bool(true)
#         ["edit_published_posts"]=> bool(true)
#         ["publish_posts"]=> bool(true)
#         ["edit_pages"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_7"]=> bool(true)
#         ["level_6"]=> bool(true)
#         ["level_5"]=> bool(true)
#         ["level_4"]=> bool(true)
#         ["level_3"]=> bool(true)
#         ["level_2"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["edit_others_pages"]=> bool(true)
#         ["edit_published_pages"]=> bool(true)
#         ["publish_pages"]=> bool(true)
#         ["delete_pages"]=> bool(true)
#         ["delete_others_pages"]=> bool(true)
#         ["delete_published_pages"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#         ["delete_others_posts"]=> bool(true)
#         ["delete_published_posts"]=> bool(true)
#         ["delete_private_posts"]=> bool(true)
#         ["edit_private_posts"]=> bool(true)
#         ["read_private_posts"]=> bool(true)
#         ["delete_private_pages"]=> bool(true)
#         ["edit_private_pages"]=> bool(true)
#         ["read_private_pages"]=> bool(true)
#       }
#     }
#     ["author"]=> object(WP_Role)#4028 (2) {
#       ["name"]=> string(6) "author"
#       ["capabilities"]=> array(10) {
#         ["upload_files"]=> bool(true)
#         ["edit_posts"]=> bool(true)
#         ["edit_published_posts"]=> bool(true)
#         ["publish_posts"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_2"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#         ["delete_published_posts"]=> bool(true)
#       }
#     }
#     ["contributor"]=> object(WP_Role)#4027 (2) {
#       ["name"]=> string(11) "contributor"
#       ["capabilities"]=> array(5) {
#         ["edit_posts"]=> bool(true)
#         ["read"]=> bool(true)
#         ["level_1"]=> bool(true)
#         ["level_0"]=> bool(true)
#         ["delete_posts"]=> bool(true)
#       }
#     }
#     ["subscriber"]=> object(WP_Role)#4026 (2) {
#       ["name"]=> string(10) "subscriber"
#       ["capabilities"]=> array(2) {
#         ["read"]=> bool(true)
#         ["level_0"]=> bool(true)
#       }
#     }
#     ["bbp_keymaster"]=> object(WP_Role)#4025 (2) {
#       ["name"]=> string(13) "bbp_keymaster"
#       ["capabilities"]=> array(29) {
#         ["keep_gate"]=> bool(true)
#         ["spectate"]=> bool(true)
#         ["participate"]=> bool(true)
#         ["moderate"]=> bool(true)
#         ["throttle"]=> bool(true)
#         ["view_trash"]=> bool(true)
#         ["publish_forums"]=> bool(true)
#         ["edit_forums"]=> bool(true)
#         ["edit_others_forums"]=> bool(true)
#         ["delete_forums"]=> bool(true)
#         ["delete_others_forums"]=> bool(true)
#         ["read_private_forums"]=> bool(true)
#         ["read_hidden_forums"]=> bool(true)
#         ["publish_topics"]=> bool(true)
#         ["edit_topics"]=> bool(true)
#         ["edit_others_topics"]=> bool(true)
#         ["delete_topics"]=> bool(true)
#         ["delete_others_topics"]=> bool(true)
#         ["read_private_topics"]=> bool(true)
#         ["publish_replies"]=> bool(true)
#         ["edit_replies"]=> bool(true)
#         ["edit_others_replies"]=> bool(true)
#         ["delete_replies"]=> bool(true)
#         ["delete_others_replies"]=> bool(true)
#         ["read_private_replies"]=> bool(true)
#         ["manage_topic_tags"]=> bool(true)
#         ["edit_topic_tags"]=> bool(true)
#         ["delete_topic_tags"]=> bool(true)
#         ["assign_topic_tags"]=> bool(true)
#       }
#     }
#     ["bbp_moderator"]=> object(WP_Role)#4024 (2) {
#       ["name"]=> string(13) "bbp_moderator"
#       ["capabilities"]=> array(25) {
#         ["spectate"]=> bool(true)
#         ["participate"]=> bool(true)
#         ["moderate"]=> bool(true)
#         ["throttle"]=> bool(true)
#         ["view_trash"]=> bool(true)
#         ["publish_forums"]=> bool(true)
#         ["edit_forums"]=> bool(true)
#         ["read_private_forums"]=> bool(true)
#         ["read_hidden_forums"]=> bool(true)
#         ["publish_topics"]=> bool(true)
#         ["edit_topics"]=> bool(true)
#         ["edit_others_topics"]=> bool(true)
#         ["delete_topics"]=> bool(true)
#         ["delete_others_topics"]=> bool(true)
#         ["read_private_topics"]=> bool(true)
#         ["publish_replies"]=> bool(true)
#         ["edit_replies"]=> bool(true)
#         ["edit_others_replies"]=> bool(true)
#         ["delete_replies"]=> bool(true)
#         ["delete_others_replies"]=> bool(true)
#         ["read_private_replies"]=> bool(true)
#         ["manage_topic_tags"]=> bool(true)
#         ["edit_topic_tags"]=> bool(true)
#         ["delete_topic_tags"]=> bool(true)
#         ["assign_topic_tags"]=> bool(true)
#       }
#     }
#     ["bbp_participant"]=> object(WP_Role)#4023 (2) {
#       ["name"]=> string(15) "bbp_participant"
#       ["capabilities"]=> array(8) {
#         ["spectate"]=> bool(true)
#         ["participate"]=> bool(true)
#         ["read_private_forums"]=> bool(true)
#         ["publish_topics"]=> bool(true)
#         ["edit_topics"]=> bool(true)
#         ["publish_replies"]=> bool(true)
#         ["edit_replies"]=> bool(true)
#         ["assign_topic_tags"]=> bool(true)
#       }
#     }
#     ["bbp_spectator"]=> object(WP_Role)#4022 (2) {
#       ["name"]=> string(13) "bbp_spectator"
#       ["capabilities"]=> array(1) {
#         ["spectate"]=> bool(true)
#       }
#     }
#     ["bbp_blocked"]=> object(WP_Role)#4021 (2) {
#       ["name"]=> string(11) "bbp_blocked"
#       ["capabilities"]=> array(28) {
#         ["spectate"]=> bool(false)
#         ["participate"]=> bool(false)
#         ["moderate"]=> bool(false)
#         ["throttle"]=> bool(false)
#         ["view_trash"]=> bool(false)
#         ["publish_forums"]=> bool(false)
#         ["edit_forums"]=> bool(false)
#         ["edit_others_forums"]=> bool(false)
#         ["delete_forums"]=> bool(false)
#         ["delete_others_forums"]=> bool(false)
#         ["read_private_forums"]=> bool(false)
#         ["read_hidden_forums"]=> bool(false)
#         ["publish_topics"]=> bool(false)
#         ["edit_topics"]=> bool(false)
#         ["edit_others_topics"]=> bool(false)
#         ["delete_topics"]=> bool(false)
#         ["delete_others_topics"]=> bool(false)
#         ["read_private_topics"]=> bool(false)
#         ["publish_replies"]=> bool(false)
#         ["edit_replies"]=> bool(false)
#         ["edit_others_replies"]=> bool(false)
#         ["delete_replies"]=> bool(false)
#         ["delete_others_replies"]=> bool(false)
#         ["read_private_replies"]=> bool(false)
#         ["manage_topic_tags"]=> bool(false)
#         ["edit_topic_tags"]=> bool(false)
#         ["delete_topic_tags"]=> bool(false)
#         ["assign_topic_tags"]=> bool(false)
#       }
#     }
#   }
#   ["role_names"]=> array(10) {
#     ["administrator"]=> string(13) "Administrator"
#     ["editor"]=> string(6) "Editor"
#     ["author"]=> string(6) "Author"
#     ["contributor"]=> string(11) "Contributor"
#     ["subscriber"]=> string(10) "Subscriber"
#     ["bbp_keymaster"]=> string(9) "Keymaster"
#     ["bbp_moderator"]=> string(9) "Moderator"
#     ["bbp_participant"]=> string(11) "Participant"
#     ["bbp_spectator"]=> string(9) "Spectator"
#     ["bbp_blocked"]=> string(7) "Blocked"
#   }
#   ["role_key"]=> string(17) "wp_12_user_roles"
#   ["use_db"]=> bool(true)
# }



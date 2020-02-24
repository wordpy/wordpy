import wp.conf       as WpC
import wp.i.cache    as WiCc
import wp.i.cat_template as WiCT
import wp.i.func     as WiFc
import wp.i.meta     as WiM
import pyx.php       as Php
array = Php.array

''' From wp/wp-includes/class-wp-post.php
Post API: WP_Post class
'''

#final class WP_Post {
class WP_Post(Php.stdClass):
  ''' Core class used to implement the WP_Post object.
  @property string page_template
  @property-read array  ancestors
  @property-read int    post_category
  @property-read string tag_input
  '''
  #def __init__(self, post):      #Orig 
  def  __init__(self, post=None): #php allows post=None in __construct
    ''' Constructor.
    @param WP_Post|object post Post object.
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    #public @var int. Post ID.
    self.ID = None

    self.post_author = 0    # self.post_author = '0'
    '''public @var str. post author ID. A numeric str, for compatibility reasons
    str! NOT int! According to codex.wordpress.org/Class_Reference/WP_Post
    '''

    #public @var str. post's local publication time.
    self.post_date = '0000-00-00 00:00:00'

    # public @var str.  The post's GMT publication time.
    self.post_date_gmt = '0000-00-00 00:00:00'

    # public @var str.  The post's content.
    self.post_content = ''

    # public @var str.  The post's title.
    self.post_title = ''

    # public @var str.  The post's excerpt.
    self.post_excerpt = ''

    # public @var str.  The post's status.
    self.post_status = 'publish'

    # public @var str.  Whether comments are allowed.
    self.comment_status = 'open'

    # public @var str.  Whether pings are allowed.
    self.ping_status = 'open'

    # public @var str.  The post's password in plain text.
    self.post_password = ''

    # public @var str.  The post's slug.
    self.post_name = ''

    # public @var str.  URLs queued to be pinged.
    self.to_ping = ''

    # public @var str.  URLs that have been pinged.
    self.pinged = ''

    # public @var str.  The post's local modified time.
    self.post_modified = '0000-00-00 00:00:00'

    # public @var str.  The post's GMT modified time.
    self.post_modified_gmt = '0000-00-00 00:00:00'

    # public @var str.  A utility DB field for post content.
    self.post_content_filtered = ''

    # public @var int * ID of a post's parent post.
    self.post_parent = 0

    # public @var str.  The unique identifier for a post, not necessarily a URL, used as the feed GUID.
    self.guid = ''

    # public @var int * A field used for ordering posts.
    self.menu_order = 0

    # public @var str.  The post's type, like post or page.
    self.post_type = 'post'

    # public @var str.  An attachment's mime type.
    self.post_mime_type = ''

    self.comment_count = 0   # self.comment_count = '0'
    ''' public @var str.  Cached comment count.
                          A numeric string, for compatibility reasons.
    str! NOT int! According to codex.wordpress.org/Class_Reference/WP_Post
    '''

    # public @var str.  Stores the post object's sanitization level.
    #                   Does not correspond to a DB field.
    self.filter = None

    #for key, value in Php.get_object_vars( post ).items():
    #  self.key = value
    for key, value in Php.get_object_vars( post ).items():
      setattr(self, key, value)   #inherite self._obj from Php.stdClass


  @staticmethod
  def get_instance( post_id ):
    ''' Retrieve WP_Post instance.
    @static
    @access public
    @global wpdb wpdb WordPress database abstraction object.
    @param int post_id Post ID.
    @return WP_Post|False Post object, False otherwise.
    '''
    wpdb = WpC.WB.Wj.wpdb  # global wpdb
    import wp.i.post as WpP

    if (not Php.is_numeric(post_id) or post_id != Php.floor(post_id) or
        not post_id):
      return False
    post_id = int(post_id)

    _post = WiCc.wp_cache_get( post_id, 'posts' )
    #print('WP_Post.get_instance 1 _post=', _post)

    if not _post:
      _post = wpdb.get_row( wpdb.prepare(
                  "SELECT * FROM {} WHERE ID = %s LIMIT 1"
                  .format(wpdb.posts), post_id ) )  # PyMySQL %d->%s
      if not _post:
        return False

      _post = WpP.sanitize_post( _post, 'raw' )
      #print("WP_Post.get_instance _post.ID={} _post = {}"
      #      .format(_post.ID, _post))
      WiCc.wp_cache_add( _post.ID, _post, 'posts' )
    elif Php.empty(_post, 'filter'):
      _post = WpP.sanitize_post( _post, 'raw' )

    return WP_Post( _post )


  def __isset(self, key):
    ''' Isset-er.
    @param string key Property to check if set.
    @return bool
    '''
    if 'ancestors' == key:
      return True

    if 'page_template' == key:
      return True

    if 'post_category' == key:
      return True

    if 'tags_input' == key:
      return True

    return WiM.metadata_exists( 'post', self.ID, key )

  #__get = __getattr__

  def __get(self, key):
    ''' Getter.
        @param string key Key to get.
        @return mixed
    '''
    if key == '_obj':             # VT Added as a subclass of Php.stdClass
      return super().__getattribute__(key)
    #try: return  self._obj[name]
    #except KeyError: pass

    import wp.i.post as WpP
    import wp.i.taxonomy as WpTx
    if 'page_template' == key and self.__isset( key ):
      return WpP.get_post_meta( self.ID, '_wp_page_template', True )

    if 'post_category' == key:
      if WpTx.is_object_in_taxonomy( self.post_type, 'category' ):
        terms = WiCT.get_the_terms( self, 'category' )
      if Php.empty(locals(), 'terms'):
        return array()

      return WiFc.wp_list_pluck( terms, 'term_id' )

    if 'tags_input' == key:
      if WpTx.is_object_in_taxonomy( self.post_type, 'post_tag' ):
        terms = WiCT.get_the_terms( self, 'post_tag' )
      if Php.empty(locals(), 'terms'):
        return array()

      return WiFc.wp_list_pluck( terms, 'name' )

    # Rest of the values need filtering.
    if 'ancestors' == key:
      value = get_post_ancestors( self )
    else:
      value = WpP.get_post_meta( self.ID, key, True )

    if self.filter:
      value = WpP.sanitize_post_field( key, value, self.ID, self.filter )
    return value


  def FilterFunc(self, Filter ):
    ''' {@Missing Summary}
    @param string Filter Filter.
    @return self|array|bool|object|WP_Post
    $this->filter = cls attribute (cls mem). $this->Filter()= method call.
    '''
    import wp.i.post as WpP
    if self.filter == Filter:
      return self

    if Filter == 'raw':
      #print('WcP.FilterFunc self.ID=', self.ID, self.filter, Filter)
      return self.get_instance( self.ID )

    return WpP.sanitize_post( self, Filter )


  def to_array(self):
    ''' Convert object to array.
        @return array Object as array.
    '''
    post = Php.get_object_vars( self )

    for key in ('ancestors', 'page_template', 'post_category', 'tags_input'):
      if hasattr(self, key):
        post[ key ] = self.__get(key)

    return post

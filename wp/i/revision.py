
def wp_is_post_revision( post ):
  ''' wp/wp-includes/revision.php
  Determines if the specified post is a revision.
  @param int|WP_Post post Post ID or post object.
  @return False|int False if not a revision, ID of revision's parent otherwise
  '''
  return False   #VT All py posts are NOT revision
  #if !post = wp_get_post_revision( post ):
  #  return False
  #return (int) post->post_parent


def wp_is_post_autosave( post ):
  ''' wp/wp-includes/revision.php
  Determines if the specified post is an autosave.
  @since 2.6.0
  @param int|WP_Post post Post ID or post object.
  @return False|int False if not a revision, ID of autosave's parent otherwise
  '''
  return False   #VT All py posts are NOT revision
  #if !post = wp_get_post_revision( post ):
  #  return False
  #if False !== strpos( post->post_name, "{post->post_parent}-autosave"):
  #  return (int) post->post_parent
  #return False


def wp_get_post_revision(post, output = object, filter = 'raw'):
  ''' wp/wp-includes/revision.php
  Gets a post revision.
  @param int|WP_Post post   The post ID or object.
  @param string      $output Optional. The required return type. One of OBJECT, ARRAY_A, or ARRAY_N, which correspond to
                             a WP_Post object, an associative array, or a numeric array, respectively. Default OBJECT.
  @param string      $filter Optional sanitation filter. See sanitize_post().
  @return WP_Post|array|null WP_Post (or array) on success, or null on failure
  '''
  '''
  if !revision = get_post( post, OBJECT, filter ):
    return revision
  if 'revision' !== revision->post_type:
    return None

  if output == OBJECT:
    return revision
  elif output == ARRAY_A:
    _revision = get_object_vars(revision)
    return _revision
  elif output == ARRAY_N:
    _revision = array_values(get_object_vars(revision))
    return _revision
  return revision
  '''
  return None   #return None for now.  Should covert above php to py



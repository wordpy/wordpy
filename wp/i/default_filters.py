import wp.i.plugin as WiPg
import pyx.php     as Php

# Sets up the default filters and actions for most
# of the WordPress hooks.
# If you need to remove a default hook, this file will
# give you the priority for which to use to remove the
# hook.
# Not all of the default hooks are found in default-filters.php
# @package WordPress

def default_filters(self):
  import wp.i.format as WiF
  ## Strip, trim, kses, special chars for string saves
  #for Filter in ( 'pre_term_name', 'pre_comment_author_name', 'pre_link_name', 'pre_link_target', 'pre_link_rel', 'pre_user_display_name', 'pre_user_first_name', 'pre_user_last_name', 'pre_user_nickname' ):
  #  WiPg.add_filter( Filter, 'sanitize_text_field'  )
  #  WiPg.add_filter( Filter, 'wp_filter_kses'       )
  #  WiPg.add_filter( Filter, '_wp_specialchars', 30 )
  #
  ## Strip, kses, special chars for string display
  #for Filter in ( 'term_name', 'comment_author_name', 'link_name', 'link_target', 'link_rel', 'user_display_name', 'user_first_name', 'user_last_name', 'user_nickname' ):
  #  if self.is_admin():
  #    # These are expensive. Run only on admin pages for defense in depth.
  #    WiPg.add_filter( Filter, 'sanitize_text_field'  )
  #    WiPg.add_filter( Filter, 'wp_kses_data'       )
  #  WiPg.add_filter( Filter, '_wp_specialchars', 30 )
  #
  ## Kses only for textarea saves
  #for Filter in ( 'pre_term_description', 'pre_link_description', 'pre_link_notes', 'pre_user_description' ):
  #  WiPg.add_filter( Filter, 'wp_filter_kses' )
  #
  ## Kses only for textarea admin displays
  #if self.is_admin():
  #  for Filter in ( 'term_description', 'link_description', 'link_notes', 'user_description' ):
  #    WiPg.add_filter( Filter, 'wp_kses_data' )
  #  WiPg.add_filter( 'comment_text', 'wp_kses_post' )
  #
  ## Email saves
  #for Filter in ( 'pre_comment_author_email', 'pre_user_email' ):
  #  WiPg.add_filter( Filter, 'trim'           )
  #  WiPg.add_filter( Filter, 'sanitize_email' )
  #  WiPg.add_filter( Filter, 'wp_filter_kses' )
  #
  ## Email admin display
  #for Filter in ( 'comment_author_email', 'user_email' ):
  #  WiPg.add_filter( Filter, 'sanitize_email' )
  #  if self.is_admin():
  #    WiPg.add_filter( Filter, 'wp_kses_data' )
  #
  ## Save URL
  #for Filter in ( 'pre_comment_author_url', 'pre_user_url', 'pre_link_url', 'pre_link_image',
  #    'pre_link_rss', 'pre_post_guid' ):
  #  WiPg.add_filter( Filter, 'wp_strip_all_tags' )
  #  WiPg.add_filter( Filter, 'esc_url_raw'       )
  #  WiPg.add_filter( Filter, 'wp_filter_kses'    )
  #
  ## Display URL
  #for Filter in ( 'user_url', 'link_url', 'link_image', 'link_rss', 'comment_url', 'post_guid' ):
  #  if self.is_admin():
  #    WiPg.add_filter( Filter, 'wp_strip_all_tags' )
  #  WiPg.add_filter( Filter, 'esc_url'           )
  #  if self.is_admin():
  #    WiPg.add_filter( Filter, 'wp_kses_data'    )
  #
  ## Slugs
  #WiPg.add_filter( 'pre_term_slug', 'sanitize_title' )
  #WiPg.add_filter( 'wp_insert_post_data', '_wp_customize_changeset_filter_insert_post_data', 10, 2 )
  #
  ## Keys
  #for Filter in ( 'pre_post_type', 'pre_post_status', 'pre_post_comment_status', 'pre_post_ping_status' ):
  #  WiPg.add_filter( Filter, 'sanitize_key' )
  #
  ## Mime types
  #WiPg.add_filter( 'pre_post_mime_type', 'sanitize_mime_type' )
  #WiPg.add_filter( 'post_mime_type', 'sanitize_mime_type' )
  #
  ## Meta
  #WiPg.add_filter( 'register_meta_args', '_wp_register_meta_args_whitelist', 10, 2 )
  #
  ## Places to balance tags on input
  #for Filter in ( 'content_save_pre', 'excerpt_save_pre', 'comment_save_pre', 'pre_comment_content' ):
  #  WiPg.add_filter( Filter, 'convert_invalid_entities' )
  #  WiPg.add_filter( Filter, 'balanceTags', 50 )
  #
  ## Format strings for display.
  #for Filter in ( 'comment_author', 'term_name', 'link_name', 'link_description', 'link_notes', 'bloginfo', 'wp_title', 'widget_title' ):
  #  WiPg.add_filter( Filter, 'wptexturize'   )
  #  WiPg.add_filter( Filter, 'convert_chars' )
  #  WiPg.add_filter( Filter, 'esc_html'      )
  #
  ## Format WordPress
  #for Filter in ( 'the_content', 'the_title', 'wp_title' ):
  #  WiPg.add_filter( Filter, 'capital_P_dangit', 11 )
  #WiPg.add_filter( 'comment_text', 'capital_P_dangit', 31 )
  #
  ## Format titles
  #for Filter in ( 'single_post_title', 'single_cat_title', 'single_tag_title', 'single_month_title', 'nav_menu_attr_title', 'nav_menu_description' ):
  #  WiPg.add_filter( Filter, 'wptexturize' )
  #  WiPg.add_filter( Filter, 'strip_tags'  )
  #
  ## Format text area for display.
  #for Filter in ( 'term_description' ):
  #  WiPg.add_filter( Filter, 'wptexturize'      )
  #  WiPg.add_filter( Filter, 'convert_chars'    )
  #  WiPg.add_filter( Filter, 'wpautop'          )
  #  WiPg.add_filter( Filter, 'shortcode_unautop')
  #
  ## Format for RSS
  #WiPg.add_filter( 'term_name_rss', 'convert_chars' )
  #
  ## Pre save hierarchy
  #WiPg.add_filter( 'wp_insert_post_parent', 'wp_check_post_hierarchy_for_loops', 10, 2 )
  #WiPg.add_filter( 'wp_update_term_parent', 'wp_check_term_hierarchy_for_loops', 10, 3 )
  #
  ## Display filters
  #WiPg.add_filter( 'the_title', 'wptexturize'   )
  #WiPg.add_filter( 'the_title', 'convert_chars' )
  #WiPg.add_filter( 'the_title', 'trim'          )
  #
  #WiPg.add_filter( 'the_content', 'wptexturize'                       )
  #WiPg.add_filter( 'the_content', 'convert_smilies',               20 )
  #WiPg.add_filter( 'the_content', 'wpautop'                           )
  #WiPg.add_filter( 'the_content', 'shortcode_unautop'                 )
  #WiPg.add_filter( 'the_content', 'prepend_attachment'                )
  #WiPg.add_filter( 'the_content', 'wp_make_content_images_responsive' )
  #
  #WiPg.add_filter( 'the_excerpt',     'wptexturize'      )
  #WiPg.add_filter( 'the_excerpt',     'convert_smilies'  )
  #WiPg.add_filter( 'the_excerpt',     'convert_chars'    )
  #WiPg.add_filter( 'the_excerpt',     'wpautop'          )
  #WiPg.add_filter( 'the_excerpt',     'shortcode_unautop')
  #WiPg.add_filter( 'get_the_excerpt', 'wp_trim_excerpt'  )
  #
  #WiPg.add_filter( 'the_post_thumbnail_caption', 'wptexturize'     )
  #WiPg.add_filter( 'the_post_thumbnail_caption', 'convert_smilies' )
  #WiPg.add_filter( 'the_post_thumbnail_caption', 'convert_chars'   )
  #
  #WiPg.add_filter( 'comment_text', 'wptexturize'            )
  #WiPg.add_filter( 'comment_text', 'convert_chars'          )
  #WiPg.add_filter( 'comment_text', 'make_clickable',      9 )
  #WiPg.add_filter( 'comment_text', 'force_balance_tags', 25 )
  #WiPg.add_filter( 'comment_text', 'convert_smilies',    20 )
  #WiPg.add_filter( 'comment_text', 'wpautop',            30 )
  #
  #WiPg.add_filter( 'comment_excerpt', 'convert_chars' )
  #
  #WiPg.add_filter( 'list_cats',         'wptexturize' )
  #
  #WiPg.add_filter( 'wp_sprintf', 'wp_sprintf_l', 10, 2 )
  #
  #WiPg.add_filter( 'widget_text', 'balanceTags' )
  #
  #WiPg.add_filter( 'date_i18n', 'wp_maybe_decline_date' )
  #
  ## RSS filters
  #WiPg.add_filter( 'the_title_rss',      'strip_tags'                    )
  #WiPg.add_filter( 'the_title_rss',      'ent2ncr',                    8 )
  #WiPg.add_filter( 'the_title_rss',      'esc_html'                      )
  #WiPg.add_filter( 'the_content_rss',    'ent2ncr',                    8 )
  #WiPg.add_filter( 'the_content_feed',   'wp_staticize_emoji'            )
  #WiPg.add_filter( 'the_content_feed',   '_oembed_filter_feed_content'   )
  #WiPg.add_filter( 'the_excerpt_rss',    'convert_chars'                 )
  #WiPg.add_filter( 'the_excerpt_rss',    'ent2ncr',                    8 )
  #WiPg.add_filter( 'comment_author_rss', 'ent2ncr',                    8 )
  #WiPg.add_filter( 'comment_text_rss',   'ent2ncr',                    8 )
  #WiPg.add_filter( 'comment_text_rss',   'esc_html'                      )
  #WiPg.add_filter( 'comment_text_rss',   'wp_staticize_emoji'            )
  #WiPg.add_filter( 'bloginfo_rss',       'ent2ncr',                    8 )
  #WiPg.add_filter( 'the_author',         'ent2ncr',                    8 )
  #WiPg.add_filter( 'the_guid',           'esc_url'                       )
  #
  ## Email filters
  #WiPg.add_filter( 'wp_mail', 'wp_staticize_emoji_for_email' )
  #
  ## Mark site as no longer fresh
  #for action in ( 'publish_post', 'publish_page', 'wp_ajax_save-widget', 'wp_ajax_widgets-order', 'customize_save_after' ):
  #  WiPg.add_action( action, '_delete_option_fresh_site' )
  #
  ## Misc filters
  #WiPg.add_filter( 'option_ping_sites',        'privacy_ping_filter'                 )
  #WiPg.add_filter( 'option_blog_charset',      '_wp_specialchars'                    ); # IMPORTANT: This must not be wp_specialchars() or esc_html() or it'll cause an infinite loop
  #WiPg.add_filter( 'option_blog_charset',      '_canonical_charset'                  )
  #WiPg.add_filter( 'option_home',              '_config_wp_home'                     )
  #WiPg.add_filter( 'option_siteurl',           '_config_wp_siteurl'                  )
  #WiPg.add_filter( 'tiny_mce_before_init',     '_mce_set_direction'                  )
  #WiPg.add_filter( 'teeny_mce_before_init',    '_mce_set_direction'                  )
  #WiPg.add_filter( 'pre_kses',                 'wp_pre_kses_less_than'               )
  WiPg.add_filter(  'sanitize_title',           WiF.sanitize_title_with_dashes,   10, 3, Wj=self )
  #WiPg.add_action( 'check_comment_flood',      'check_comment_flood_db',       10, 4 )
  #WiPg.add_filter( 'comment_flood_filter',     'wp_throttle_comment_flood',    10, 3 )
  #WiPg.add_filter( 'pre_comment_content',      'wp_rel_nofollow',              15    )
  #WiPg.add_filter( 'comment_email',            'antispambot'                         )
  #WiPg.add_filter( 'option_tag_base',          '_wp_filter_taxonomy_base'            )
  #WiPg.add_filter( 'option_category_base',     '_wp_filter_taxonomy_base'            )
  #WiPg.add_filter( 'the_posts',                '_close_comments_for_old_posts', 10, 2)
  #WiPg.add_filter( 'comments_open',            '_close_comments_for_old_post', 10, 2 )
  #WiPg.add_filter( 'pings_open',               '_close_comments_for_old_post', 10, 2 )
  #WiPg.add_filter( 'editable_slug',            'urldecode'                           )
  #WiPg.add_filter( 'editable_slug',            'esc_textarea'                        )
  #WiPg.add_filter( 'nav_menu_meta_box_object', '_wp_nav_menu_meta_box_object'        )
  #WiPg.add_filter( 'pingback_ping_source_uri', 'pingback_ping_source_uri'            )
  #WiPg.add_filter( 'xmlrpc_pingback_error',    'xmlrpc_pingback_error'               )
  #WiPg.add_filter( 'title_save_pre',           'trim'                                )
  #
  #WiPg.add_action( 'transition_comment_status', '_clear_modified_cache_on_transition_comment_status', 10, 2 )
  #
  #WiPg.add_filter( 'http_request_host_is_external',    'allowed_http_request_hosts', 10, 2 )
  #
  ## REST API filters.
  #WiPg.add_action( 'xmlrpc_rsd_apis',            'rest_output_rsd' )
  #WiPg.add_action( 'wp_head',                    'rest_output_link_wp_head', 10, 0 )
  #WiPg.add_action( 'template_redirect',          'rest_output_link_header', 11, 0 )
  #WiPg.add_action( 'auth_cookie_malformed',      'rest_cookie_collect_status' )
  #WiPg.add_action( 'auth_cookie_expired',        'rest_cookie_collect_status' )
  #WiPg.add_action( 'auth_cookie_bad_username',   'rest_cookie_collect_status' )
  #WiPg.add_action( 'auth_cookie_bad_hash',       'rest_cookie_collect_status' )
  #WiPg.add_action( 'auth_cookie_valid',          'rest_cookie_collect_status' )
  #WiPg.add_filter( 'rest_authentication_errors', 'rest_cookie_check_errors', 100 )
  #
  ## Actions
  #WiPg.add_action( 'wp_head',             '_wp_render_title_tag',            1     )
  #WiPg.add_action( 'wp_head',             'wp_enqueue_scripts',              1     )
  #WiPg.add_action( 'wp_head',             'wp_resource_hints',               2     )
  #WiPg.add_action( 'wp_head',             'feed_links',                      2     )
  #WiPg.add_action( 'wp_head',             'feed_links_extra',                3     )
  #WiPg.add_action( 'wp_head',             'rsd_link'                               )
  #WiPg.add_action( 'wp_head',             'wlwmanifest_link'                       )
  #WiPg.add_action( 'wp_head',             'adjacent_posts_rel_link_wp_head', 10, 0 )
  #WiPg.add_action( 'wp_head',             'locale_stylesheet'                      )
  #WiPg.add_action( 'publish_future_post', 'check_and_publish_future_post',   10, 1 )
  #WiPg.add_action( 'wp_head',             'noindex',                          1    )
  #WiPg.add_action( 'wp_head',             'print_emoji_detection_script',     7    )
  #WiPg.add_action( 'wp_head',             'wp_print_styles',                  8    )
  #WiPg.add_action( 'wp_head',             'wp_print_head_scripts',            9    )
  #WiPg.add_action( 'wp_head',             'wp_generator'                           )
  #WiPg.add_action( 'wp_head',             'rel_canonical'                          )
  #WiPg.add_action( 'wp_head',             'wp_shortlink_wp_head',            10, 0 )
  #WiPg.add_action( 'wp_head',             'wp_custom_css_cb',                101   )
  #WiPg.add_action( 'wp_head',             'wp_site_icon',                    99    )
  #WiPg.add_action( 'wp_footer',           'wp_print_footer_scripts',         20    )
  #WiPg.add_action( 'template_redirect',   'wp_shortlink_header',             11, 0 )
  #WiPg.add_action( 'wp_print_footer_scripts', '_wp_footer_scripts'                 )
  #WiPg.add_action( 'init',                'check_theme_switched',            99    )
  #WiPg.add_action( 'after_switch_theme',  '_wp_sidebars_changed'                   )
  #WiPg.add_action( 'wp_print_styles',     'print_emoji_styles'                     )
  #
  #if Php.isset( _GET['replytocom'] ):
  #    WiPg.add_action( 'wp_head', 'wp_no_robots' )
  #
  ## Login actions
  #WiPg.add_filter( 'login_head',          'wp_resource_hints',             8     )
  #WiPg.add_action( 'login_head',          'wp_print_head_scripts',         9     )
  #WiPg.add_action( 'login_head',          'print_admin_styles',            9     )
  #WiPg.add_action( 'login_head',          'wp_site_icon',                  99    )
  #WiPg.add_action( 'login_footer',        'wp_print_footer_scripts',       20    )
  #WiPg.add_action( 'login_init',          'send_frame_options_header',     10, 0 )
  #
  ## Feed Generator Tags
  #for action in ( 'rss2_head', 'commentsrss2_head', 'rss_head', 'rdf_header', 'atom_head', 'comments_atom_head', 'opml_head', 'app_head' ):
  #  WiPg.add_action( action, 'the_generator' )
  #
  ## Feed Site Icon
  #WiPg.add_action( 'atom_head', 'atom_site_icon' )
  #WiPg.add_action( 'rss2_head', 'rss2_site_icon' )
  #
  #
  ## WP Cron
  #if not Php.defined( 'DOING_CRON' ):
  #  WiPg.add_action( 'init', 'wp_cron' )
  #
  ## 2 Actions 2 Furious
  #WiPg.add_action( 'do_feed_rdf',                'do_feed_rdf',                             10, 1 )
  #WiPg.add_action( 'do_feed_rss',                'do_feed_rss',                             10, 1 )
  #WiPg.add_action( 'do_feed_rss2',               'do_feed_rss2',                            10, 1 )
  #WiPg.add_action( 'do_feed_atom',               'do_feed_atom',                            10, 1 )
  #WiPg.add_action( 'do_pings',                   'do_all_pings',                            10, 1 )
  #WiPg.add_action( 'do_robots',                  'do_robots'                                      )
  #WiPg.add_action( 'set_comment_cookies',        'wp_set_comment_cookies',                  10, 2 )
  #WiPg.add_action( 'sanitize_comment_cookies',   'sanitize_comment_cookies'                       )
  #WiPg.add_action( 'admin_print_scripts',        'print_emoji_detection_script'                   )
  #WiPg.add_action( 'admin_print_scripts',        'print_head_scripts',                      20    )
  #WiPg.add_action( 'admin_print_footer_scripts', '_wp_footer_scripts'                             )
  #WiPg.add_action( 'admin_print_styles',         'print_emoji_styles'                             )
  #WiPg.add_action( 'admin_print_styles',         'print_admin_styles',                      20    )
  #WiPg.add_action( 'init',                       'smilies_init',                             5    )
  #WiPg.add_action( 'plugins_loaded',             'wp_maybe_load_widgets',                    0    )
  #WiPg.add_action( 'plugins_loaded',             'wp_maybe_load_embeds',                     0    )
  #WiPg.add_action( 'shutdown',                   'wp_ob_end_flush_all',                      1    )
  ## Create a revision whenever a post is updated.
  #WiPg.add_action( 'post_updated',               'wp_save_post_revision',                   10, 1 )
  #WiPg.add_action( 'publish_post',               '_publish_post_hook',                       5, 1 )
  #WiPg.add_action( 'transition_post_status',     '_transition_post_status',                  5, 3 )
  #WiPg.add_action( 'transition_post_status',     '_update_term_count_on_transition_post_status', 10, 3 )
  #WiPg.add_action( 'comment_form',               'wp_comment_form_unfiltered_html_nonce'          )
  #WiPg.add_action( 'wp_scheduled_delete',        'wp_scheduled_delete'                            )
  #WiPg.add_action( 'wp_scheduled_auto_draft_delete', 'wp_delete_auto_drafts'                      )
  #WiPg.add_action( 'admin_init',                 'send_frame_options_header',               10, 0 )
  #WiPg.add_action( 'importer_scheduled_cleanup', 'wp_delete_attachment'                           )
  #WiPg.add_action( 'upgrader_scheduled_cleanup', 'wp_delete_attachment'                           )
  #WiPg.add_action( 'welcome_panel',              'wp_welcome_panel'                               )
  #
  ## Navigation menu actions
  #WiPg.add_action( 'delete_post',                '_wp_delete_post_menu_item'         )
  #WiPg.add_action( 'delete_term',                '_wp_delete_tax_menu_item',   10, 3 )
  #WiPg.add_action( 'transition_post_status',     '_wp_auto_add_pages_to_menu', 10, 3 )
  #
  ## Post Thumbnail CSS class filtering
  #WiPg.add_action( 'begin_fetch_post_thumbnail_html', '_wp_post_thumbnail_class_filter_add'    )
  #WiPg.add_action( 'end_fetch_post_thumbnail_html',   '_wp_post_thumbnail_class_filter_remove' )
  #
  ## Redirect Old Slugs
  #WiPg.add_action( 'template_redirect',  'wp_old_slug_redirect'              )
  #WiPg.add_action( 'post_updated',       'wp_check_for_changed_slugs', 12, 3 )
  #WiPg.add_action( 'attachment_updated', 'wp_check_for_changed_slugs', 12, 3 )
  #
  ## Nonce check for Post Previews
  #WiPg.add_action( 'init', '_show_post_preview' )
  #
  ## Output JS to reset window.name for previews
  #WiPg.add_action( 'wp_head', 'wp_post_preview_js', 1 )
  #
  ## Timezone
  #WiPg.add_filter( 'pre_option_gmt_offset','wp_timezone_override_offset' )
  #
  ## Admin Color Schemes
  #WiPg.add_action( 'admin_init', 'register_admin_color_schemes', 1)
  #WiPg.add_action( 'admin_color_scheme_picker', 'admin_color_scheme_picker' )
  #
  ## If the upgrade hasn't run yet, assume link manager is used.
  #WiPg.add_filter( 'default_option_link_manager_enabled', '__return_true' )
  #
  ## This option no longer exists; tell plugins we always support auto-embedding.
  #WiPg.add_filter( 'default_option_embed_autourls', '__return_true' )
  #
  ## Default settings for heartbeat
  #WiPg.add_filter( 'heartbeat_settings', 'wp_heartbeat_settings' )
  #
  ## Check if the user is logged out
  #WiPg.add_action( 'admin_enqueue_scripts', 'wp_auth_check_load' )
  #WiPg.add_filter( 'heartbeat_send',        'wp_auth_check' )
  #WiPg.add_filter( 'heartbeat_nopriv_send', 'wp_auth_check' )
  #
  ## Default authentication filters
  #WiPg.add_filter( 'authenticate', 'wp_authenticate_username_password',  20, 3 )
  #WiPg.add_filter( 'authenticate', 'wp_authenticate_email_password',     20, 3 )
  #WiPg.add_filter( 'authenticate', 'wp_authenticate_spam_check',         99    )
  #WiPg.add_filter( 'determine_current_user', 'wp_validate_auth_cookie'          )
  #WiPg.add_filter( 'determine_current_user', 'wp_validate_logged_in_cookie', 20 )
  #
  ## Split term updates.
  #WiPg.add_action( 'admin_init',        '_wp_check_for_scheduled_split_terms' )
  #WiPg.add_action( 'split_shared_term', '_wp_check_split_default_terms',  10, 4 )
  #WiPg.add_action( 'split_shared_term', '_wp_check_split_terms_in_menus', 10, 4 )
  #WiPg.add_action( 'split_shared_term', '_wp_check_split_nav_menu_terms', 10, 4 )
  #WiPg.add_action( 'wp_split_shared_term_batch', '_wp_batch_split_terms' )
  #
  ## Email notifications.
  #WiPg.add_action( 'comment_post', 'wp_new_comment_notify_moderator' )
  #WiPg.add_action( 'comment_post', 'wp_new_comment_notify_postauthor' )
  #WiPg.add_action( 'after_password_reset', 'wp_password_change_notification' )
  #WiPg.add_action( 'register_new_user',      'wp_send_new_user_notifications' )
  #WiPg.add_action( 'edit_user_created_user', 'wp_send_new_user_notifications', 10, 2 )
  #
  ## REST API actions.
  #WiPg.add_action( 'init',          'rest_api_init' )
  #WiPg.add_action( 'rest_api_init', 'rest_api_default_filters',   10, 1 )
  #WiPg.add_action( 'rest_api_init', 'register_initial_settings',  10 )
  #WiPg.add_action( 'rest_api_init', 'create_initial_rest_routes', 99 )
  #WiPg.add_action( 'parse_request', 'rest_api_loaded' )
  #
  ## Filters formerly mixed into wp-includes
  ## Theme
  #WiPg.add_action( 'wp_loaded', '_custom_header_background_just_in_time' )
  #WiPg.add_action( 'wp_head', '_custom_logo_header_styles' )
  #WiPg.add_action( 'plugins_loaded', '_wp_customize_include' )
  #WiPg.add_action( 'transition_post_status', '_wp_customize_publish_changeset', 10, 3 )
  #WiPg.add_action( 'admin_enqueue_scripts', '_wp_customize_loader_settings' )
  #WiPg.add_action( 'delete_attachment', '_delete_attachment_theme_mod' )
  #
  ## Calendar widget cache
  #WiPg.add_action( 'save_post', 'delete_get_calendar_cache' )
  #WiPg.add_action( 'delete_post', 'delete_get_calendar_cache' )
  #WiPg.add_action( 'update_option_start_of_week', 'delete_get_calendar_cache' )
  #WiPg.add_action( 'update_option_gmt_offset', 'delete_get_calendar_cache' )
  #
  ## Author
  #WiPg.add_action( 'transition_post_status', '__clear_multi_author_cache' )
  #
  ## Post
  #WiPg.add_action( 'init', 'create_initial_post_types', 0 ); # highest priority
  #WiPg.add_action( 'admin_menu', '_add_post_type_submenus' )
  #WiPg.add_action( 'before_delete_post', '_reset_front_page_settings_for_post' )
  #WiPg.add_action( 'wp_trash_post',      '_reset_front_page_settings_for_post' )
  #WiPg.add_action( 'change_locale', 'create_initial_post_types' )
  #
  ## Post Formats
  #WiPg.add_filter( 'request', '_post_format_request' )
  #WiPg.add_filter( 'term_link', '_post_format_link', 10, 3 )
  #WiPg.add_filter( 'get_post_format', '_post_format_get_term' )
  #WiPg.add_filter( 'get_terms', '_post_format_get_terms', 10, 3 )
  #WiPg.add_filter( 'wp_get_object_terms', '_post_format_wp_get_object_terms' )
  #
  ## KSES
  #WiPg.add_action( 'init', 'kses_init' )
  #WiPg.add_action( 'set_current_user', 'kses_init' )
  #
  ## Script Loader
  #WiPg.add_action( 'wp_default_scripts', 'wp_default_scripts' )
  #WiPg.add_action( 'wp_enqueue_scripts', 'wp_localize_jquery_ui_datepicker', 1000 )
  #WiPg.add_action( 'admin_enqueue_scripts', 'wp_localize_jquery_ui_datepicker', 1000 )
  #WiPg.add_filter( 'wp_print_scripts', 'wp_just_in_time_script_localization' )
  #WiPg.add_filter( 'print_scripts_array', 'wp_prototype_before_jquery' )
  #WiPg.add_filter( 'customize_controls_print_styles', 'wp_resource_hints', 1 )
  #
  #WiPg.add_action( 'wp_default_styles', 'wp_default_styles' )
  #WiPg.add_filter( 'style_loader_src', 'wp_style_loader_src', 10, 2 )
  #
  ## Taxonomy
  #WiPg.add_action( 'init', 'create_initial_taxonomies', 0 ); # highest priority
  #WiPg.add_action( 'change_locale', 'create_initial_taxonomies' )
  #
  ## Canonical
  #WiPg.add_action( 'template_redirect', 'redirect_canonical' )
  #WiPg.add_action( 'template_redirect', 'wp_redirect_admin_locations', 1000 )
  #
  ## Shortcodes
  #WiPg.add_filter( 'the_content', 'do_shortcode', 11 ); # AFTER wpautop()
  #
  ## Media
  #WiPg.add_action( 'wp_playlist_scripts', 'wp_playlist_scripts' )
  #WiPg.add_action( 'customize_controls_enqueue_scripts', 'wp_plupload_default_settings' )
  #
  ## Nav menu
  #WiPg.add_filter( 'nav_menu_item_id', '_nav_menu_item_id_use_once', 10, 2 )
  #
  ## Widgets
  #WiPg.add_action( 'init', 'wp_widgets_init', 1 )
  #
  ## Admin Bar
  ## Don't remove. Wrong way to disable.
  #WiPg.add_action( 'template_redirect', '_wp_admin_bar_init', 0 )
  #WiPg.add_action( 'admin_init', '_wp_admin_bar_init' )
  #WiPg.add_action( 'before_signup_header', '_wp_admin_bar_init' )
  #WiPg.add_action( 'activate_header', '_wp_admin_bar_init' )
  #WiPg.add_action( 'wp_footer', 'wp_admin_bar_render', 1000 )
  #WiPg.add_action( 'in_admin_header', 'wp_admin_bar_render', 0 )
  #
  ## Former admin filters that can also be hooked on the front end
  #WiPg.add_action( 'media_buttons', 'media_buttons' )
  #WiPg.add_filter( 'image_send_to_editor', 'image_add_caption', 20, 8 )
  #WiPg.add_filter( 'media_send_to_editor', 'image_media_send_to_editor', 10, 3 )
  #
  ## Embeds
  #WiPg.add_action( 'rest_api_init',          'wp_oembed_register_route'              )
  #WiPg.add_filter( 'rest_pre_serve_request', '_oembed_rest_pre_serve_request', 10, 4 )
  #
  #WiPg.add_action( 'wp_head',                'wp_oembed_add_discovery_links'         )
  #WiPg.add_action( 'wp_head',                'wp_oembed_add_host_js'                 )
  #
  #WiPg.add_action( 'embed_head',             'enqueue_embed_scripts',           1    )
  #WiPg.add_action( 'embed_head',             'print_emoji_detection_script'          )
  #WiPg.add_action( 'embed_head',             'print_embed_styles'                    )
  #WiPg.add_action( 'embed_head',             'wp_print_head_scripts',          20    )
  #WiPg.add_action( 'embed_head',             'wp_print_styles',                20    )
  #WiPg.add_action( 'embed_head',             'wp_no_robots'                          )
  #WiPg.add_action( 'embed_head',             'rel_canonical'                         )
  #WiPg.add_action( 'embed_head',             'locale_stylesheet',              30    )
  #
  #WiPg.add_action( 'embed_content_meta',     'print_embed_comments_button'           )
  #WiPg.add_action( 'embed_content_meta',     'print_embed_sharing_button'            )
  #
  #WiPg.add_action( 'embed_footer',           'print_embed_sharing_dialog'            )
  #WiPg.add_action( 'embed_footer',           'print_embed_scripts'                   )
  #WiPg.add_action( 'embed_footer',           'wp_print_footer_scripts',        20    )
  #
  #WiPg.add_filter( 'excerpt_more',           'wp_embed_excerpt_more',          20    )
  #WiPg.add_filter( 'the_excerpt_embed',      'wptexturize'                           )
  #WiPg.add_filter( 'the_excerpt_embed',      'convert_chars'                         )
  #WiPg.add_filter( 'the_excerpt_embed',      'wpautop'                               )
  #WiPg.add_filter( 'the_excerpt_embed',      'shortcode_unautop'                     )
  #WiPg.add_filter( 'the_excerpt_embed',      'wp_embed_excerpt_attachment'           )
  #
  #WiPg.add_filter( 'oembed_dataparse',       'wp_filter_oembed_result',        10, 3 )
  #WiPg.add_filter( 'oembed_response_data',   'get_oembed_response_data_rich',  10, 4 )
  #WiPg.add_filter( 'pre_oembed_result',      'wp_filter_pre_oembed_result',    10, 3 )
  
  #Php.unset( Filter, action )

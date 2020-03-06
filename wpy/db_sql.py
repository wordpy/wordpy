#!/usr/bin/python3
from collections import OrderedDict as ODict

CreateTbs = ODict()  # Create Tables in MySql/MariaDb Database

# wp-admin/includes/schema.php
'''
Indexes have a maximum size of 767 bytes. Historically, we haven't need to be concerned about that.
As of 4.2, however, we moved to utf8mb4, which uses 4 bytes per character. This means that an index which
used to have room for floor(767/3) = 255 characters, now only has room for floor(767/4) = 191 characters.
'''
max_index_length = 191

CreateTbs['users'] = '''CREATE TABLE {Pfx}users (
  ID bigint(20) unsigned NOT NULL auto_increment,
  user_login varchar(60) NOT NULL default '',
  user_pass varchar(255) NOT NULL default '',
  user_nicename varchar(50) NOT NULL default '',
  user_email varchar(100) NOT NULL default '',
  user_url varchar(100) NOT NULL default '',
  user_registered datetime NOT NULL default '0000-00-00 00:00:00',
  user_activation_key varchar(255) NOT NULL default '',
  user_status int(11) NOT NULL default '0',
  display_name varchar(250) NOT NULL default '',
  spam tinyint(2) NOT NULL default '0',
  deleted tinyint(2) NOT NULL default '0',
  PRIMARY KEY  (ID),
  KEY user_login_key (user_login),
  KEY user_nicename (user_nicename),
  KEY user_email (user_email)
) {Options}'''

CreateTbs['usermeta'] = '''CREATE TABLE {Pfx}usermeta (
  umeta_id bigint(20) unsigned NOT NULL auto_increment,
  user_id bigint(20) unsigned NOT NULL default '0',
  meta_key varchar(255) default NULL,
  meta_value longtext,
  PRIMARY KEY  (umeta_id),
  KEY user_id (user_id),
  KEY meta_key (meta_key( %s ))
) {Options}''' % max_index_length

# Blog specific tables. Most blog specific tables do not need Federated
# Except that many plugins still use wp_options rather than wp_id_options
CreateTbs['options'] = '''CREATE TABLE {Pfx}options (
  option_id bigint(20) unsigned NOT NULL auto_increment,
  option_name varchar(191) NOT NULL default '',
  option_value longtext NOT NULL,
  autoload varchar(20) NOT NULL default 'yes',
  PRIMARY KEY  (option_id),
  UNIQUE KEY option_name (option_name)
) {Options}'''  # TbPfx = wp_4_

# bp-core/admin/bp-core-admin-schema
# Install database tables for the Notifications component.
# bp_core_install_notifications() {
CreateTbs['bp_notifications'] = '''CREATE TABLE {Pfx}bp_notifications (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) NOT NULL,
  item_id bigint(20) NOT NULL,
  secondary_item_id bigint(20),
  component_name varchar(75) NOT NULL,
  component_action varchar(75) NOT NULL,
  date_notified datetime NOT NULL,
  is_new bool NOT NULL DEFAULT 0,
  KEY item_id (item_id),
  KEY secondary_item_id (secondary_item_id),
  KEY user_id (user_id),
  KEY is_new (is_new),
  KEY component_name (component_name),
  KEY component_action (component_action),
  KEY useritem (user_id,is_new)
) {Options}'''

CreateTbs['bp_notifications_meta'] = '''CREATE TABLE {Pfx}bp_notifications_meta (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  notification_id bigint(20) NOT NULL,
  meta_key varchar(255) DEFAULT NULL,
  meta_value longtext DEFAULT NULL,
  KEY notification_id (notification_id),
  KEY meta_key (meta_key(191))
) {Options}'''

# Install database tables for the Activity component.
# bp_core_install_activity_streams() {
CreateTbs['bp_activity'] = '''CREATE TABLE {Pfx}bp_activity (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) NOT NULL,
  component varchar(75) NOT NULL,
  type varchar(75) NOT NULL,
  action text NOT NULL,
  content longtext NOT NULL,
  primary_link text NOT NULL,
  item_id bigint(20) NOT NULL,
  secondary_item_id bigint(20) DEFAULT NULL,
  date_recorded datetime NOT NULL,
  hide_sitewide bool DEFAULT 0,
  mptt_left int(11) NOT NULL DEFAULT 0,
  mptt_right int(11) NOT NULL DEFAULT 0,
  is_spam tinyint(1) NOT NULL DEFAULT 0,
  KEY date_recorded (date_recorded),
  KEY user_id (user_id),
  KEY item_id (item_id),
  KEY secondary_item_id (secondary_item_id),
  KEY component (component),
  KEY type (type),
  KEY mptt_left (mptt_left),
  KEY mptt_right (mptt_right),
  KEY hide_sitewide (hide_sitewide),
  KEY is_spam (is_spam)
) {Options}'''

CreateTbs['bp_activity_meta'] = '''CREATE TABLE {Pfx}bp_activity_meta (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  activity_id bigint(20) NOT NULL,
  meta_key varchar(255) DEFAULT NULL,
  meta_value longtext DEFAULT NULL,
  KEY activity_id (activity_id),
  KEY meta_key (meta_key(191))
) {Options}'''

# Install database tables for the Notifications component.
# bp_core_install_friends() {
CreateTbs['bp_friends'] = '''CREATE TABLE {Pfx}bp_friends (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  initiator_user_id bigint(20) NOT NULL,
  friend_user_id bigint(20) NOT NULL,
  is_confirmed bool DEFAULT 0,
  is_limited bool DEFAULT 0,
  date_created datetime NOT NULL,
  KEY initiator_user_id (initiator_user_id),
  KEY friend_user_id (friend_user_id)
) {Options}'''

# Install database tables for the Groups component.
# bp_core_install_groups() {
CreateTbs['bp_groups'] = '''CREATE TABLE {Pfx}bp_groups (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  creator_id bigint(20) NOT NULL,
  name varchar(100) NOT NULL,
  slug varchar(200) NOT NULL,
  description longtext NOT NULL,
  status varchar(10) NOT NULL DEFAULT 'public',
  enable_forum tinyint(1) NOT NULL DEFAULT '1',
  date_created datetime NOT NULL,
  KEY creator_id (creator_id),
  KEY status (status)
) {Options}'''

CreateTbs['bp_groups_members'] = '''CREATE TABLE {Pfx}bp_groups_members (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  group_id bigint(20) NOT NULL,
  user_id bigint(20) NOT NULL,
  inviter_id bigint(20) NOT NULL,
  is_admin tinyint(1) NOT NULL DEFAULT '0',
  is_mod tinyint(1) NOT NULL DEFAULT '0',
  user_title varchar(100) NOT NULL,
  date_modified datetime NOT NULL,
  comments longtext NOT NULL,
  is_confirmed tinyint(1) NOT NULL DEFAULT '0',
  is_banned tinyint(1) NOT NULL DEFAULT '0',
  invite_sent tinyint(1) NOT NULL DEFAULT '0',
  KEY group_id (group_id),
  KEY is_admin (is_admin),
  KEY is_mod (is_mod),
  KEY user_id (user_id),
  KEY inviter_id (inviter_id),
  KEY is_confirmed (is_confirmed)
) {Options}'''

CreateTbs['bp_groups_groupmeta'] = '''CREATE TABLE {Pfx}bp_groups_groupmeta (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  group_id bigint(20) NOT NULL,
  meta_key varchar(255) DEFAULT NULL,
  meta_value longtext DEFAULT NULL,
  KEY group_id (group_id),
  KEY meta_key (meta_key(191))
) {Options}'''

# Install database tables for the Messages component.
# bp_core_install_private_messaging() {
CreateTbs['bp_messages_messages'] = '''CREATE TABLE {Pfx}bp_messages_messages (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  thread_id bigint(20) NOT NULL,
  sender_id bigint(20) NOT NULL,
  subject varchar(200) NOT NULL,
  message longtext NOT NULL,
  date_sent datetime NOT NULL,
  KEY sender_id (sender_id),
  KEY thread_id (thread_id)
) {Options}'''

CreateTbs['bp_messages_recipients'] = '''CREATE TABLE {Pfx}bp_messages_recipients (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) NOT NULL,
  thread_id bigint(20) NOT NULL,
  unread_count int(10) NOT NULL DEFAULT '0',
  sender_only tinyint(1) NOT NULL DEFAULT '0',
  is_deleted tinyint(1) NOT NULL DEFAULT '0',
  KEY user_id (user_id),
  KEY thread_id (thread_id),
  KEY is_deleted (is_deleted),
  KEY sender_only (sender_only),
  KEY unread_count (unread_count)
) {Options}'''

CreateTbs['bp_messages_notices'] = '''CREATE TABLE {Pfx}bp_messages_notices (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  subject varchar(200) NOT NULL,
  message longtext NOT NULL,
  date_sent datetime NOT NULL,
  is_active tinyint(1) NOT NULL DEFAULT '0',
  KEY is_active (is_active)
) {Options}'''

CreateTbs['bp_messages_meta'] = '''CREATE TABLE {Pfx}bp_messages_meta (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  message_id bigint(20) NOT NULL,
  meta_key varchar(255) DEFAULT NULL,
  meta_value longtext DEFAULT NULL,
  KEY message_id (message_id),
  KEY meta_key (meta_key(191))
) {Options}'''

# Install database tables for the Profiles component.
# bp_core_install_extended_profiles() {

# These values should only be updated if they are not already present.
#if ( ! bp_get_option( 'bp-xprofile-base-group-name' ) )
#  bp_update_option( 'bp-xprofile-base-group-name', _x( 'General', 'First field-group name', 'buddypress' ) );
#if ( ! bp_get_option( 'bp-xprofile-fullname-field-name' ) ) {
#  bp_update_option( 'bp-xprofile-fullname-field-name', _x( 'Display Name', 'Display name field', 'buddypress' ) );

CreateTbs['bp_xprofile_groups'] = '''CREATE TABLE {Pfx}bp_xprofile_groups (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name varchar(150) NOT NULL,
  description mediumtext NOT NULL,
  group_order bigint(20) NOT NULL DEFAULT '0',
  can_delete tinyint(1) NOT NULL,
  KEY can_delete (can_delete)
) {Options}'''

CreateTbs['bp_xprofile_fields'] = '''CREATE TABLE {Pfx}bp_xprofile_fields (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  group_id bigint(20) unsigned NOT NULL,
  parent_id bigint(20) unsigned NOT NULL,
  type varchar(150) NOT NULL,
  name varchar(150) NOT NULL,
  description longtext NOT NULL,
  is_required tinyint(1) NOT NULL DEFAULT '0',
  is_default_option tinyint(1) NOT NULL DEFAULT '0',
  field_order bigint(20) NOT NULL DEFAULT '0',
  option_order bigint(20) NOT NULL DEFAULT '0',
  order_by varchar(15) NOT NULL DEFAULT '',
  can_delete tinyint(1) NOT NULL DEFAULT '1',
  KEY group_id (group_id),
  KEY parent_id (parent_id),
  KEY field_order (field_order),
  KEY can_delete (can_delete),
  KEY is_required (is_required)
) {Options}'''

CreateTbs['bp_xprofile_data'] = '''CREATE TABLE {Pfx}bp_xprofile_data (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  field_id bigint(20) unsigned NOT NULL,
  user_id bigint(20) unsigned NOT NULL,
  value longtext NOT NULL,
  last_updated datetime NOT NULL,
  KEY field_id (field_id),
  KEY user_id (user_id)
) {Options}'''

CreateTbs['bp_xprofile_meta'] = '''CREATE TABLE {Pfx}bp_xprofile_meta (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  object_id bigint(20) NOT NULL,
  object_type varchar(150) NOT NULL,
  meta_key varchar(255) DEFAULT NULL,
  meta_value longtext DEFAULT NULL,
  KEY object_id (object_id),
  KEY meta_key (meta_key(191))
) {Options}'''

#Insert the default group and fields.
#$insert_sql = array();
#if ( ! $wpdb->get_var( "SELECT id FROM {$bp_prefix}bp_xprofile_groups WHERE id = 1" ) ) {
#  $insert_sql[] = "INSERT INTO {$bp_prefix}bp_xprofile_groups ( name, description, can_delete ) VALUES ( " . $wpdb->prepare( '%s', stripslashes( bp_get_option( 'bp-xprofile-base-group-name' ) ) ) . ", '', 0 );";
#}
#if ( ! $wpdb->get_var( "SELECT id FROM {$bp_prefix}bp_xprofile_fields WHERE id = 1" ) ) {
#  $insert_sql[] = "INSERT INTO {$bp_prefix}bp_xprofile_fields ( group_id, parent_id, type, name, description, is_required, can_delete ) VALUES ( 1, 0, 'textbox', " . $wpdb->prepare( '%s', stripslashes( bp_get_option( 'bp-xprofile-fullname-field-name' ) ) ) . ", '', 1, 0 );";
#}

# Install database tables for the Sites component.
# bp_core_install_blog_tracking() {
CreateTbs['bp_user_blogs'] = '''CREATE TABLE {Pfx}bp_user_blogs (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id bigint(20) NOT NULL,
  blog_id bigint(20) NOT NULL,
  KEY user_id (user_id),
  KEY blog_id (blog_id)
) {Options}'''

CreateTbs['bp_user_blogs_blogmeta'] = '''CREATE TABLE {Pfx}bp_user_blogs_blogmeta (
  id bigint(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  blog_id bigint(20) NOT NULL,
  meta_key varchar(255) DEFAULT NULL,
  meta_value longtext DEFAULT NULL,
  KEY blog_id (blog_id),
  KEY meta_key (meta_key(191))
) {Options}'''



'''
wdb3> select * from mysql.servers;
| Server_name      | Host      | Db          | Username  | Password          | Port | Socket | Wrapper | Owner |
| db1_global       | db1       | wp_global  | wpdb_user | wpdb_pass    | 3306 |        | mysql   | root  |

DROP SERVER 'db1_global';

dev.mysql.com/doc/refman/5.7/en/create-server.html
  server_name should be a unique reference to the server. = PRIMARY KEY
  wrapper_name should be mysql. Other values are not currently supported.
  OWNER option is currently not applied, and has no effect on the ownership or operation of the server connection that is created.

[bad!] update servers set host='127.0.0.1', port=53301 where Server_name = 'db3.wp_global';
[good] ALTER SERVER 'db3.wp_global' options (host '127.0.0.1', port 53301);
'''
#CreateDbSvrSql = '''CREATE SERVER 'db1_global' FOREIGN DATA WRAPPER 'mysql'
#   OPTIONS (HOST 'db1', DATABASE 'wp_global', USER 'wpdb_user', PASSWORD
#   'wpdb_pass', PORT 3306, SOCKET '', OWNER 'root')'''


# /fs/dev/wp/sql/create-federated-tables/drop-wp_bpuser-tables.sql
'''
  DROP TABLE {Pfx}bp_activity;
  DROP TABLE {Pfx}bp_activity_meta;
  DROP TABLE {Pfx}bp_friends;
  DROP TABLE {Pfx}bp_groups;
  DROP TABLE {Pfx}bp_groups_groupmeta;
  DROP TABLE {Pfx}bp_groups_members;
  DROP TABLE {Pfx}bp_messages_messages;
  DROP TABLE {Pfx}bp_messages_meta;
  DROP TABLE {Pfx}bp_messages_notices;
  DROP TABLE {Pfx}bp_messages_recipients;
  DROP TABLE {Pfx}bp_notifications;
  DROP TABLE {Pfx}bp_notifications_meta;
  DROP TABLE {Pfx}bp_user_blogs;
  DROP TABLE {Pfx}bp_user_blogs_blogmeta;
  DROP TABLE {Pfx}bp_xprofile_data;
  DROP TABLE {Pfx}bp_xprofile_fields;
  DROP TABLE {Pfx}bp_xprofile_groups;
  DROP TABLE {Pfx}bp_xprofile_meta;
  DROP TABLE {Pfx}usermeta;
  DROP TABLE {Pfx}users;

#No Drop TABLE {Pfx}options;

DropBpUsersTables = (
  'bp_activity',
  'bp_activity_meta',
  'bp_friends',
  'bp_groups',
  'bp_groups_groupmeta',
  'bp_groups_members',
  'bp_messages_messages',
  'bp_messages_meta',
  'bp_messages_notices',
  'bp_messages_recipients',
  'bp_notifications',
  'bp_notifications_meta',
  'bp_user_blogs',
  'bp_user_blogs_blogmeta',
  'bp_xprofile_data',
  'bp_xprofile_fields',
  'bp_xprofile_groups',
  'bp_xprofile_meta',
  'usermeta',
  'users',
)
FederatedTables = DropBpUsersTables + ('options',)
'''



def InitVersions(self):
  # The WordPress version string
  # @global string wp_version
  self.wp_version = '4.7.1'
  
  # Holds the WordPress DB revision, increments when changes are made to the WordPress DB schema.
  # @global int wp_db_version
  self.wp_db_version = 38590

  # Holds the TinyMCE version
  # @global string tinymce_version
  self.tinymce_version = '4403-20160901'
  
  # Holds the required PHP version
  # @global string required_php_version
  self.required_php_version = '5.2.4'
  
  # Holds the required MySQL version
  # @global string required_mysql_version
  self.required_mysql_version = '5.0'

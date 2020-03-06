import config.host_loc as cHL
import config.host     as cHO
import wpy.time        as wTm
ODict = cHO.ODict

ReloadA2   = "sudo systemctl reload  apache2.service"
RestartA2  = "sudo systemctl restart apache2.service"
def RestartPhpCmd(H):
  PhpFpmVer = '7.2' if H.Host == cHO.H000002 else '7.1'
  return "sudo systemctl restart php{}-fpm.service".format(PhpFpmVer)

#if Host == cHO.H000002:
#  ln -s /fs/app /fs/app

def SvrCmds(Seq, D, H):   # D = DeploySiteCls(SId)
  # using svn co, no need to create wp-content, plugins, & themes dir.
  # H.WC.SCDir +' '+ H.WC.SPDir +' '+ H.WC.STDir +' '+ H.WC.SDDir
  #MkDirs   =(H.WC.WebD +' '+ H.WC.WWwDir +' '+ H.WC.WPDir +' '+ H.WC.WTDir
  #           +' '+ H.WC.WwwD +' '+ H.WC.SDir +' '+ H.WC.LogD)
  #ChownDirs=(                H.WC.WWwDir +' '+ H.WC.WPDir +' '+ H.WC.WTDir
  #           +' '+ H.WC.WwwD +' '+ H.WC.SDir +' '+ H.WC.LogD)
  ChownDirs=' '.join((H.WC.WWwDir, H.WC.WPDir, H.WC.WTDir,
                      H.WC.WwwD, H.WC.SDir, H.WC.LogD))
  MkDirs = H.WC.WebD +' '+ ChownDirs

  if Seq == 0: return ODict([
    # Id,  Required, Cmd
    ( 10, (False,'echo "$(hostname --fqdn) $(hostname -I) $(date)"'
                 ' >> /tmp/ssh_`date "+%Y%m%d%H"`'   )),
    ( 11, (True ,'df . ; hostname -I'                )),
    ( 21, (False,'sudo apt install subversion'       )),
    ( 22, (True ,'sudo mkdir -p -m 770 '+ MkDirs     )),
    ( 25, (True ,'sudo touch '        + H.WC.LogDebug)),
    ( 26, (True ,'sudo chmod 660 '    + H.WC.LogDebug)),
    ( 28, (True ,'sudo chown -R '+ cHL.UsrGrpLocAdm +' '+ ChownDirs )),
    ( 31, (True ,'sudo chown sshfs:ubt /etc/apache2'
                 ' /etc/apache2/sites-available'     )),
    ( 32, (True ,'sudo chmod g+w        /etc/apache2'
                 ' /etc/apache2/sites-available'     )),
  ])

  elif Seq == 1: return ODict([
    # Id,  Required, Cmd
    (121, (True ,'mv '   +H.WC.SDir+'index.php '+H.WC.SDir+'index.Orig.php' )),
    (122, (True ,'ln -s '+H.WC.SDir+'index-redis.php '+H.WC.SDir+'index.php')),
    (123, (True ,'ls -l '+H.WC.SDir+'index.php '+H.WC.SDir+'index.Orig.php' )),
    (160, (True ,'sudo mkdir -p '+ cHL.BkpDir
                                 + cHO.A2_SitesAv    )), #include cHO.A2_Dir
    (161, (True ,'sudo mv '+cHO.A2_DirConf+'.20* '+ cHL.BkpDir + cHO.A2_Dir)),
    (162, (True ,'sudo mv '+cHO.A2_SitesAv+D.SName+'.conf.20* '
                           + cHL.BkpDir+ cHO.A2_SitesAv)),
    (181, (True ,'sudo chown -R '+ cHO.UsrGrpWww +' '+ ChownDirs )),
    (182, (True ,'sudo find '+ ChownDirs +' -type f -exec chmod 660 {} +')),
    #             sudo find .               -type f -exec chmod 660 {} +
    (183, (True ,'sudo find '+ ChownDirs +' -type d -exec chmod 770 {} +')),
    #             sudo find .               -type d -exec chmod 660 {} +
    (185, (True ,'sudo a2ensite '+ D.SName          )),
    # mod headers for cross domain fonts: zinoui.com/blog/cross-domain-fonts
    (186, (True ,'sudo a2enmod  headers'           )),
    (191, (True ,ReloadA2   )),
    (192, (False,RestartA2  )),
    (193, (True ,RestartPhpCmd(H) )),
  ])


PatchDict = {}
#PSlug: (search for StrInFile [If File was patched], FPath, Orig, Patch),

PatchDict['wp'] = (
	# for tag-cloud, tagcloud
  ('!important',   'wp-includes/category-template.php',
    b'''$args['unit'] ) . ";''',
    b'''$args['unit'] ) . " !important;''' ,
  ),

  ## /fs/md/wp/p/hyperdb-db.php
  #('VT',   'wp-includes/wp-db.php',
  # b"'|DELETE(?:\s+LOW_PRIORITY|\s+QUICK|\s+IGNORE)*(?:\s+FROM)?'",
  # b"'|DELETE(?:.+FROM)?'",),  #VT fixed core.trac.wordpress.org/ticket/37660

  ('VT1',          'wp-admin/includes/schema.php',
    b"function wp_get_db_schema( $scope = 'all', $blog_id = null ) {\n"
    b"	global $wpdb;"  ,

    b"function wp_get_db_schema( $scope = 'all', $blog_id = null ) {\n"
    b"	global $wpdb;\n"
    b"	if ( defined('WPY_NEW_SITE_ID') && defined('WPY_NEW_BLOG_ID') ) {\n"
    b"		$site_id = WPY_NEW_SITE_ID;             // VT1 Add\n"
    b"		$blog_id = WPY_NEW_BLOG_ID;             // VT1 Add\n"
    b"		$wpdb->set_blog_id($blog_id, $site_id); // VT1 Add\n"
    b"	} //VT Add End" ,
  ),

  ('VT2',          'wp-admin/includes/schema.php',
    b"function populate_network( $network_id = 1, $domain = '', $email = '',"
      b" $site_name = '', $path = '/', $subdomain_install = false ) {",

    b"function populate_network( $network_id = 1, $domain = '', $email = '',"
      b" $site_name = '', $path = '/', $subdomain_install = false,"
      b" $blog_id = 1 ) { //VT2 Add: , $blog_id = 1" ,
  ),

  ('VT3',          'wp-admin/includes/schema.php',
    b"$wpdb->insert( $wpdb->blogs, array( 'site_id' => $network_id,"
      b" 'blog_id' => 1, 'domain' => $domain, 'path' => $path,"
      b" 'registered' => current_time( 'mysql' ) ) );" ,

    b"#VT3 Changed from 'blog_id' => 1 to below 'blog_id' => $blog_id\n"
    b"$wpdb->insert( $wpdb->blogs, array( 'site_id' => $network_id,"
      b" 'blog_id' => $blog_id, 'domain' => $domain, 'path' => $path,"
      b" 'registered' => current_time( 'mysql' ) ) );\n"
    b"		# VT3 Added below 4 Lines:\n"
    b"		$WpBlogsInsertId = $wpdb->insert_id;\n"
    b"		if ($blog_id != $WpBlogsInsertId) {\n"
    b"			error_log('Warning! Newly inserted wp_blogs has blog_id="
      b" $WpBlogsInsertId, that is different from the given blog_id=$blog_id."
      b" Choose to use $WpBlogsInsertId instead!');\n"
    b"		}" ,
  ),
  ('#VT Add defined', 'wp-includes/wp-db.php',
    b"public function get_blog_prefix( $blog_id = null ) {\n"
    b"		if ( is_multisite() ) {" ,
    b"public function get_blog_prefix( $blog_id = null ) {\n"
    b"		if ( is_multisite() || defined('WP_INSTALLING')) { #VT Add defined",
  ),

  ('#VT Add GetPostContentFromRados', 'wp-includes/class-wp-post.php',
  #b"			$_post = sanitize_post( $_post, 'raw' );\n"
    b"wp_cache_add( $_post->ID, $_post, 'posts' );" ,
    b"""#VT Add GetPostContentFromRados below
			if ( $_post->post_content == '[wpy]' )
				$_post->post_content = file_get_contents("http://ww1.wordpy.com:8080/blogid/{$wpdb->blogid}/{$_post->ID}/");
			wp_cache_add( $_post->ID, $_post, 'posts' );""" ,
  ),
  #    $_post->post_excerpt
)

PatchDict['merc'] = (
  ('191',          'mercator.php',
    b'domain varchar(255) NOT NULL,' ,
    b'domain varchar(191) NOT NULL,' ,
  ),
)

PatchDict['bbp'] = (   # See /fs/md/wp/bbpress-js-css-cannot-load.md
  ('VT Orig',      'bbpress.php',
    b"$this->plugin_dir = apply_filters( 'bbp_plugin_dir_path', plugin_dir_path( $this->file ) );" ,
    b"#$this->plugin_dir = apply_filters( 'bbp_plugin_dir_path', plugin_dir_path( $this->file ) ); # VT Orig\n"
    b"$this->plugin_dir = apply_filters( 'bbp_plugin_dir_path', WP_PLUGIN_DIR . '/bbpress/' );   #VT New" ,
  ),
)

PatchDict['bp'] = (
  ('time()+10',    'bp-core/bp-core-functions.php',
    b"false, time() - 1000," ,
    b"$_COOKIE['bp-message'], time()+10," ,
  ),
  ('<!iframe',     'bp-core/classes/class-bp-media-extractor.php',
    b"#src=(" ,
    b"#(?<!iframe) src=(" ,
  ),
)

PatchDict['MSiteOn'] = (
  ('#wpy.exe Uncomment#',   'wp-config.php',
    b'#MSiteOff#',   b'#wpy.exe Uncomment#\n' ,
  ),
)

PatchDict['SUNRISE'] = (
  ('#VT Enable SUNRISE', 'wp-config.php',
    b'#SUNRISE#',         b'#VT Enable SUNRISE\n' ,
  ),
)

AvadaReduxCoreFramework = b'''
				if ( strpos( FusionRedux_Helpers::cleanFilePath( __FILE__ ), FusionRedux_Helpers::cleanFilePath( get_stylesheet_directory() ) ) !== false || strpos( FusionRedux_Helpers::cleanFilePath( __FILE__ ), FusionRedux_Helpers::cleanFilePath( get_template_directory_uri() ) ) !== false || strpos( FusionRedux_Helpers::cleanFilePath( __FILE__ ), FusionRedux_Helpers::cleanFilePath( WP_CONTENT_DIR . '/themes/' ) ) !== false ) {
					self::$_is_plugin = false;
				} else {
					// Check if plugin is a symbolic link, see if it's a plugin. If embedded, we can't do a thing.
					if ( strpos( self::$_dir, ABSPATH ) === false ) {
						if ( ! function_exists( 'get_plugins' ) ) {
							require_once wp_normalize_path( ABSPATH . 'wp-admin/includes/plugin.php' );
						}

						$is_plugin = false;
						foreach ( get_plugins() as $key => $value ) {
							if ( is_plugin_active( $key ) && strpos( $key, 'fusionredux-framework.php' ) !== false ) {
								self::$_dir = trailingslashit( FusionRedux_Helpers::cleanFilePath( WP_CONTENT_DIR . '/plugins/' . plugin_dir_path( $key ) . 'FusionReduxCore/' ) );
								$is_plugin  = true;
							}
						}
						if ( ! $is_plugin ) {
							self::$_is_plugin = false;
						}
					}
				}

				if ( self::$_is_plugin == true || self::$_as_plugin == true ) {
					self::$_url = plugin_dir_url( __FILE__ );
				} else {
					if ( strpos( FusionRedux_Helpers::cleanFilePath( __FILE__ ), FusionRedux_Helpers::cleanFilePath( get_template_directory() ) ) !== false ) {
						$relative_url = str_replace( FusionRedux_Helpers::cleanFilePath( get_template_directory() ), '', self::$_dir );
						self::$_url   = trailingslashit( get_template_directory_uri() . $relative_url );
					} else if ( strpos( FusionRedux_Helpers::cleanFilePath( __FILE__ ), FusionRedux_Helpers::cleanFilePath( get_stylesheet_directory() ) ) !== false ) {
						$relative_url = str_replace( FusionRedux_Helpers::cleanFilePath( get_stylesheet_directory() ), '', self::$_dir );
						self::$_url   = trailingslashit( get_stylesheet_directory_uri() . $relative_url );
					} else {
						$wp_content_dir = trailingslashit( FusionRedux_Helpers::cleanFilePath( WP_CONTENT_DIR ) );
						$wp_content_dir = trailingslashit( str_replace( '//', '/', $wp_content_dir ) );
						$relative_url   = str_replace( $wp_content_dir, '', self::$_dir );
						self::$_url     = trailingslashit( self::$wp_content_url . $relative_url );
					}
				}

				self::$_url       = apply_filters( "fusionredux/_url", self::$_url );
				self::$_dir       = apply_filters( "fusionredux/_dir", self::$_dir );
				self::$_is_plugin = apply_filters( "fusionredux/_is_plugin", self::$_is_plugin );'''

PatchDict['AvadaRedux'] = (
  ('/*  VT Comment out', '/fs/web/t/Avada/includes/lib/inc/redux/framework/FusionReduxCore/framework.php',
    AvadaReduxCoreFramework,
    b'''
						/*  VT Comment out''' + AvadaReduxCoreFramework + b'''
						 */
						self::$_url       = get_bloginfo('template_directory') . '/includes/lib/inc/redux/framework/FusionReduxCore/';   # VT New
						self::$_is_plugin = false;   # VT New''' ,
  ),
)

AvadaRmFontSizeFromTagCloudFilter = b"add_filter( 'wp_tag_cloud', array( $this, 'remove_font_size_from_tagcloud' ) );"

PatchDict['AvadaTagCloud'] = (
  ('# VT removed filter', '/fs/web/t/Avada/includes/class-avada-init.php',
    AvadaRmFontSizeFromTagCloudFilter,
    b'# '+ AvadaRmFontSizeFromTagCloudFilter + b'    # VT removed filter' ,
  ),
)

AvadaRmFontSizeFromTagCloudFunc = b'''
	public function remove_font_size_from_tagcloud( $tagcloud ) {
		return preg_replace( '/ style=(["\'])[^\1]*?\1/i', '', $tagcloud, -1 );
	}'''

PatchDict['AvadaTagCloud'] = (
  ('/*  VT Comment out', '/fs/web/t/Avada/includes/class-avada-init.php',
    AvadaRmFontSizeFromTagCloudFunc,
    b'/*  VT Comment out remove_font_size_from_tagcloud()\n\t'+ \
      AvadaRmFontSizeFromTagCloudFunc + b' */' ,
  ),
)


# Target= Plugin ('bp',...) or 'wp'
def PatchFiles(H, Target, BaseDir):
  Sftp = H.WH.Sftp
  if Target in PatchDict:  # in PatchDict.keys():
    BackedUpFiles = []
    for P in PatchDict[Target]:
      StrInFile= P[0]  # Str In File if File Already Patched
      FName    = P[1]
      File     = BaseDir + FName   #Full Path of Orig File
      OldStr   = P[2]
      NewStr   = P[3]
      BkpFile  = File + wTm.DotNowYMDHM()
      print('Target File=',File, '. Find StrInFile=', StrInFile, 'to see if'
            ' File had been patched. OldStr=', OldStr,', NewStr=', NewStr)
      with Sftp.open(File, 'r') as F_Sftp:
        FInData = F_Sftp.read()
      if StrInFile.encode() in FInData:
        print('Target file already patched. Skip.')
        continue

      #Orig: else: start
      if File in BackedUpFiles:
        print('Target',BkpFile,' already BackedUp. No need to backup again')
      else:
        print('Target not backed up. Rename Target to BkpFile:', BkpFile)
        if H.WH.SftpPathExist(BkpFile):
          Sftp.remove(BkpFile)
        Sftp.rename(File, BkpFile)
        BackedUpFiles.append(File)

      FOutData = FInData.replace(OldStr, NewStr)
      print('Try to patch and save file:', File)
      with Sftp.open(File, 'w') as F_Sftp:
        F_Sftp.write(FOutData)

      if FName == 'wp-config.php':  # write patched wp-config to LocalFile
        import wpy.web_deploy as WD
        LocalFile = H.WC.LocSiteDir + FName + wTm.DotNowYMDHM()
        with open(LocalFile, 'w') as FOut:
          FOut.write(FOutData.decode())
      #Orig: else: end


# wordpy
WordPress PHP translated to pure native Python. Optimized to manage data, users, posts, etc in WordPress files and MySQL in private, public, or hybrid cloud using SSH.


# Installation
cd ~
git clone https://github.com/wordpy/wordpy.git
cd  wordpy   # =  cd ~/wordpy
vi  config/host.py config/db.py # search for '#TODO' and change its config 


## There are 4 ways to create the initial blog or global database tables:
1)   Do it in WordPress

2~4) below

ipython -i -c "import wpy.web_deploy as WD"
>>> DBlog = WD.DeployBlogCls(1, ConnSsh=False)
>>> DBlog.CreateDb_GrantUser()

2) DBlog.CreateBlog()  # uses: DBlog.WH0.Exec("wp wpy-site create --path=...")
3) DBlog.BDB.Exec(<SQL from wp-admin/includes/schema.php>)
4) DBlog.CreateBlogSa() below using SqlAlchemy
   ipython -i -c "import wpy.web_deploy as WD"
   > DBlog = WD.DeployBlogCls(1, ConnSsh=False)
   > DBlog.CreateBlogSa()   # or:  WpModels, Db = DBlog.CreateBlogSa()

>>> DBlog.CreateBlogSa()

mysql
> use wp_global;  -- after [2]
> show tables;    -- after [3]
+-----------------------+
| Tables_in_wp_global   |
+-----------------------+
| wp_blog_versions      |
| wp_blogs              |
| wp_commentmeta        |
| wp_comments           |
| wp_links              |
| wp_options            |
| wp_postmeta           |
| wp_posts              |
| wp_registration_log   |
| wp_signups            |
| wp_site               |
| wp_sitemeta           |
| wp_term_relationships |
| wp_term_taxonomy      |
| wp_termmeta           |
| wp_terms              |
| wp_usermeta           |
| wp_users              |
+-----------------------+
18 rows in set (0.001 sec)


# You can Deploy WordPress sites by:

DSite = WD.DeploySiteCls(1, cHO.H100003)
DSite.DownloadWp()
DSite.SetupWDoc()
DSite.InstallAllThemes()
DSite.InstallAllPlugins()
DSite.WrapUpWDeploy()
DSite.DomainMapping()


## Later on, you can activate Plugins and Themes to your Blog

>>> DBlog.BlogActivatePlugin(Slug='bp')
>>> DBlog.BlogActivateTheme(Slug=None)
>>> DBlog.UpdateBlogDesc()
...



ipython -i -c "from wpy.web import WB"
>>> WB.GetBlogObjWpObj(1)
>>> WB.Bj.BDB.Exec('show databases')
Out: (<wpy.web.BlogCls at 0x7fcaa37e2e48>, <wpy.web.WpCls at 0x7fcac38998d0>)


In WordPress, you can have network of sites (Sites).
Each Site can have many Blogs.
As you can see below, every blog is store in a Blog Object (Bj).

>>> WB.BId
Out: 1
>>> WB.Bj.BId
Out: 1

>>> WB.Bj.BDB.Exec('show databases')
Out:
[OrderedDict([('Database', 'information_schema')]),
 OrderedDict([('Database', 'mysql')]),
 OrderedDict([('Database', 'performance_schema')]),
 OrderedDict([('Database', 'wp_global')])]

>>> WB.Wj.wpdb
Out:
<Php.Object(LudicrousDBCls)> (76) {
  ['Wj']=> <WpCls> <wpy.web.WpCls object at 0x7fcac38998d0>
  ['Bj']=> <BlogCls> <wpy.web.BlogCls object at 0x7fcaa37e2e48>
  ['AutoCommit']=> <bool> True
  ['show_errors']=> <bool> False
  ['suppress_errors']=> <bool> False
  ['num_queries']=> <int> 0
  ['num_rows']=> <int> 0
  ['rows_affected']=> <int> 0
  ['insert_id']=> <int> 0
  ['col_meta']=> <str>   array(0) { }
  ['table_charset']=> <str>   array(0) { }
  ['check_current_query']=> <bool> True
  ['checking_collation']=> <bool> False
  ['reconnect_retries']=> <int> 3
  ['prefix']=> <str> wp_
  ['table_prefix']=> <str> wp_
  ['base_prefix']=> <str> wp_
  ['ready']=> <bool> False
  ['blogid']=> <int> 1
  ['siteid']=> <int> 1
  ['blog_tables']=> <str>   array(10) {
    [0]=> <str> commentmeta
    [1]=> <str> comments
    [2]=> <str> links
    [3]=> <str> options
    [4]=> <str> postmeta
    [5]=> <str> posts
    [6]=> <str> term_relationships
    [7]=> <str> term_taxonomy
    [8]=> <str> termmeta
    [9]=> <str> terms
  }
  ['global_tables']=> <str>   array(2) {
    [0]=> <str> users
    [1]=> <str> usermeta
  }
  ['ms_global_tables']=> <str>   array(6) {
    [0]=> <str> blog_versions
    [1]=> <str> blogs
    [2]=> <str> registration_log
    [3]=> <str> signups
    [4]=> <str> site
    [5]=> <str> sitemeta
  }
  ['field_types']=> <str>   array(0) { }
  ['is_mysql']=> <NoneType> None
  ['incompatible_modes']=> <str>   array(5) {
    [0]=> <str> NO_ZERO_DATE
    [1]=> <str> ONLY_FULL_GROUP_BY
    [2]=> <str> STRICT_TRANS_TABLES
    [3]=> <str> STRICT_ALL_TABLES
    [4]=> <str> TRADITIONAL
  }
  ['has_connected']=> <bool> False
  ['use_mysqli']=> <bool> True
  ['dbuser']=> <str> root
  ['dbpassword']=> <str> wpdb_pass
  ['dbname']=> <str> wp_global
  ['dbhost']=> <str> pa80:3306
  ['last_table']=> <str>
  ['last_found_rows_result']=> <NoneType> None
  ['save_queries']=> <bool> False
  ['dbhs']=> <str>   array(0) { }
  ['dbconns']=> <str>   array(0) { }
  ['LDbServers']=> <str>   array(1) {
    ['global']=> <str>     array(2) {
      ['read']=> <str>       array(2) {
        [50]=> <str>         array(1) {
          [0]=> <str>           array(7) {
            ['host']=> <str> db1
            ['name']=> <str> wp_global
            ['user']=> <str> wpdb_user
            ['password']=> <str> wpdb_pass
            ['write']=> <int> 50
            ['read']=> <int> 50
            ['timeout']=> <float> 0.6
          }
        }
        [51]=> <str>         array(1) {
          [0]=> <str>           array(7) {
            ['host']=> <str> db2
            ['name']=> <str> wp_global
            ['user']=> <str> wpdb_user
            ['password']=> <str> wpdb_pass
            ['write']=> <int> 51
            ['read']=> <int> 51
            ['timeout']=> <float> 0.6
          }
        }
      }
      ['write']=> <str>       array(2) {
        [50]=> <str>         array(1) {
          [0]=> <str>           array(7) {
            ['host']=> <str> db1
            ['name']=> <str> wp_global
            ['user']=> <str> wpdb_user
            ['password']=> <str> wpdb_pass
            ['write']=> <int> 50
            ['read']=> <int> 50
            ['timeout']=> <float> 0.6
          }
        }
        [51]=> <str>         array(1) {
          [0]=> <str>           array(7) {
            ['host']=> <str> db2
            ['name']=> <str> wp_global
            ['user']=> <str> wpdb_user
            ['password']=> <str> wpdb_pass
            ['write']=> <int> 51
            ['read']=> <int> 51
            ['timeout']=> <float> 0.6
          }
        }
      }
    }
  }
  ['LDbTables']=> <str>   array(0) { }
  ['LDbCallbacks']=> <str>   array(0) { }
  ['save_query_callback']=> <NoneType> None
  ['persistent']=> <bool> False
  ['max_connections']=> <int> 10
  ['check_tcp_responsiveness']=> <bool> True
  ['srtm']=> <str>   array(0) { }
  ['db_connections']=> <str>   array(0) { }
  ['open_connections']=> <str>   array(0) { }
  ['dbh2host']=> <str>   array(0) { }
  ['last_used_server']=> <str>   array(0) { }
  ['used_servers']=> <str>   array(0) { }
  ['save_backtrace']=> <bool> True
  ['default_lag_threshold']=> <NoneType> None
  ['charset']=> <str> utf8mb4
  ['collate']=> <str> utf8mb4_unicode_ci
  ['DbConnErrNum']=> <dict> {}
  ['DbConnErrMsg']=> <dict> {}
  ['GDB']=> <GlobalDbCls> <wpy.db.GlobalDbCls object at 0x7fcac95a3588>
  ['BDB']=> <BlogDbCls> <wpy.db.BlogDbCls object at 0x7fcac3889240>
  ['commentmeta']=> <str> wp_commentmeta
  ['comments']=> <str> wp_comments
  ['links']=> <str> wp_links
  ['options']=> <str> wp_options
  ['postmeta']=> <str> wp_postmeta
  ['posts']=> <str> wp_posts
  ['term_relationships']=> <str> wp_term_relationships
  ['term_taxonomy']=> <str> wp_term_taxonomy
  ['termmeta']=> <str> wp_termmeta
  ['terms']=> <str> wp_terms
  ['users']=> <str> wp_users
  ['usermeta']=> <str> wp_usermeta
  ['blog_versions']=> <str> wp_blog_versions
  ['blogs']=> <str> wp_blogs
  ['registration_log']=> <str> wp_registration_log
  ['signups']=> <str> wp_signups
  ['site']=> <str> wp_site
  ['sitemeta']=> <str> wp_sitemeta
}

>>> import pyx.php as Php
>>> post = Php.array()
>>> post['post_title'] = 'WordPy -- WordPress PHP translated to pure Python.'
>>> import wp.i.post as WiP
>>> WiP.wp_insert_post(post)


Later on, you can deploy more blogs and switch between Blogs with ease.

vi wp/conf.py                    # change SiteOD and BlogOD, etc
vi config/host.py config/db.py   # change accordingly



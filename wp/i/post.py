#!/usr/bin/python3.5
# vi /usr/local/lib/python3.5/dist-packages/wordpress_xmlrpc/wordpress.py
from   datetime    import datetime
import pyx.php     as Php
import wpy.time    as wTm
import wpy.xmlcli  as XmlC       # Xml Client Class
import wp.conf     as WpC
import wp.i.cls.error     as WcE  # WP_Error
import wp.i.cls.post      as WcP
import wp.i.cls.post_type as WcPT
import wp.i.cache    as WiCa
import wp.i.format   as WiF
import wp.i.func     as WiFc
import wp.i.l10n     as WiTr
import wp.i.meta     as WiM
import wp.i.option   as WiO
import wp.i.plugin   as WiPg
import wp.i.revision as WiR
import wp.i.taxonomy as WiTx
#from   wp.i.wpdb import wpdb

array, ODict = Php.array, Php.ODict
ARRAY_A = 'ARRAY_A'
ARRAY_N = 'ARRAY_N'

# tommcfarlin.com/post-status-when-updating/
EnableFuturePostStatus = False


#class PostC:  #Post Class variables are shared among class instances
#  Bj = Exit = XmlCli = BDB = None
#  # /usr/local/lib/python3.5/dist-packages/wordpress_xmlrpc/methods/posts.py
def IniXmlMethods():
  WpC.WB.Bj.XmlMethods = ['GetPosts', 'GetPost', 'NewPost', 'EditPost',
         'DeletePost' , 'GetPostStatusList', 'GetPostFormats' , 'GetPostTypes',
         'GetPostType', 'GetRevisions',      'RestoreRevision',]
  

# Move all staticmethods to module fuctions. staticmethod has no benifit other than grouping them in a class, but we're already grouping all in this module


#def InitPostGlobals(self):
#  ''' Initialize the Post Types globals. Call from wp.settings. self = WpC.WB.Wj
#  global var==>self.var, except: var=self.var=same Obj,mutable array
#  global var in the rest of this module is assigned to the same mutable obj
#  '''
#  if not Php.is_array(getattr(self, 'wp_post_types',         None)):
#    self.wp_post_types         = array()
#  # wp-includes/capabilities.php
#  if not Php.is_array(getattr(self, 'post_type_meta_caps',   None)):
#    self.post_type_meta_caps   = array()
#  if not Php.is_array(getattr(self, '_wp_post_type_features',None)):
#    self._wp_post_type_features= array()
#  if not Php.is_array(getattr(self, 'wp_post_statuses',      None)):
#    self.wp_post_statuses      = array()
#
#  #global wp_post_types, wp_post_statuses  # , wp_rewrite
#  #global post_type_meta_caps, _wp_post_type_features
#  # set to the same mutable array() below. Php = array()
#  #wp_post_types         = self.wp_post_types           #= same mutable array()
#  #post_type_meta_caps   = self.post_type_meta_caps     #= same mutable array()
#  #_wp_post_type_features= self._wp_post_type_features  #= same mutable array()
#  #wp_post_statuses      = self.wp_post_statuses        #= same mutable array()
#  #wp_rewrite            = self.wp_rewrite              #= same mutable Obj
#  WcPT.InitPostTypesGlobals(self)



def user_can_richedit():
  "benjaminhorn.io/code/wordpress-visual-editor-not-visible-because-of-user-agent-sniffing/)"
  return True

def current_user_can( *args, **kwargs):
  return True

__, _x, _n_noop = WiTr.__, WiTr._x, WiTr._n_noop


Sel_P_TR_TT_T_Sql = ("SELECT p.ID, COUNT(p.ID) AS IDs, p.post_title, "
  "p.post_date, t.name, t.term_id, tt.term_taxonomy_id "
  "FROM       {T}  t          "
  "INNER JOIN {TT} tt ON ( t.term_id         = tt.term_id         ) "
  "INNER JOIN {TR} tr ON (tr.term_taxonomy_id= tt.term_taxonomy_id) "
  "INNER JOIN {P}  p  ON ( p.ID              = tr.object_id       ) "
  "WHERE tt.taxonomy   =  'post_tag' "
  "AND   p.post_title  =  %(title)s "
  "AND   p.post_type   =  'post' "
  "AND   p.post_status =  'publish' "
  "AND   p.post_date   =  %(Date)s "
  "AND   t.name IN (%(Sym)s, %(TypeR)s ) "
  "GROUP BY p.ID HAVING IDs > 1 ORDER BY p.ID" )
#  AND   p.post_date   =  {Date!r} AND   t.name IN ({Sym!r}, {TypeR!r} )
# bang !r stackoverflow.com/questions/25441628/
# repr() shows quotes: {!r}; str() doesn't: {!s}. "{!r}".format('a') => "'a'"

Sel_P_Pm_Sql = '''SELECT p.ID, p.post_title, p.post_date, pm.meta_id,
          pm.meta_key, tr.term_taxonomy_id
   FROM wp_4_posts p
   LEFT JOIN wp_4_postmeta pm ON ( p.ID = pm.post_id )
   LEFT JOIN wp_4_term_relationships tr ON ( p.ID = tr.object_id )
   WHERE p.post_type   = 'post'
   AND   p.post_status = 'publish'
   AND   p.post_date   > '2016-01-01'
   AND   p.post_title like 'BABA%'
'''

SelDupPostsSql = ("SELECT p.ID FROM {P} p "
  "WHERE p.post_date  = %(Date)s "
  #"AND  p.post_type   = 'post' "
  #"AND  p.post_status = 'publish' "
  "AND   p.post_title = %(Title)s")

SelPostIdByPostNameSql = ("SELECT p.ID FROM {P} p "
  "WHERE p.post_name  {PostNameOp} %(PostName)s ")

SelPostContentByPostIdSql = ("SELECT p.ID, p.post_content FROM {P} p "
  "WHERE p.ID  {PIdOp} %(PId)s ")

#DELETE p, pm, tr FROM wp_300_posts p LEFT JOIN wp_300_postmeta pm ON ( p.ID = pm.post_id ) LEFT JOIN wp_300_term_relationships tr ON ( p.ID = tr.object_id )
DelPostPmTr = ( "DELETE p, pm, tr FROM {P} p "
  "LEFT JOIN {PM} pm ON ( p.ID = pm.post_id   ) "
  "LEFT JOIN {TR} tr ON ( p.ID = tr.object_id ) " )

DelPostPmTrByDateTitleSql = ( DelPostPmTr +
  "WHERE p.post_date {DateOp} %(Date)s "
  #"AND  p.post_type   = 'post' "
  #"AND  p.post_status = 'publish' "
  "AND   p.post_title {TitleOp} %(Title)s" )

DelPostPmTrByTypeStatusIdDateAuthorSql = ( DelPostPmTr +
  "WHERE p.post_type   = 'post' "
  "AND   p.post_status in ('publish','trash') "
  "AND   p.id      {PIdOp}  %(PId)s "
  "AND   p.post_date   {DateOp} %(Date)s "
  "AND   p.post_author {AIdOp}  %(AId)s  " )
# select id, post_author, post_date, left(post_title, 30) from wp_50_posts where post_title like '%fedex%'

DelPostPmTrByTypeStatusAuthorSql = ( DelPostPmTr +
  "WHERE p.post_type   = 'post' "
  "AND   p.post_status in ('publish','trash') "
  "AND   p.post_author {AIdOp}  %(AId)s  " )

DelPostPmTrByPostNameIdSql = ( DelPostPmTr +
  "WHERE p.post_name   = %(PostName)s "
  "AND   p.id   {PIdOp}  %(PId)s " )

DelPostPmTrByPostIdSql  = DelPostPmTr + "WHERE p.id {PIdOp} %(PId)s "   # {PId}
DelPostPmTrInPostIdsSql = DelPostPmTr + "WHERE p.id in ({InStr})"


# Remove Unused Terms & Fixing Term Counts. www.shawnhooper.ca/2015/10/cleaning-up-unused-terms-in-wordpress-database-in-mysql/
# 1) Delete Term Relationships: already deleted all posts and postmeta,
#    but links between those post IDs and taxonomies still existed. So del:
#    DELETE FROM wp_term_relationships
#    WHERE object_id NOT IN (SELECT ID FROM wp_posts)
DelUnusedTermRelSql = ("DELETE FROM {TR} "
  "WHERE object_id  NOT IN (SELECT ID FROM {P})")
# 2) Update Term Counts: update term counts for each taxonomy.  In deleting the hundreds of posts, many would now be used 0 times, but others would still have at least one post in them.  This will clean all of that up:
# UPDATE wp_term_taxonomy tt SET count = (SELECT count(p.ID)
# FROM wp_term_relationships tr LEFT JOIN wp_posts p ON p.ID = tr.object_id
# WHERE tr.term_taxonomy_id = tt.term_taxonomy_id)
UpdateTermCountsSql = ("UPDATE {TT} tt SET count = (SELECT count(p.ID) "
  "FROM {TR} tr LEFT JOIN {P} p ON p.ID = tr.object_id "
  "WHERE tr.term_taxonomy_id = tt.term_taxonomy_id)")
# 3) Delete All Unused Terms: (Terms no longer in use have a count of 0)
# DELETE wt FROM wp_terms a
# INNER JOIN wp_term_taxonomy b ON a.term_id = b.term_id WHERE b.count = 0
DeleteUnusedTermSql = ("DELETE t, tt FROM {T} t "
  "INNER JOIN {TT} tt ON t.term_id = tt.term_id WHERE tt.count = 0")

# wordpress.org/support/topic/how-to-remove-orphaned-term_relationships/
# DELETE tr FROM wp_term_relationships tr INNER JOIN wp_term_taxonomy tt
#   ON (tr.term_taxonomy_id = tt.term_taxonomy_id)
# WHERE tt.taxonomy != 'link_category'
# AND tr.object_id NOT IN (SELECT ID FROM wp_posts)

''' Publish "Missed schedule" = "定时发布失败" posts:
update wp_20_posts set post_status = 'publish'  where post_status = 'future'
'''

'''dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
parameters found in the tuple or dictionary params are bound to the variables in the operation. Specify variables using %s or %(name)s parameter style (that is, using format or pyformat style). 
 Variable substitution can only happen at value, not column name or table name!!!
'''

def XmlNewOrEditPost(WpPost, DupPostAction = 'skip'):
  ''' If WpPost.id > 0:  EditPost instead NewPost
  DupPostAction =
    'del' : Delete all prior posts if their dates and titles matches WpPost
    'skip': Skip trying to create new WpPost.  Return - WpPost.id as dup post
  Return: WpPost.id for NewPost, or EditSuccess for EditPost
  '''
  IniXmlMethods()
  if WpPost.id > 0:    # WpPost.id > 0, update previous post
    return XmlC.CliCall('EditPost', WpPost)
  XmlNewPost(WpPost, DupPostAction)


def XmlNewPost(WpPost, DupPostAction = 'skip'):
  '''
  DupPostAction = :
    'del'  : Delete all prior posts if their dates and titles matches WpPost
    'skip' : Skip trying to create new WpPost.  Return - WpPost.id as dup post
    'nocheck': Don't even try to check if there is any dup post. save db query
  Return: WpPost.id for NewPost, or - WpPost.id (negative) as dup post
  '''
  IniXmlMethods()
  if WpPost.id != 0:
    raise ValueError('XmlNewPost: WpPost.id must be zero!')

  if DupPostAction != 'nocheck':
    rows = SelDupPosts_with_SameDateAndTitle(WpPost)
    if len(rows) > 0:                 #if Dup Post Exists
      if DupPostAction   == 'del':
        DelDupPosts_with_SameDateAndTitle(WpPost)
      elif DupPostAction == 'skip':
        return - rows[0]['ID']  #= post id, as WpPost.id is None for new post
  return XmlC.CliCall('NewPost', WpPost=WpPost)


def XmlGetPosts():
  IniXmlMethods()
  WpPosts = XmlC.CliCall('GetPosts')
  WpDict = ODict(); n = 0
  for WpPost in WpPosts:
    n = n + 1
    WpDict[WpPost.title] = [ WpPost.id ]
    print("\n\nn=", str(n), "WpPost.id & .title= ", str(WpPost.id),
          str(WpPost.title), "\nWpPost.terms= ", str(WpPost.terms))
    # pprint(vars(WpPost))   # print("Post ID= {a:5d}".format(a=ids))
    m = 0
    for term in WpPost.terms:
      # pprint(vars(term))
      if ((term.name == "WordPress Python") and (m ==0)): # Avoid dup term.name
        # print(str("m="), m, WpPost.custom_fields)
        m = m + 1
        # for custom_field in WpPost.custom_fields:
          # print("custom_field= " + str(custom_field))
          # print("value= {}, key= {}, id= {}".format(value, key, id))
    print(str("\npost_format= "), WpPost.post_format)
  return WpDict


def XmlGetPost(post_id, optional_args=None):
  IniXmlMethods()
  WpPost = XmlC.CliCall('GetPost', post_id=post_id,
                         optional_args=optional_args)
  print("\n\nWpPost.id & .title= ", str(WpPost.id), str(WpPost.title),
        "\nWpPost.terms= ", str(WpPost.terms))
  # pprint(vars(WpPost))
  m = 0
  for term in WpPost.terms:
    # pprint(vars(term))
    if ((term.name == "WordPress Python") and (m == 0)): # Avoid dup term.name
      # print(str("m="), m, WpPost.custom_fields)
      # WpPost.custom_fields = [{'key'='', 'id'='', 'value'=''}, {},...]
      m = m + 1
      for custom_field in WpPost.custom_fields:
        id         = custom_field['id']
        key, value = custom_field['key'], custom_field['value']
        print("custom_field= " + str(custom_field))
        print(" id= "+str(id)+", key= "+str(key)+", value= "+str(value))
        if key == "_layout":
          print("  _layout= ", str(value), "\n")
  print(str("\npost_format= "), WpPost.post_format)


def XmlGetPostFormats():
  IniXmlMethods()
  WpPostFormats = XmlC.CliCall('GetPostFormats')
  print("postformats= ", str(WpPostFormats))
  for WpPostFormat in WpPostFormats:
      print("postformat= ", str(WpPostFormat))

def XmlGetPostTypes():
  IniXmlMethods()
  WpPostTypes = XmlC.CliCall('GetPostTypes')
  print("posttypes= ", str(WpPostTypes))
  for WpPostType in WpPostTypes:
      print("posttype= ", str(WpPostType))

def XmlGetPostType(posttype):
  IniXmlMethods()
  WpPostType = XmlC.CliCall('GetPostType', posttype)
  print("posttype= ", str(WpPostType))
  #pprint(vars(WpPostType))


## Start BDB Methods       ######################
def Disabled_DelSymPosts(Sym, DateBorA='datea', DateTxt='20300101'):
  ' Alternative: , DateTxt=wTm.NowYMD()): '
  Tb = WpC.WB.Bj.BDB.TbB; print('\n Disabled_DelSymPosts:')
  DelSql = DelPostPmTrByDateTitleSql.format(P=Tb.Post, PM=Tb.PostM,
              TR=Tb.TermRel, DateOp = '<' if DateBorA == 'dateb' else '>=',
              TitleOp='like')
  DelSqlDict = {'Date': DateTxt, 'Title': Sym +'%', }
  return WpC.WB.Bj.BDB.Exec(DelSql, DelSqlDict, 'delete', 10)

def DelDupPosts_with_SameDateAndTitle(WpPost):
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelDupPosts_with_SameDateAndTitle:')
  DelSql = DelPostPmTrByDateTitleSql.format(P=Tb.Post, PM=Tb.PostM,
              TR=Tb.TermRel, DateOp = '=', TitleOp ='=')
  DelSqlDict = {'Date' : WpPost.date.strftime('%Y-%m-%d %H:%M'),
                'Title': WpPost.title,                          }
  return WpC.WB.Bj.BDB.Exec(DelSql, DelSqlDict, 'delete', 10)

def SelDupPosts_with_SameDateAndTitle(WpPost):
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelDupPosts_with_SameDateAndTitle:')
  SelSql = SelDupPostsSql.format(P=Tb.Post)
  SelSqlDict = {'Date' : WpPost.date.strftime('%Y-%m-%d %H:%M'),
                'Title': WpPost.title,                          }
  rows = WpC.WB.Bj.BDB.Exec(SelSql, SelSqlDict, 'fetchall', 10)
  print('SelDupPosts_with_SameDateAndTitle rows=', rows)  #= [{'ID': 3896}]
  return rows
  #if not rows:
  #  return None
  #return rows[0]['ID']


# WiP.DelPostByDateAuthorId(2720, '2016-03-28', 1006)
def DelPostByDateAuthorId(PostId, Date, AuthorId):
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelPostByDateAuthorId:')
  DelSql = DelPostPmTrByTypeStatusIdDateAuthorSql.format(P=Tb.Post,PM=Tb.PostM,
      TR=Tb.TermRel, PIdOp = '>', DateOp = '>', AIdOp = '=')
  DelSqlDict = {'PId':PostId, 'Date':Date, 'AId': AuthorId, }
  return WpC.WB.Bj.BDB.Exec(DelSql, DelSqlDict)#Action='delete' parsed from Sql

def DelPostByAuthorId(AuthorId):
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelPostByAuthorId:')
  DelSql = DelPostPmTrByTypeStatusAuthorSql.format(P=Tb.Post, PM=Tb.PostM,
      TR=Tb.TermRel, AIdOp = '=')
  DelSqlDict = {'AId': AuthorId, }
  return WpC.WB.Bj.BDB.Exec(DelSql, DelSqlDict)#Action='delete' parsed from Sql

def DelDupPostsPmTr(PId, PostName):
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelDupPostsPmTr:')
  DelSql = DelPostPmTrByPostNameIdSql.format(
               P =Tb.Post, PM=Tb.PostM, TR=Tb.TermRel, PIdOp = '=' )
  DelSqlDict = {'PId':PId, 'PostName':PostName}
  return WpC.WB.Bj.BDB.Exec(DelSql, DelSqlDict)

# "DELETE p, pm, tr FROM wp_50_posts p "
# "LEFT JOIN wp_50_postmeta pm ON ( p.ID = pm.post_id ) "
# "LEFT JOIN wp_50_term_relationships tr ON ( p.ID = tr.object_id ) WHERE p.ID > 14274;
#/fs/py/web/news$ python RmWordPyDupPosts.py >> /fs/log/web/RadRemoveObj.log 2>&1
#/fs/log/web$ grep 'Success Rad.ctxLogNews.remove_object' RadRemoveObj.log | wc
#    69     207    5444

def DelPostByPostId(PostId, PIdOp = '='):
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelPostByPostId:', PostId, PIdOp)
  DelSql = DelPostPmTrByPostIdSql.format(P =Tb.Post   , PM=Tb.PostM,
                                         TR=Tb.TermRel, PIdOp=PIdOp )
  return WpC.WB.Bj.BDB.Exec(DelSql, {'PId':PostId,})  #Action='delete' parsed from Sql

def DelPostInPostIds(PostIds):
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelPostInPostIds:', PostIds)
  assert isinstance(PostIds, (list, tuple))
  SqlInStr = WpC.WB.Bj.BDB.GetSqlInStr(PostIds)   # = %s, %s, %s, ...
  DelSql = DelPostPmTrInPostIdsSql.format(P=Tb.Post    , PM=Tb.PostM,
                                          TR=Tb.TermRel, InStr=SqlInStr )
  return WpC.WB.Bj.BDB.Exec(DelSql, PostIds)  #Action='delete' parsed from Sql

# import wp.i.post as WiP; WiP.DelPostByPostId(65045, '>')
# select id, user_id, primary_link, secondary_item_id, date_recorded, LEFT(content, 30) from wp_bp_activity where item_id = 20 and secondary_item_id > 65045;
# DELETE from wp_bp_activity where item_id = 20 and secondary_item_id > 65045;
# Query OK, 69 rows affected (25.32 sec)


def DelUnusedTermRel():
  "Remove Unused Terms & Fixing Term Counts (See above)"
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DelUnusedTermRel:')
  DelSql = DelUnusedTermRelSql.format(P=Tb.Post, TR=Tb.TermRel)
  return WpC.WB.Bj.BDB.Exec(DelSql)  #Action= 'delete' parsed from Sql

def UpdateTermCounts():
  Tb = WpC.WB.Bj.BDB.TbB; print('\n UpdateTermCounts:')
  UpdateSql = UpdateTermCountsSql.format(
                    P=Tb.Post, TR=Tb.TermRel, TT=Tb.TermTax)
  return WpC.WB.Bj.BDB.Exec(UpdateSql)  #Action= 'delete' parsed from Sql

def DeleteUnusedTerm():
  Tb = WpC.WB.Bj.BDB.TbB; print('\n DeleteUnusedTerm:')
  DelSql = DeleteUnusedTermSql.format(T=Tb.Term, TT=Tb.TermTax)
  return WpC.WB.Bj.BDB.Exec(DelSql)  #Action= 'delete' parsed from Sql


# Need update
def update_post_author(self, name, value, autoload=None, DbName=None,
                       Pfx=None):
  DbName = self.DbName    if DbName is None else DbName
  Pfx    = self.Tbs.TbPfx if Pfx    is None else Pfx
  Sql =("UPDATE wp_posts SET post_author = [new_author_id] "
        "WHERE post_author = [old_author_id];")
  Sql= ("UPDATE {}.{}options ".format(DbName, Pfx) +
        " SET option_value =%(value)s WHERE option_name =%(name)s;")
  SqlDict = {'name':name, 'value':value, }
  return self.Exec(Sql, SqlDict, 'update')


def SelFeaturedImage(WpGetId, PostType):
  " wordpress.org/support/topic/mysql-query-to-grab-featured-image "
  SelWpSql = ("SELECT wm2.post_id, wm2.meta_value "
    "FROM {x}posts p1 "
    "LEFT JOIN "
    "  {x}postmeta wm1 "
    "  ON ( wm1.post_id = p1.id "
    "       AND wm1.meta_key = '_thumbnail_id' "
    "       AND wm1.meta_value IS NOT None "
    "     ) "
    "LEFT JOIN "
    "  {x}postmeta wm2 "
    "  ON ( wm1.meta_value = wm2.post_id "
    "        AND wm2.meta_key = '_wp_attached_file' "
    "        AND wm2.meta_value IS NOT None "
    "     ) "
    "WHERE "
    "  p1.id=%(id)s "
    "  AND p1.post_status='publish' "
    "  AND p1.post_type='%(pt)s'").format(x=WpC.WB.Bj.BDB.Tbs.TbPfx)

  SelWpDict = {'id':WpGetId, 'pt':PostType,}
  Results = WpC.WB.Bj.BDB.Exec(SelWpSql, SelWpDict, 'fetchall', print, 10)

  print("Results= {}".format(Results))
  return Results

##### End BDB Methods ######################

# End WiP.PostC

# WiP.wp_post_delete( list(range(12279, 12306)))

def wp_post_delete(Ids, Force=True, DeferTermCount=True):
  ''' <id>… One or more IDs of posts to delete.
  [--force] Skip the trash bin.
  [--defer-term-counting] Recalculate term count in batch for performance boost
  '''
  if isinstance(Ids, str):
    Ids = (Ids, )
  elif isinstance(Ids, int):
    Ids = (str(Ids),)
  elif Php.is_array(Ids):
    Ids = array( str(i) for i in Ids )
  Cmd = "wp --path={} --url={} post delete {} ".format(
        WpC.WB.Bj.WC0.SDir, WpC.WB.Bj.SFQDN, ' '.join(Ids))
  if Force:          Cmd += ' --force'
  if DeferTermCount: Cmd += ' --defer-term-counting'
  WpC.WB.Bj.WH0.Exec(Cmd)

#def PrintPostDetails(Post):   # Better pprint( vars( WpPost ))
#  print("Post.id= {}, Post.title = {}".format(Post.id, Post.title))
#  print( "Post.date    = " + str(Post.date         ))
#  if hasattr(Post, "terms"):
#    print("terms = " + str(Post.terms))
#  if hasattr(Post, "terms_names"):
#    print("terms_names  = " + str(Post.terms_names ))
#  # if hasattr( Post, "custom_fields" ):
#  #   print("custom_fields= " + str(Post.custom_fields))
#  print("Post.content = " + Post.content[:80]      )
#  return


#def SelWpCol(Sql, BDB):
#  SelWpSql ="SELECT {} FROM {} {}".format( Sql.WpCol, Sql.WpPutTb, Sql.Where)
#  Results = BDB.Exec(SelWpSql, None, 'fetchall', print, 1)
#  WpColValues = [ row[Sql.WpCol] for row in Results ]
#  print("WpColValues= {}".format(WpColValues))
#  return WpColValues



#######################################
### following from wp-includes/class-wp-xmlrpc-server.php 
#######################################

def wp_newPost( args ):
  "@type array custom_fields  Array of meta key/value pairs to add to the post"
  if Php.isset( post_data['custom_fields'] ):
    set_custom_fields( post_ID, post_data['custom_fields'] )

def set_custom_fields(post_id, fields):
  ''' Set custom fields for post.
  @param int post_id Post ID.
  @param array fields Custom fields.
  '''
  post_id = int( post_id )
  
  for meta in Php.Array( fields ):
    if Php.isset(meta, 'id'):
      #TODO: implement in wp.i.meta:
      #    get_metadata_by_mid, update_metadata_by_mid, delete_metadata_by_mid
      meta['id'] = int( meta['id'] )
      pmeta = get_metadata_by_mid( 'post', meta['id'] )
      if Php.isset(meta['key']):
        meta['key'] = WiF.wp_unslash( meta['key'] )
        if meta['key'] != pmeta.meta_key:
          continue
        meta['value'] = WiF.wp_unslash( meta['value'] )
        if current_user_can( 'edit_post_meta', post_id, meta['key'] ):
          update_metadata_by_mid( 'post', meta['id'], meta['value'] )
      elif current_user_can( 'delete_post_meta', post_id, pmeta.meta_key ):
        delete_metadata_by_mid( 'post', meta['id'] )
    elif current_user_can( 'add_post_meta', post_id,
                           WiF.wp_unslash( meta['key'])):
      add_post_meta( post_id, meta['key'], meta['value'] )


######################################
# [get post by post name instead of id](stackoverflow.com/questions/12905763/)
######################################
#function get_post_by_name($post_name, $output = OBJECT) {
#  global $wpdb;
#  $post = $wpdb->get_var( $wpdb->prepare( "SELECT ID FROM $wpdb->posts WHERE post_name = %s AND post_type='post'", $post_name ));
#  if ( $post )
#    return get_post($post, $output);
#  return null;
#}

def get_post_by_name(post_name, output = 'OBJECT'):
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  Sql = "SELECT ID FROM {} WHERE post_name = %s AND post_type='post'"
  post_ID = wpdb.get_var( wpdb.prepare(Sql.format(wpdb.posts), post_name ))
  if post_ID:
    return get_post(post_ID, output)
  return None


#######################################
### following from wp-includes/post.php
### Core Post API * @package WordPress * @subpackage Post
#######################################

##
## Post Type Registration
##

# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
def create_initial_post_types(Wj=None):
  " Creates the initial post types when 'init' action is fired."
  " Need to run InitPostTypes(self) before running this "
  register_post_type( 'post', array(
    ('labels', array(
      ('name_admin_bar', _x( 'Post', 'add new from admin bar' )),
    )),
    ('public' , True),
    ('_builtin', True), # internal use only. don't use this when registering your own post type.
    ('_edit_link', 'post.php?post=%d'), # internal use only. don't use this when registering your own post type.
    ('capability_type', 'post'),
    ('map_meta_cap', True),
    ('menu_position', 5),
    ('hierarchical', False),
    ('rewrite', False),
    ('query_var', False),
    ('delete_with_user', True),
    ('supports', array( 'title', 'editor', 'author', 'thumbnail', 'excerpt', 'trackbacks', 'custom-fields', 'comments', 'revisions', 'post-formats' )),
    ('show_in_rest', True),
    ('rest_base', 'posts'),
    ('rest_controller_class', 'WP_REST_Posts_Controller'),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_type( 'page', array(
    ('labels', array(
      ('name_admin_bar', _x( 'Page', 'add new from admin bar' )),
    )),
    ('public', True),
    ('publicly_queryable', False),
    ('_builtin', True), # internal use only. don't use this when registering your own post type. */
    ('_edit_link', 'post.php?post=%d'), # internal use only. don't use this when registering your own post type. */
    ('capability_type', 'page'),
    ('map_meta_cap', True),
    ('menu_position', 20),
    ('hierarchical', True),
    ('rewrite', False),
    ('query_var', False),
    ('delete_with_user', True),
    ('supports', array( 'title', 'editor', 'author', 'thumbnail', 'page-attributes', 'custom-fields', 'comments', 'revisions' )),
    ('show_in_rest', True),
    ('rest_base', 'pages'),
    ('rest_controller_class', 'WP_REST_Posts_Controller'),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_type( 'attachment', array(
    ('labels', array(
      ('name', _x('Media', 'post type general name')),
      ('name_admin_bar', _x( 'Media', 'add new from admin bar' )),
      ('add_new', _x( 'Add New', 'add new media' )),
      ('edit_item', __( 'Edit Media' )),
      ('view_item', __( 'View Attachment Page' )),
      ('attributes', __( 'Attachment Attributes' )),
    )),
    ('public', True),
    ('show_ui', True),
    ('_builtin', True), # internal use only. don't use this when registering your own post type. */
    ('_edit_link', 'post.php?post=%d'), # internal use only. don't use this when registering your own post type. */
    ('capability_type', 'post'),
    ('capabilities', array(
    (  'create_posts', 'upload_files'),
    )),
    ('map_meta_cap', True),
    ('hierarchical', False),
    ('rewrite', False),
    ('query_var', False),
    ('show_in_nav_menus', False),
    ('delete_with_user', True),
    ('supports', array( 'title', 'author', 'comments' )),
    ('show_in_rest', True),
    ('rest_base', 'media'),
    ('rest_controller_class', 'WP_REST_Attachments_Controller'),
  ), Wj=Wj )  # Added Wj=Wj

  add_post_type_support( 'attachment:audio', 'thumbnail', Wj=Wj )  # Added Wj=Wj
  add_post_type_support( 'attachment:video', 'thumbnail', Wj=Wj )  # Added Wj=Wj

  register_post_type( 'revision', array(
    ('labels', array(
      ('name', __( 'Revisions' )),
      ('singular_name', __( 'Revision' )),
    )),
    ('public', False),
    ('_builtin', True), # internal use only. don't use this when registering your own post type. */
    ('_edit_link', 'revision.php?revision=%d'), # internal use only. don't use this when registering your own post type. */
    ('capability_type', 'post'),
    ('map_meta_cap', True),
    ('hierarchical', False),
    ('rewrite', False),
    ('query_var', False),
    ('can_export', False),
    ('delete_with_user', True),
    ('supports', array( 'author', )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_type( 'nav_menu_item', array(
    ('labels', array(
      ('name', __( 'Navigation Menu Items' )),
      ('singular_name', __( 'Navigation Menu Item' )),
    )),
    ('public', False),
    ('_builtin', True), # internal use only. don't use this when registering your own post type. */
    ('hierarchical', False),
    ('rewrite', False),
    ('delete_with_user', False),
    ('query_var', False),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_type( 'custom_css', array(
    ('labels', array(
      ('name'         , __( 'Custom CSS' )),
      ('singular_name', __( 'Custom CSS' )),
    )),
    ('public'          , False),
    ('hierarchical'    , False),
    ('rewrite'         , False),
    ('query_var'       , False),
    ('delete_with_user', False),
    ('can_export'      , True),
    ('_builtin'        , True), # internal use only. don't use this when registering your own post type.
    ('supports'        , array( 'title', 'revisions' )),
    ('capabilities'    , array(
      ('delete_posts'          , 'edit_theme_options'),
      ('delete_post'           , 'edit_theme_options'),
      ('delete_published_posts', 'edit_theme_options'),
      ('delete_private_posts'  , 'edit_theme_options'),
      ('delete_others_posts'   , 'edit_theme_options'),
      ('edit_post'             , 'edit_css'),
      ('edit_posts'            , 'edit_css'),
      ('edit_others_posts'     , 'edit_css'),
      ('edit_published_posts'  , 'edit_css'),
      ('read_post'             , 'read'),
      ('read_private_posts'    , 'read'),
      ('publish_posts'         , 'edit_theme_options'),
    )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_type( 'customize_changeset', array(
    ('labels', array(
      ('name'              , _x( 'Changesets', 'post type general name' )),
      ('singular_name'     , _x( 'Changeset', 'post type singular name' )),
      ('menu_name'         , _x( 'Changesets', 'admin menu' )),
      ('name_admin_bar'    , _x( 'Changeset', 'add new on admin bar' )),
      ('add_new'           , _x( 'Add New', 'Customize Changeset' )),
      ('add_new_item'      , __( 'Add New Changeset' )),
      ('new_item'          , __( 'New Changeset' )),
      ('edit_item'         , __( 'Edit Changeset' )),
      ('view_item'         , __( 'View Changeset' )),
      ('all_items'         , __( 'All Changesets' )),
      ('search_items'      , __( 'Search Changesets' )),
      ('not_found'         , __( 'No changesets found.' )),
      ('not_found_in_trash', __( 'No changesets found in Trash.' )),
    )),
    ('public', False),
    ('_builtin', True), # internal use only. don't use this when registering your own post type.
    ('map_meta_cap', True),
    ('hierarchical', False),
    ('rewrite', False),
    ('query_var', False),
    ('can_export', False),
    ('delete_with_user', False),
    ('supports', array( 'title', 'author' )),
    ('capability_type', 'customize_changeset'),
    ('capabilities', array(
      ('create_posts', 'customize'),
      ('delete_others_posts', 'customize'),
      ('delete_post', 'customize'),
      ('delete_posts', 'customize'),
      ('delete_private_posts', 'customize'),
      ('delete_published_posts', 'customize'),
      ('edit_others_posts', 'customize'),
      ('edit_post', 'customize'),
      ('edit_posts', 'customize'),
      ('edit_private_posts', 'customize'),
      ('edit_published_posts', 'do_not_allow'),
      ('publish_posts', 'customize'),
      ('read', 'read'),
      ('read_post', 'customize'),
      ('read_private_posts', 'customize'),
    )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'publish', array(
    ('label'      , _x( 'Published', 'post status' )),
    ('public'     , True),
    ('_builtin'   , True), # internal use only. */
    ('label_count', _n_noop( 'Published <span class="count">(%s)</span>', 'Published <span class="count">(%s)</span>' )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'future', array(
    ('label'      , _x( 'Scheduled', 'post status' )),
    ('protected'  , True),
    ('_builtin'   , True), # internal use only. */
    ('label_count', _n_noop('Scheduled <span class="count">(%s)</span>', 'Scheduled <span class="count">(%s)</span>' )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'draft', array(
    ('label'      , _x( 'Draft', 'post status' )),
    ('protected'  , True),
    ('_builtin'   , True), # internal use only. */
    ('label_count', _n_noop( 'Draft <span class="count">(%s)</span>', 'Drafts <span class="count">(%s)</span>' )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'pending', array(
    ('label'      , _x( 'Pending', 'post status' )),
    ('protected'  , True),
    ('_builtin'   , True), # internal use only. */
    ('label_count', _n_noop( 'Pending <span class="count">(%s)</span>', 'Pending <span class="count">(%s)</span>' )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'private', array(
    ('label'      , _x( 'Private', 'post status' )),
    ('private'    , True),
    ('_builtin'   , True), # internal use only. */
    ('label_count', _n_noop( 'Private <span class="count">(%s)</span>', 'Private <span class="count">(%s)</span>' )),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'trash', array(
    ('label'      , _x( 'Trash', 'post status' )),
    ('internal'   , True),
    ('_builtin'   , True), # internal use only. */
    ('label_count', _n_noop( 'Trash <span class="count">(%s)</span>', 'Trash <span class="count">(%s)</span>' )),
    ('show_in_admin_status_list', True),
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'auto-draft', array(
    ('label'   , 'auto-draft'),
    ('internal', True),
    ('_builtin', True), # internal use only. */
  ), Wj=Wj )  # Added Wj=Wj

  register_post_status( 'inherit', array(
    ('label'   , 'inherit'),
    ('internal', True),
    ('_builtin', True), # internal use only. */
    ('exclude_from_search', False),
  ), Wj=Wj )  # Added Wj=Wj


#def get_post( post = None, output = None, Filter = 'raw' ):
def get_post( post = None, output = 'OBJECT', Filter = 'raw' ):
  '''L430 Retrieves post data given a post ID or post object.
  See sanitize_post() for optional filter values. Also, the parameter
  `post`, must be given as a variable, since it is passed by reference.
  @global WP_Post post
  @param int|WP_Post|None post   Optional. Post ID or post object. Defaults to
                                 global post.
  @param str output Optional. The required return type. One of OBJECT, ARRAY_A, or ARRAY_N, which correspond to a WP_Post object, an associative array, or a numeric array, respectively. Default OBJECT.
  @param str Filter Optional. Type of Filter to apply. Accepts 'raw', 'edit',
  # filter = py built-in func             'db',  or 'display'. Default 'raw'.
  @return WP_Post|array|None Type corresponding to output on success or None on
              failure. When output is OBJECT, a `WP_Post` instance is returned.
  '''
  if Php.empty(locals(), 'post') and Php.isset(WpC.WB.Wj.__dict__, 'post'):
    post = WpC.WB.Wj.post  # = WpC.WB.Wj.__dict__['post']
  #print('WiP.get_post post=', post)

  if isinstance(post, WcP.WP_Post):
    _post = post
  elif Php.is_object( post ):
    if Php.empty(post, 'filter'):
      _post = sanitize_post( post, 'raw' )
      #_post = new WP_Post( _post )
      _post = WcP.WP_Post( _post )
    elif 'raw' == post.filter:
      #_post = new WP_Post( post )
      _post = WcP.WP_Post( post )
    else:
      _post = WcP.WP_Post.get_instance( post.ID )
  else:
    _post = WcP.WP_Post.get_instance( post )
    #print('WiP.get_post else post=', post, _post.ID, _post.__dict__)

  if not _post:
    return None
  # $this->filter = cls attribute (cls mem). $this->Filter()= method call.
  _post = _post.FilterFunc( Filter )

  if output == ARRAY_A:
    return _post.to_array()
  elif output == ARRAY_N:
    return Php.array_values( _post.to_array() )

  return _post


def get_post_ancestors( post ):
  '''L470 Retrieve ancestors of a post.
  @since 2.5.0
  @param int|WP_Post post Post ID or post object.
  @return array Ancestor IDs or empty array if none are found.
  '''
  post = get_post( post )

  if not post or Php.empty(post,'post_parent') or post.post_parent == post.ID:
    return array()
  ancestors = array()
  Id= ancestors[None] = post.post_parent
  ancestor = get_post( Id )

  while ancestor:
    # Loop detection: If the ancestor has been seen before, break.
    if ( Php.empty(ancestor, 'post_parent') or
         ancestor.post_parent == post.ID    or
         Php.in_array(ancestor.post_parent, ancestors) ):
      break
    Id = ancestors[None] = ancestor.post_parent
    ancestor = get_post( Id )

  return ancestors


def get_post_field( field, post = None, context = 'display' ):
  '''L511 Retrieve data from a post field based on Post ID.
  Examples of the post field: 'post_type', 'post_status', 'post_content',
  etc and based off of the post object property or key names.
  The context values are based off of the taxonomy filter functions and
  supported values are found within those functions.
  @see sanitize_post_field()
  @param string      field   Post field name.
  @param int|WP_Post post    Optional. Post ID or post obj. Defaults to current post.
  @param string      context Optional. How to filter the field. Accepts 'raw', 'edit', 'db',
                              or 'display'. Default 'display'.
  @return string The value of the post field on success, empty string on failure.
  '''
  post = get_post( post )
  if not post:
    return ''
  if not Php.isset(post, field):
    return ''
  return sanitize_post_field(field, getattr(post, field), post.ID, context)


def get_post_status( ID = '' ):
  '''L554 Retrieve the post status based on the Post ID.
  If the post ID is of an attachment, then the parent post status will be given
  instead.
  @param int|WP_Post ID Optional. Post ID or post object. Default empty.
  @return string|False Post status on success, False on failure.
  '''
  post = get_post(ID)
  if not Php.is_object(post):
    return False

  if 'attachment' == post.post_type:
    if 'private' == post.post_status:
      return 'private'

    # Unattached attachments are assumed to be published.
    if ( 'inherit' == post.post_status ) and ( 0 == post.post_parent):
      return 'publish'

    # Inherit status from the parent.
    if post.post_parent and ( post.ID != post.post_parent ):
      parent_post_status = get_post_status( post.post_parent )
      if 'trash' == parent_post_status:
        return get_post_meta( post.post_parent, '_wp_trash_meta_status', True )
      else:
        return parent_post_status

  # Filters the post status.
  # @param string  post_status The post status.
  # @param WP_Post post        The post object.
  return WiPg.apply_filters( 'get_post_status', post.post_status, post )


def get_post_statuses():
  '''L601 Retrieve all of the WordPress supported post statuses.
  Posts have a limited set of valid status values, this provides the
  post_status values and descriptions.
  @return dict List of post statuses.
  '''
  status = array(
    ('draft'  , __( 'Draft' )),
    ('pending', __( 'Pending Review' )),
    ('private', __( 'Private' )),
    ('publish', __( 'Published' )),
  )
  return status


def get_page_statuses():
  '''L622 Retrieve all of the WordPress support page statuses.
  Pages have a limited set of valid status values, this provides the
  post_status values and descriptions.
  @return dict List of page statuses.
  '''
  status = array(
    ('draft'  , __( 'Draft' )),
    ('private', __( 'Private' )),
    ('publish', __( 'Published' )),
  )
  return status


# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
#def register_post_status(post_status, args = array() ):
def register_post_status( post_status, args = array(), Wj=None ):
  '''L675 Register a post status. Do not use before init.
  A simple function for creating or modifying a post status based on the
  parameters given. The function will accept an array (second optional
  parameter), along with a string for the post status name.
  Arguments prefixed with an _underscore shouldn't be used by plugins and themes.
  @global array wp_post_statuses Inserts new post status object into the list
  @param string post_status Name of the post status.
  @param array|string args {
    Optional. Array or string of post status arguments.
    @type bool|str label    A descriptive name for the post status marked
                            for translation. Defaults to value of post_status.
    @type bool|array label_count Descriptive text to use for nooped plurals.
                               Default array of label, twice
    @type bool exclude_from_search Whether to exclude posts w/ this post status
                         from search results. Default is value of internal.
    @type bool _builtin  Whether the status is built-in. Core-use only.
                         Default False.
    @type bool public    Whether posts of this status should be shown
                         in the front end of the site. Default False.
    @type bool internal  Whether the status is for internal use only.
                         Default False.
    @type bool protected Whether posts with this status should be protected.
                         Default False.
    @type bool private   Whether posts with this status should be private.
                         Default False.
    @type bool publicly_queryable Whether posts with this status should be
                         publicly-queryable. Default is value of public.
    @type bool show_in_admin_all_list    Whether to include posts in the edit
                         listing for their post type. Default = internal.
    @type bool show_in_admin_status_list Show in the list of statuses with post
                         counts at top of edit listings,  Default = internal.
                         e.g. All (12) | Published (9) | My Custom Status (2)
  } @return object
  '''
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_post_statuses = Wj.wp_post_statuses  # global wp_post_statuses

  # set in InitPostTypes: wp_post_statuses = Wj.wp_post_statuses = array()
  #if not Php.is_array(wp_post_statuses):
  #  wp_post_statuses = array()

  # Args prefixed with an underscore are reserved for internal use.
  defaults = array(
    ('label', False),
    ('label_count', False),
    ('exclude_from_search', None),
    ('_builtin', False),
    ('public', None),
    ('internal', None),
    ('protected', None),
    ('private', None),
    ('publicly_queryable', None),
    ('show_in_admin_status_list', None),
    ('show_in_admin_all_list', None),
  )
  args = WiFc.wp_parse_args(args, defaults)
  #args = (object) args
  args = Php.Object(args)

  post_status = WiF.sanitize_key(post_status)
  args.name = post_status

  # Set various defaults.
  if None == args.public and None == args.internal and None == args.protected and None == args.private:
    args.internal = True

  if None == args.public:
    args.public = False

  if None == args.private:
    args.private = False

  if None == args.protected:
    args.protected = False

  if None == args.internal:
    args.internal = False

  if None == args.publicly_queryable:
    args.publicly_queryable = args.public

  if None == args.exclude_from_search:
    args.exclude_from_search = args.internal

  if None == args.show_in_admin_all_list:
    args.show_in_admin_all_list = not args.internal

  if None == args.show_in_admin_status_list:
    args.show_in_admin_status_list = not args.internal

  if False is args.label:
    args.label = post_status

  if False is args.label_count:
    args.label_count = ( args.label, args.label )

  wp_post_statuses[post_status] = args

  return args


def get_post_status_object( post_status ):
  '''L752 Retrieve a post status object by name.
  @global array wp_post_statuses List of post statuses.
  @see register_post_status()
  @param string post_status The name of a registered post status.
  @return object|None A post status object.
  '''
  wp_post_statuses = WpC.WB.Wj.wp_post_statuses  # global wp_post_statuses
  if Php.empty(wp_post_statuses, post_status):
    return None
  return wp_post_statuses[post_status]


def get_post_stati( args = array(), output = 'names', operator = 'and' ):
  '''L778 Get a list of post statuses.
  @global array wp_post_statuses List of post statuses.
  @see register_post_status()
  @param array|string args     Optional. Array or string of post status arguments to compare against
                                properties of the global `wp_post_statuses objects`. Default empty array.
  @param string       output   Optional. The type of output to return, either 'names' or 'objects'. Default 'names'.
  @param string       operator Optional. The logical operation to perform. 'or' means only one element
                                from the array needs to match; 'and' means all elements must match.
                                Default 'and'.
  @return array A list of post status names or objects.
  '''
  wp_post_statuses = WpC.WB.Wj.wp_post_statuses  # global wp_post_statuses
  field = 'name' if 'names' == output else False
  return WiFc.wp_filter_object_list(wp_post_statuses, args, operator, field)


def is_post_type_hierarchical( post_type ):
  '''L798 Whether the post type is hierarchical.
  A False return value might also mean that the post type does not exist.
  @see get_post_type_object()
  @param string post_type Post type name
  @return bool Whether post type is hierarchical.
  '''
  if not post_type_exists( post_type ):
    return False

  post_type = get_post_type_object( post_type )
  return post_type.hierarchical


def post_type_exists( post_type ):
  '''L816 Check if a post type is registered.
  @see get_post_type_object()
  @param string post_type Post type name.
  @return bool Whether post type is registered.
  '''
  return bool(get_post_type_object( post_type ))
 

def get_post_type( post = None ):
  '''L828 Retrieve the post type of the current post or of a given post.
  @since 2.1.0
  @param int|WP_Post|None post Optional. Post ID or post object. Default is global post.
  @return string|False          Post type on success, False on failure.
  '''
  post = get_post( post )
  if post:
    return post.post_type
  return False


def get_post_type_object( post_type ):
  '''L847 Retrieve a post type object by name.
  @global array wp_post_types List of post types.
  @see register_post_type()
  @param string post_type The name of a registered post type.
  @return object|None A post type object.
  @return WP_Post_Type|None WP_Post_Type object if it exists, None otherwise.
  '''
  wp_post_types = WpC.WB.Wj.wp_post_types  # global wp_post_types
  if not Php.is_scalar( post_type ) or Php.empty(wp_post_types, post_type):
    return None
  return wp_post_types[ post_type ]


def get_post_types( args = array(), output = 'names', operator = 'and' ):
  '''L875 Get a list of all registered post type objects.
  @global array wp_post_types List of post types.
  @see register_post_type() for accepted arguments.
  @param array|string args     Optional. An array of key : value arguments to match against
                                the post type objects. Default empty array.
  @param string       output   Optional. The type of output to return. Accepts post type 'names'
                                or 'objects'. Default 'names'.
  @param string       operator Optional. The logical operation to perform. 'or' means only one
                                element from the array needs to match; 'and' means all elements
                                must match; 'not' means no elements may match. Default 'and'.
  @return array A list of post type names or objects.
  '''
  wp_post_types = WpC.WB.Wj.wp_post_types  # global wp_post_types

  field = 'name' if 'names' == output else False

  return WiFc.wp_filter_object_list(wp_post_types, args, operator, field)


# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
#def register_post_type(post_type, args = array() ):
def register_post_type( post_type, args = array(), Wj=None ):
  '''L1016N  Registers a post type.
  Note: Post type registrations should not be hooked before the
  {@see 'init'} action. Also, any taxonomy connections should be
  registered via the `taxonomies` argument to ensure consistency
  when hooks such as {@see 'parse_query'} or {@see 'pre_get_posts'}
  are used.
  Post types can support any number of built-in core features such
  as meta boxes, custom fields, post thumbnails, post statuses,
  comments, and more. See the `supports` argument for a complete
  list of supported features.
  @global array      wp_post_types List of post types.
  @param str post_type Post type key. Must not exceed 20 characters and may
                       only contain lowercase alphanumeric characters, dashes,
                       and underscores. See sanitize_key().
  @param array|str   args {
    Array or str of arguments for registering a post type.
    @type str   label  Name of the post type shown in the menu. Usually plural.
                       Default is value of labels['name'].
    @type array labels An array of labels for this post type. If not set, post
                       labels are inherited for non-hierarchical types and page
                       labels for hierarchical ones. See get_post_type_labels()
                       for a full list of supported labels.
    @type str description A short descriptive summary of what the post type is.
                          Default empty.
    @type bool public Whether a post type is intended for use publicly either
               via the admin interface or by front-end users. While the default
               settings of exclude_from_search, publicly_queryable, show_ui,
               and show_in_nav_menus are inherited from public, each does not
               rely on this relationship and controls a very specific intention
               Default False.
    @type bool     hierarchical         Whether the post type is hierarchical (e.g. page). Default False.
    @type bool     exclude_from_search  Whether to exclude posts with this post type from front end search
                                        results. Default is the opposite value of public.
    @type bool     publicly_queryable   Whether queries can be performed on the front end for the post type
                                        as part of parse_request(). Endpoints would include:
                                        * ?post_type={post_type_key}
                                        * ?{post_type_key}={single_post_slug}
                                        * ?{post_type_query_var}={single_post_slug}
                                        If not set, the default is inherited from public.
    @type bool     show_ui              Whether to generate and allow a UI for managing this post type in the
                                        admin. Default is value of public.
    @type bool     show_in_menu         Where to show the post type in the admin menu. To work, show_ui
                                        must be True. If True, the post type is shown in its own top level
                                        menu. If False, no menu is shown. If a string of an existing top
                                        level menu (eg. 'tools.php' or 'edit.php?post_type=page'), the post
                                        type will be placed as a sub-menu of that.
                                        Default is value of show_ui.
    @type bool     show_in_nav_menus    Makes this post type available for selection in navigation menus.
                                        Default is value public.
    @type bool     show_in_admin_bar    Makes this post type available via the admin bar. Default is value
                                        of show_in_menu.
    @type bool     show_in_rest          Whether to add the post type route in the REST API 'wp/v2' namespace.
    @type string   rest_base             To change the base url of REST API route. Default is $post_type.
    @type string   rest_controller_class REST API Controller class name. Default is 'WP_REST_Posts_Controller'.
    @type int      menu_position        The position in the menu order the post type should appear. To work,
                                        show_in_menu must be True. Default None (at the bottom).
    @type str      menu_icon            The url to the icon to be used for this menu. Pass a base64-encoded
                                        SVG using a data URI, which will be colored to match the color scheme
                                        -- this should begin with 'data:image/svg+xml;base64,'. Pass the name
                                        of a Dashicons helper class to use a font icon, e.g.
                                        'dashicons-chart-pie'. Pass 'none' to leave div.wp-menu-image empty
                                        so an icon can be added via CSS. Defaults to use the posts icon.
    @type str      capability_type      The string to use to build the read, edit, and delete capabilities.
                                        May be passed as an array to allow for alternative plurals when using
                                        this argument as a base to construct the capabilities, e.g.
                                        array('story', 'stories'). Default 'post'.
    @type array    capabilities         Array of capabilities for this post type. capability_type is used
                                        as a base to construct capabilities by default.
                                        See get_post_type_capabilities().
    @type bool     map_meta_cap         Whether to use the internal default meta capability handling.
                                        Default False.
    @type array    supports             Core feature(s) the post type supports. Serves as an alias for calling
                                        add_post_type_support() directly. Core features include 'title',
                                        'editor', 'comments', 'revisions', 'trackbacks', 'author', 'excerpt',
                                        'page-attributes', 'thumbnail', 'custom-fields', and 'post-formats'.
                                        Additionally, the 'revisions' feature dictates whether the post type
                                        will store revisions, and the 'comments' feature dictates whether the
                                        comments count will show on the edit screen. Defaults is an array
                                        containing 'title' and 'editor'.
    @type callable register_meta_box_cb Provide a callback function that sets up the meta boxes for the
                                        edit form. Do remove_meta_box() and add_meta_box() calls in the
                                        callback. Default None.
    @type array    taxonomies           An array of taxonomy identifiers that will be registered for the
                                        post type. Taxonomies can be registered later with
                                        or register_taxonomy_for_object_type().
                                          Default empty array.
    @type bool|str    has_archive          Whether there should be post type archives, or if a string, the
                                            archive slug to use. Will generate the proper rewrite rules if
                                            rewrite is enabled. Default False.
    @type bool|array  rewrite              {
        Triggers the handling of rewrites for this post type. To prevent rewrite, set to False.
        Defaults to True, using post_type as slug. To specify rewrite rules, an array can be
        passed with any of these keys:
  
        @type str    slug       Customize the permastruct slug. Defaults to post_type key.
        @type bool   with_front Whether the permastruct should be prepended with WP_Rewrite::front.
                                 Default True.
        @type bool   feeds      Whether the feed permastruct should be built for this post type.
                                 Default is value of has_archive.
        @type bool   pages      Whether the permastruct should provide for pagination. Default True.
        @type const  ep_mask    Endpoint mask to assign. If not specified and permalink_epmask is set,
                                 inherits from permalink_epmask. If not specified and permalink_epmask
                                 is not set, defaults to EP_PERMALINK.
    }
    @type str|bool    query_var            Sets the query_var key for this post type. Defaults to post_type
                                            key. If False, a post type cannot be loaded at
                                            ?{query_var}={post_slug}. If specified as a string, the query
                                            ?{query_var_string}={post_slug} will be valid.
    @type bool        can_export           Whether to allow this post type to be exported. Default True.
    @type bool        delete_with_user     Whether to delete posts of this type when deleting a user. If True,
                                            posts of this type belonging to the user will be moved to trash
                                            when then user is deleted. If False, posts of this type belonging
                                            to the user will *not* be trashed or deleted. If not set (the default),
                                            posts are trashed if post_type_supports('author'). Otherwise posts
                                            are not trashed or deleted. Default None.
    @type bool        _builtin             FOR INTERNAL USE ONLY! True if this post type is a native or
                                            "built-in" post_type. Default False.
    @type str         _edit_link           FOR INTERNAL USE ONLY! URL segment to use for edit link of
                                            this post type. Default 'post.php?post=%d'.
  }
  @return WP_Post_Type|WP_Error The registered post type object, or an error object.
  '''
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_post_types = Wj.wp_post_types  # global wp_post_types

  # set in InitPostTypes: wp_post_types = Wj.wp_post_types = array()
  #if not Php.is_array( wp_post_types ):
  #  wp_post_types = array()

  # Sanitize post type name
  post_type = WiF.sanitize_key( post_type )

  if Php.empty(locals(), 'post_type') or len( post_type ) > 20:
    WiFc._doing_it_wrong( register_post_type.__name__,  #__FUNCTION__,
        __( 'Post type names must be between 1 and 20 characters in length.' ),
        '4.2' )
    return WcE.WP_Error( 'post_type_length_invalid',
        __( 'Post type names must be between 1 and 20 characters in length.' ))

  #post_type_object = WcPT.WP_Post_Type(post_type, args )
  post_type_object = WcPT.WP_Post_Type( post_type, args, Wj=Wj )
  post_type_object.add_supports()
  post_type_object.add_rewrite_rules()
  post_type_object.register_meta_boxes()

  wp_post_types[ post_type ] = post_type_object
  
  post_type_object.add_hooks()
  post_type_object.register_taxonomies()
  
  # Fires after a post type is registered.
  # @param string post_type Post type.
  # @param object args      Arguments used to register the post type.
  #WiPg.do_action( 'registered_post_type', post_type, args )

  return args


# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
#def get_post_type_capabilities( args ):
def get_post_type_capabilities( args, Wj=None ):
  '''L1156N  Build an obj w/ all post type capabilities out of a post type obj
  Post type capabilities use the 'capability_type' argument as a base, if the
  capability is not set in the 'capabilities' argument array or if the
  'capabilities' argument is not supplied.
  The capability_type argument can optionally be registered as an array, with
  the 1st value being singular and the 2nd plural, e.g. array('story,'stories')
  Otherwise, an 's' will be added to the value for the plural form. After
  registration, capability_type will always be a string of the singular value.
  By default, seven keys are accepted as part of the capabilities array:
  - edit_post, read_post, and delete_post are meta capabilities, which are then
    generally mapped to corresponding primitive capabilities depending on the
    context, which would be the post being edited/read/deleted and the user or
    role being checked. Thus these capabilities would generally not be granted
    directly to users or roles.
  - edit_posts - Controls whether objects of this post type can be edited.
  - edit_others_posts - Controls whether objects of this type owned by other
    users can be edited. If the post type does not support an author, then
    this will behave like edit_posts.
  - publish_posts - Controls publishing objects of this post type.
  - read_private_posts - Controls whether private objects can be read.
  These four primitive capabilities are checked in core in various locations.
  There are also seven other primitive capabilities which are not referenced
  directly in core, except in map_meta_cap(), which takes the 3 aforementioned
  meta capabilities and translates them into one or more primitive capabilities
  that must then be checked against the user or role, depending on the context.
  - read - Controls whether objects of this post type can be read.
  - delete_posts - Controls whether objects of this post type can be deleted.
  - delete_private_posts - Controls whether private objects can be deleted.
  - delete_published_posts - Controls whether published objects can be deleted.
  - delete_others_posts - Controls whether objects owned by other users can be
    can be deleted. If the post type does not support an author, then this will
    behave like delete_posts.
  - edit_private_posts - Controls whether private objects can be edited.
  - edit_published_posts - Controls whether published objects can be edited.
  These additional capabilities are only used in map_meta_cap(). Thus, they are
  only assigned by default if the post type is registered w/ the 'map_meta_cap'
  argument set to True (default is False).
  @see register_post_type()
  @see map_meta_cap()
  @param object args Post type registration arguments.
  @return object object with all the capabilities as member variables.
  '''
  if not Php.is_array( args.capability_type ):
    args.capability_type = array( args.capability_type, args.capability_type + 's' )

  #Singular base for meta capabilities, plural base for primitive capabilities.
  #list( $singular_base, $plural_base ) = $args->capability_type
  singular_base, plural_base = args.capability_type[:2]

  default_capabilities = array(
    # Meta capabilities
    ('edit_post'         , 'edit_'         + singular_base),
    ('read_post'         , 'read_'         + singular_base),
    ('delete_post'       , 'delete_'       + singular_base),
    # Primitive capabilities used outside of map_meta_cap():
    ('edit_posts'        , 'edit_'         + plural_base),
    ('edit_others_posts' , 'edit_others_'  + plural_base),
    ('publish_posts'     , 'publish_'      + plural_base),
    ('read_private_posts', 'read_private_' + plural_base),
  )

  # (Primitive capabilities used within map_meta_cap():
  if args.map_meta_cap:
    default_capabilities_for_mapping = array(
      ('read'                  , 'read'),
      ('delete_posts'          , 'delete_'           + plural_base),
      ('delete_private_posts'  , 'delete_private_'   + plural_base),
      ('delete_published_posts', 'delete_published_' + plural_base),
      ('delete_others_posts'   , 'delete_others_'    + plural_base),
      ('edit_private_posts'    , 'edit_private_'     + plural_base),
      ('edit_published_posts'  , 'edit_published_'   + plural_base),
    )
    default_capabilities = Php.array_merge(
                       default_capabilities, default_capabilities_for_mapping )

  capabilities = Php.array_merge( default_capabilities, args.capabilities )

  # Post creation capability simply maps to edit_posts by default:
  if not Php.isset( capabilities, 'create_posts'):
    capabilities['create_posts'] = capabilities['edit_posts']

  # Remember meta capabilities for future reference.
  if args.map_meta_cap:
    _post_type_meta_capabilities( capabilities, Wj=Wj )

  return Php.Object(capabilities)


# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
#def _post_type_meta_capabilities( capabilities = None ):
def _post_type_meta_capabilities( capabilities = None, Wj=None ):
  '''L1212N  Store or return a list of post type meta caps for map_meta_cap().
  @global array post_type_meta_caps Used to store meta capabilities.
  @param array capabilities Post type meta capabilities.
  '''
  if Wj is None:
    Wj = WpC.WB.Wj
  post_type_meta_caps = Wj.post_type_meta_caps # global post_type_meta_caps
  for core, custom in capabilities.items():
    if core in ( 'read_post', 'delete_post', 'edit_post' ):
      post_type_meta_caps[ custom ] = core


def get_post_type_labels( post_type_object ):
  '''L1276N Builds an object with all post type labels out of a post type obj.
  Accepted keys of the label array in the post type object:
  - `name` - General name for the post type, usually plural. The same and overridden
           by `post_type_object.label`. Default is 'Posts' / 'Pages'.
  - `singular_name` - Name for one object of this post type. Default is 'Post' / 'Page'.
  - `add_new` - Default is 'Add New' for both hierarchical and non-hierarchical types.
              When internationalizing this string, please use a {@link https://codex.wordpress.org/I18n_for_WordPress_Developers#Disambiguation_by_context gettext context}
              matching your post type. Example: `_x( 'Add New', 'product', 'textdomain' );`.
  - `add_new_item` - Label for adding a new singular item. Default is 'Add New Post' / 'Add New Page'.
  - `edit_item` - Label for editing a singular item. Default is 'Edit Post' / 'Edit Page'.
  - `new_item` - Label for the new item page title. Default is 'New Post' / 'New Page'.
  - `view_item` - Label for viewing a singular item. Default is 'View Post' / 'View Page'.
  - `view_items` - Label for viewing post type archives. Default is 'View Posts' / 'View Pages'.
  - `search_items` - Label for searching plural items. Default is 'Search Posts' / 'Search Pages'.
  - `not_found` - Label used when no items are found. Default is 'No posts found' / 'No pages found'.
  - `not_found_in_trash` - Label used when no items are in the trash. Default is 'No posts found in Trash' /
                         'No pages found in Trash'.
  - `parent_item_colon` - Label used to prefix parents of hierarchical items. Not used on non-hierarchical
                        post types. Default is 'Parent Page:'.
  - `all_items` - Label to signify all items in a submenu link. Default is 'All Posts' / 'All Pages'.
  - `archives` - Label for archives in nav menus. Default is 'Post Archives' / 'Page Archives'.
  - `attributes` - Label for the attributes meta box. Default is 'Post Attributes' / 'Page Attributes'.
  - `insert_into_item` - Label for the media frame button. Default is 'Insert into post' / 'Insert into page'.
  - `uploaded_to_this_item` - Label for the media frame filter. Default is 'Uploaded to this post' /
                            'Uploaded to this page'.
  - `featured_image` - Label for the Featured Image meta box title. Default is 'Featured Image'.
  - `set_featured_image` - Label for setting the featured image. Default is 'Set featured image'.
  - `remove_featured_image` - Label for removing the featured image. Default is 'Remove featured image'.
  - `use_featured_image` - Label in the media frame for using a featured image. Default is 'Use as featured image'.
  - `menu_name` - Label for the menu name. Default is the same as `name`.
  - `filter_items_list` - Label for the table views hidden heading. Default is 'Filter posts list' /
                        'Filter pages list'.
  - `items_list_navigation` - Label for the table pagination hidden heading. Default is 'Posts list navigation' /
                            'Pages list navigation'.
  - `items_list` - Label for the table hidden heading. Default is 'Posts list' / 'Pages list'.
  
  Above, the first default value is for non-hierarchical post types (like posts)
  and the second one is for hierarchical post types (like pages).
  
  Note: To set labels used in post type admin notices, see the {@see 'post_updated_messages'} filter.
  @param object|WP_Post_Type post_type_object Post type object.
  @return object Object with all the labels as member variables.
  '''
  nohier_vs_hier_defaults = array(
    ('name', array( _x('Posts', 'post type general name'), _x('Pages', 'post type general name') )),
    ('singular_name', array( _x('Post', 'post type singular name'), _x('Page', 'post type singular name') )),
    ('add_new', array( _x('Add New', 'post'), _x('Add New', 'page') )),
    ('add_new_item', array( __('Add New Post'), __('Add New Page') )),
    ('edit_item', array( __('Edit Post'), __('Edit Page') )),
    ('new_item', array( __('New Post'), __('New Page') )),
    ('view_item', array( __('View Post'), __('View Page') )),
    ('view_items', array( __('View Posts'), __('View Pages') )),
    ('search_items', array( __('Search Posts'), __('Search Pages') )),
    ('not_found', array( __('No posts found.'), __('No pages found.') )),
    ('not_found_in_trash', array( __('No posts found in Trash.'), __('No pages found in Trash.') )),
    ('parent_item_colon', array( None, __('Parent Page:') )),
    ('all_items', array( __( 'All Posts' ), __( 'All Pages' ) )),
    ('archives', array( __( 'Post Archives' ), __( 'Page Archives' ) )),
    ('attributes', array( __( 'Post Attributes' ), __( 'Page Attributes' ) )),
    ('insert_into_item', array( __( 'Insert into post' ), __( 'Insert into page' ) )),
    ('uploaded_to_this_item', array( __( 'Uploaded to this post' ), __( 'Uploaded to this page' ) )),
    ('featured_image', array( __( 'Featured Image' ), __( 'Featured Image' ) )),
    ('set_featured_image', array( __( 'Set featured image' ), __( 'Set featured image' ) )),
    ('remove_featured_image', array( __( 'Remove featured image' ), __( 'Remove featured image' ) )),
    ('use_featured_image', array( __( 'Use as featured image' ), __( 'Use as featured image' ) )),
    ('filter_items_list', array( __( 'Filter posts list' ), __( 'Filter pages list' ) )),
    ('items_list_navigation', array( __( 'Posts list navigation' ), __( 'Pages list navigation' ) )),
    ('items_list', array( __( 'Posts list' ), __( 'Pages list' ) )),
  )
  nohier_vs_hier_defaults['menu_name'] = nohier_vs_hier_defaults['name']

  labels = _get_custom_object_labels(post_type_object, nohier_vs_hier_defaults)

  post_type = post_type_object.name

  #default_labels = clone labels
  default_labels = Php.clone(labels)

  # Filters the labels of a specific post type.
  # The dynamic portion of the hook name, `post_type`, refers to
  # the post type slug.
  # @see get_post_type_labels() for the full list of labels.
  # @param object labels Object with labels for the post type as member variables.
  #labels = WiPg.apply_filters( "post_type_labels_{post_type}", labels )

  # Ensure that the filtered labels contain all required default values.
  labels = Php.Object(Php.array_merge(
           Php.Array(default_labels), Php.Array(labels) ))
  return labels


def _get_custom_object_labels( Obj, nohier_vs_hier_defaults ):
  '''L1340N Build an obj with custom-something obj (post type, taxonomy) labels
  out of a custom-something object
  @param object Obj                  A custom-something object.
  @param array  nohier_vs_hier_defaults Hierarchical vs non-hierarchical
                                        default labels.
  @return object Object containing labels for the given custom-something object
  '''
  Obj.labels = Php.Array( Obj.labels )
  if Php.isset(Obj, 'label') and Php.empty(Obj.labels, 'name'):
    Obj.labels['name'] = Obj.label
  if ( not Php.isset(Obj.labels, 'singular_name') and
           Php.isset(Obj.labels, 'name') ):
    Obj.labels['singular_name'] = Obj.labels['name']
  if not Php.isset(Obj.labels, 'name_admin_bar'):
    Obj.labels['name_admin_bar'] = Obj.labels['singular_name'] if Php.isset(
                                   Obj.labels, 'singular_name') else Obj.name
  if not Php.isset(Obj.labels, 'menu_name') and Php.isset(Obj.labels, 'name'):
    Obj.labels['menu_name'] = Obj.labels['name']
  if ( not Php.isset(Obj.labels, 'all_items') and
           Php.isset(Obj.labels, 'menu_name') ):
    Obj.labels['all_items'] = Obj.labels['menu_name']
  if ( not Php.isset(Obj.labels, 'archives') and
           Php.isset(Obj.labels, 'all_items') ):
    Obj.labels['archives'] = Obj.labels['all_items']

  #print("_get_custom_object_labels nohier_vs_hier_defaults=", nohier_vs_hier_defaults)
  #print("_get_custom_object_labels Obj.labels="             , Obj.labels             )
  defaults = array()
  for key, value in nohier_vs_hier_defaults.items():
    defaults[key] = value[1] if Obj.hierarchical else value[0]
  labels = Php.array_merge( defaults, Obj.labels )
  #print("_get_custom_object_labels defaults="          , defaults           )
  Obj.labels = Php.Object(Obj.labels)
  #print("_get_custom_object_labels labels="             , labels             )
  #print("_get_custom_object_labels Php.Object(labels)=" , Php.Object(labels) )

  #print("WiP._get_custom_object_labels Php.Object(labels)",
  #       Php.Object(labels))
  return Php.Object(labels)


# Add Wj, since in wp.i.default_filters, WpC.WB.Wj was not initialized yet
#def add_post_type_support(post_type, feature): #VT Added to accept *OtherArgs
#def add_post_type_support( post_type, *Feature ):
def add_post_type_support( post_type, Feature, *OtherArgs, Wj=None ):
  '''L1408N  Register support of certain features for a post type.
  All core features are directly associated with a functional area of the edit
  screen, such as the editor or a meta box. Features include: 'title','editor',
  'comments', 'revisions', 'trackbacks', 'author', 'excerpt','page-attributes',
  'thumbnail', 'custom-fields', and 'post-formats'.
  
  Additionally, the 'revisions' feature dictates whether the post type will
  store revisions, and the 'comments' feature dictates whether the comments
  count will show on the edit screen.
  @global array _wp_post_type_features
  @param string       post_type The post type for which to add the feature.
  @param string|array Feature   The Feature being added, accepts an array of
                                 feature strings or a single string.
  '''
  # global _wp_post_type_features
  if Wj is None:
    Wj = WpC.WB.Wj
  _wp_post_type_features = Wj._wp_post_type_features
  AllArgs = post_type, Feature, *OtherArgs

  features = Php.Array(Feature)
  for f in features:
    #print("add_post_type_support features=", features, f)
    if post_type not in _wp_post_type_features:
      _wp_post_type_features[post_type] = array()  #VT Added to init dict

    # php.net/manual/function.func-num-args.php
    # Gets the number of arguments passed to the function 
    #if len(Feature) == 1: # num_args = len(Feature) - 1, as 1 being post_type
    if Php.func_num_args(AllArgs) == 2:    # func_num_args = len(AllArgs)
      _wp_post_type_features[post_type][f] = True
    else:
      #_wp_post_type_features[post_type][f] = Feature[1] # 2-len(post_type) =1
      _wp_post_type_features[post_type][f]= Php.array_slice(
                                            Php.func_get_args(AllArgs), 2 )
    # www.php2python.com/wiki/function.func-get-args/
    # http://php.net/manual/function.func-get-args.php


def post_type_supports( post_type, feature ):
  ''' Check a post type's support for a given feature.
  @global array _wp_post_type_features
  @param string post_type The post type being checked.
  @param string feature   The feature being checked.
  @return bool Whether the post type supports the given feature.
  '''
  # global _wp_post_type_features
  _wp_post_type_features = WpC.WB.Wj._wp_post_type_features
  #return ( isset(  _wp_post_type_features[post_type][feature] ) )
  return Php.isset( _wp_post_type_features[post_type], feature )


def is_post_type_viewable( post_type ):
  ''' Determines whether a post type is considered "viewable".
  For built-in post types such as posts and pages, the 'public' value will be
  evaluated.
  For all others, the 'publicly_queryable' value will be used.
  @param string|WP_Post_Type post_type Post type name or object.
  @return bool Whether the post type should be considered viewable.
  ''' 
  if Php.is_scalar( post_type ):
    post_type = get_post_type_object( post_type )
    if not post_type:
      return False
  return post_type.publicly_queryable or (
         post_type._builtin and post_type.public )


def get_posts( args = None ):
  '''L1567N  wp/wp-includes/post.php
  Retrieve list of latest posts or posts matching criteria.
  @see WP_Query::parse_query()
  @param array args {
    Optional. Arguments to retrieve posts. See WP_Query::parse_query() for all
    available arguments.
    @type int     numberposts Total # of posts to retrieve. Is an alias of
                               posts_per_page in WP_Query.
                               Accepts -1 for all. Default 5.
    @type int|str category    Category ID or comma-separated list of IDs
                               (this or any children).
                               Is an alias of cat in WP_Query. Default 0.
    @type array   include     An array of post IDs to retrieve, sticky posts
                               will be included. Is an alias of post__in in
                               WP_Query. Default empty array.
    @type array   exclude     An array of post IDs not to retrieve. Default
                               empty array.
    @type bool    suppress_filters Whether to suppress filters. Default True.
  }
  @return array List of posts.
  '''
  print('WiP.get_post args=', args)
  defaults = array(
    ('numberposts', 5      ),
    ('category'  , 0      ), ('orderby' , 'date' ),
    ('order'     , 'DESC' ), ('include' , array()),
    ('exclude'   , array()), ('meta_key', ''     ),
    ('meta_value', ''     ), ('post_type', 'post' ),
    ('suppress_filters', True),
  )

  r = WiFc.wp_parse_args( args, defaults )
  if Php.empty(r, 'post_status'):
    r['post_status'] = 'inherit' if 'attachment'==r['post_type'] else 'publish'
  if not Php.empty(r, 'numberposts') and Php.empty(r, 'posts_per_page'):
    r['posts_per_page'] = r['numberposts']
  if not Php.empty(r, 'category'):
    r['cat'] = r['category']
  if not Php.empty(r, 'include'):
    incposts = WiFc.wp_parse_id_list( r['include'] )
    r['posts_per_page'] = len(incposts)   # only the number of posts included
    r['post__in'] = incposts
  elif not Php.empty(r, 'exclude'):
    r['post__not_in'] = WiFc.wp_parse_id_list( r['exclude'] )

  r['ignore_sticky_posts'] = True
  r['no_found_rows'] = True

  #get_posts = new WP_Query    #TODO  <<<<=== Need to make it work
  #return get_posts.query(r)   #TODO  <<<<=== Need to make it work

##
## Post meta functions
##

def add_post_meta( post_id, meta_key, meta_value, unique = False ):
  ''' wp/wp-includes/post.php
  Add meta data field to a post.
  Post meta data is called "Custom Fields" on the Administration Screen.
  @param int    post_id    Post ID.
  @param string meta_key   Metadata name.
  @param mixed  meta_value Metadata value. Must be serializable if non-scalar.
  @param bool   unique     Optional. Whether the same key should not be added.
                            Default False.
  @return int|False Meta ID on success, False on failure.

  meta_value MUST BE serialized!!!!
  '''
  # Make sure meta is added to the post, not a revision.
  the_post = WiR.wp_is_post_revision(post_id)
  if the_post:
    post_id = the_post
  return WiM.add_metadata('post', post_id, meta_key, meta_value, unique)


def delete_post_meta( post_id, meta_key, meta_value = '' ):
  ''' wp/wp-includes/post.php
  Remove metadata matching criteria from a post.
  You can match based on the key, or key and value. Removing based on key and
  value, will keep from removing duplicate metadata with the same key. It also
  allows removing all metadata matching key, if needed.
  @param int    post_id    Post ID.
  @param string meta_key   Metadata name.
  @param mixed  meta_value Optional. Metadata value. Must be serializable if
                            non-scalar. Default empty.
  @return bool True on success, False on failure.
  '''
  # Make sure meta is added to the post, not a revision.
  the_post = WiR.wp_is_post_revision(post_id)
  if the_post:
    post_id = the_post
  return WiM.delete_metadata('post', post_id, meta_key, meta_value)


def get_post_meta( post_id, key = '', single = False ):
  ''' wp/wp-includes/post.php
  Retrieve post meta field for a post.
  @param int    post_id Post ID.
  @param string key     Optional. The meta key to retrieve. By default, returns
                         data for all keys. Default empty.
  @param bool   single  Optional. Whether to return single value. Default False
  @return mixed Will be an array if single is False. Will be value of meta data
                field if single is True.
  '''
  return WiM.get_metadata('post', post_id, key, single)


def update_post_meta( post_id, meta_key, meta_value, prev_value = '' ):
  ''' wp/wp-includes/post.php
  Update post meta field based on post ID.
  Use the prev_value parameter to differentiate between meta fields with the
  same key and post ID.
  If the meta field for the post does not exist, it will be added.
  @param int    post_id    Post ID.
  @param string meta_key   Metadata key.
  @param mixed  meta_value Metadata value. Must be serializable if non-scalar.
  @param mixed  prev_value Optional. Previous value to check before removing.
                            Default empty.
  @return int|bool Meta ID if the key didn't exist, True on successful update,
                   False on failure.
  '''
  # Make sure meta is added to the post, not a revision.
  the_post = WiR.wp_is_post_revision(post_id)
  if the_post:
    post_id = the_post
  return WiM.update_metadata('post', post_id, meta_key, meta_value, prev_value)


def delete_post_meta_by_key( post_meta_key ):
  ''' wp/wp-includes/post.php
  Delete everything from post meta matching meta key.
  @param string post_meta_key Key to search for when deleting.
  @return bool Whether the post meta key was deleted from the database.
  '''
  return WiM.delete_metadata( 'post', None, post_meta_key, '', True )





def sanitize_post( post, context = 'display' ):
  ''' wp/wp-includes/post.php
  Sanitize every post field.
  If the context is 'raw', then the post object or array will get minimal
  sanitization of the integer fields.
  @see sanitize_post_field()
  @param object|WP_Post|array post    The Post Object or Array
  @param string               context Optional. How to sanitize post fields.
                                       Accepts 'raw', 'edit', 'db', or 'display'.
                                       Default 'display'.
  @return object|WP_Post|array The now sanitized Post Object or Array (will be the
                               same type as post).
  '''
  if Php.is_object(post):
    #print("WiP.sanitize_post post.ID={} post={}".format(post.ID,post))
    # Check if post already filtered for this context.
    #if getattr(post, 'filter', '') == context:
    if Php.isset(post, 'filter') and context == post.filter:
      return post
    if not Php.isset(post, 'ID'):
      post.ID = 0
    #foreach ( array_keys(get_object_vars(post)) as field )
    #print("WiP.sanitize_post post.ID={} post={}".format(post.ID,post))
    #for field in dir(post):
    for  field in Php.array_keys(Php.get_object_vars(post)):
      #if not field.startswith(('__',)):  #no need for stdClass._obj
      setattr(post, field, sanitize_post_field(field, getattr(post, field),
                           post.ID, context))
      #print("WiP.sanitize_post post.ID={} field={}".format(post.ID,field),
      #      getattr(post, field), context)
    post.filter = context
  elif Php.is_array( post ):
    # Check if post already filtered for this context.
    #if post.get('filter', '') == context:
    if Php.isset(post, 'filter') and context == post['filter']:
      return post
    if not Php.isset(post, 'ID'):
      post['ID'] = 0
    #foreach ( array_keys(post) as field )
    for field in Php.array_keys(post):    #  same as post.keys():
      post[field] = sanitize_post_field(field, post[field], post['ID'],context)
    post['filter'] = context

  return post


def sanitize_post_field( field, value, post_id, context = 'display' ):
  ''' wp/wp-includes/post.php
  Sanitize post field based on context.
  Possible context values are:  'raw', 'edit', 'db', 'display', 'attribute' and
  'js'. The 'display' context is used by default. 'attribute' and 'js' contexts
  are treated like 'display' when calling filters.
  @param string field   The Post Object field name.
  @param mixed  value   The Post Object value.
  @param int    post_id Post ID.
  @param string context Optional. How to sanitize post fields. Looks for 'raw',
                        'edit', 'db', 'display', 'attribute' and 'js'.
                        Default 'display'.
  @return mixed Sanitized value.
  '''
  int_fields = ('ID', 'post_parent', 'menu_order')
  if field in int_fields:
    value = int(value)

  # Fields which contain arrays of integers.
  array_int_fields = ('ancestors', )
  if field in array_int_fields:
    #value = array_map( 'absint', value)  #php, to py:
    #value =  array( *[ xFn.AbsInt(v) for v in value ] ) #same as:
    value = Php.array_map( Php.absint, value )
    return value

  if 'raw' == context:
    return value

  prefixed = False
  #if False is not (field, 'post_'):  #php2python.com/wiki/function.strpos/
  if 'post_' in field:
    prefixed = True
    field_no_prefix = Php.str_replace('post_', '', field)  #same as:

  if 'edit' == context:
    Format_to_edit = ('post_content', 'post_excerpt', 'post_title',
                      'post_password')
    #if prefixed:
    #  # Filters the value of a specific post field to edit.
    #  # The dynamic portion of the hook name, `field`, refers to the post
    #  # field name.
    #  # @param mixed value   Value of the post field.
    #  # @param int   post_id Post ID.
    #  #value = WiPg.apply_filters( "edit_{field}", value, post_id )

    #  # Filters the value of a specific post field to edit.
    #  # The dynamic portion of the hook name, `field_no_prefix`, refers to
    #  # the post field name.
    #  # @param mixed value   Value of the post field.
    #  # @param int   post_id Post ID.
    #  #value = WiPg.apply_filters( "{field_no_prefix}_edit_pre", value, post_id )
    #else:
    #  #value = WiPg.apply_filters( "edit_post_{field}", value, post_id )

    if field in Format_to_edit:
      if 'post_content' == field:
        value = WiF.format_to_edit(value, user_can_richedit())
      else:
        value = WiF.format_to_edit(value)
    else:
      value = esc_attr(value)

  elif 'db' == context:
    pass
    #if prefixed:
    #  # Filters the value of a specific post field before saving.
    #  # The dynamic portion of the hook name, `field`, refers to the post
    #  # field name.
    #  # @param mixed value Value of the post field.
    #  #value = WiPg.apply_filters( "pre_{field}", value )
     
    #  # Filters the value of a specific field before saving.
    #  # The dynamic portion of the hook name, `field_no_prefix`, refers
    #  # to the post field name.
    #  # @param mixed value Value of the post field.
    #  #value = WiPg.apply_filters( "{field_no_prefix}_save_pre", value )
    #else:
    #  #value = WiPg.apply_filters( "pre_post_{field}", value )
    #  # Filters the value of a specific post field before saving.
    #  # The dynamic portion of the hook name, `field`, refers to the post
    #  # field name.
    #  # @param mixed value Value of the post field.
    #  #value = WiPg.apply_filters( "{field}_pre", value )

  else:
    ## Use display filters by default.
    #if prefixed:
    #  # Filters the value of a specific post field for display.
    #  # The dynamic portion of the hook name, `field`, refers to the post
    #  # field name.
    #  # @param mixed  value   Value of the prefixed post field.
    #  # @param int    post_id Post ID.
    #  # @param string context Context for how to sanitize the field. Possible
    #  #                        values include 'raw', 'edit', 'db', 'display',
    #  #                        'attribute' and 'js'.
    #  #value = WiPg.apply_filters( field, value, post_id, context )
    #else:
    #  #value = WiPg.apply_filters( "post_{field}", value, post_id, context )

    if 'attribute' == context:
      value = esc_attr(value)
    elif 'js' == context:
      value = esc_js(value)

  return value





#def wp_insert_post(postarr, wp_error = False ):  # Orig
def wp_insert_post( postarr, wp_error = False, user_id=1001, ReturnArray=False,
                    Callback = None, SkipDupPost = False ):  # VT Added
  ''' wp/wp-includes/post.php
  VT enhanced so py can set the post_author to predetermined user_id
  Insert or update a post.
  If postarr parameter has 'ID' set to a value, post will be updated.
  You can set post date manually, by setting values for 'post_date'
  and 'post_date_gmt' keys. You can close comments or open comments by
  setting value for 'comment_status' key.
  @see sanitize_post()
  @global wpdb wpdb WordPress database abstraction object.
  @param array postarr {
    An array of elements that make up a post to update or insert.
    int ID             post ID. If equal to something other than 0,
                       post with that ID will be updated. Default 0.
    int post_author    ID of user who added the post. Default is
                       current user ID.
    str post_date      date of post. Default is current time.
    str post_date_gmt  date of post in GMT timezone. Default is
                       value of `post_date`.
    mix post_content   post content. Default empty.
    str post_content_filtered filtered post content. Default empty.
    str post_title     post title. Default empty.
    str post_excerpt   post excerpt. Default empty.
    str post_status    post status. Default 'draft'.
    str post_type      post type. Default 'post'.
    str comment_status If post can accept comments. Accepts 'open' or 'closed'.
                       Default is value 'default_comment_status' option.
    str ping_status    If post can accept pings. Accepts 'open' or 'closed'.
                       Default is value of 'default_ping_status' option.
    str post_password  password to access post. Default empty.
    str post_name      post name. Default is sanitized post title
                       when creating a new post.
    str to_ping        Space or carriage return-separated list of URLs to ping.
                       Default empty.
    str pinged         Space or carriage return-separated list of URLs that
                       have been pinged. Default empty.
    str post_modified  date when post was last modified. Default = current time
    str post_modified_gmt     date when post was last modified in GMT
                       timezone. Default is current time.
    int post_parent    for post it belongs to, if any. Default 0.
    int menu_order     order post should be displayed in. Default 0.
    str post_mime_type mime type of post. Default empty.
    str guid           Global Unique ID for referencing post. Default empty
    array post_category Array of category names, slugs, or IDs.
                        Defaults to value of the 'default_category' option.
#VT#array tags_input    Array of tags to set for the post, or a string of tags
                        separated by commas #Orig def missing, VT added
    arr tax_input      Array of taxonomy terms keyed by their taxonomy name.
                       Default empty.
    arr meta_input     Array of post meta values keyed by their post meta key.
                       Default empty.
  }
  @param bool  wp_error Optional. Whether to return a WP_Error on
                       failure. Default False.
  @return int|WP_Error post ID on success. value 0 or WP_Error on failure.

  VT added param option to ReturnArray
  Originally, `wp_insert_post()` updates all the dates and only return PostId
    But postarr in calling func is not aware of changes in `wp_insert_post()`
    Hence postarr added to Redis and Rados lacks the updated dates.
      wp> get_post(106853)
      => object(WP_Post)#10402 (25) {
        ["ID"]               => int(106853)
        ["post_author"]      => int(27280)
        ["post_date"]        => string(19) "0000-00-00 00:00:00"  #<= Blank!
        ["post_date_gmt"]    => string(19) "2017-10-13 06:52:00"
        ["post_modified"]    => string(19) "0000-00-00 00:00:00"  #<= Blank!
        ["post_modified_gmt"]=> string(19) "0000-00-00 00:00:00"  #<= Blank!
    So modified `wp_insert_post()` to return postarr if ReturnArray=True
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  #user_id = get_current_user_id()  #VT user_id get passed in now

  defaults = array(
    ('post_author'  , user_id), # str in wp init php, but int in db! use db int!
    # str! NOT int! According to codex.wordpress.org/Class_Reference/WP_Post
    ('post_content' , ''),
    ('post_content_filtered', ''),
    ('post_title'   , ''),
    ('post_excerpt' , ''),
    ('post_status'  , 'draft'),
    ('post_type'    , 'post'),
    ('comment_status', ''),
    ('ping_status'  , ''),
    ('post_password', ''),
    ('to_ping'      , ''),
    ('pinged'       , ''),
    ('post_parent'  , 0),
    ('menu_order'   , 0),
    ('guid'         , ''),
    ('import_id'    , 0),
    ('context'      , ''),
  )

  postarr = WiFc.wp_parse_args(postarr, defaults)
  #unset(  postarr[ 'filter' ] )
  try: del postarr[ 'filter' ]
  except: pass

  postarr = sanitize_post(postarr, 'db')

  # Are we updating or creating?
  post_ID = 0
  update = False
  guid = postarr['guid']

  if not Php.empty(postarr, 'ID'):
    update = True

    # Get the post ID and GUID.
    post_ID = postarr['ID']
    post_before = get_post( post_ID )
    if Php.is_null( post_before ):
      if wp_error:
        return WcE.WP_Error('invalid_post', 'Invalid post ID.')
      return 0

    guid = get_post_field( 'guid', post_ID )
    previous_status = get_post_field('post_status', post_ID )
  else:
    previous_status = 'new'

  #post_type= postarr.get('post_type', 'post')
  post_type = 'post' if Php.empty(postarr, 'post_type'
                                  ) else postarr['post_type']

  post_title = postarr['post_title']
  post_content = postarr['post_content']
  post_excerpt = postarr['post_excerpt']
  #print("WiP.wp_insert_post: postarr[post_name]=",postarr.get('post_name',''))

  if Php.isset(postarr, 'post_name'):
    post_name = postarr['post_name']
  elif update:
    # For an update, don't modify the post_name if it wasn't supplied as an arg
    post_name = post_before.post_name

  maybe_empty = ( 'attachment' != post_type
    and not post_content and not post_title and not post_excerpt
    and post_type_supports( post_type, 'editor' )
    and post_type_supports( post_type, 'title' )
    and post_type_supports( post_type, 'excerpt' ) )

  # Filters whether the post should be considered "empty".
  # The post is considered "empty" if both:
  # 1. The post type supports the title, editor, and excerpt fields
  # 2. The title, editor, and excerpt fields are all empty
  # Returning a truthy value to the filter will effectively short-circuit
  # the new post being inserted, returning 0. If wp_error is True, a WP_Error
  # will be returned instead.
  # @param bool  maybe_empty Whether the post should be considered "empty".
  # @param array postarr     Array of post data.
  #if WiPg.apply_filters( 'wp_insert_post_empty_content', maybe_empty, postarr ):
  if maybe_empty:
    if wp_error:
      return WcE.WP_Error('empty_content',
                          'Content, title, and excerpt are empty.')
    else:
      return 0

  #post_status = postarr.get('post_status', 'draft')
  post_status = 'draft' if ( Php.empty(postarr, 'post_status')
                      ) else postarr['post_status']
  if 'attachment' == post_type and post_status not in (
                                   'inherit', 'private', 'trash' ):
    post_status = 'inherit'

  if not Php.empty(postarr, 'post_category'):
    # Filters out empty terms.
    post_category = Php.array_filter( postarr['post_category'] )

  # Make sure we set a valid category.
  if (Php.empty(locals(), 'post_category') or 0 == len( post_category ) or
      not Php.is_array( post_category)):
    # 'post' requires at least one category.
    if 'post' == post_type and 'auto-draft' != post_status:
      #post_category = [ PostC.Option_default_category, ]
      post_category = Php.array( WiO.get_option('default_category') )
    else:
      post_category = array()

  # Don't allow contributors to set the post slug for pending review posts.
  if 'pending' == post_status and not current_user_can( 'publish_posts' ):
    post_name = ''

  # Create a valid post name. Drafts and pending posts are allowed to have
  # an empty post name.
  if Php.empty(locals(), 'post_name'):
    if post_status not in ( 'draft', 'pending', 'auto-draft' ):
      post_name = WiF.sanitize_title(post_title)
    else:
      post_name = ''
    #print('wp_insert_post if: post_name =', post_name)
  else:
    # On updates, we need to check to see if it's using the old, fixed
    #    sanitization context.
    check_name = WiF.sanitize_title( post_name, '', 'old-save' )
    if ( update and Php.strtolower( Php.urlencode( post_name ) ) == check_name
                and get_post_field( 'post_name', post_ID ) == check_name ):
      post_name = check_name
    else:  # new post, or slug has changed.
      post_name = WiF.sanitize_title(post_name)
    #print('wp_insert_post else: post_name =', post_name)

  # If the post date is empty (due to having been new or a draft) and status
  # is not 'draft' or 'pending', set date to now.
  if (Php.empty(postarr, 'post_date')):
    #    or '0000-00-00 00:00:00' == postarr['post_date']):
    if (Php.empty(postarr, 'post_date_gmt')):
      #  or '0000-00-00 00:00:00' == postarr['post_date_gmt']):
      #post_date = WiFc.current_time( 'mysql' )
      #post_date = datetime.utcnow()
      # VT Added Type = 'datetime' to return current_time in py datetime format
      post_date = WiFc.current_time( 'datetime' )
    else:  #VT changed from get_date_from_gmt to GetDtFromGmtDt as date= dt
      #post_date = WiF.get_date_from_gmt( postarr['post_date_gmt'] )
      post_date = WiF.GetDtFromGmtDt( postarr['post_date_gmt'] )
    # post_date & post_date_gmt here in py are all in datetime format, not str
    #post_date = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
  else:
    # Convert to timezone aware so can compare dates < or >
    post_date = wTm.SetDtToWebHostTz( postarr['post_date'] )

  ## Validate the date.
  #mm = Php.substr( post_date, 5, 2 )
  #jj = Php.substr( post_date, 8, 2 )
  #aa = Php.substr( post_date, 0, 4 )
  #valid_date = wp_checkdate( mm, jj, aa, post_date )
  #if not valid_date:
  #  if wp_error:
  #    return WcE.WP_Error('invalid_date', __( 'Invalid date.' ))
  #  else:
  #    return 0

  if (Php.empty(postarr, 'post_date_gmt')):
    #  or '0000-00-00 00:00:00' == postarr['post_date_gmt']):
    if post_status not in ( 'draft', 'pending', 'auto-draft' ):
      #VT changed from    get_gmt_from_date to GetGmtDtFromDt as date= dt
      #post_date_gmt= WiF.get_gmt_from_date( post_date )
      post_date_gmt = WiF.GetGmtDtFromDt( post_date )
    else:
      #post_date_gmt = '0000-00-00 00:00:00'
      # [make datetime object in year 0](stackoverflow.com/questions/17709751/)
      post_date_gmt = wTm.SetDtToUtc( wTm.DtMin ) # = datetime.min + 1 day
  else:
    #post_date_gmt = postarr['post_date_gmt']
    # Convert to timezone aware so can compare dates < or >
    post_date_gmt = wTm.SetDtToUtc( postarr['post_date_gmt'] )

  if update:    #  or '0000-00-00 00:00:00' == post_date:
    #post_modified    =WiFc.current_time( 'mysql' )
    #post_modified_gmt=WiFc.current_time( 'mysql', 1 )
    # VT Added Type  = 'datetime'  to return current_time in py datetime format
    post_modified    = WiFc.current_time( 'datetime' )
    post_modified_gmt= WiFc.current_time( 'datetime', 1 )
    # post_date & post_date_gmt here in py are all in datetime format, not str
    #post_modified    = datetime.strptime(post_modified,    '%Y-%m-%d %H:%M:%S')
    #post_modified_gmt= datetime.strptime(post_modified_gmt,'%Y-%m-%d %H:%M:%S')
  else:
    post_modified    = post_date
    post_modified_gmt= post_date_gmt

  ## Comment out below since all posts are 'publish'
  if 'attachment' != post_type:
    #below TypeError: can't compare offset-naive and offset-aware datetimes
    #now = DtNowWithLocalSysTz(), datetime.utcnow()
    # [Can't compare naive & aware datetime.now()]
    now  = wTm.DtNowInUtcTz()  # all dates must be dt w/ tz so can compare <,>
    if 'publish' == post_status:
      #now = gmdate('Y-m-d H:i:59')
      #if mysql2date('U', post_date_gmt, False) > mysql2date('U', now, False):
      #if datetime.strptime(post_date_gmt, '%Y-%m-%d %H:%M:%S') > now:
      #Orig in Php post_date_gmt is str, now datetime
      if post_date_gmt > now and EnableFuturePostStatus:
        post_status = 'future'
    elif 'future' == post_status:
      #now = gmdate('Y-m-d H:i:59')
      #if mysql2date('U', post_date_gmt, False) <= mysql2date('U',now, False):
      #if datetime.strptime(post_date_gmt, '%Y-%m-%d %H:%M:%S') <= now:
      if post_date_gmt <= now: #Orig in Php post_date_gmt is str, now datetime
        post_status = 'publish'

  # Comment status.
  if Php.empty(postarr, 'comment_status'):
    if update:
      comment_status = 'closed'
    else:
      import wp.i.comment as WiC
      comment_status = WiC.get_default_comment_status( post_type )
  else:
    comment_status = postarr['comment_status']

  # These variables are needed by compact() later.
  post_content_filtered = postarr['post_content_filtered']
  post_author = postarr['post_author'] if Php.isset(postarr, 'post_author'
                                          ) else user_id
  # ping_status = get_default_comment_status( post_type, 'pingback' 
  #               ) if not postarr['ping_status'] else postarr['ping_status']
  ping_status = Php.empty(postarr, 'ping_status')
  # to_ping = sanitize_trackback_urls( postarr['to_ping']
  #                          ) if Php.isset(postarr, 'to_ping') else ''
  to_ping = ''
  pinged = postarr['pinged'] if Php.isset(postarr, 'pinged') else ''
  import_id = postarr['import_id'] if Php.isset(postarr, 'import_id') else 0

  # The 'wp_insert_post_parent' filter expects all variables to be present.
  # Previously, these variables would have already been extracted
  #menu_order = int( postarr.get('menu_order', 0))
  if Php.isset( postarr, 'menu_order' ):
    menu_order = int(postarr['menu_order'])
  else:
    menu_order = 0

  #post_password = postarr.get('post_password', '')
  post_password = postarr['post_password'] if Php.isset(
                                             postarr, 'post_password') else ''
  if 'private' == post_status:
    post_password = ''

  post_parent = int( postarr.get('post_parent', 0))
  if Php.isset( postarr, 'post_parent' ):
    post_parent = int(postarr['post_parent'])
  else:
    post_parent = 0

  # Filters the post parent -- used to check for and prevent hierarchy loops.
  # @param int   post_parent Post parent ID.
  # @param int   post_ID     Post ID.
  # @param array new_postarr Array of parsed post data.
  # @param array postarr Array of sanitized,but otherwise unmodified post data
  #post_parent = WiPg.apply_filters('wp_insert_post_parent', post_parent,
  #               post_ID, Php.compact(locals(), Php.array_keys( postarr ) ), postarr )

  # If post is being untrashed and it has a desired slug stored in post meta,
  # reassign it.
  if 'trash' == previous_status and 'trash' != post_status:
    desired_post_slug = get_post_meta( post_ID, '_wp_desired_post_slug', True )
    if desired_post_slug:
      delete_post_meta( post_ID, '_wp_desired_post_slug' )
      post_name = desired_post_slug

  #If a trashed post has the desired slug, change it and let this post have it
  #TODO: Uncomment below after finishing:  get_posts = new WP_Query
  #if 'trash' != post_status and post_name:
  #  wp_add_trashed_suffix_to_post_name_for_trashed_posts( post_name, post_ID)

  # When trashing an existing post, change its slug to allow non-trashed posts to use it.
  if ('trash' == post_status and 'trash' != previous_status and
      'new' != previous_status ):
    post_name = wp_add_trashed_suffix_to_post_name_for_post( post_ID )

  if Callback is None:    # VT Added. Don't add '-2' to slug when modify post
    post_name = wp_unique_post_slug( post_name, post_ID, post_status, post_type,
                                     post_parent, SkipDupPost = SkipDupPost )
    if post_name is None and SkipDupPost:    # VT Added
      if wp_error:
        return WcE.WP_Error('dup_post_error',
                  'Skip Duplicate post as SkipDupPost is True', wpdb.last_error)
      else:
        return 0

  # Don't unslash.
  #post_mime_type = postarr.get('post_mime_type', '')
  post_mime_type = postarr['post_mime_type'] if Php.isset(
                                           postarr, 'post_mime_type' ) else ''

  # Expected_slashed (everything!).
  data = Php.compact(locals(), 'post_author', 'post_date', 'post_date_gmt',
      'post_content', 'post_content_filtered', 'post_title', 'post_excerpt',
      'post_status', 'post_type', 'comment_status', 'ping_status',
      'post_password', 'post_name', 'to_ping', 'pinged', 'post_modified',
      'post_modified_gmt', 'post_parent', 'menu_order','post_mime_type','guid')

  emoji_fields = ( 'post_title', 'post_content', 'post_excerpt' )

  for emoji_field in emoji_fields:
    if Php.isset( data, emoji_field ):
      charset = wpdb.get_col_charset( wpdb.posts, emoji_field )
      if 'utf8' == charset:
        data[ emoji_field ] = wp_encode_emoji( data[ emoji_field ] )

  #if 'attachment' == post_type:
  #  # Filters attachment post data before it is updated in or added to database
  #  # @param array data    An array of sanitized attachment post data.
  #  # @param array postarr An array of unsanitized attachment post data.
  #  #data = WiPg.apply_filters( 'wp_insert_attachment_data', data, postarr )
  #else:
  #  # Filters slashed post data just before it is inserted into the database.
  #  # @param array data    An array of slashed post data.
  #  # @param array postarr An array of sanitized, but otherwise unmodified
  #  #                      post data
  #  #data = WiPg.apply_filters( 'wp_insert_post_data', data, postarr )

  if Callback is None:            # VT Added
    Insert = not update
  else:
    data, post_ID, update, Insert = Callback(data, post_ID, update) #VT

  data = WiF.wp_unslash( data )
  where = array( ( 'ID', post_ID ) )

  if update:
    # Fires immediately before an existing post is updated in the database.
    # @param int   post_ID Post ID.
    # @param array data    Array of unslashed post data.
    #WiPg.do_action( 'pre_post_update', post_ID, data )
    wpdb.debug_data, wpdb.debug_where = data, where   # VT for Debug only
    if False is wpdb.update( wpdb.posts, data, where ):
      if wp_error:
        return WcE.WP_Error('db_update_error',
                     'Could not update post in the database', wpdb.last_error)
      else:
        return 0
  #else:                       # VT Orig
  elif Insert:                 # VT Added
    # If there is a suggested ID, use it if not already present.
    if not Php.empty(locals(), import_id):
      import_id = int(import_id)
      if not wpdb.get_var( wpdb.prepare( "SELECT ID FROM {} WHERE ID = %d"
                                         .format(wpdb.posts), import_id) ):
        data['ID'] = import_id
    if False is wpdb.insert( wpdb.posts, data ):
      if wp_error:
        return WcE.WP_Error('db_insert_error',
                   'Could not insert post into the database', wpdb.last_error)
      else:
        return 0
    post_ID = int(wpdb.insert_id)
    # Use the newly generated post_ID.
    where = array( ( 'ID', post_ID ) )

  if Php.empty(data, 'post_name') and data['post_status'] not in (
                           'draft', 'pending', 'auto-draft' ):
    data['post_name'] = wp_unique_post_slug( WiF.sanitize_title(
                        data['post_title'], post_ID ), post_ID,
                        data['post_status'], post_type, post_parent )
    wpdb.update( wpdb.posts, array( ('post_name', data['post_name'] )), where)
    clean_post_cache( post_ID )

  if WiTx.is_object_in_taxonomy( post_type, 'category' ):
    wp_set_post_categories( post_ID, post_category )

  if ( Php.isset(postarr, 'tags_input') and
        WiTx.is_object_in_taxonomy(post_type, 'post_tag') ):
    wp_set_post_tags( post_ID, postarr['tags_input'] )

  # New-style support for all custom taxonomies.
  if not Php.empty(postarr, 'tax_input'):
    for taxonomy, tags in postarr['tax_input'].items():
      taxonomy_obj = WiTx.get_taxonomy(taxonomy)
      if not taxonomy_obj:
        # translators: %s: taxonomy name
        WiFc._doing_it_wrong( wp_insert_post.__name__,   # __FUNCTION__,
                        sprintf('Invalid taxonomy: %s.', taxonomy ), '4.4.0' )
        continue

      # array = hierarchical, string = non-hierarchical.
      if Php.is_array( tags ):
        tags = Php.array_filter(tags)
      if current_user_can( 'taxonomy_obj.cap.assign_terms' ):
        wp_set_post_terms( post_ID, tags, taxonomy )

  if not Php.empty(postarr, 'meta_input'):
    for field, value in postarr['meta_input'].items():
      update_post_meta( post_ID, field, value )

  current_guid = get_post_field( 'guid', post_ID )

  # Set GUID.
  if not update and '' == current_guid:
    import wp.i.link_template as WiLT
    wpdb.update( wpdb.posts, array( ('guid', WiLT.get_permalink(post_ID) )),
                                     where )

  if 'attachment' == postarr['post_type']:
    if not Php.empty(postarr, 'file'):
      update_attached_file( post_ID, postarr['file'] )

    if not Php.empty(postarr, 'context'):
      add_post_meta( post_ID, '_wp_attachment_context', postarr['context'], True )

  # Set or remove featured image.
  if Php.isset( postarr, '_thumbnail_id' ):
    thumbnail_support = current_theme_supports( 'post-thumbnails', post_type ) and post_type_supports( post_type, 'thumbnail' ) or 'revision' == post_type
    if not thumbnail_support and 'attachment' == post_type and post_mime_type:
      if wp_attachment_is( 'audio', post_ID ):
        thumbnail_support = post_type_supports( 'attachment:audio', 'thumbnail' ) or current_theme_supports( 'post-thumbnails', 'attachment:audio' )
      elif wp_attachment_is( 'video', post_ID ):
        thumbnail_support = post_type_supports( 'attachment:video', 'thumbnail' ) or current_theme_supports( 'post-thumbnails', 'attachment:video' )
    
    if thumbnail_support:
      thumbnail_id = int( postarr['_thumbnail_id'] )
      if -1 == thumbnail_id:
        delete_post_thumbnail( post_ID )
      else:
        set_post_thumbnail( post_ID, thumbnail_id )

  clean_post_cache( post_ID )
  post = get_post( post_ID )

  if not Php.empty(postarr, 'page_template') and 'page' == data['post_type']:
    post.page_template = postarr['page_template']
    page_templates = wp_get_theme().get_page_templates( post )
    if ('default' != postarr['page_template'] and
         not Php.isset(page_templates[ postarr], 'page_template') ):
      if wp_error:
        return WcE.WP_Error( 'invalid_page_template',
                             __( 'Invalid page template.' ) )
      update_post_meta( post_ID, '_wp_page_template', 'default' )
    else:
      update_post_meta( post_ID, '_wp_page_template', postarr['page_template'] )

  if 'attachment' != postarr['post_type']:
    wp_transition_post_status( data['post_status'], previous_status, post )
  else:
    #if update:
    #  # Fires once an existing attachment has been updated.
    #  # @param int post_ID Attachment ID.
    #  #WiPg.do_action( 'edit_attachment', post_ID )
    #  #post_after = get_post( post_ID )

    #  # Fires once an existing attachment has been updated.
    #  # @param int     post_ID      Post ID.
    #  # @param WP_Post post_after   Post object following the update.
    #  # @param WP_Post post_before  Post object before the update.
    #  #WiPg.do_action( 'attachment_updated', post_ID, post_after, post_before )
    #else:
    #  # Fires once an attachment has been added.
    #  # @param int post_ID Attachment ID.
    #  #WiPg.do_action( 'add_attachment', post_ID )

    pass # Commnet out below, Redundant.  return same thing at the end
    # if ReturnArray:
    #   data['ID'] = post_ID
    #   return data
    # return post_ID

  #if update:
  #  # Fires once an existing post has been updated.
  #  # @param int     post_ID Post ID.
  #  # @param WP_Post post    Post object.
  #  #WiPg.do_action( 'edit_post', post_ID, post )
  #  #post_after = get_post(post_ID)

  #  # Fires once an existing post has been updated.
  #  # @param int     post_ID      Post ID.
  #  # @param WP_Post post_after   Post object following the update.
  #  # @param WP_Post post_before  Post object before the update.
  #  #WiPg.do_action( 'post_updated', post_ID, post_after, post_before)

  # Fires once a post has been saved.
  # The dynamic portion of the hook name, `post.post_type`, refers to
  # the post type slug.
  # @param int     post_ID Post ID.
  # @param WP_Post post    Post object.
  # @param bool    update Whether this is an existing post being updated or not
  #WiPg.do_action( "save_post_{post.post_type}", post_ID, post, update )

  # Fires once a post has been saved.
  # @param int     post_ID Post ID.
  # @param WP_Post post    Post object.
  # @param bool    update Whether this is an existing post being updated or not
  #WiPg.do_action( 'save_post', post_ID, post, update )

  # Fires once a post has been saved.
  # @param int     post_ID Post ID.
  # @param WP_Post post    Post object.
  # @param bool    update Whether this is an existing post being updated or not
  #WiPg.do_action( 'wp_insert_post', post_ID, post, update )

  if ReturnArray:
    if 'ID' not in data:
      data['ID'] = post_ID
    return data    # Return post array
  return post_ID





def wp_unique_post_slug( slug, post_ID, post_status, post_type, post_parent,
                         SkipDupPost = False ):
  ''' Computes a unique slug for the post, when given the desired slug and some post details.
  @global wpdb       wpdb WordPress database abstraction object.
  @global WP_Rewrite wp_rewrite
  @param string slug        The desired slug (post_name).
  @param int    post_ID     Post ID.
  @param string post_status No uniqueness checks are made if the post is still draft or pending.
  @param string post_type   Post type.
  @param int    post_parent Post parent ID.
  @return string Unique slug for the post, based on post_name (with a -1, -2, etc. suffix)
  '''
  print("WiP.wp_unique_post_slug receive slug=", slug, post_ID, post_status,
        post_type, post_parent)
  if ( post_status in ( 'draft', 'pending', 'auto-draft' ) or
      ('inherit' == post_status and 'revision' == post_type ) ):
    return slug
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  wp_rewrite = WpC.WB.Wj.wp_rewrite  # global wp_rewrite
  original_slug = slug

  feeds = wp_rewrite.feeds
  if not Php.is_array( feeds):
    feeds = array()

  if 'attachment' == post_type:
    # Attachment slugs must be unique across all types.
    check_sql = ("SELECT post_name FROM {} WHERE post_name = %s AND ID != %d "
                 "LIMIT 1".format(wpdb.posts))
    post_name_check = wpdb.get_var( wpdb.prepare( check_sql, slug, post_ID ) )

    # Filters whether the post slug would make a bad attachment slug.
    # @param bool   bad_slug Whether the slug would be bad as an attachment slug.
    # @param string slug     The post slug.
    if (post_name_check or Php.in_array(slug, feeds) or 'embed' == slug or
        WiPg.apply_filters( 'wp_unique_post_slug_is_bad_attachment_slug',
                            False, slug )):
      suffix = 2
      while post_name_check:
        alt_post_name = _truncate_post_slug( slug,
                            200 - (len(str(suffix)) + 1)) +"-"+ str(suffix)
        post_name_check = wpdb.get_var( wpdb.prepare(
                          check_sql, alt_post_name, post_ID ) )
        suffix += 1

      slug = alt_post_name
  elif is_post_type_hierarchical( post_type ):
    if 'nav_menu_item' == post_type:
      return slug

    #Page slugs must be unique within their own trees. Pages are in a separate
    # namespace than posts so page slugs are allowed to overlap post slugs.
    check_sql = ("SELECT post_name FROM {} WHERE post_name = %s AND "
                 "post_type IN ( %s, 'attachment' ) AND ID != %d AND "
                 "post_parent = %d LIMIT 1".format(wpdb.posts))
    post_name_check = wpdb.get_var( wpdb.prepare( check_sql, slug, post_type,
                                    post_ID, post_parent ) )

    # Filters whether the post slug would make a bad hierarchical post slug.
    # @param bool   bad_slug    Whether the post slug would be bad in a
    #                           hierarchical post context.
    # @param string slug        The post slug.
    # @param string post_type   Post type.
    # @param int    post_parent Post parent ID.
    if (post_name_check or Php.in_array(slug, feeds) or 'embed' == slug or
        Php.preg_match( "@^($wp_rewrite.pagination_base)?\d+$@", slug )): # or
      #  WiPg.apply_filters('wp_unique_post_slug_is_bad_hierarchical_slug',
      #                     False, slug, post_type, post_parent )):
      suffix = 2
      while post_name_check:
        alt_post_name = _truncate_post_slug( slug,
                            200 - ( len(str(suffix)) + 1 )) + "-"+ str(suffix)
        post_name_check = wpdb.get_var( wpdb.prepare(check_sql, alt_post_name,
                                        post_type, post_ID, post_parent ) )
        suffix += 1

      slug = alt_post_name
  else:
    # Post slugs must be unique across all posts.
    check_sql = ("SELECT post_name FROM {} WHERE post_name = %s AND "
                 "post_type = %s AND ID != %d LIMIT 1".format(wpdb.posts))
    post_name_check = wpdb.get_var( wpdb.prepare( check_sql, slug, post_type,
                                    post_ID ) )

    if SkipDupPost and post_name_check:  # VT Added
      return None                        # VT Added

    # Prevent new post slugs that could result in URLs that conflict with
    #    date archives.
    post = get_post( post_ID )
    conflicts_with_date_archive = False
    slug_num = Php.intval( slug )
    if ('post' == post_type and ( not post or post.post_name != slug ) and
        Php.preg_match( '/^[0-9]+/', slug ) and slug_num):
      permastructs = Php.array_values( Php.array_filter(
                   Php.explode( '/', WiO.get_option( 'permalink_structure'))))
      postname_index = Php.array_search( '%postname%', permastructs )

      #Potential date clashes are as follows:
      #- Any integer in the first permastruct position could be a year.
      #- An int between 1 and 12 that follows 'year' conflicts with 'monthnum'
      #- An int between 1 and 31 that follows 'monthnum' conflicts with 'day'.
      if ( 0 == postname_index or
          (postname_index and '%year%' == permastructs[ postname_index - 1 ]
           and 13 > slug_num ) or
          (postname_index and '%monthnum%' == permastructs[postname_index - 1]
           and 32 > slug_num )
      ):
        conflicts_with_date_archive = True

    # Filters whether the post slug would be bad as a flat slug.
    # @param bool   bad_slug Whether the post slug would be bad as a flat slug
    # @param string slug      The post slug.
    # @param string post_type Post type.
    if (post_name_check or Php.in_array(slug, feeds) or 'embed' == slug or
        conflicts_with_date_archive or
        WiPg.apply_filters( 'wp_unique_post_slug_is_bad_flat_slug', False,
                            slug, post_type ) ):
      suffix = 2
      while post_name_check:
        alt_post_name = _truncate_post_slug( slug,
                            200 - ( len(str(suffix)) + 1 )) + "-"+ str(suffix)
        post_name_check = wpdb.get_var( wpdb.prepare(
                              check_sql, alt_post_name, post_type, post_ID ) )
        suffix += 1

      slug = alt_post_name

  print("WiP.wp_unique_post_slug return slug=", slug)
  # Filters the unique post slug.
  # @param string slug          The post slug.
  # @param int    post_ID       Post ID.
  # @param string post_status   The post status.
  # @param string post_type     Post type.
  # @param int    post_parent   Post parent ID
  # @param string original_slug The original post slug.
  return WiPg.apply_filters( 'wp_unique_post_slug', slug, post_ID,
                          post_status, post_type, post_parent, original_slug )


def _truncate_post_slug( slug, length = 200 ):
  ''' Truncate a post slug.
  @see utf8_uri_encode()
  @param string slug   The slug to truncate.
  @param int    length Optional. Max length of the slug. Default 200 (char)
  @return string The truncated slug.
  '''
  if len( slug ) > length:
    decoded_slug = Php.urldecode( slug )
    if decoded_slug == slug:
      slug = Php.substr( slug, 0, length )
    else:
      slug = WiF.utf8_uri_encode( decoded_slug, length )
  return Php.rtrim( slug, '-' )


def wp_add_post_tags( post_id = 0, tags = '' ):
  ''' Add tags to a post.
  @see wp_set_post_tags()
  @param int          post_id Optional. The Post ID. Does not default to the ID of the global post.
  @param string|array tags    Optional. An array of tags to set for the post, or a string of tags
                               separated by commas. Default empty.
  @return array|False|WP_Error Array of affected term IDs. WP_Error or False
                               on failure.
  '''
  return wp_set_post_tags(post_id, tags, True)


def wp_set_post_tags( post_id = 0, tags = '', append = False ):
  ''' Set the tags for a post.
  @see wp_set_object_terms()
  @param int          post_id Optional. The Post ID. Does not default to the ID of the global post.
  @param string|array tags    Optional. An array of tags to set for the post, or a string of tags
                               separated by commas. Default empty.
  @param bool         append  Optional. If True, don't delete existing tags, just add on. If False,
                               replace the tags with the new tags. Default False.
  @return array|False|WP_Error Array of term taxonomy IDs of affected terms. WP_Error or False on failure.
  '''
  return wp_set_post_terms( post_id, tags, 'post_tag', append)


def wp_set_post_terms( post_id = 0, tags = '', taxonomy = 'post_tag', append = False ):
  '''
  Set the tags for a post. @see wp_set_object_terms()
  
  @param int          post_id Optional. The Post ID. Does not default to the ID of the global post.
  @param string|array tags    Optional. An array of tags to set for the post, or a string of tags
                               separated by commas. Default empty.
  @param bool         append  Optional. If True, don't delete existing tags, just add on. If False,
                               replace the tags with the new tags. Default False.
  @return array|False|WP_Error Array of term taxonomy IDs of affected terms. WP_Error or False on failure.
  ction wp_set_post_tags( post_id = 0, tags = '', append = False ) {
  eturn wp_set_post_terms( post_id, tags, 'post_tag', append)
  
  
  Set the terms for a post.  @see wp_set_object_terms()
  @param int          post_id  Optional. The Post ID. Does not default to the ID of the global post.
  @param string|array tags     Optional. An array of terms to set for the post, or a string of terms
                                separated by commas. Default empty.
  @param string       taxonomy Optional. Taxonomy name. Default 'post_tag'.
  @param bool         append   Optional. If True, don't delete existing terms,
                               just add on. If False, replace the terms with
                               the new terms. Default False.
  @return array|False|WP_Error Array of term taxonomy IDs of affected terms. WP_Error or False on failure.
  '''
  post_id = int(post_id)

  if not post_id:
    return False

  if Php.empty(locals(), 'tags'):
    tags = array()

  if not Php.is_array( tags):
    comma = _x( ',', 'tag delimiter' )
    if ',' != comma:
      tags = Php.str_replace( comma, ',', tags )
    tags = Php.explode( ',', Php.trim( tags, " \n\t\r\0\x0B," ) )

  # Hierarchical taxonomies must always pass IDs rather than names so that
  # children with the same names but different parents aren't confused.
  if WiTx.is_taxonomy_hierarchical( taxonomy ):
    tags = Php.array_unique( Php.array_map( Php.intval, tags ) )

  return WiTx.wp_set_object_terms( post_id, tags, taxonomy, append )


def wp_set_post_categories( post_ID = 0, post_categories = array(), append = False ):
  ''' Set categories for a post.
  If the post categories parameter is not set, then the default category is
  going used.
  @param int       post_ID         Optional. The Post ID. Does not default to the ID
                                    of the global post. Default 0.
  @param array|int post_categories Optional. List of categories or ID of category.
                                    Default empty array.
  @param bool      append         If True, don't delete existing categories, just add on.
                                   If False, replace the categories with the new categories.
  @return array|False|WP_Error Array of term taxonomy IDs of affected categories. WP_Error or False on failure.
  '''
  post_ID = int(post_ID)
  post_type = get_post_type( post_ID )
  post_status = get_post_status( post_ID )
  # If post_categories isn't already an array, make it one:
  post_categories = Php.Array( post_categories )
  if Php.empty(locals(), 'post_categories'):
    if 'post' == post_type and 'auto-draft' != post_status:
      post_categories = array( WiO.get_option('default_category') )
      append = False
    else:
      post_categories = array()
  elif 1 == len( post_categories ) and '' == Php.reset( post_categories ):
    return True

  return wp_set_post_terms( post_ID, post_categories, 'category', append )


def wp_transition_post_status( new_status, old_status, post ):
  ''' Fires actions related to the transitioning of a post's status.
  When a post is saved, the post status is "transitioned" from one status to another,
  though this does not always mean the status has actually changed before and after
  the save. This function fires a number of action hooks related to that transition:
  the generic {@see 'transition_post_status'} action, as well as the dynamic hooks
  {@see 'old_status_to_new_status'} and {@see 'new_status_post.post_type'}. Note
  that the function does not transition the post object in the database.
  
  For instance: When publishing a post for the first time, the post status may transition
  from 'draft' – or some other status – to 'publish'. However, if a post is already
  published and is simply being updated, the "old" and "new" statuses may both be 'publish'
  before and after the transition.
  @param string  new_status Transition to this post status.
  @param string  old_status Previous post status.
  @param WP_Post post Post data.
  '''
  pass
  # Fires when a post is transitioned from one status to another.
  # @param string  new_status New post status.
  # @param string  old_status Old post status.
  # @param WP_Post post       Post object.
  #WiPg.do_action( 'transition_post_status', new_status, old_status, post )

  # Fires when a post is transitioned from one status to another.
  # The dynamic portions of the hook name, `new_status` and `old status`,
  # refer to the old and new post statuses, respectively.
  # @param WP_Post post Post object.
  #WiPg.do_action( "{old_status}_to_{new_status}", post )

  # Fires when a post is transitioned from one status to another.
  # The dynamic portions of the hook name, `new_status` and `post.post_type`
  # , refer to the new post status and post type, respectively.
  # note: When this action is hooked using a particular post status (like
  # 'publish', as `publish_{post.post_type}`), it will fire both when a post
  # is first transitioned to that status from something else, as well as upon
  # subsequent post updates (old and new status are both the same).
  # Therefore, if you are looking to only fire a callback when a post is first
  # transitioned to a status, use {@see 'transition_post_status'} hook instead.
  # @param int     post_id Post ID.
  # @param WP_Post post    Post object.
  #WiPg.do_action( "{new_status}_{post.post_type}", post.ID, post )



def get_page_uri( page = 0 ):
  ''' Build the URI path for a page.
  Sub pages will be in the "directory" under the parent page post name.
  @since 4.6.0 Converted the `page` parameter to optional.
  @param WP_Post|object|int page Optional. Page ID or WP_Post object.
                                  Default is global post.
  @return string|False Page URI, False on error.
  '''
  if not isinstance(page, WcP.WP_Post):
    page = get_post( page )
  
  if not page:
    return False
  
  uri = page.post_name
  
  for parent in page.ancestors:
    parent = get_post( parent )
    if parent and parent.post_name:
      uri = parent.post_name + '/' + uri
  
  # Filters the URI for a page.
  # @param string  uri  Page URI.
  # @param WP_Post page Page object.
  return WiPg.apply_filters( 'get_page_uri', uri, page )




def wp_insert_attachment( args, File = False, parent = 0, wp_error = False ):
  ''' Insert an attachment.
  If you set the 'ID' in the args parameter, it will mean that you are
  updating and attempt to update the attachment. You can also set the
  attachment name or title by setting the key 'post_name' or 'post_title'.
  You can set the dates for the attachment manually by setting the 'post_date'
  and 'post_date_gmt' keys' values.
  By default, the comments will use the default settings for whether the
  comments are allowed. You can close them manually or keep them open by
  setting the value for the 'comment_status' key.
  @see wp_insert_post()
  @param string|array args   Arguments for inserting an attachment.
  @param string       File   Optional. Filename.
  @param int          parent Optional. Parent post ID.
  @param bool         wp_error Optional. Whether to return a WP_Error on failure. Default false.
  @return int|WP_Error The attachment ID on success. The value 0 or WP_Error on failure.
  '''
  defaults = array(
    ('file'       , File),
    ('post_parent', 0   ),
  )

  data = wp_parse_args( args, defaults )

  if not Php.empty(locals(), parent ):
    data['post_parent'] = parent

  data['post_type'] = 'attachment'
  return wp_insert_post( data, wp_error)





def clean_post_cache( post ):
  ''' Will clean the post in the cache.
  Cleaning means delete from the cache of the post. Will call to clean the term
  object cache associated with the post ID.
  This function not run if _wp_suspend_cache_invalidation is not empty. See
  wp_suspend_cache_invalidation().
  @global bool _wp_suspend_cache_invalidation
  @param int|WP_Post post Post ID or post object to remove from the cache.
  '''
  #global _wp_suspend_cache_invalidation
  if not Php.empty( {**locals(), **WpC.WB.Wj.__dict__},
                    '_wp_suspend_cache_invalidation'):
    return
  
  post = get_post( post )
  if Php.empty(locals(), 'post' ):
    return
  
  WiCa.wp_cache_delete( post.ID, 'posts' )
  WiCa.wp_cache_delete( post.ID, 'post_meta' )
  
  WiTx.clean_object_term_cache( post.ID, post.post_type )
  
  WiCa.wp_cache_delete( 'wp_get_archives', 'general' )
  
  # Fires immediately after the given post's cache is cleaned.
  # @param int     post_id Post ID.
  # @param WP_Post post    Post object.
  #do_action( 'clean_post_cache', post.ID, post )
  
  if 'page' == post.post_type:
    WiCa.wp_cache_delete( 'all_page_ids', 'posts' )
  
    # Fires immediately after the given page's cache is cleaned.
    # @param int post_id Post ID.
    #do_action( 'clean_page_cache', post.ID )
  
  WiCa.wp_cache_set( 'last_changed', Php.microtime(), 'posts' )






def wp_add_trashed_suffix_to_post_name_for_trashed_posts( post_name, post_ID = 0 ):
  ''' Adds a suffix if any trashed posts have a given slug.
  Store its desired (i.e. current) slug so it can try to reclaim it
  if the post is untrashed.
  For internal use.
  @param string post_name Slug.
  @param string post_ID   Optional. Post ID that should be ignored. Default 0.
  '''
  trashed_posts_with_desired_slug = get_posts( array(
    ('name', post_name),
    ('post_status', 'trash'),
    ('post_type', 'any'),
    ('nopaging', True),
    ('post__not_in', array( post_ID, ),)
  ) )

  if not Php.empty(locals(), 'trashed_posts_with_desired_slug'):
    for _post in trashed_posts_with_desired_slug:
      wp_add_trashed_suffix_to_post_name_for_post( _post )


def wp_add_trashed_suffix_to_post_name_for_post( post ):
  ''' Adds a trashed suffix For a given post.
  Store its desired (i.e. current) slug so it can try to reclaim it
  if the post is untrashed.
  For internal use.
  @param WP_Post post The post.
  '''
  wpdb = WpC.WB.Wj.wpdb  # global wpdb
  post = get_post( post )
  if '__trashed' == Php.substr( post.post_name, -9 ):
    return post.post_name

  add_post_meta( post.ID, '_wp_desired_post_slug', post.post_name )
  post_name = _truncate_post_slug( post.post_name, 191 ) + '__trashed'
  wpdb.update( wpdb.posts, { 'post_name', post_name }, { 'ID', post.ID } )
  clean_post_cache( post.ID )
  return post_name


def Post():
  P = array(
    ('post_author'  , 1001),
    ('post_content' , 'Wolrd'),
    ('post_content_filtered', ''),
    ('post_title'   , 'Hello'),
    ('post_excerpt' , 'Hi'),
    ('post_status'  , 'publish'),
    ('post_type'    , 'post'),
    #('comment_status', ''),
    #('ping_status'  , ''),
    #('post_password', ''),
    #('to_ping'      , ''),
    #('pinged'       , ''),
    #('post_parent'  , 0),
    #('menu_order'   , 0),
    #('guid'         , ''),
    #('import_id'    , 0),
    #('context'      , ''),
  )
  wp_insert_post( P )


def NewPostHelloWorld():
  postattr = array(
    ('post_author'  , user_id),
    ('post_content' , 'Wolrd'),
    ('post_content_filtered', ''),
    ('post_title'   , 'Hello'),
    ('post_excerpt' , 'Hi'),
    ('post_status'  , 'publish'),
    ('post_type'    , 'post'),
    #('comment_status', ''),
    #('ping_status'  , ''),
    #('post_password', ''),
    #('to_ping'      , ''),
    #('pinged'       , ''),
    #('post_parent'  , 0),
    #('menu_order'   , 0),
    #('guid'         , ''),
    #('import_id'    , 0),
    #('context'      , ''),
  )
  print( wp_insert_post( postattr ))



##wp-settings.php
#create_initial_post_types()


if __name__ == '__main__':
  from wordpress_xmlrpc import WordPressPost #, WordPressPage
  WpPost       = WordPressPost()
  WpPost.Sym   = 'BABA'
  WpPost.TypeR = '8-K'
  WpPost.DateHr= "2007-11-07 00:00:00"
  WpPost.title = "BABA Title"
  #cur.execute("select id from %s where id > 0", (("wp_4_posts",),))
  #cur.execute("select id from wp_4_posts where id > %s", ((80000,),))
  # Variable substitution can only happen at value, not column name or table name!!!
  Sql = "select id from wp_4_posts where id > %s" # "SELECT `*`  FROM %s"
  SqlArgs = (80000,)                               # ( WpPutTbPosts, )
  # print(BDB.Exec(Sql, SqlArgs, 'fetchall', print), 1)

'''
SELECT
  p1.id, p1.post_title, wm2.meta_value
FROM
  wp_52_posts p1
LEFT JOIN
  wp_52_postmeta wm1
  ON ( wm1.post_id = p1.id
       AND wm1.meta_key = "_thumbnail_id"
       AND wm1.meta_value IS NOT NULL
     )
LEFT JOIN
  wp_52_postmeta wm2
  ON ( wm1.meta_value = wm2.post_id
        AND wm2.meta_key = "_wp_attached_file"
        AND wm2.meta_value IS NOT NULL
     )
WHERE
  p1.post_status="publish"
  AND p1.post_type="post"
ORDER BY
  p1.post_date DESC".format( Sql.WpCol, Sql.WpPutTb, Sql.Where)


  @staticmethod
  def Disabled_NewOrEditPost(WpPost):
    Tb  = WpC.WB.Bj.BDB.TbB     # Tables
    PrePostsSql = Sel_P_TR_TT_T_Sql.format(
                       P=Tb.Post, T=Tb.Term, TT=Tb.TermTax, TR=Tb.TermRel)
    PrePostsDict= {'title':WpPost.title, 'Date':WpPost.DateHr,
                     'Sym':WpPost.Sym,  'TypeR':WpPost.TypeR, }
    PrePosts = WpC.WB.Bj.BDB.Exec(PrePostsSql, PrePostsDict, 'fetchall', 10)
  
    print(PrePosts)   #  [{PrePost}, {PrePost}....]
    lenPrePosts = len(PrePosts)
  
    def CheckIfPrePostHasID (i):
      if 'ID' in PrePosts[i]:
        id = PrePosts[i]['ID']
        print("i={}, WpPost.id = PrePosts[i]['ID'] = {}".format(i, WpPost.id))
        return id
      else:
        print("\n\nERROR error: NO PrePosts [i] ID FOUND!!\n\n".format(i))
        WpC.WB.Bj.Exit("Stop Program!!")
  
    if   lenPrePosts == 0:
      print("\nNo PrePost Found! Try to add a new post!\n")
    else:
      WpPost.id = CheckIfPrePostHasID (0)
      if lenPrePosts == 1:
        print("\nFound only 1 PrePost PostID={}.  Try to update it!\n"
                .format(WpPost.id))
      else:
        print("\nFound {} PrePosts! Update ONLY first PostID={}"
              .format(lenPrePosts, WpPost.id))
        for i, PrePost in enumerate( PrePosts ):
          if i> 0:    # Delete Dup Posts other than the first occurance
            id = CheckIfPrePostHasID (i)
            print("\nDeleting PrePost i={}, ID={}\n".format( i, id ))
            Disabled_DelDupPost(PrePost['ID'])
  
    return PostC.NewOrEditPost(WpPost)   # = WpPost.id
  

SELECT
    u1.id,
    u1.login,
    u1.password,
    u1.email,
    m1.meta_value AS firstname,
    m2.meta_value AS lastname,
    m3.meta_value AS country
FROM wp_users u1
JOIN wp_usermeta m1 ON (m1.user_id = u1.id AND m1.meta_key = 'first_name')
JOIN wp_usermeta m2 ON (m2.user_id = u1.id AND m2.meta_key = 'last_name')
JOIN wp_usermeta m3 ON (m3.user_id = u1.id AND m3.meta_key = 'country')
WHERE

# JOIN = INNER JOIN
SELECT
    ID, user_email, user_login, 
    first_name.meta_value as first_name,
    last_name.meta_value as last_name,
    phone_number.meta_value as phone_number,
    wp_capabilities.meta_value as wp_capabilities 
FROM wp_users
    JOIN wp_usermeta AS wp_capabilities ON wp_capabilities.user_id=ID
        AND wp_capabilities.meta_key='wp_capabilities'
    LEFT JOIN wp_usermeta AS first_name ON first_name.user_id=ID
        AND first_name.meta_key='first_name'
    LEFT JOIN wp_usermeta AS last_name ON last_name.user_id=ID
        AND last_name.meta_key='last_name'
    LEFT JOIN wp_usermeta AS phone_number ON phone_number.user_id=ID
        AND phone_number.meta_key='phone_number'
WHERE
    wp_capabilities.meta_value LIKE '%administrator%'
ORDER BY
    first_name<Paste>


DelPostPmTrByDateTitleSql = (
DELETE p, pm, tr FROM wp_50_posts p LEFT JOIN wp_50_postmeta pm ON ( p.ID = pm.post_id )
    LEFT JOIN wp_50_term_relationships tr ON ( p.ID = tr.object_id ) WHERE p.ID > 14274;





[how to delete duplicate rows from a table in mysql](stackoverflow.com/questions/3271396/)
wrapping it into a derived table? (Based on www.xaprb.com/blog/2006/06/23/how-to-select-from-an-update-target-in-mysql/)

DELETE FROM employee WHERE (empid, empssn) NOT IN
( SELECT  empid, empssn FROM
( SELECT MIN(empid) AS empid, empssn FROM employee GROUP BY empssn
) X
);

DELETE FROM wp_50_posts WHERE (ID, post_excerpt) NOT IN
( SELECT  ID, post_excerpt FROM
( SELECT MIN(ID) AS ID, post_excerpt FROM wp_50_posts GROUP BY post_excerpt
) X);

#SELECT ID, post_author, post_date, post_date_gmt, post_title, post_name, post_modified, left(post_excerpt,20)
SELECT ID, post_author, post_date_gmt, RIGHT(post_name,20), LEFT(post_excerpt,20), post_status
FROM wp_50_posts WHERE (ID, post_excerpt) NOT IN ( SELECT  ID, post_excerpt FROM
( SELECT MIN(ID) AS ID, post_excerpt FROM wp_50_posts GROUP BY post_excerpt ) X  WHERE post_type = 'post' AND LENGTH(post_excerpt) > 10 );

SELECT ID, post_author, post_date_gmt, RIGHT(post_name,20), LEFT(post_excerpt,20), post_status
FROM wp_50_posts WHERE (ID, post_excerpt) NOT IN ( SELECT  ID, post_excerpt FROM
( SELECT MIN(ID) AS ID, post_excerpt FROM wp_50_posts GROUP BY post_excerpt ) X )
AND post_type = 'post' AND LENGTH(post_excerpt) > 10;

#AND post_type = 'post' AND post_excerpt IS NOT NULL AND TRIM(post_excerpt) <> '';   #SAME result

DELETE p, pm, tr FROM wp_50_posts p LEFT JOIN wp_50_postmeta pm ON ( p.ID = pm.post_id )
LEFT JOIN wp_50_term_relationships tr ON ( p.ID = tr.object_id )
WHERE (ID, post_excerpt) NOT IN ( SELECT  ID, post_excerpt FROM
( SELECT MIN(ID) AS ID, post_excerpt FROM wp_50_posts GROUP BY post_excerpt ) X )
AND post_type = 'post' AND LENGTH(post_excerpt) > 10;



select count(*) from wp_300_posts; # | count(*) | |    19347 |


SELECT ID, post_date_gmt, left(post_content, 50), post_title, post_parent FROM wp_300_posts WHERE post_type = 'topic' AND post_content LIKE "%company-article.info%";
SELECT ID, post_date_gmt, left(post_content, 50), post_title FROM wp_300_posts WHERE post_type = 'topic' AND post_content LIKE "%viagra%" AND post_content NOT LIKE "%cnn.com%";

wp --path=/fs/www/wpy --url=wordpy.com post delete --force 28962 29356 23446 20487 9218  19024  96882 64796 5585 31691 27804 

DELETE p, pm, tr FROM wp_300_posts p LEFT JOIN wp_300_postmeta pm ON ( p.ID = pm.post_id ) LEFT JOIN wp_300_term_relationships tr ON ( p.ID = tr.object_id )
WHERE p.post_type = 'topic' AND post_content NOT LIKE "%game%" AND post_content NOT LIKE "%wpy%" AND p.post_content LIKE
"%abercrombie outlet%";
"%themedica.com%";
"%oakley%";
"%scientific-equipment%";
"%educational-equipment%";
"%uppowerleveling.com%";
"%cheapbeats%"; "%cheapdrebeatsus.net%"; "%cheapdrebeatscouk.com%";
"%mbtshoessaleout.com%"; "%mbt shoes%";
"%rolex%"; "%replica%";
"%canadagoose.jouwweb.nl%";
"%soccerforcheap.com%"; "%portfolik.com%"; "%www.bjbead.com%%"; "%cheapbeatsheadphone2013.com%";  "%topsocialite.com%";
1 row only: "%miiplaza.net%"; "%dubai-architecture.info%", "%advancedgrafx.com%"; "%powerleveling%"; "%cheapflatshop.com%"; "%studsetka.ru%"; "%rfjason.com%"; "%www.f1portal.net%";

"%cheapflats.us%" AND post_content NOT LIKE "%game%";
"<!--break-->%"  AND post_content NOT LIKE "%game%";   # 18564 rows affected
"%massage%" AND post_content NOT LIKE "%game%";
"%Dysfunction%";
"%Erectile%";
"%viagra%" AND post_content NOT LIKE "%cnn.com%";
"%sbwire.com%";
"%company-article.info%";

select count(*) from wp_300_posts; # count(*) | |    16501 |


SELECT SUBSTRING_INDEX( SUBSTRING_INDEX(post_content, '<a href="', -1) , '>', 1) AS link FROM wp_300_posts WHERE post_content like "%viagra%";   # '%some link:%'
Erectile_Dysfunction.html

[Mysql count instances of substring, then order by](stackoverflow.com/questions/5427467/)
select left(post_content, 50), (CHAR_LENGTH(post_content) - CHAR_LENGTH(REPLACE(post_content, 'http', ''))) / CHAR_LENGTH('http') AS cnt FROM wp_300_posts WHERE post_type = 'topic' AND post_content NOT LIKE "%game";

[Using column alias in WHERE clause of MySQL query produces an error](http://stackoverflow.com/questions/942571/)
select ID, substring(post_content, 1, 80), post_title, (CHAR_LENGTH(post_content) - CHAR_LENGTH(REPLACE(post_content, 'http', ''))) / CHAR_LENGTH('http') AS cnt FROM wp_300_posts WHERE post_type = 'topic' AND post_content NOT LIKE "%game%" AND post_content NOT LIKE "%wpy%" having cnt > 10 ORDER BY cnt;



SELECT p.ID, COUNT(p.ID) AS IDs, p.post_title, p.post_date, t.name, t.term_id, tt.term_taxonomy_id
FROM       wp_4_terms              t
INNER JOIN wp_4_term_taxonomy      tt ON ( t.term_id         = tt.term_id         )
INNER JOIN wp_4_term_relationships tr ON (tr.term_taxonomy_id= tt.term_taxonomy_id)
INNER JOIN wp_4_posts              p  ON ( p.ID              = tr.object_id       )
WHERE tt.taxonomy   = 'post_tag' AND  p.post_title = %(title)s AND   p.post_type   =  'post' AND
      p.post_status = 'publish'  AND  p.post_date  = %(Date)s  AND   t.name IN (%(Sym)s, %(TypeR)s )
GROUP BY p.ID HAVING IDs > 1 ORDER BY p.ID {'TypeR': '6-K', 'Date': '2014-10-01 00:05:00', 'Sym': 'ATV', 'title': 'ATV [Acorn International,]  6-K: (Original Filing)'}

SELECT p.ID, COUNT(p.ID) AS IDs, p.post_title, p.post_date, t.name, t.term_id, tt.term_taxonomy_id FROM       wp_4_terms  t          INNER JOIN wp_4_term_taxonomy tt ON ( t.term_id         = tt.term_id         ) INNER JOIN wp_4_term_relationships tr ON (tr.term_taxonomy_id= tt.term_taxonomy_id) INNER JOIN wp_4_posts  p  ON ( p.ID              = tr.object_id       ) WHERE tt.taxonomy   =  'post_tag' AND   p.post_title  =  'ATV [Acorn International,]  6-K: (Original Filing)' AND   p.post_type   =  'post' AND   p.post_status =  'publish' AND   p.post_date   =  '2014-10-01 00:05:00' AND   t.name IN ('ATV', '6-K' ) GROUP BY p.ID HAVING IDs > 1 ORDER BY p.ID

'''



#!/usr/bin/python3
# vi /usr/local/lib/python3/dist-packages/wordpress_xmlrpc/wordpress.py
from   wordpress_xmlrpc import WordPressTerm
import pyx.php     as Php
import pyx.type    as xTp
import pyx.format  as Fmt
import pyx.unicode as UC
import wpy.xmlcli  as XmlC       # Xml Client Class
import wp.conf     as WpC
import wp.i.format as WiF
import wp.i.cls.term as WcT
import config.log as cLog; L = cLog.logger
array = Php.array

#wpdb set in Web.WpBlogCls
#    for Module in (WpT, WiM, WiU, WiO, WpTx):
#      Module.wpdb = self.Wj.wpdb

WpTermOpAttrs = [ 'id','slug','term_group','term_taxonomy_id','parent','count']
TermDbCols= ['term_id','slug','term_group','term_taxonomy_id','parent','count']
WpTermAttrsValsDict = dict( zip(WpTermOpAttrs, TermDbCols) )
WpTermAttrsValsDict = dict( zip(TermDbCols, WpTermOpAttrs) )
'''
>>> A = list( range(10) );          #= [0,  1,  2,  3,  4,  5,  6,  7,  8,  9]
>>> B = [i+i*10 for i in range(10)] #= [0, 11, 22, 33, 44, 55, 66, 77, 88, 99]
>>> dict(zip(A,B))
{0: 0, 1: 11, 2: 22, 3: 33, 4: 44, 5: 55, 6: 66, 7: 77, 8: 88, 9: 99}
>>> {i:j for i,j in zip(A,B)}
{0: 0, 1: 11, 2: 22, 3: 33, 4: 44, 5: 55, 6: 66, 7: 77, 8: 88, 9: 99}
'''

class WordpyTermC(WordPressTerm, xTp.BaseCls):
  '''WordpyTermC & TermC.AddWpTerms convert all TName to .strip.().lower()
     or db will be: fedex, FedEx Fedex, etc
  can't change id to Id!!
  Wj.TermD[ WpTerm.taxonomy][WpTerm.name] = WpTerm.id, WpTerm.slug, \
       WpTerm.term_group, WpTerm.term_taxonomy_id, WpTerm.parent, WpTerm.count
  return { r['name'] : (r['term_id'],r['slug'],r['term_group'],
           r['term_taxonomy_id'],r['parent'],r['count']) for r in Results }
  '''
  _RequiredAttrs = ['taxonomy', 'name',]
  #   cannot change 'id' to 'Id', or will have xmlrpc error !!!
  #_OptionalAttrs=['slug','id','term_taxonomy_id']  #can't change id to Id!!
  _OptionalAttrs = WpTermOpAttrs
  #_InitAttrs = _RequiredAttrs + _OptionalAttrs  # Done in xTp.BaseCls
  #_OptionalAttrsDefaultVal = 5  #None  #Child Class can set default value

  def __init__(self, *args, SetAttrFromTermD=False, TermArr=None, WP_Term=None,
                    **kwargs):
    #super().__init__(*args, **kwargs) #= super(xTp.BaseCls, self).method(arg)
    WordPressTerm.__init__(self)
    xTp.BaseCls.__init__(self, *args, **kwargs)

    if SetAttrFromTermD is True:
      TermD = WpC.WB.Wj.TermD
      if self.taxonomy in TermD and self.name in TermD[self.taxonomy]:
        for i,v in enumerate(TermD[self.taxonomy][self.name]):
          setattr(self, WpTermOpAttrs[i], v)
    elif isinstance(WP_Term, WcT.WP_Term):
      for k,v in WP_Term._obj.items():
        if k in TermDbCols:   # if k=='term_id': k='id' #Done in __setattr__
          setattr(self, k, v)
    elif isinstance(TermArr, array):
      for k,v in TermArr.items():
        if k in TermDbCols:   # if k=='term_id': k='id' #Done in __setattr__
          setattr(self, k, v)
    else:
      #try:    L.debug('WordpyTermC: {}', self.id)
      #except: pass
      if getattr(self, 'name', None) is not None:
        self.name = self.name.strip().lower()
      if getattr(self, 'slug', None) is None:
        self.slug = UC.WpySlugify(self.name)

  def __getattribute__(self, attr):
    " Translate WpTerm.term_id to WpTerm.id "
    if attr == 'term_id':
      attr = 'id'
    return super().__getattribute__(attr)

  def __setattr__(self, attr, value):
    " Translate WpTerm.term_id to WpTerm.id "
    if attr == 'term_id':
      attr = 'id'  # self.id = value
    super().__setattr__(attr, value)

  def GetTuple(self):
    ''' return (self.id, self.slug, self.term_group, self.term_taxonomy_id,
                self.parent, self.count)
    '''
    return tuple(getattr(self, col) for col in WpTermOpAttrs)


def InitTermGlobals(self):
  ''' Initialize self.TermD. self = WB.Wj
  global var==>self.var, except: var=self.var=same Obj,mutable[],{},ODict
  global var in the rest of this module is assigned to the same mutable obj

  TermD is an instance var for the same instances of self = WB.Wj to share,
  so the same Wj will NOT need to reload the same Term FOR THE SAME BLOG!!!
  #Old: Wj.TermD[Bj.BId][WpTerm.taxonomy][WpTerm.name] \
  #           = WpTerm.id, WpTerm.slug    # Changed from TermC.Dict to Wj.TermD
  Since Wj = self.Wjs[self.BId], so BId is included in Wj, so simply TermD to:
  #Wj.TermD[WpTerm.taxonomy][WpTerm.name] = WpTerm.id, WpTerm.slug
  Wj.TermD[ WpTerm.taxonomy][WpTerm.name] = WpTerm.id, WpTerm.slug, \
                                            WpTerm.term_taxonomy_id
  '''
  if not isinstance(getattr(self, 'TermD', None), dict):
    self.TermD = {}
    L.info("WpT.InitTermGlobals self.TermD = {}  # = Wj.TermD")
  #try:    self.TermD[self.BId]      #Since Wj = self.Wjs[self.BId], so BId is
  #except: self.TermD[self.BId] = {} #  included in Wj, TermD[self.BId] =>TermD
  # LoadTermsFromDbToDict()


# global WpTerms  # global needed since it is changed in except below
# TermD     ={'post_tag': {'SNP':(2983,slug), 'EJ':(55,slug), ..},
#            'category': {'SNP':(2983,slug), 'EJ':(55,slug), ..},}
# TermNames={'post_tag': [FL.Sym, TypeR, FL.Date, Co.CIK],
#            'category': [FL.Sym,]                               }
def IniXmlMethods():
  WpC.WB.Bj.XmlMethods = ['GetTaxonomies', 'GetTaxonomy', '', 'GetTerms',
                          'GetTerm', 'NewTerm', 'EditTerm', 'DeleteTerm',]


class TermC:
  ''' WpTerms is an instances var to keep track of Terms in this run
  '''
  Taxonomies = ['post_tag', 'category']
  #Bj = Exit = XmlCli = BDB = None
  #XmlMethods = ['GetTaxonomies', 'GetTaxonomy', '', 'GetTerms', 'GetTerm',
  #              'NewTerm', 'EditTerm', 'DeleteTerm',]

  def __init__(self, WpTerms=None):
    "DO NOT pass array to WpTerms=[]), or Mutable default arg problems!"
    # L.debug('\nTermC init...\n')
    self.WpTerms = [] if WpTerms is None else list(WpTerms)
    "self.WpTerms used for XmlRpcTerm"
    self.terms = array()   # self.terms => Term.terms => postattr['tax_input']
    "self.terms   used for Ssh postarr"
    self.ValidateWpTerms()

  def ValidateWpTerms(self):
    for i, T in enumerate(self.WpTerms):
      if not T:
        continue
      Id = getattr(T, 'id', 0)
      if not Id or not isinstance(Id, int) or Id < 1:
        AddedTerm = self.AddWpTerm(T.taxonomy, T.name, i)
        if AddedTerm is not None:
          self.WpTerms[i] = AddedTerm

  def  AddWpTerm(self, Tax, TName, i=''): #'post_tag', 'some_name', i):
    '''Add one Term into db
       params TermName: str
    '''
    Tax, TName = Tax.strip().lower(), TName.strip().lower()
    Wj = WpC.WB.Wj
    TName = SanitizeTermName(TName)
    if TName is None:
      return None
    L.info("\n{} AddWpTerm: Taxonomy={}, TName={}", i ,Tax, TName)

    #if Wj.XmlRpcTerm:
    #  WpTerm_TermD = GetWpTermFromWjTermD(Tax, TName)
    #  if WpTerm_TermD:  # if WpTerm Match Found in TermD
    #    if self.Add_WpTerm_to_WpTerms(WpTerm_TermD):
    #      L.info("AddWpTerm: WpTerm_TermD and Add_WpTerm_to_WpTerms! "
    #             "No need to: WpTerms.append(WpTerm_TermD)")
    #    else:
    #      self.WpTerms.append(WpTerm_TermD)
    #      L.info("AddWpTerm: WpTerm_TermD and not Add_WpTerm_to_WpTerms!  "
    #             "WpTerms.append(WpTerm_TermD)")
    #    return WpTerm_TermD
    #  #else:  if not WpTerm_TermD:  # if WpTerm not Match Found in TermD

    #  L.info("not WpTerm_TermD!  Try XmlNewTerm: ")
    #  WpTerm = WordpyTermC(Tax, TName) #Cls init: ,slug=UC.WpySlugify(TName))
    #  WpTerm = XmlNewTerm(WpTerm)   #XmlNewTerm returns None if error
    #else:
    #  WpTerm = InsertTermIfNotExist(Tax, TName, slug=None, Return='WordpyTermC')

    WpTerm_TermD = GetWpTermFromWjTermD(Tax, TName)
    if WpTerm_TermD:  # if WpTerm Match Found in TermD
      #self.AppendToWpTerms_terms(WpTerm_TermD)
      self.Add_WpTerm_to_WpTerms(WpTerm_TermD)
      self.Add_TermId_to_Terms(  WpTerm_TermD)
      return WpTerm_TermD

    #else:  #if not WpTerm_TermD:  # if WpTerm not Match Found in TermD
    if Wj.XmlRpcTerm:
      L.info("Cannot GetWpTermFromWjTermD!  Try XmlNewTerm: ")
      WpTerm = WordpyTermC(Tax, TName) #Cls init: ,slug=UC.WpySlugify(TName))
      WpTerm = XmlNewTerm(WpTerm)   #XmlNewTerm returns None if error
    else:
      L.info("Cannot GetWpTermFromWjTermD!  Try InsertTermIfNotExist: ")
      WpTerm = InsertTermIfNotExist(Tax, TName, slug=None) #, Return='WordpyTermC')
    if WpTerm is None:
      return None
    # Add to TermD
    #Wj.TermD[WpTerm.taxonomy][WpTerm.name] = WpTerm.id, WpTerm.slug
    #return { r['name'] : (r['term_id'],r['slug'],r['term_group'],
    #         r['term_taxonomy_id'],r['parent'],r['count']) for r in Results }
    #Wj.TermD[WpTerm.taxonomy][WpTerm.name] = WpTerm.id, WpTerm.slug, \
    #     WpTerm.term_group,WpTerm.term_taxonomy_id,WpTerm.parent,WpTerm.count
    Wj.TermD[ WpTerm.taxonomy][WpTerm.name] = WpTerm.GetTuple()

    #self.AppendToWpTerms_terms(WpTerm)
    self.Add_WpTerm_to_WpTerms(WpTerm)
    self.Add_TermId_to_Terms(  WpTerm)
    return WpTerm

  #def AppendToWpTerms_terms(self, WpTerm):
  #  self.Add_WpTerm_to_WpTerms(WpTerm)
  #  self.Add_TermId_to_Terms(  WpTerm)

  def Add_WpTerm_to_WpTerms(self, WpTerm):   # (self, Tax, TName):
    ''' self.WpTerms=[] is an instances var to keep track of WpTerms
    '''
    Tax, TName = WpTerm.taxonomy.strip().lower(), WpTerm.name.strip().lower()
    for WpTermInWpTerms in self.WpTerms:
       if ( Tax   == WpTermInWpTerms.taxonomy.strip().lower() and
            TName == WpTermInWpTerms.name.strip().lower()        ):
          L.info('Add_WpTerm_to_WpTerms: Found Match in self.WpTerms: Tax= {}'
                ', TName= {}', Tax, TName)
          return False
    L.info("Add_WpTerm_to_WpTerms: No match found in self.WpTerms: Tax= {}"
           ", TName= {}. Add to: self.WpTerms.append(WpTerm)", Tax, TName)
    self.WpTerms.append(WpTerm)
    return True

  def Add_TermId_to_Terms(self, WpTerm):
    ''' self.terms=array() is an instances var to keep track of WpTerm.id & tax
        self.terms => Term.terms => postattr['tax_input']
    '''
    Tax, TermId = WpTerm.taxonomy.strip().lower(), WpTerm.id
    if not isinstance(self.terms.get(Tax,None), array): #if not self.terms[Tax]:
      self.terms[Tax] = array()
    elif Tax in self.terms and TermId in self.terms[Tax]:
      L.info("Add_TermId_to_Terms: Found Match in self.terms: Tax= {}, "
             "TermId= {}", Tax, TermId)
      return False

    L.info("Add_TermId_to_Terms: No match found in self.terms: Tax= {}",
           ", TermId={}. Add to: self.terms[Tax].append(TermId)", Tax, TermId)
    self.terms[Tax].append(TermId)
    return True


  def AddWpTerms(self, Tax, TermNamesL): #'post_tag', [FL.Sym, TypeR,..]
    '''WordpyTermC & TermC.AddWpTerms convert all TName to .strip.().lower()
       or db will be: fedex, FedEx Fedex, etc
       Also convert TermNamesL into list and Sanitize it
    '''
    # Bad for ckj! Fmt.Sanitize('起底网戒学校：...') = '. .'
    # if isinstance(TermNamesL, (list, tuple)):
    #   TermNamesL = [ Fmt.Sanitize(str(k)) for k in TermNamesL ]
    # elif isinstance(TermNamesL, (str, bytes, int, float, complex)):
    #   TermNamesL = [ Fmt.Sanitize(str(TermNamesL)), ]
    if isinstance(TermNamesL, (str, bytes, int, float, complex)):
      TermNamesL = [ str(TermNamesL) ]
    if not isinstance(TermNamesL, (list, tuple)):
      L.info("AddWpTerm: TermNamesL passed in NOT in (str, list, tuple)!!")
      return False

    for i, TName in enumerate(TermNamesL):
      self.AddWpTerm(Tax, TName, i) #'post_tag', FL.Sym:w




# Move all staticmethods to module fuctions. staticmethod has no benifit other than grouping them in a class, but we're already grouping all in this module

# Begin TermC Original @staticmethod

def LoadTermsFromDbToDict():
  " Changed from TermC.Dict to Wj.TermD "
  " Load Terms from db into a new Wj.TermD. Init Wj.TermD "
  Wj = WpC.WB.Wj
  Wj.TermD = {}
  for Tax in TermC.Taxonomies: #category={'SNP':(2983,slug),'EJ':(55,slug)
    TermD_V = Wj.TermD[Tax] = GetTermsFromDb(Tax)
    L.info("\n Loaded TermD['{}'].  Its len={}\n\n", Tax,len(TermD_V))
  L.info("\n TermC Tax={}, len(Wj.TermD)={}", Tax, len(Wj.TermD))
  #Bad# TermC.Map = map(str.lower, Wj.TermD)
  #Err# 'providers' in TermC.Map['post_tag']
  #Err# RuntimeError: dictionary changed size during iteration


def GetWpTermFromWjTermD(Tax, TName):
  ''' TermD is an instance var for the same instances of self = WB.Wj to share,
      so the same Wj will NOT need to reload the same Term FOR THE SAME BLOG!!!
  Wj.TermD[WpTerm.taxonomy][WpTerm.name] = WpTerm.id, WpTerm.slug, ...
  return: WpTerm = WordpyTermC()
  '''
  Wj = WpC.WB.Wj
  if not Wj.TermD:          # Changed from TermC.Dict to Wj.TermD
    LoadTermsFromDbToDict() # Load Terms into TermD from db if Wj.TermD is empty
  TNameSL = TName.strip().lower()
  L.info("Try find match in TermD: Tax={}, TName={}".format(Tax, TName) +
         '' if TNameSL == TName else (", Diff TName.lower()= "+ TNameSL))

  for TN in ( (TNameSL,) + (() if TNameSL == TName else (TName,)) ):
    if TN in Wj.TermD[Tax]:
      L.info('  Match! TN = {}', TN) # v) v = Wj.TermD[Tax][TN]
      return WordpyTermC(Tax, TN      , SetAttrFromTermD=True) #id=v[0], slug=v[1])

  for TermD_TN in Wj.TermD[Tax].keys():#for TermD_TN,v in Wj.TermD[Tax].items()
    if TNameSL == TermD_TN.strip().lower():
      L.info('  Match! TermD_TN.lower() = {}', TNameSL)
      return WordpyTermC(Tax, TermD_TN, SetAttrFromTermD=True) #id=v[0], slug=v[1])
  L.info('')

  return False


def SanitizeTermName(TName):
  #L.debug("SanitizeTermName TName=", TName)
  HasCjk = False

  if UC.AlphabetDetector().any_cjk(TName):
    TName = UC.RmPunctuation(TName, KeepStrs= ('-','_'), Unicode=True)
    HasCjk = True
  else:
    TName = Fmt.Sanitize(str(TName))  #This removes all Chinese chars!
    TName = UC.RmPunctuation(TName, KeepStrs= ('-','_'), Unicode=False)
    if any(len(s)>40 for s in TName.split()):
      L.info('AddWpTerm: One of the word len in TName > 40!  Skip!')
      return None

  (MinLen, MaxLen) = (2, 40) if HasCjk else (3, 60)

  TName = WiF.sanitize_title( TName.strip().lower() ) #sanitize has lower()
  msg = 'SanitizeTermName: '

  if TName is None:
    L.info("{} TName='{}' is None!  Skip!", msg, TName)
    return None
  elif len(TName) < MinLen:
    L.info("{} len(TName='{}') < MinLen = {}! Skip!", msg, TName, MinLen)
    return None
  elif len(TName) > MaxLen:
    L.info("{} len(TName='{}') > MaxLen = {}! Cut to [:{}]!",
          msg, TName, MaxLen, MaxLen)
    TName = TName[:MaxLen]
  return TName



def InsertTermIfNotExist(Tax, TName, slug=None):  #, Return='WordpyTermC'):
  ''' TName.strip.().lower() or dup terms inserted to db: fedex, FedEx Fedex,..
  TName : term name
  Tax   : taxonomy, ='category' by default for posts
          for other custom post types like woo-commerce it is product_cat
  [Auto insert terms if not exist](stackoverflow.com/questions/3010124/)
  if Return = 'term_id' , return term_id of existing TermArr['term_id'], or
                                            newly inserted TermObj.term_id
  if Return = 'WordpyTermC', return WordpyTermC Obj, by default.
  '''
  import wp.i.taxonomy as WiTx
  import config.db     as cDB
  TName = TName.strip().lower()
  #get the category to check if exists
  L.info("InsertTermIfNotExist get_term_by 'name': {} {}", TName , Tax)
  TermObj  = WiTx.get_term_by('name', TName , Tax)

  #check existence
  if TermObj is False:
    if slug is None:
      slug = UC.WpySlugify(TName)
    # term not exist create it
    TermArr= WiTx.wp_insert_term(TName, Tax, array( ('slug',slug) ))
    #=array(('term_id',394315),('term_taxonomy_id',394312),('slug',"huang-jie"))
    L.info("InsertTermIfNotExist. TermObj not in db. wp_insert_term {}",TermArr)
    if WpC.WB.Wj.is_wp_error( TermArr ):
      return None
    #[SQLAlchemy Obtain Primary Key With Autoincrement Before Commit]
    #    (stackoverflow.com/questions/620610/)
    #You don't need to commit, you just need to flush. Default:
    # class sqlalchemy.orm.session.sessionmaker(bind=None,
    #       class_=<class 'sqlalchemy.orm.session.Session'>, autoflush=True,
    #       autocommit=False, expire_on_commit=True, info=None, **kw)
    if cDB.AutoCommit:
      #TermObj= WiTx.get_term_by('name', TName , Tax)  # same as:
      TermObj = WiTx.get_term_by('id', TermArr['term_id'], Tax)  # Faster?!
      if not TermObj:
        raise ValueError(TermObj)
    else:
      TermObj = WcT.WP_Term(TermArr)
      assert TermObj.name == TName
      if not getattr(TermObj, 'term_group', ''):
        TermObj.term_group = 0   # term_group default to 0!!
        # select * from wp_terms where term_group != 0; Out: Empty set
      if not getattr(TermObj, 'parent', ''):
        TermObj.parent = 0   # parent default to 0!!
      if not getattr(TermObj, 'term_group', ''):
        TermObj.term_group = 0   # term_group default to ''!!
      if not getattr(TermObj, 'count', ''):
        TermObj.count = 0   # count default to 0!!
    L.info("InsertTermIfNotExist. TermObj= {}", TermObj)
    #if   Return == 'term_id':
    #  return TermArr['term_id']
    #elif Return == 'WordpyTermC':
    #return WordpyTermC(Tax, TName, slug=TermArr['slug'],
    #       id=TermArr['term_id'], term_taxonomy_id=TermArr['term_taxonomy_id'])
    #return WordpyTermC(Tax, TName, TermArr = TermArr)
    return  WordpyTermC(Tax, TName, WP_Term = TermObj)
  else:
    if WpC.IsCnBlog(WpC.WB.Wj.BId):
      TName = UC.StrQ2B(TName) #(UC.StrQ2B('世界５００强')=='世界500强' #= True
    try:    assert TermObj.name     == TName
    except: L.warning("\n TermObj.name='{}' != TName='{}'",
                      TermObj.name,TName)
    assert TermObj.taxonomy == Tax
    #if   Return == 'term_id':
    #  return TermObj.term_id
    #elif Return == 'WordpyTermC':
    L.info("InsertTermIfNotExist. TermObj in db. Return WordpyTermC")
    #return WordpyTermC(Tax, TName, slug=TermObj.slug,
    #             id=TermObj.term_id, term_taxonomy_id=TermObj.term_taxonomy_id)
    return  WordpyTermC(Tax, TName, WP_Term = TermObj)

  # pid    = 168  # post we will set it's Terms
  # #append= True : don't delete existing terms, just add on.
  # #      = False: replace the terms with the new terms. Default False.
  # append = True # True means it will add the term beside already set terms
  # #setting post terms
  # res = wp_set_post_terms(pid, [TermId,], Tax, append)


# AddWpTerm: Taxonomy= post_tag , TName= 世界５００强
# Try find match in TermD: Tax=post_tag, TName=世界５００强 Cannot GetWpTermFromWjTermD!  Try InsertTermIfNotExist:
# InsertTermIfNotExist get_term_by 'name': 世界５００强 post_tag
# wpdb.get_term_by term= <Php.Object(stdClass)> (9) = [ (term_id : 177585), (name : 世界500强), (slug : shi-jie-500-qiang), (term_group : 0), (term_taxonomy_id : 177582), (taxonomy : post_tag), (description : ), (parent : 0), (count : 2) ]
# wpdb.get_term_by term.term_id= 177585
#
# import pyx.unicode as UC
# UC.StrQ2B('世界５００强')              #Out: '世界500强'
# UC.StrQ2B('世界５００强')=='世界500强' #Out: True




# python-wordpress-xmlrpc.readthedocs.org/en/latest/examples/taxonomies.html
def XmlNewTerm(WpTerm):
  Bj = WpC.WB.Bj
  IniXmlMethods()
  WpTerm.id = XmlC.CliCall('NewTerm', WpTerm=WpTerm)
  if not WpTerm.id:  # is None:
    return None
  # SELECT SQL_NO_CACHE slug FROM ...: only prevent query result from being
  #    cached, but it cannot clear cache after query
  # [Clear MySQL query cache](http://stackoverflow.com/questions/5231678/)
  Bj.BDB.Exec("RESET QUERY CACHE") #empty SELECT result if don't RESET
  GetSlugSql= "SELECT slug FROM "+ Bj.BDB.TbB.Term +" WHERE term_id =%s"

  for Try in range(5):
    SlugDict  = Bj.BDB.Exec(GetSlugSql, (WpTerm.id,), 'fetchone', 2)
    if SlugDict is None:
      L.warning("\n Don't know why but SlugDict is None from BDB.Exec! "
               "Retry: {}", Try)
      #L.debug(Bj.BDB.Exec(
      #        SELECT slug FROM wp_20_terms WHERE term_id >= %s', (72623,)))
    else:
      break

  if SlugDict is None or 'slug' not in SlugDict:
    L.warning('\n\nSlugDict is still None after 5 tries! Giving up!\n')
  else:
    Slug = SlugDict['slug']
    if Slug != WpTerm.slug:
      L.warning("WpTerm created '{}' has Slug={} that is different "
                "from WpTerm.slug ={}.  Set WpTerm.slug = Slug",
                WpTerm.name, Slug, WpTerm.slug)
      WpTerm.slug = Slug

  return WpTerm

## Start BDB Methods       ######################

def GetAllTermsFromDb():
  Bj = WpC.WB.Bj
  #SELECT t.term_id, t.name FROM wp_4_terms t NATURAL JOIN
  #    wp_4_term_taxonomy tt WHERE tt.taxonomy = 'post_tag';
  GetAllTermsSql = "SELECT name, term_id FROM "+ Bj.BDB.TbB.Term
  L.info('GetAllTermsFromDb: ')
  Results = Bj.BDB.Exec(GetAllTermsSql, None, 'fetchall', 2)
  #         [{'term_id':87763, 'name':'2011-02-02'},]
  return {r['name']:r['term_id'] for r in Results}
  #      {'2015-06-03': 7550, '2009-06-22': 8350,..}

def GetTermsFromDb(taxonomy):
  Bj = WpC.WB.Bj
  Tb = Bj.BDB.TbB   # Tables
  #GetTermsSql = ("SELECT t.term_id, t.name, t.slug FROM "+ Tb.Term +
  #    " t NATURAL JOIN "+ Tb.TermTax +" tt WHERE tt.taxonomy=%s")
  GetTermsSql  = ("SELECT t.term_id, t.name, t.slug, t.term_group, "
       "tt.term_taxonomy_id, tt.parent, tt.count FROM {} t NATURAL JOIN {} tt "
       "WHERE tt.taxonomy=%s".format(Tb.Term, Tb.TermTax))
  L.info('GetTermsFromDb: ')
  Results = Bj.BDB.Exec(GetTermsSql, (taxonomy,), 'fetchall', 2)
  #         [{'term_id':87763, 'name':'2011-02-02'},]
  #return {r['name'] : (r['term_id'],r['slug']) for r in Results}
  #return {r['name'] : (r['term_id'],r['slug'],r['term_group'],
  #        r['term_taxonomy_id'],r['parent'],r['count']) for r in Results }
  return { r['name'] : tuple(r[col] for col in TermDbCols) for r in Results }
  #      {'SNP':(2983,slug), 'EJ':(55,slug), ..}

## Start wp-cli Methods       ######################
def wp_term_create(tax, name, slug=None, desc=None, parent=None,
                   porcelain=None):
  ''' wp-cli.org/commands/term/create/
  <taxonomy> Taxonomy for the new term
  <term>     A name for the new term
  [--slug=<slug>] unique slug for the new term. Defaults to sanitized name
  [--description=<description>] A description for the new term.
  [--parent=<term-id>] A parent for the new term.
  [--porcelain] Output just the new term id.
  '''
  Bj = WpC.WB.Bj
  L.info('wp_term_create {} {} {} {} {} {}',
         tax, name, slug, desc, parent, porcelain)
  Cmd = "wp --path={} --url={} term create {} {}".format(Bj.WC0.SDir,
         Bj.SFQDN, tax, name)
  if slug:      Cmd += ' --slug='       + slug
  if desc:      Cmd += ' --description='+ desc
  if parent:    Cmd += ' --parent='     + parent
  if porcelain: Cmd += ' --porcelain'
  return Bj.WH0.Exec(Cmd)

def wp_term_delete(tax, term_ids):
  ''' http://wp-cli.org/commands/term/delete/
  <taxonomy> Taxonomy for the new term
  <term-id>… One or more IDs of terms to delete
  '''
  Bj = WpC.WB.Bj
  if   isinstance(term_ids, int):
    term_ids = ( str(term_ids), )
  elif isinstance(term_ids, str):
    term_ids = ( term_ids, )
  elif isinstance(term_ids, (tuple, list)):
    term_ids = [ str(i) for i in term_ids if str(i).isdigit() ]
  else:
    L.info('passed bad term_ids into wp_term_delete()')
    return False
  L.info('wp_term_delete {} {}', tax, term_ids)
  return Bj.WH0.Exec("wp --path={} --url={} term delete {} {}".format(
           Bj.WC0.SDir, Bj.SFQDN, tax, ' '.join(term_ids)))

# End TermC Original @staticmethod



def TaxSlug(taxonomy):
  return 'tag' if taxonomy == 'post_tag' else taxonomy

#def HrefTxtSlug(TName, Href, taxonomy='post_tag'):
#  " Merged into HrefSlug() "
#  WpTerm_TermD = GetWpTermFromWjTermD(taxonomy, Href)
#  #if Href in WpC.WB.Wj.TermD[taxonomy]:  #no compare .lower()
#  if  WpTerm_TermD:  # if Href Match Found in TermD, also compare .lower()
#    Slug = WpTerm_TermD.slug  #= WpC.WB.Wj.TermD[taxonomy][Href][1]
#  else:
#    Slug = UC.WpySlugify(Href)
#    L.warning("HrefTxtSlug Href={} not in WpTerms.TermD".format(Href))
#    L.info("Replace Href slug with UC.WpySlugify(Href)".format(Slug))
#  return  '<a href="/{}/{}/">{}</a>'.format(TaxSlug(taxonomy), Slug, TName)
#  #return '<a href="/tag/{}/">{}</a>'.format(UC.WpySlugify(Href), Txt)
#
#def HrefSlug(TName, taxonomy='post_tag'):
#  WpTerm_TermD = GetWpTermFromWjTermD(taxonomy, TName)
#  #if TName in WpC.WB.Wj.TermD[taxonomy]:  #no compare .lower()
#  if  WpTerm_TermD:  # if TName Match Found in TermD, also compare .lower()
#    Slug = WpTerm_TermD.slug  #= WpC.WB.Wj.TermD[taxonomy][TName][1]
#  else:
#    Slug = UC.WpySlugify(TName)
#    L.info("Warning! HrefSlug TName={} not in WpTerms.TermD", TName)
#    L.info("Replace TName slug with UC.WpySlugify(TName)", Slug)
#  return  '<a href="/{}/{}/">{}</a>'.format(TaxSlug(taxonomy), Slug, TName)
#  #return '<a href="/tag/{}/">{}</a>'.format(UC.WpySlugify(TName), TName)
#
#def WpTermLink(Term):
#  " Merged into HrefSlug() "
#  if Term is None:
#    return None
#  if not GetWpTermFromWjTermD(Term.taxonomy, Term.name):
#    L.warning("not found GetWpTermFromWjTermD(Term.taxonomy, Term.name)")
#  return  '<a href="/{}/{}/">{}</a>'.format(
#          TaxSlug(Term.taxonomy), Term.slug, Term.name)

def HrefSlug(TName, taxonomy='post_tag', Href=None, Slug=None):
  if TName is None:
    return None
  if isinstance(TName, WordpyTermC):
    taxonomy = TName.taxonomy
    Slug     = TName.slug
    TName    = TName.name
  WpTerm_TermD = GetWpTermFromWjTermD(taxonomy, TName if Href is None else Href)
  if  WpTerm_TermD:  # if TName Match Found in TermD, also compare .lower()
    Slug = Slug or WpTerm_TermD.slug
    #    = WpC.WB.Wj.TermD[taxonomy][TName if Href is None else Href)][1]
  else:
    Slug = Slug or UC.WpySlugify(TName if Href is None else Href)
    L.warning("HrefSlug {} not in Wj.TermD",
              TName if Href is None else Href)
    L.info("Replace Slug with UC.WpySlugify(TName if Href is None else Href) =",
           Slug)
  return  '<a href="/{}/{}/">{}</a>'.format(TaxSlug(taxonomy), Slug, TName)
  #return '<a href="/tag/{}/">{}</a>'.format(UC.WpySlugify(TName), TName)

def GenKeywordLinksForAllWpTerms(WpTerms):
  KwHrefs = []
  for Term in WpTerms:
    if Term is None:
      continue
    #KwHrefs.append( WpTermLink(Term) )
    KwHrefs.append ( HrefSlug(Term) )
  return ', '.join(KwHrefs)




'''
/cf/py/web$ ipython -i -c "import news.ProcessNews as PNews"<Paste>
>>> PNews.ProcessCaijingLogNews()
>>> import wp.conf as WpC; wpdb = WpC.WB.Wj.wpdb; TermD = WpC.WB.Wj.TermD
>>> TermD
>>> for key,value in TermD.items():
...   print('\n', key)
...   Seq = 0
...   for k,v in value.items():
...      print('  ', k, v )
...      Seq += 1
...      if Seq > 10:
...        break
 post_tag
   caijing (65, 'caijing')
   最新 (71, 'zui-xin')
   公告 (74, 'gong-gao')
   上市公司 (77, 'shang-shi-gong-si')
   业绩 (80, 'ye-ji')
   期货圈名人 (83, 'qi-huo-quan-ming-ren')
   实时 (86, 'shi-shi')
   财经 (89, 'cai-jing')
   全球新闻 (92, 'quan-qiu-xin-wen')
   区别对待沪深指数的短期表现 (95, 'qu-bie-dui-dai-hu-shen-zhi-shu-de-duan-qi-biao-xian')
   _张中秦_新浪博客 (98, 'zhang-zhong-qin-xin-lang-bo-ke')
 category
   Uncategorized (1, 'uncategorized')
   news (59, 'news')
   games (62, 'games')
   companies (68, 'companies')

>>> len(TermD['post_tag'])  #Out: 85908
>>> len(TermD['category'])  #Out: 4
>>> import wp.conf as WpC; wpdb = WpC.WB.Wj.wpdb; TermD = WpC.WB.Wj.TermD
>>> import wp.i.taxonomy as WiTx;  Tax  = 'post_tag'
>>> TermObj = WiTx.get_term_by('name', '上市公司', Tax); TermObj
<Php.Object(WP_Term)> (10) {
  ['term_id']=> <int> 77
  ['name']=> <str> 上市公司
  ['slug']=> <str> shang-shi-gong-si
  ['term_group']=> <int> 0
  ['term_taxonomy_id']=> <int> 77
  ['taxonomy']=> <str> post_tag
  ['description']=> <str>
  ['parent']=> <int> 0
  ['count']=> <int> 952
  ['filter']=> <str> raw
}
>>> TermObj1 = WiTx.get_term_by('name', '川普', Tax); TermObj1
<Php.Object(WP_Term)> (10) {
  ['term_id']=> <int> 61490
  ['name']=> <str> 川普
  ['slug']=> <str> chuan-pu
  ['term_group']=> <int> 0
  ['term_taxonomy_id']=> <int> 61487
  ['taxonomy']=> <str> post_tag
  ['description']=> <str>
  ['parent']=> <int> 0
  ['count']=> <int> 3
  ['filter']=> <str> raw
}

'''

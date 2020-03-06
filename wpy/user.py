#!/usr/bin/python3
#from pprint import pprint
#pprint(userdata)  # TypeError: unhashable type: 'instancemethod'
#   TypeError: p = self._dispatch.get(type(object).__repr__, None)
#   because: self._dispatch is a dict, but type(object).__repr__ = method
#userdata is array, inspect.ismethod(A.__repr__) is True
#Copied pprint to wpy.PPrint and modified it,
#so PPrint(Php.array) will work for len(array.__repr__()) > 80
from wpy.PPrint import pprint as PPrint

from wordpress_xmlrpc import AuthenticatedMethod    # Client,
from wpy.xmlcli import Client
# /usr/local/lib/python3/dist-packages/wordpress_xmlrpc/wordpress.py
from wordpress_xmlrpc.wordpress import WordPressBase #, WordPressUser

import pyx.encrypt as xEcr
import pyx.php     as Php
import pyx.type    as xTp
import pyx.format  as Fmt
import pyx.unicode as UC
import wp.conf     as WpC
import wp.i.format as WiF
import wp.i.user   as WiU
import config.log as cLog; L = cLog.logger
array, ODict = Php.array, Php.ODict
# Module.Wj   = self.Wj  set in Web.WpBlogCls


# python3 -i -c "import wpy.web as Web; S = Web.SiteCls(1, Hosts=(cHO.WpPub0W0,), WebConf=True, ConnSsh=True); import wp.i.user as WiU;"


AdminUserD = {   # User Dict, rather than ODict
  # ID :  user_login    ,user_nicename, display_name     ,
  #       user_email                  , user_pass
  1001 : ('wordpy_info', 'info'       , 'info'           ,
         'info@wordpy.com'            , 'wordpy_password'),
}

def GetAdminUserIdByLogin(Login):
  for Id,V in AdminUserD.items():
    if V[0] == Login:
      return Id
  #return [ Id for Id,V in AdminUserD.items() if V[0] == Login ][0]


# wordpy.com/wp-admin/profile.php
# Nickname (required)
# Display name publicly as: SelectBox:
#    user_login =
#    display_name = WordPy AI
#    user_login =

# Display name (Default=user_login=username) is selectable between user's
#   ULogin=username, first name, last name, first/last, last/first, or NickName
# Nickname (Default=user_login=username) gives an option to set
#   display name to something other than username or real name
# NickName give option to set DispName to it other than ULogin or f/last
# NiceName = slug is unique key!!

MapDbWpUserOD = ODict([      # Map db table Dict
  # wp.py var, (db columns, php var: True if used in UData & Same as db columns
  ('UId'     , ('ID'                 ,True ,)),
  ('ULogin'  , ('user_login'         ,True ,)),
  ('UPass'   , ('user_pass'          ,True ,)),
  ('NiceName', ('user_nicename', 'nicename',)), # unique key
  ('UEmail'  , ('user_email'         ,True ,)),
  ('UUrl'    , ('user_url'           ,True ,)),
  ('RegDate' , ('user_registered'    ,True ,)), # Y-m-d h:m:s
  ('ActvKey' , ('user_activation_key',False,)),
  ('UStatus' , ('user_status'        ,False,)),
  ('DispName', ('display_name'       ,True ,)),
  ('Spam'    , ('spam'               ,False,)),
  ('Deleted' , ('deleted'            ,False,)),
])
MapDbWpUserMetaD = {  # Map db wp_usermeta.meta_key
  # wp.py    : meta_key vals
  'Roles'    : ('roles'        , True,), #wp_6100_capabilities
  'NickName' : ('nickname'     , True,),
  'FirstName': ('first_name'   , True,),
  'LastName' : ('last_name'    , True,),
  'Desc'     : ('description'  , True,),
 #'UseSsl'   : ('use_ssl'      , True,),
 #'SrcDomain': ('source_domain', True,),
 #'PrimaryB' : ('primary_blog' , True,),
}

UserPyAttrs = ([ k for k in MapDbWpUserOD.keys()    ] +
               [ k for k in MapDbWpUserMetaD.keys() ]  )

MapDbBpGrpT = (  # Map db wp_bp_xprofile_fields Dict
  # wp.py      , # db columns      #Need fixing!!!!
  'GrpAdmId'   , # 'wp_bp_groups_members.user_id', #wp_bp_groups.creator_id'
  'GrpName'    , # 'wp_bp_groups.name'           , #'group_name'
  'GrpSlug'    , # 'wp_bp_groups.slug'           , #'group_slug'
  'GrpAddUIds', # None,
)
XmlPyPhpBpGrpD  = { k: k for k in MapDbBpGrpT }
XmlPhpPhpBpGrpD = { k: k for k in MapDbBpGrpT }

#DbUserColumns = [ V[0] for V in MapDbWpUserOD.values() ]

DbXProfFColumns = [   #Db xprofile_fields Columns
  'id',
  'group_id',
  'parent_id',
  'type',
  'name',
  'description',
  'is_required',
  'is_default_option',
  'field_order',
  'option_order',
  'order_by',
  'can_delete',
]


class AdminUserCls(xTp.BaseCls):
  #import wp.i.cls.user  as WcU
  #assert DbUserColumns == WcU.WP_User.DbUserColumns
  _InitAttrs = xTp.BaseCls._InitAttrs + UserPyAttrs

  def __init__(self, UId, *args, **kwargs):
    # super().__init__(*args, **kwargs) #= super(xTp.BaseCls,self).method(arg)
    self.UId = UId
    #L.debug('  AdminUserCls UId= {}', UId)
    self.ULogin, self.NiceName, self.DispName, self.UEmail, self.UPass \
        = AdminUserD[UId]


class DbXProfFCls(xTp.BaseCls):   #Db xprofile_fields Class
  _InitAttrs = xTp.BaseCls._InitAttrs + DbXProfFColumns
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)  # = super(xTp.BaseCls, self).method(arg)


MapWpXmlUserD = {
 # MapDbWpUserOD       # Map db table Dict
  #xmlrpc.py : xmlrpc.php (None if Same Name as xmlrpc.py)
  'UId'      : 'user_id'     , #Orig: 'Id' : ('id','user_id',),
  'ULogin'   : 'username'    ,
  'UPass'    : None          ,
  'NiceName' : 'nicename'    ,
  'UEmail'   : 'email'       ,
  'UUrl'      : 'url'         ,
  'RegDate'  : 'registered'  ,
  'DispName' : 'display_name',
 # MapDbWpUserMetaD    # Map db wp_usermeta Dict
  'Roles'    : 'roles'       ,
  'NickName' : 'nickname'    ,
  'FirstName': 'first_name'  ,
  'LastName' : 'last_name'   ,
  'Desc'     : 'bio'         ,
 # Moved SetUIdTo from wordpy/xmlrpc.php to wp.user.InsertUser
 #'SetUIdTo'  : None          ,
}

XmlPyPhpWpUserD ={k:(k if v is None else v) for k,v in MapWpXmlUserD.items()}
XmlPhpPhpWpUserD= { (k if v is None else v) :
                    (k if v is None else v) for k,v in MapWpXmlUserD.items() }


# select * from wp_bp_xprofile_groups;
# id| name           | description                    |group_order|can_delete
# --+----------------+--------------------------------+-----------+----------
#  1| Profile        | Personal Profile               |          0|         0
# 10| Personal       | Personal Info                  |          0|         1
# 20| Phone Email URL| Optional: Phone, Email, Web URL|          0|         1
# 30| Social         | Social Accounts                |          0|         1
# 50| Company        | Company Profile                |          0|         1
# 70| Address        | Optional: Address              |          0|         1
# 80| Legal          | Legal Info                     |          0|         1
# 90| Finance        | Financial Info                 |          0|         1

# select id, group_id, parent_id, type, left(name, 25), left(description, 45), field_order, order_by from wp_bp_xprofile_fields where id < 1000;

MapXmlBpXProfD = {
  #UId:(xmlrpc.py var name  , xmlrpc.php var (None if Same Name as xmlrpc.py)
    0: ('UId'               ,None,),
  # Following Generated by Db.CompareBpXProfFields_vs_MapXmlBpXProfD()
    1: ('DispName'          ,None,), #Start: Group  1 Profile
    2: ('Country'           ,None,),
  101: ('MemType'           ,None,), #Start: Group 10 Personal
  111: ('FirstName'         ,None,),
  112: ('LastName'          ,None,),
}
XmlPyPhpBpXProfD = {   v[0] :
                      (v[0] if v[1] is None else v[1])
                      for v in MapXmlBpXProfD.values() }  # if v[0] != 'UId'}
XmlPhpPhpBpXProfD = { (v[0] if v[1] is None else v[1]) :
                      (v[0] if v[1] is None else v[1])
                      for v in MapXmlBpXProfD.values() }

MemTypes = {   #Abbr must all be lower case for php
  #Abbr:  Name             , SingleName        , HasDir
  'p' : ('Persons'         , 'Person'          , 'Person' ,),
  'co': ('Companies'       , 'Company'         , 'Co'     ,),
}

#AllMemTypes = {**WpyMemTypes,**WdpMemTypes} #py3:Dict1+Dict2+3
CompanyTypes = ('co',)   # =MemType[-2:]
PersonTypes  = ('p',)    # =MemType[-1:]


def GetMemTypeName(MemType, SingleName=False):
  if not MemType or len(MemType) > 5:
    raise ValueError("GetMemTypeName got bad MemType=", MemType)
  SiteName = MemType[:3].lower()
  if SiteName not in WpC.AllSites():
    raise ValueError("GetMemTypeName MemType has bad SiteName=", SiteName)
  MemTypeAbbr = MemType[3:].lower()
  return MemTypes[ MemTypeAbbr ][1 if SingleName else 0]


def IsMemberPerson(MemType):
  " return True if Member is a Person.  Ref to: /fs/web/p/wordpy/xmlrpc.php"
  return MemType[-1:] in PersonTypes

def IsMemberCompany(MemType):
  " return True if Member is a Company. Ref to: /fs/web/p/wordpy/xmlrpc.php"
  return MemType[-2:] in CompanyTypes

def GetUserUrl(       SUrl, NiceName):
  return SUrl +'m/'+ NiceName +'/'
def GetUserProfUrl(SUrl, NiceName):
  return GetUserUrl(  SUrl, NiceName) +'profile/'

def GetAuthorHref( SUrl, NiceName, DispName):
  return '<a href="{}author/{}/">{}</a>'.format(SUrl, NiceName, DispName)
def GetMemHref(    UUrl, DispName):
  return '<a href="{}">{}</a>'.format(UUrl, DispName)
def GetProfileHref(UUrl, DispName):
  return '<a href="{}profile/">{}</a>'.format(UUrl, DispName)  #UUrl endswith /


class MemberCls:
  ''' WpUsersNames = { Name1:UId1, Name2:UId2,...} is a class var to keep track
  of existing Names in WpUser database with all other instances of MemberCls(),
  so to avoid trying to re-insert duplicate names into WpUsers db.
  '''
  WpUsersNames = {}

  def __init__(self):
    self.UId = WpC.WB.Wj.CurrentUId = 0
    self.CnBlog        = WpC.IsCnBlog(self.BId)            #True or False
    self.PersonMember  = IsMemberPerson(self.MemType)      #True or False
    self.CompanyMember = IsMemberCompany(self.MemType)     #True or False
    self.SetWpUser()

  def SetWpUser(self):
    from nameparser import HumanName
    from datetime import datetime
    import wpy.time   as wTm
    if hasattr(self, 'Bj'):
      L.info('MemberCls.SetWpUser', self.Bj)
    #self.UId=1101 #If no ID, create new user. if ID!=None, update user w/ ID
    self.Name            = self.Name.strip()
    # self.SetUIdTo       = SetUIdTo  #Already set in MemberCls.__init__()
    AlphaDetect          = UC.AlphabetDetector()
    self.NameHasCjk      = AlphaDetect.any_cjk(self.Name)  #True or False

    #if Member.Attrs[1]== '公司': #elif DFile.Col1Name == '公司':
    if self.CompanyMember:
      if not getattr(self, 'CoName', None):
        self.CoName      = self.Name
      if not getattr(self, 'CoDispName', None):
        if self.NameHasCjk:
          self.CoDispName= (self.Name.replace('有限责任公司','')
                           .replace('有限公司','').replace('公司',''))
        else:
          self.CoDispName= self.Name
      if not getattr(self, 'DispName', None):
        self.DispName    = self.CoDispName
    #if Member.Attrs[1]  == '姓名': #if DFile.Col1Name   == '姓名':
    else:   #if self.PersonMember:
      if self.NameHasCjk:
        ParsedCnLastName, ParsedCnFirstName = UC.ParseCnName(self.Name)
      else:
        ParsedName = HumanName(self.Name)
        if not getattr(self, 'NameTitle', None) and ParsedName.title:
          self.NameTitle   = ParsedName.title
      if not getattr(self, 'FirstName', None):
        if self.NameHasCjk:
          #self.FirstName= self.Name[1:]
          self.FirstName = ParsedCnFirstName
        else:
          self.FirstName = ParsedName.first   #self.Name.split(' ')[:-1]
      if not getattr(self, 'LastName', None):
        if self.NameHasCjk:
          #self.LastName = self.Name[0]
          self.LastName  = ParsedCnLastName
        else:
          self.LastName  = ParsedName.last    #self.Name.split(' ')[-1]
      if not getattr(self, 'DispName', None):
        self.DispName    = self.Name  # = self.LastName + self.FirstName

    if self.NameHasCjk:
      if self.CompanyMember:
        Pinyins          = UC.TranslateCnNameToEn(self.Name, True)
        self.DispNameTr  = ' '.join(Pinyins)
        self.CoNameTr    = self.DispNameTr
        self.CoDispNameTr= Fmt.RmCoSuffix(self.CoNameTr)
      else:
        DispNameTrList = []
        if self.LastName:
          LastNamePinyins  = UC.TranslateCnNameToEn(self.LastName , False)
          self.LastNameTr  = ''.join(LastNamePinyins )
          DispNameTrList.append(self.LastNameTr)
        if self.FirstName:
          FirstNamePinyins = UC.TranslateCnNameToEn(self.FirstName, False)
          self.FirstNameTr = ''.join(FirstNamePinyins)
          DispNameTrList.append(self.FirstNameTr)
        self.DispNameTr  = ' '.join(DispNameTrList)

    if not getattr(self, 'NiceName'    , None):
      if   getattr(self, 'CoDispNameTr', None):
        NiceName = self.CoDispNameTr
      elif getattr(self, 'DispNameTr'  , None):
        NiceName = self.DispNameTr
      elif getattr(self, 'DispName'    , None):
        NiceName = self.DispName
      else:
        NiceName = self.Name
      # UC.WpySlugify("天使") => (pinyin) = 'tian-shi'.  UC.WpySlugify returns str.lower()
      self.NiceName= UC.WpySlugify(NiceName.lower()) # = slug = unique key!!

    ### Wp_User below ###
    # DispName is selectable btw ULogin, first,last,f/l,l/f, or NickName
    # DispName is selectable btw ULogin, first,last,f/l,l/f, or NickName
    #NickName give option to set DispName to it other than ULogin or f/l
    self.NickName  = self.DispName
    if not getattr(self, 'ULoginPref ', None):
      #=ULogin Prefix  = 'wpy-', or 'wdp-'
      BName = getattr(self.Bj, 'BName', '')
      self.ULoginPref = (BName or self.Bj.SName) +'-'
    if not getattr(self, 'ULogin', None):
      self.ULogin  = self.ULoginPref + self.NiceName.replace('-','')
    if not getattr(self, 'UPass' , None):
      L.debug('self.Bj.BU.UPass = {}', self.Bj.BU.UPass)
      self.UPass     = xEcr.PwdEncode(self.Bj.BU.UPass, self.Bj.SFQDN
                     + '/m/' + self.NiceName).decode()   # SFQDN=wordpy.com
    #=xEcr.PwdEncode(self.Bj.BU.UPass,'wordpy.com/m/'+self.NiceName).decode()
    if not getattr(self, 'UEmail' , None):
      self.UEmail  = self.ULogin +'@m.wordpy.com'
    self.UUrl      = self.Url = GetUserUrl(self.Bj.SUrl, self.NiceName)
    self.Roles     = 'author' if hasattr(self, 'SrcUrl') else 'subscriber'
    if not getattr(self, 'RegDate', None):
      #self.RegDate = datetime.strptime('2016-01-01 00:00', '%Y-%m-%d %H:%M')
      self.RegDate  = datetime.strftime(wTm.GenRandomPriorDatetime(
                      '2015-1-1'), wTm.DashYMDHMS)

    ### BpXProfile below ###
    if not getattr(self, 'Country', None):
      self.Country  = 'CN China' if self.CnBlog else 'US United States'
    if not getattr(self, 'CoURL', None) and self.CompanyMember:
      self.CoURL    = self.UUrl
    self.AuthorHref = GetAuthorHref(self.Bj.SUrl, self.NiceName, self.DispName)
    self.MemHref    = GetMemHref(      self.UUrl, self.DispName)
    self.ProfileHref= GetProfileHref(  self.UUrl, self.DispName)
    #    GrpName can be Cn
    self.GrpAdmId   = getattr(self, 'GrpAdmId',   self.Bj.SUId)
    self.GrpAddUIds = getattr(self, 'GrpAddUIds', (self.GrpAdmId,) )
    if not getattr(self, 'GroupTitle', None):
      self.BTitle   = self.Bj.WC0.BTitle #='WordPy AI' or 'WordPy Finance'
      #    .GroupTitle='WordPy AI' +' '+ 'Programmers'
      #self.GroupTitle= self.BTitle  +' '+ AllMemTypes[self.MemType][0]
      self.GroupTitle = self.BTitle  +' '+ GetMemTypeName(self.MemType)

    self.GrpName    = self.GroupTitle + (' 公众群' if self.CnBlog else
                                         ' Public Group')

    #    GrpSlug is always En
    self.GroupTitleEn = getattr(self, 'GroupTitleEn', self.GroupTitle)
    if AlphaDetect.any_cjk(self.GroupTitleEn):
      self.GroupTitleEn = ' '.join(UC.TranslateCnNameToEn(
                                   self.GroupTitleEn, self.CompanyMember))
    #GrpCountry = '' if self.Country.startswith('US') else self.Country[2:]
    self.GrpSlug = UC.WpySlugify(self.GroupTitleEn) # + GrpCountry)

    L.info('\nMemberCls attributes:')
    PPrint({ attr:(getattr(self, attr, ''))
             for attr in dir(self) if not attr.startswith(
             ('_','definition','Sources','GameReviewsUrls',))})
    #for attr in dir(self):
    #  if not attr.startswith(('_',)): # 'Member')):
    #    L.info("{:15}: {}", attr, getattr(Member, attr, ''))
    L.info('')


  def AddWpUserBpGroupXProf(self, add_cap=None, add_role=None):
    " replace: wp.xml.XmlAddWpUserBpGroupXProf "
    WpC.WB.Bj.HashPwd = getattr(self, 'HashPwd', True)

    if self.Name in self.WpUsersNames:
      self.UId = WpC.WB.Wj.CurrentUId = self.WpUsersNames[ self.Name ]
      L.info("\nDid not InsertUser. Previously inserted Member.Name & UId = {}",
             " {}\n", self.Name, self.UId)
      return self.UId

    self.UId = WpC.WB.Wj.CurrentUId = self.InsertUser()
    if self.UId == 0:
      L.info("\nError! Cannot InsertUser.\n\n")
      return False
    if self.UId < 0:  # = negative! DupUser id # = -self.UId
      L.info("\nDid not InsertUser. Duplicate Member.UId= {}\n", -self.UId)
      self.WpUsersNames[ self.Name ] = -self.UId
      return self.UId

    self.WpUsersNames[ self.Name ] = self.UId
    L.info("\nNewly inserted Member.UId= {}\n", self.UId)
    if add_cap:   # 'manage_categories'
      WiU.wp_add_cap( self.UId, add_cap)
    if add_role and add_role != 'subscriber':   # 'author'
      WiU.wp_add_role(self.UId, add_role)
    if not self.GrpName:
      L.info("Cannot create GrpName as it is None!")
      return False
    self.XmlAddBpGroupXProf()
    #if i >= 4: import sys; sys.exit()
    return self.UId


  def XmlInsertUser(self):
    Wp_User = WpXmlUser()   # Use WpXmlUser, not Orig WordPressUser()
    for k,v in XmlPyPhpWpUserD.items():
      if k.lower() == 'id':  #If no Id, create new user.
        continue             # if Id != null, update user with Id
      # if k == 'Roles': L.info('\n Roles = {} {}', v, getattr(self, k))
      if hasattr(self, k):
        setattr(Wp_User, v, getattr(self, k))
    L.info("\n Wp_User =")
    PPrint({attr:(getattr(Wp_User, attr, '')) for attr in dir(Wp_User)
                  if not attr.startswith(('_','definition',))})
    wp=Client(**self.Bj.XmlCli)
    return int( wp.call(WpXmlInsertUser(Wp_User)) )

  def XmlAddBpGroupXProf(self):
    XMem    = WpXmlBpMem()
    #  if   self.ULoginPref == 'Wpy-':
    #    XMem    = BpXProfileMember(self)
    #  elif self.ULoginPref == 'CnDb-':    #=ULogin Prefix
    #    XMem    = BpXProfileDebtor(self)
    #  elif self.ULoginPref == 'UsCn-':    #=ULogin Prefix
    #    XMem    = BpXProfileSec(self)
    #  else:
    #    raise ValueError("ULoginPref not in ('Wpy-', CnDb-',) !!")
    # XMem.Id = self.UId  #Comment out. XmlPyPhpBpXProfD below takes care of
    for k,v in XmlPyPhpBpXProfD.items():
      if hasattr(self, k):
        setattr(XMem, v, getattr(self, k))
        #XMem.FirstName = self.FirstName   #should be done by setattr above
    for k,v in XmlPyPhpBpGrpD.items():
      if hasattr(self, k):
        setattr(XMem, v, getattr(self, k))
    PPrint({attr:(getattr(XMem, attr, '')) for attr in dir(XMem)
                  if not attr.startswith(('_','definition',))})
    L.info("XMem above: \n")
    wp=Client(**self.Bj.XmlCli)
    AllSuccess = int( wp.call(WpXmlSetBpGrpXProf(XMem)) )
    L.info("WpXmlSetBpGrpXProf AllSuccess= {} {}", AllSuccess,
          'Y' if AllSuccess == 1 else 'N! Problems!')
    return AllSuccess

  def XmlAddWpUserBpGroupXProf(self, add_cap=None, add_role=None):
    import wp.i.user  as WpU
    self.UId  = self.XmlInsertUser()
    if self.UId == 0:
      L.info("Error! Cannot InsertUser.")
    elif self.UId > 0:
      L.info("\n Newly inserted Member.Id= {}\n\n", self.UId)
      #if add_cap or add_role:
      if add_cap:   # 'manage_categories'
        WpU.wp_add_cap( self.UId, add_cap)
      if add_role:   # 'author'
        WpU.wp_add_role(self.UId, add_role)
      self.XmlAddBpGroupXProf()
      self.SetUIdTo += 1
      #if i >= 4: import sys; sys.exit()
    else:   # self.UId = negative! DupUser id # = -self.UId
      self.UId = - self.UId
      L.info("Did not InsertUser. Duplicate Member.Id= {}", self.UId)
    return self.UId


  def InsertUser(self):
    import wp.i.cls.user  as WcU
    #ULogin Checked by wp_insert_user!!
    #if not getattr(self, 'ULogin', None):
    #  L.info("Cannot InsertUser.  ULogin is blank!")
    #  return 0
    #wp_insert_user allows blank email, but db refuses blank or null email!
    if not getattr(self, 'UEmail', None):
      L.info("Cannot InsertUser.  UEmail is blank!")
      return 0

    ''' Replaced by below: if WpC.WB.Wj.is_wp_error( UserId ):
    if WiU.username_exists(self.ULogin):
      DupUser = WiU.get_user_by( 'login', self.ULogin )
      PPrint(DupUser.__dict__)
      L.info("Cannot InsertUser.  ULogin={} already exists in ID={}",
             self.ULogin, DupUser.ID)
      #PPrint(DupUser.get_role_caps())
      return 0 - DupUser.ID   # return negative ID # as DupUser ID

    if WiU.email_exists(self.UEmail):
      DupUser = WiU.get_user_by( 'email', self.UEmail )
      L.info("Cannot InsertUser.  UEmail={} already exists in ID={}",
             self.UEmail, DupUser.ID)
      #PPrint(DupUser.get_role_caps())
      return 0 - DupUser.ID   # return negative ID # as DupUser ID
    '''
    # unset( U['ID'] )
    L.info("InsertUser ULogin={}, UEmail={}", self.ULogin, self.UEmail)
    #wordpress.org/support/topic/programmatically-add-user-using-wp_insert_user
    UData = array()
    for PyVar, V in {**MapDbWpUserOD,**MapDbWpUserMetaD}.items(): #Combine 2 dicts
      # Include to UData only if V[1] != False
      # If no ID, create new user. if ID!=None, update user with ID
      if V[1] == False or V[0] == 'ID':
        continue
      PhpVar = V[0] if V[1] == True else V[1]
      UData[PhpVar] = getattr(self, PyVar, '')
    if not UData['user_pass']:
      #UData['user_pass']= wp_generate_password( 10,True,True )
      UData['user_pass'] = xEcr.PwdEncode(self.Bj.BU.UPass, self.Bj.SFQDN
                           + '/m/' + self.NiceName).decode()
    if not UData['user_url']:
      #UData['user_url'] = get_site_url()
      UData[ 'user_url'] = self.Bj.BUrl
    if not UData['roles']:
      UData['roles'] = 'subscriber'

    # wordpy.com/wp-admin/network/admin.php?page=ss_options
    # Disable: Filter Login Requests: Some plugins and themes bypass the standard registration forms. If you check this, Stop Spammers will try to intercept the login int the WordPress user login module. This will cause some overhead, but gives Stop Spammers another shot at detecting Spam.
    SetUIdTo  = getattr(self, 'SetUIdTo',0)
    LenULogin = len(self.ULogin)
    Tries = 5

    for  ULoginSuffix in range(Tries):
      if ULoginSuffix > 0:
        self.ULogin = self.ULogin[:LenULogin] + str(ULoginSuffix)
        UData['user_login'] = self.ULogin
        L.info("\n SetUIdTo={} > 0 and DupUser has the same user_login! Retry "
               "wp_insert_user with '{}' append to user_login. New ULogin={}.",
               SetUIdTo, ULoginSuffix, self.ULogin)

      UserId = WiU.wp_insert_user( UData, SetUIdTo = SetUIdTo )

      if WpC.WB.Wj.is_wp_error( UserId ):
        L.info("wpy.user.MemberClass.InsertUser {}", UserId)  #, UserId.errors
        for ErrCode in ('existing_user_email', 'existing_user_login'):
          if (ErrCode in UserId.errors.keys()):
            DupUserId = getattr(UserId, 'error_data', None).get(ErrCode, 0)
            L.info('\n DupUserId = {} {} {}', DupUserId, ErrCode, UserId)
        if   'existing_user_login' in UserId.errors.keys():
          if SetUIdTo > 0 and ULoginSuffix < (Tries - 1):
            continue
          return 0 - DupUserId   # return negative ID # as DupUser ID
        elif 'existing_user_email' in UserId.errors.keys():
          return 0 - DupUserId   # return negative ID # as DupUser ID
        L.info("{} Error! Cannot InsertUser.", ULoginSuffix)
        return 0
      break

    #User = WiU.get_user_by( 'id', UserId )
    User  = WcU.WP_User(UserId)
    L.info("Inserted UserId= {}", UserId)
    # L.info("get_role_caps=")
    # PPrint(User.get_role_caps())

    #www.authorsure.com/827/wordpress-username-security
    #wordpress.org/support/topic/wpdb-update-user_login-also-updates-user_nicename
    # wp_insert_user use user_login as user_nicename, if there's no nicename
    # enable following if need to make sure and force to use nicename.lower
    # if UData.get('nicename', ''):
    #   NicenameLower = UData['nicename'].lower()
    #   userdata = { 'ID'            : UserId,
    #                'user_nicename' : NicenameLower,)
    #   wp_update_user(userdata) #WP auto update nicenme from upper to lower
    #   L.info("Updated UserId=UserId to user_nicename=NicenameLower")

    #ifisset(args[5]) and (int)args[5] !=0:
    if getattr(self, 'SetUIdTo', 0) > 0 and UserId != self.SetUIdTo:
      raise Exception('Cannot just update TbG.User ID. Need to update other Tbs'
                ' using WpC.WB.Bj.GDB.s.add(User), instead of wpdb.wpdb.insert')
      L.info("Update from UserId=UserId to SetUIdTo= {}", self.SetUIdTo)
      Sql =("UPDATE {}:{} SET ID=%s WHERE ID=%s"
            .format(WpC.WB.Bj.GDB.DbName, WpC.WB.Bj.GDB.TbG.User))
      RowDict = WpC.WB.Bj.GDB.Exec(Sql, (self.SetUIdTo, UserId,),)
      UserId = self.SetUIdTo

      if self.SetUIdTo > 2000:
        self.SetUIdTo += 1

    return UserId



# update wp_bp_xprofile_fields set name='Company Display Name' where id=501

def CompareBpXProfFields_vs_MapXmlBpXProfD():
  SDb = Db.SiteDbCls(1)
  SDb.DbH.SshOpen('CompareBpXProfFields_vs_MapXmlBpXProfD SDb.DbH')
  #SDb.Exec('show databases')
  #PPrint(SDb.TbG.__dict__)
  #SDb.TbG.BpXProfF
  RowDicts = SDb.GetBpXProfFields()
  #for Row in RowDicts:
  # # if Row['id'] < 1000:  #Default IdMax=999
  # L.info("{:5} {:30} {:50}", Row['id'],Row['name'],Row['description'])
  XProfObjs = [DbXProfFCls(**RowDict) for RowDict in RowDicts] #Objs List
  with open('/tmp/MapXmlBpXProfD.py', 'w') as FOut:
   for X in XProfObjs:
    #L.info("{:5} {:30} {:50}", X.id, X.name, X.description)
    #...replace('CompanyName','CoName').replace('CompanyDept','CoDept')...
    #Change to: ...replace('Company','Co')...
    #  Old: CompanyName CompanyDept CompanyURL CompanyEmail CompanyMainPhone
    #  New: CoName      CoDept      CoURL      CoEmail      CoMainPhone
    X.name = X.name.replace(' and ','').replace(' or ','Or').replace(' on ','On').replace(' by ','By').replace(' ','').replace('-','').replace('/','').replace('(Translate)','Tr').replace('Company','Co').replace('PostalCode','PostCode').replace('Province','Prov').replace('Department','Dept').replace('Exchange','Ex').replace('Percent','Pct').replace('Registration','Reg').replace('RevenueGrowth','RevGrow').replace('EarningsGrowth','EarnGrow').replace('ValueRevenue','ValRev').replace('ValueEBITDA','ValEBIT').replace('RevenuePerShare','Rev').replace('Operating','Op').replace('Institutions','Institute').replace('NonPayment','NonPay').replace('YearAgo','YrAgo').replace('MobilePhone','Mobile').replace('FreeCashFlow','FreeCashFl').replace('(Default=username)','').replace('MemberType','MemType')
    QuotedN = repr(X.name)  #= "'"+X.name+"'"
    #L.info("    {:20}=> {:3},", QuotedN, UId))      #php arra
    #L.info("    {:20}: {},", QuotedN, QuotedN))  #py class de
    #Line= "  {:3}: ({:20},{:20},None,),".format(X.id, QuotedN, QuotedN)
    Line = "  {:3}: ({:20},None,None,),".format(X.id, QuotedN)
    L.info(Line)
    FOut.write(Line +'\n')




class WpXmlInsertUser(AuthenticatedMethod):
  """  Create a new user on the blog.
  Params: `content`: A :class:`WordPressPost` instance with at least
                    `username`, `content` and `content` values set.
  Returns: ID of the newly-created blog post (an integer).
  """
  method_name   = 'wp.InsertUser'
  method_args   = ('content',)
  #optional_args = ('user_pass','SetUIdTo','GrpName')

class WpXmlSetBpGrpXProf(AuthenticatedMethod):
  """  Create a new user on the blog.
  Params: `content`: A :class:`WordPressPost` instance with at least
                    `username`, `content` and `content` values set.
  Returns: ID of the newly-created blog post (an integer).
  """
  method_name   = 'wp.SetBpGrpXProf'
  method_args   = ('content',)
  #optional_args = ('user_id',)

class WpXmlUser(WordPressBase):
  definition = XmlPhpPhpWpUserD
  #'registered' : DateTimeFieldMap('registered'),#Orig class WordPressUser()
  #'registered' : 'registered',                  #VT Changed to
  # won't run WordPressBase.__init__() unless super().__init__()

class WpXmlBpMem(WordPressBase):
  definition = { **XmlPhpPhpBpXProfD, **XmlPhpPhpBpGrpD }
  # won't run WordPressBase.__init__() unless super().__init__()
  # def __init__(self, Obj):
  #   self.UId = Obj.Id
  #   for k,v in XmlPyPhpBpXProfD.items():
  #     if hasattr(Obj, k):
  #       setattr(self, v, getattr(Obj, k))
  #       #self.FirstName = Obj.FirstName   #should be done by setattr above
  #   L.info("\n XMem =")
  #   PPrint({attr:(getattr(XMem, attr, '')) for attr in dir(XMem)
  #                 if not attr.startswith(('_','definition',))})

# class BpXProfileMember(WpXmlBpMem):
#   def __init__(self, Obj):
#     WpXmlBpMem.__init__(self, Obj, XmlPyPhpBpXProfD)
# class BpXProfileDebtor(WpXmlBpMem):
#   def __init__(self, Obj):
#     WpXmlBpMem.__init__(self, Obj, XmlPyPhpBpXProfD)
# class BpXProfileSec(WpXmlBpMem):
#   pass


'''
wp_global]> select * from  wp_bp_groups where ID > 1330;
| id   | creator_id | name                 | slug                  | description                                                                                   | status | enable_forum | date_created        | parent_id |
| 1333 |       1001 | pcgamer Public Group | pcgamer-united-states | Welcome to pcgamer Public Group!  pcgamer-united-states
 Please feel free to join this Group. | public |            1 | 0000-00-00 00:00:00 |         0 |

wp_global]> select * from  wp_bp_groups_members  where group_ID > 1330;
| id    | group_id | user_id | inviter_id | is_admin | is_mod | user_title  | date_modified       | comments | is_confirmed | is_banned | invite_sent |
| 79693 |     1333 |    1001 |          0 |        1 |      0 | Group Admin | 2017-03-12 22:59:03 |          |            1 |         0 |           0 |

wp_global]> select * from  wp_bp_groups_groupmeta where group_ID > 1330;
| id    | group_id | meta_key                  | meta_value          |
| 71203 |     1333 | total_member_count        | 1                   |
| 71209 |     1333 | last_activity             | 2017-03-12 22:59:06 |
| 71215 |     1333 | forum_id                  | a:1:{i:0;i:131378;} |
| 71221 |     1333 | _bbp_forum_enabled_131378 | 1                   |

wp> groups_delete_group( 1333 )

'''

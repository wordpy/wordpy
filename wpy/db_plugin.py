import config.db as cDB
import pyx.type  as xTp
import wp.conf   as WpC
ODict = cDB.ODict


#class xTbC:

# TbsBp = Buddypress (Bp) Tables.  Only available if 'bp' in WpSitePluginD
TbsBpPy = (
   'BpActy'             , 'BpActyMeta'           , 'BpFriend' , 'BpGrp',
   'BpGrpGrpMeta'       , 'BpGrpMem'             , 'BpMsgMsg' ,
   'BpMsgMeta'          , 'BpMsgNoti'            , 'BpMsgRcpt',
   'BpNoti'             , 'BpNotiMeta'           , 'BpUsrBlog',
   'BpUsrBBlgMeta'      , 'BpXProfData'          , 'BpXProfF' ,
   'BpXProfGrp'         , 'BpXProfMeta'          ,
)

TbsBpWp = (
   'bp_activity'        , 'bp_activity_meta'     , 'bp_friends','bp_groups',
   'bp_groups_groupmeta', 'bp_groups_members'    , 'bp_messages_messages'  ,
   'bp_messages_meta'   , 'bp_messages_notices'  , 'bp_messages_recipients',
   'bp_notifications'   , 'bp_notifications_meta', 'bp_user_blogs'         ,
   'bp_user_blogs_blogmeta','bp_xprofile_data'   , 'bp_xprofile_fields'    ,
   'bp_xprofile_groups' , 'bp_xprofile_meta'     ,
)


#def InitPluginTbsCls(cls):
#  cls.TbsBpPy = TbsBpPy
#  cls.TbsBpWp = TbsBpWp

def InitPluginTbsObj(Obj):
  if getattr(Obj, 'SId', None) is None:   # GDb
    WHasBp = True
  else:                                   # If db has bp_ tables
    WHasBp = 'bp' in WpC.SitePluginD[Obj.SId].keys()
  if WHasBp: # If database contains bp_ tables
    SPfx   = getattr(Obj, 'SPfx'  , WpC.WPfx)
    #Obj.TbsBp= { i: SPfx + j for i,j in zip(TbsBpPy, TbsBpWp) }
    Obj.TbsBp = ODict([ (i, SPfx + j)
                         for i,j in zip(TbsBpPy, TbsBpWp) ])
    #Obj.TbsGlobal= {**Obj.TbsUsr, **Obj.TbsBp} #py3: Dict1+Dict2
    Obj.TbsGlobal = xTp.MergeODicts(Obj.TbsUsr, Obj.TbsBp)
  else:
    print('Something must be wrong in InitPluginTbs as WHasBp is False!')

  #TbsGlobal = Global Tables in Cluster db  (db1/2/3 & db2/2)

  #FederatedX Tbls
  #Obj.TbsFed= {**Obj.TbsGlobal, **{'Options' : Obj.TbPfx +'options',}}
  Obj.TbsFed =    Obj.TbsGlobal.copy()
  Obj.TbsFed['Options'] = Obj.TbPfx +'options'



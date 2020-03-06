import wpy.db      as wDB
import sa.sa_cls as Sa


class SaGlobalDbCls(wDB.GlobalDbCls, Sa.SqlAlchemyCls):
  def __init__(self, *args, config=None, Database=None, **kwargs):
    wDB.GlobalDbCls.__init__(self, *args, **kwargs)
    Sa.SqlAlchemyCls.__init__(self, config=config, Database=Database)

class SaSiteDbCls(wDB.SiteDbCls, Sa.SqlAlchemyCls):
  def __init__(self, *args, config=None, Database=None, **kwargs):
    wDB.SiteDbCls.__init__(self, *args, **kwargs)
    Sa.SqlAlchemyCls.__init__(self, config=config, Database=Database)

class SaBlogDbCls(wDB.BlogDbCls, Sa.SqlAlchemyCls):
  #def __init__(self, BId, DbHost=None, WH=None, ConnSsh=False, Exit=print):
  #  wDB.BlogDbCls.__init__(self, BId, getattr(self, 'Bj', None), DbHost,
  #                         WH, ConnSsh, Exit)
  def __init__(self, *args, config=None, Database=None, **kwargs):
    wDB.BlogDbCls.__init__(self, *args, **kwargs)
    Sa.SqlAlchemyCls.__init__(self, config=config, Database=Database)


class SaDbBareCls(wDB.DbCls, Sa.SqlAlchemyCls):
  def __init__(self, *args, config=None, Database=None, **kwargs):
    wDB.DbCls.__init__(self, *args, **kwargs)
    Sa.SqlAlchemyCls.__init__(self, config=config, Database=Database)

class SaDbCls(wDB.DbCls, Sa.SqlAlchemyCls):
  def __init__(self, DbUser, DbPass, DbHost, DbPort, DbName,
               config=None, Database=None, **kwargs):
    self.DbUser, self.DbPass = DbUser, DbPass
    self.DbHost, self.DbPort, self.DbName = DbHost, DbPort, DbName
    wDB.DbCls.__init__(self, self.DbHost, IniConf=False, **kwargs)
    Sa.SqlAlchemyCls.__init__(self, config=config, Database=Database)


# [Python logging made (stupidly) simple](github.com/Delgan/loguru)
# pip install loguru

from loguru import logger
import sys
L = logger
#Use:
#from  config.log    import logger as L

# https://docs.python.org/3/library/logging.html#logging-levels)
# NOTSET    0
# DEBUG    10
# INFO     20
# WARNING  30  <<--- Default
# ERROR    40
# CRITICAL 50

LogLevelD = dict(
 #name= Severity # Logger method
  TRACE   =  5,  # logger.trace()     # <<-- not in logging
  DEBUG   = 10,  # logger.debug()
  INFO    = 20,  # logger.info()
  SUCCESS = 25,  # logger.success()   # <<-- not in logging
  WARNING = 30,  # logger.warning()
  ERROR   = 40,  # logger.error()
  CRITICAL= 50,  # logger.critical()
)

#LogFile = '/tmp/logfile.log'
StdOut = sys.stdout    # or = LogFile
ModuleName = 'log_module'
DefaultLogLevel= 'INFO'
CurLogLevel    = 'ERROR'   # Will set to 'INFO' in SetCurLogLevel()
LogLevelNum    = LogLevelD[CurLogLevel]  # = 20

#Use: if cLog.LessEqCurLogLevel('DEBUG'):  # if VerboseOn:
def LessEqCurLogLevel(log_level):
  return LogLevelD[log_level] <= LogLevelD[CurLogLevel]


FormatDefault  = '{time} {level} {message}'
FormatTimeLong = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
Format         = "<green>{time:HH:mm:ss}</green> <level>{message}</level>"


# start: moved from pyx.func
#
VerboseOn   = True
# Use:
#VerboseOn = True  # Turn on/off V(...)

FlushStdout = True

def Verbose(*args, **kwargs):
  if VerboseOn:
    L.info(*args, **kwargs)
    if FlushStdout:
      sys.stdout.flush()

V = Verbose


def ExcInfo(Msg='Error!', **kwargs):
  ''' Use cLog.ExcInfo() instead of L.exception() since L.exception() always
      include backtrace after L.add(backtrace=True) by default.
  '''
  LogExcInfo(sys.exc_info(), Msg=Msg, **kwargs)

def LogExcInfo(SysExcInfo, Try = None, Msg = 'Error!', SkipType=None,
               TraceBack=False):
  ''' SysExcInfo = sys.exc_info()
  SysExcInfo[0] =  <class 'xmlrpc.client.Fault'>
  SysExcInfo[1] =  a class instance if exception type is a class obj
  SysExcInfo[2] =  <traceback object at 0x7ff7dafba388>
  '''
  if Try or Msg:
    L.error(f"Try = {Try} " if Try else '' + Msg)
  if ( SkipType is None or
      (SkipType is not None and not isinstance(SysExcInfo[0], SkipType) and
                                not issubclass(SysExcInfo[0], SkipType))):
    L.error('  type     = {}', SysExcInfo[0])
  L.error(  '  value    = {}', SysExcInfo[1])
  if TraceBack:
    L.error('  traceback= {}', SysExcInfo[2])
  #Unexpected error. type:  <class 'xmlrpc.client.Fault'>
  #Error value    :  <Fault 500: 'A term with the name provided already exists in this taxonomy.'>

PrintError = LogExcInfo

# # docs.python.org/3/library/sys.html#sys.exc_info
# try: x = 1/0
# except ZeroDivisionError as e:
#   L.exception("{} {} [{}]", type(e), isinstance(e, Exception), e)
#   SysExcInfo = sys.exc_info()
#   L.error(" {} {} [{}] {}\n", SysExcInfo[0] is type(e), SysExcInfo[1] is e,
#           SysExcInfo[1], SysExcInfo)
# # Out:
#   <class 'ZeroDivisionError'> True [division by zero]
#   True True [division by zero]
#    (<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero',), <traceback object at 0x7f3bd53c22c8>)

def VerboseReturnValue(func):
  '''
  >>> @VerboseReturnValue
  >>> def ABC(val):
  ...   return val
  >>> ABC(True ) #print: ABC: True , return: True
  >>> ABC(False) #print: ABC: False, return: False
  >>> ABC(None ) #print: ABC: None , return: None
  '''
  def wrapper(*args, **kwargs):
    Return = func(*args, **kwargs)
    if VerboseOn:
      L.info(func.__name__)  #, end=': ')
      if   Return is False: L.info('False')
      elif Return is True : L.info('True' )
      elif Return is None : L.info('None' )
      else:                 L.info(Return )
    return Return
  return wrapper
#
# start: moved from pyx.func



def SetCurLogLevel(LogLevel=CurLogLevel, RemoveLogBeforeAdd=True, LogFOut=StdOut):
  global CurLogLevel, LogLevelNum  #, VerboseOn
  LogLevel = LogLevel.upper()
  if LogLevel != CurLogLevel:
    if RemoveLogBeforeAdd:
      L.remove()
    #L.add(sys.stderr, format=FormatDefault, filter="my_module", level="INFO")
    #L.add(LogFile, format=FormatTime)
    L.add(LogFOut, format=Format, level=LogLevel)
    L.debug("SetCurLogLevel to {} using {}", LogLevel, L)
    CurLogLevel = LogLevel
    LogLevelNum = LogLevelD[CurLogLevel]  # = 20
    # VerboseOn = bool(LessEqCurLogLevel('INFO'))

SetCurLogLevel(DefaultLogLevel)



# [Logging with Loguru in Flask · GitHub](https://gist.github.com/M0r13n/0b8c62c603fdbc98361062bd9ebe8153)
# config.py
'''
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'SUPER-SECRET'
  LOGFILE = "log.log"

class DevelopmentConfig(Config):
  DEBUG = True
  LOG_BACKTRACE = True
  LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
  LOG_BACKTRACE = False
  LOG_LEVEL = 'INFO'

config = {
  'development': DevelopmentConfig,
  'production' : ProductionConfig,
  'default'    : DevelopmentConfig
}


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
import logging

db = SQLAlchemy()

# create a custom handler
class InterceptHandler(logging.Handler):
  def emit(self, record):
    logger_opt = L.opt(depth=6, exception=record.exc_info)
    logger_opt.log(record.levelno, record.getMessage())

# application factory pattern
def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)
  db.init_app(app)
  # logging properties are defined in config.py
  L.start(app.config['LOGFILE'], level=app.config['LOG_LEVEL'],
               format="{time} {level} {message}",
               backtrace=app.config['LOG_BACKTRACE'], rotation='25 MB')
  #register loguru as handler
  app.logger.addHandler(InterceptHandler())
  # register Blueprints here
  # ...
  return app

# simple example of how to use loguru in your flask application
# Just create a new InterceptHandler and add it to your app. Different settings should be configured in your config file, so that it is easy to change settings.
# Logging is then as easy as:
L.info("I am logging from loguru!")
'''



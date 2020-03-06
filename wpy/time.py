#!/usr/bin/python3
from datetime import datetime
import pytz    # sudo python3 -m pip install pytz  tzlocal

# docs.python.org/3/library/time.html#time.perf_counter (New in Py 3.3)
#time.perf_counter()
# Return the value (in fractional seconds) of a performance counter, i.e. a clock with the highest available resolution to measure a short duration. It does include time elapsed during sleep and is system-wide. The reference point of the returned value is undefined, so that only the difference between the results of consecutive calls is valid.
import time
from random import random

DefaultTimeZoneStr = 'US/Pacific'

#ShortYMD , ShortYMDHM = "%Y%m%d"     , "%Y%m%d%H%M"
#ShortYMDH, ShortYMDHMS= "%Y%m%d%H"   , "%Y%m%d%H%M%S"
#LongYMD  , LongYMDHM  = '%Y-%m-%d'   , '%Y-%m-%d %H:%M'
#LongYMDH , LongYMDHMS = '%Y-%m-%d %H', '%Y-%m-%d %H:%M:%S'

MD       , MDH, MDHM  = '%m%d'       , '%m%d%H', '%m%d%H%M'
YMD      , YMDHM      = '%Y%m%d'     , '%Y%m%d%H%M'
YMDH     , YMDHMS     = '%Y%m%d%H'   , '%Y%m%d%H%M%S'
DashYMD  , DashYMDHM  = '%Y-%m-%d'   , '%Y-%m-%d %H:%M'
DashYMDH , DashYMDHMS = '%Y-%m-%d %H', '%Y-%m-%d %H:%M:%S'
SlashMDY , SlashMDYHM = '%m/%d/%Y'   , '%m/%d/%Y %H:%M'
SlashMDYH, SlashMDYHMS= '%m/%d/%Y %H', '%m/%d/%Y %H:%M:%S'
ColonHMS , HMS        = '%H:%M:%S'   , '%H%M%S'

def NowUnix():
  return time.time()
def NowYMD():
  return time.strftime(YMD)      # = '20151115'
def NowYMDH():
  return time.strftime(YMDH)
def NowYMDHM():
  return time.strftime(YMDHM)
def NowYMDHMS():
  return time.strftime(YMDHMS)
def NowDashYMD():
  return time.strftime(DashYMD)      # = '20151115'
def NowDashYMDH():
  return time.strftime(DashYMDH)
def NowDashYMDHM():
  return time.strftime(DashYMDHM)  #= datetime.now().strftime('%Y-%m-%d %H:%M')
def NowDashYMDHMS():
  return time.strftime(DashYMDHMS)
def NowColonHMS():
  return time.strftime(ColonHMS)
def NowHMS():
  return time.strftime(HMS)

def DotNowYMDHM():
  return '.'+ NowYMDHM()

#StaticYMDHM = NowYMDHM()
#DotYMDHM    = '.'+ StaticYMDHM
#NowYMDSlashHM= time.strftime("%Y%m%d/%H%M")

def DtMD(Dt):
  return datetime.strftime(Dt, MD)

AddSleepSec = 0
SleepMaxSec = 3

# set DtMin to datetime.min + 1 day so To prevent from OverflowError when
#    converting datetime.min to timezone w/ negative number of hours
DtMin = datetime(1,1,2,0,0)  # =datetime.min +1day, else err convert tz -n hr
# datetime.min = datetime(1,1,1,0,0)
# >>> UtcToDt( datetime.min, 'US/Pacific')
# OverflowError: date value out of range
# >>> UtcToDt( DtMin, 'US/Pacific')
# datetime.datetime(1, 1, 1, 16, 7, tzinfo=<DstTzInfo 'US/Pacific' LMT-1 day, 16:07:00 STD>)

UnixMin = datetime.utcfromtimestamp(0)     # = datetime(1970, 1, 1, 0, 0)
#= datetime.strptime('1/1/1970', SlashMDY)

# sec.gov/edgar/searchedgar/ftpusers.htm
# bulk FTP transfer requests be performed between 9 PM and 6 AM Eastern time

# ubuntuforums.org/showthread.php?t=403715  py static var within func like c
#PcPrev=[]= Mutable default argument retrain its state between functional calls
#           work much like global var, but local scope
def SleepSec(PcPrev = [0], Tz='ET'):
  " Only sleep max SleepMaxSec secs,  ET = EST or EDT "
  d    = datetime.now()
  Now  = time.perf_counter()
  Prev = PcPrev[0]
  PcPrev[0] = Now #if Prev==0: Prev=Now #no need to sleep=0 at the 1st time
  if Tz == 'ET' and d.isoweekday() in range(1,6) and d.hour > 3 and d.hour < 18:
    DeltaSec = Now - Prev   #(d - d_Prev).total_seconds()
    # Only sleep max SleepMaxSec secs
    return (SleepMaxSec - DeltaSec) if DeltaSec < SleepMaxSec else 0
  else:
    return 0   #sleep(sec): sec can be floating point number

#def SleepSeconds():
#  d = datetime.now()
#  #Today8am = d.replace(hour=4, minute=0, second=1, microsecond=0)
#  #d = Today8am  # print(Today8am)
#  #if d.isoweekday() in range(1, 6) and d.hour not in range(4, 18):
#  if  d.isoweekday() in range(1, 6) and d.hour > 3 and d.hour < 18:
#    return SleepMaxSec   #if M~F, 4am PST = 7am EST < Now < 6pm PST = 9pm EST
#  else: return 0

def Sleep(Seconds=1, Tz='ET', BizHourSleep=True, Msg=None):
  Sec = Seconds + (SleepSec(Tz=Tz) if BizHourSleep else 0) + AddSleepSec
  if Msg is not None:
    print(Msg, 'Sleep', Sec)
  time.sleep(Sec)


# stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
# Since Python 3 timedelta supports multiplication with floats
def GenRandomPriorDatetime(StartDate = '2015-1-1'):
  start = datetime.strptime(StartDate, '%Y-%m-%d')
  end   = datetime.now()
  return start + (end - start) * random()


def GetNumDaysBetween2Dates(Dt1, Dt2):
  Delta = Dt1 - Dt2
  return Delta.days

def GetNumDaysBeforeToday(Dt):
  return GetNumDaysBetween2Dates(datetime.now(), Dt)


def DtToUtc(Dt, TzStr=None):
  ''' Convert datetime Dt.tzinfo to GMT=UTC time, using pytz.sourceforge.net
  except if: (H,M,S) == (0,0,0): return the same with tzinfo=<UTC>
             Dt.tzinfo == pytz.utc. Return as is.
             Dt.tzinfo != None and != pytz.utc. Convert tz to UTC
  params: Dt = datetime obj
         TzStr = cHO.DC0000 ==> 'US/Pacific' = default
  #class WordPressPost(WordPressBase):
  #  definition = {
  #    'date': DateTimeFieldMap('post_date_gmt'),  #<<== xmlrpc expects GMT!!

  [check if dt obj is localized w/ pytz?](stackoverflow.com/questions/5802108)
      if PostDate.tzinfo is None:
  '''
  print("DtToUtc params: Dt={}, Local Timezone={}".format(Dt,TzStr))
  if Dt.tzinfo is not None:
    if Dt.tzinfo is pytz.utc:
      print("  Dt.tzinfo is already pytz.utc. Return as is.")
      return Dt
    UtcDt = Dt.astimezone(pytz.utc)
    print("  Dt.tzinfo is not None and !=pytz.utc. Convert tz to UTC=", UtcDt)
    return UtcDt                    #=datetime(2016, 10, 18,0,0, tzinfo=<UTC>)
  if (Dt.hour, Dt.minute, Dt.second) == (0, 0, 0):
    UtcDt = pytz.utc.localize(Dt) #=datetime(2016, 10, 18, 0, 0, tzinfo=<UTC>)
    print("  No need to convert time as time=0:0:0. Set tz to UTC=", UtcDt)
    return UtcDt
  if TzStr is None:
    tz = WebHostTz()
    print("  TzStr is None. Get tz = WebHostTz() =", tz)
  else:
    #tz= pytz.timezone(GetTimeZoneByTzStr(TzStr))
    tz = GetPytzTimeZoneByTzStr(TzStr)
    print("  TzStr is not None."
          "  Convert tz = GetPytzTimeZoneByTzStr(TzStr) =", tz)
  #UtcDt = PytzTimeZone(TzStr).localize(Dt).astimezone(pytz.utc)
  UtcDt  = tz.localize(Dt).astimezone(pytz.utc)
  print("  Dt.tzinfo is None. Convert tz to UtcDt=", UtcDt)
  return UtcDt                  #= datetime(2016, 10, 18, 2, 11, tzinfo=<UTC>)


def GetTzStrByDcNum(DcNum):
  import config.host as cHO
  for tzStr, DcNums in cHO.DcTimeZones.items():
    if DcNum in DcNums:
      return tzStr
  raise ValueError('GetTzStrByDcNum got unknown DcNum= '+ DcNum)

def GetUtcOffsetFromTz(TzStr= DefaultTimeZoneStr):
  TzNow = datetime.now(pytz.timezone(TzStr))
  return TzNow.utcoffset().total_seconds()/3600

def GetPytzTimeZoneByTzStr(TzStr, DefaultTzStr=DefaultTimeZoneStr):
  " Exception Returns: <DstTzInfo 'US/Pacific'...> "
  try:    return pytz.timezone(TzStr    )
  except: return pytz.timezone(DefaultTzStr)

def GetPytzTimeZoneByDcNum(DcNum, DefaultTzStr=DefaultTimeZoneStr):
  " Exception Returns: <DstTzInfo 'US/Pacific'...> "
  try:    return pytz.timezone(GetTzStrByDcNum(DcNum))
  except: return pytz.timezone(DefaultTzStr         )

def WebHostTz(DefaultDcNum = None):
  import wp.conf      as WpC
  try:    return GetPytzTimeZoneByDcNum( WpC.WB.Wj.Bj.WH0.DcNum )
  except:
    try:
      import config.host as cHO
      if DefaultDcNum is None:
        DefaultDcNum = cHO.DC0000
      return GetPytzTimeZoneByDcNum( DefaultDcNum )
    except: return GetPytzTimeZoneByDcNum( '' )

def LocalSysTz():
  "[Convert UTC datetime str to local dt]stackoverflow.com/questions/4770297/"
  "return <UTC> for vt2hp, not 'US/Pacific' !!! "
  import tzlocal   # sudo python3 -m pip install pytz  tzlocal
  return tzlocal.get_localzone() # get pytz tzinfo

def LocalTz():
  import config.host as cHO
  return GetPytzTimeZoneByDcNum( cHO.LocHostDcNum )

def UtcTz():
  return pytz.utc


#WrongDt = P.date_gmt.replace(tzinfo = wTm.pytz.timezone('Asia/Hong_Kong'))
## datetime.datetime(2018, 3, 20, 20, 56, tzinfo=<DstTzInfo 'Asia/Hong_Kong' LMT+7:37:00 STD>)
#date_cn = WrongDt.astimezone(wTm.pytz.utc)
##  datetime.datetime(2018, 3, 20, 13, 19, tzinfo=<UTC>)

# Above Wrong! [dt obj show wrong timezone offset](stackoverflow.com/questions/6410971)  Below to correct:

#tz = wTm.pytz.timezone('Asia/Hong_Kong')
#WrongDt = tz.localize( wTm.datetime(2018,3,20,20,56,00))
##       = datetime.datetime(2018, 3, 20, 20, 56, tzinfo=<DstTzInfo 'Asia/Hong_Kong' HKT+8:00:00 STD>)
#date_cn = WrongDt.astimezone(wTm.pytz.utc)
##       = datetime.datetime(2018, 3, 20, 12, 56, tzinfo=<UTC>)

# [dt obj show wrong timezone offset](stackoverflow.com/questions/6410971)
# official pytz website states that you should always use localize or astimezone instead of passing a timezone object to datetime.datetime.

def DtToLocalSysTz(Dt):
  if not isinstance(Dt, datetime):
    raise TypeError('expects datetime, but got {}'.format(Dt))
  #return Dt.replace(tzinfo=LocalSysTz())
  return LocalSysTz().localize(Dt)

def SetDtToWebHostTz(Dt):
  if not isinstance(Dt, datetime):
    raise TypeError('expects datetime, but got {}'.format(Dt))
  #return Dt.replace(tzinfo=WebHostTz())
  return WebHostTz().localize(Dt)

def SetDtToUtc(Dt):           # Utc = Gmt
  if not isinstance(Dt, datetime):
    raise TypeError('expects datetime, but got {}'.format(Dt))
  #Below: ValueError('Not naive datetime (tzinfo is already set)')
  #return pytz.utc.localize(Dt)
  return Dt.replace(tzinfo=pytz.utc)

def UtcToDt(UtcDt, NewTzStr):    # Utc = Gmt
  if not isinstance(UtcDt, datetime):
    raise TypeError('expects datetime, but got {}'.format(UtcDt))
  #return Dt.replace(tzinfo=NewTzStr)

  NewPytzTz = GetPytzTimeZoneByTzStr(NewTzStr)
  #Below: ValueError('Not naive datetime (tzinfo is already set)')
  #return pytz.utc.localize(UtcDt).astimezone(NewPytzTz)
  return UtcDt.replace(tzinfo=pytz.utc).astimezone(NewPytzTz)

def DtNowWithLocalSysTz():
  #return datetime.now().replace(tzinfo=LocalSysTz())
  return DtToLocalSysTz(datetime.utcnow())
def DtNowInLocalSysTzWithMicroSec():
  " same as DtNowWithLocalSysTz "
  return datetime.now(LocalSysTz())
def DtNowInLocalSysTz():
  return datetime.now(LocalSysTz()).replace(microsecond=0)
def DtNowInLocalTzWithMicroSec():
  return datetime.now(LocalTz())
def DtNowInLocalTz():
  return datetime.now(LocalTz()).replace(microsecond=0)

def UtcNowInUtcTz():
  " equals DtNowWithLocalSysTz() if LocalSysTz = UTC "
  " use datetime.utcnow() (stackoverflow.com/questions/15307623/) "
  return SetDtToUtc( datetime.utcnow() )
def DtNowInUtcTz():
  " same as UtcNowInUtcTz "
  return datetime.now(UtcTz())
UtcNow = DtNowInUtcTz

def DtNowInWebHostTz():
  return datetime.now(WebHostTz())


def IsDstNow(TzStr= DefaultTimeZoneStr):
  '''[find if timezone currently in daylight savings time]
     (stackoverflow.com/questions/19774709/)
  1Line =lambda TzStr: bool(datetime.now(pytz.timezone(TzStr)).dst())'''
  return bool(datetime.now(pytz.timezone(TzStr)).dst())

#IsDstNow("America/Los_Angeles")
#IsDstNow("Europe/London")

def NonDstPlusOneHour(LocalTz= DefaultTimeZoneStr):
  return 0 if IsDstNow(LocalTz) else 1

def Today():
  return datetime.today().date()

def IsDtEqToday(Dt):
  "[check if date is same day as datetime.today()](stackoverflow.com/questions/6407362/) "
  return Dt.date() == Today()
def IsDtBeforeToday(Dt):
  return Dt.date() < Today()

# wTm.DtCompareToday(wTm.datetime.now() + timedelta(1), '>')  # Out[27]: True
def DtCompareToday(Dt, Op='=='):
  if Op == '<':
    return Dt.date() <  Today()
  if Op == '<=':
    return Dt.date() <= Today()
  if Op == '>=':
    return Dt.date() >= Today()
  if Op == '>':
    return Dt.date() >  Today()
  return   Dt.date() == Today()

# for tz in pytz.all_timezones:
#   if tz.startswith('US'):
#     print(tz)
# US/Alaska
# US/Aleutian
# US/Arizona
# US/Central
# US/East-Indiana
# US/Eastern
# US/Hawaii
# US/Indiana-Starke
# US/Michigan
# US/Mountain
# US/Pacific
# US/Pacific-New
# US/Samoa


def GuessDatetimeFromMMDD(MMDashDD):
  ''' if Now= 2017-1-20 and MMDashDD = 2-29 (meaning 2016-2-29),
  the following will produce 2017-2-29, which is bad!
     DateStr= str(datetime.now().year)+'-'+ MMDashDD
     Date   = datetime.strptime( DateStr, '%Y-%m-%d' )
  So here guess and return YearNow - 1 or 2, given only MMDashDD
  '''
  Now = datetime.now()   # or datetime.today()
  YearNow, MonthNow, DateNow = Now.year, Now.month, Now.day
  MonthStr, DateStr = MMDashDD.split('-')
  MonthInt, DateInt = int(MonthStr), int(DateStr)
  if ( (MonthInt == MonthNow and DateInt > (DateNow + 1)) # +1 day for Cn time
       or (MonthInt >  MonthNow) ):
    YearInt = YearNow - 1
  else:
    YearInt = YearNow
  try:    return datetime(YearInt    , MonthInt, DateInt)
  except: return datetime(YearInt - 1, MonthInt, DateInt) # avoid 2017-2-29



def StructTimeToUnixTime(StructTime):
  '  structTime = time.localtime() '
  return time.mktime(StructTime)

def UnixTimeToDatetime(UnixTime):
  return datetime.fromtimestamp(UnixTime)

def StructTimeToDatetime(StructTime):
  ''' [convert time.struct_time obj to datetime]
      (stackoverflow.com/questions/1697815)
  '''
  return UnixTimeToDatetime(StructTimeToUnixTime(StructTime))  # same as:
  #datetime.datetime(*StructTime[:6]) #Out:datetime.datetime(2009,11,8,20,32,35)


def FillYearWithZeros(Str):
  if '-' not in Str:
    return Str
  Str1 = Str.split('-')[0]
  LenStr1 = len(Str1)
  if not Str1.isdigit(): raise
  if LenStr1 > 4:        raise   # len 0 or ''.isdigit() == False
  if LenStr1 < 4:
    return Str1.zfill(4) + Str[LenStr1:]  # Change 1 to 0001 Year.
  return Str


def Str2Date(Str, Format=None):
  '''[remove unconverted data from dt obj](stackoverflow.com/questions/5045210)
    >>> Str = '2017-09-04 05:38:14.549233+00:00'
    >>> try: datetime.strptime(Str, DashYMDHMS)
    ... except ValueError as Err:  print(Err.args)
    ('unconverted data remains: .549233+00:00',)
  '''
  Str = Str.strip()
  LenStr = len(Str)

  try:
    if isinstance(Format, str):
      if Format[:3] == '%Y-' and '-' in Str:
        Str = FillYearWithZeros(Str)
      #ValueError: time data '1-01-02 00:00:00'
      #    does not match format '%Y-%m-%d %H:%M:%S'
      return datetime.strptime(Str, Format)

    elif Str.isdigit():
      if 6 <= LenStr <=  8:                   #= 20181231, 201211, 2012112
        return datetime.strptime(Str, YMD)    #= '%Y%m%d'
      if LenStr ==  10:                       #= 2018123112
        return datetime.strptime(Str, YMDH)   #= '%Y%m%d%H'
      if LenStr ==  12:                       #= 201812311259
        return datetime.strptime(Str, YMDHM)  #= '%Y%m%d%H%M'
      if LenStr ==  14:                       #= 20181231125945
        return datetime.strptime(Str, YMDHMS) #= '%Y%m%d%H%M%S'

    elif ' ' in Str:
      if ':' in Str:
        ColSplits = Str.split(':')
        if len(ColSplits) == 2:
          if '-' in Str:                               #= 2018-12-31 12:59
            Str = FillYearWithZeros(Str)
            return datetime.strptime(Str, DashYMDHM)   #= '%Y-%m-%d %H:%M'
          if '/' in Str:                               #= 12/31/2018 12:59
            return datetime.strptime(Str, SlashMDYHM)  #= '%m/%d/%Y %H:%M'
        elif len(ColSplits) >= 3:
          if '-' in Str:                               #= 2018-12-31 12:59:45
            Str = FillYearWithZeros(Str)
            return datetime.strptime(Str, DashYMDHMS)  #= '%Y-%m-%d %H:%M:%S'
          if '/' in Str:                               #= 12/31/2018 12:59:45
            return datetime.strptime(Str, SlashMDYHMS) #= '%m/%d/%Y %H:%M:%S'
      else:   # No ':' in Str:
          if '-' in Str:                               #= 2018-12-31 12
            Str = FillYearWithZeros(Str)
            return datetime.strptime(Str, DashYMDH)    #= '%Y-%m-%d %H'
          if '/' in Str:                               #= 12/31/2018 12
            return datetime.strptime(Str, SlashMDYH)   #= '%m/%d/%Y %H'

    else:  # Str no digits and no ' ' in Str
      if 8 <= LenStr <= 10:   # 2000-1-1, 12/12/2012
        if '-' in Str:                                 #= 2018-12-31
          Str = FillYearWithZeros(Str)
          return datetime.strptime(Str, DashYMD)       #= '%Y-%m-%d'
        if '/' in Str:                                 #= 12/31/2018
          return datetime.strptime(Str, SlashMDY)      #= '%m/%d/%Y'

  except ValueError as Err:
    # '2017-09-04 05:38:14.549233+00:00'
    # below: ValueError: unconverted data remains: .549233
    #a.NewsXAttrs['post_date_gmt'].split('+')[0]   #or: ['post_date_gmt'][:19]
    ErrMsgPfx    = 'unconverted data remains: '
    LenErrMsgPfx = 26  # = len(ErrMsgPfx)
    if len(Err.args) > 0 and Err.args[0][:LenErrMsgPfx] == ErrMsgPfx:
      Str = Str[:-(len(Err.args[0]) - LenErrMsgPfx)]
      return Str2Date(Str, Format)
    #else: raise
  except:
    import sys, pyx.func as xFn
    xFn.PrintError(sys.exc_info(), 1, 'Str2Date Error!')

  print("Cannot parse datetime from '{}'! Return UnixMin datetime".format(Str))
  return UnixMin


# Str2Date( '2015-10-15 11:33:20.738 45162 INFO core.api.wsgi yadda yadda.', DashYMDHMS)
#-> time.struct_time(tm_year=2015, tm_mon=10, tm_mday=15, tm_hour=11, tm_min=33, ...


import time, sys
import collections


LogFilePfx = '' # In wpy.web_deploy, set to: 'web_deploy/'+ 'wpy.' #self.Site


class RedirectOutput:
  """context manager for reditrecting stdout/err to files
  [redirect py output to file (bash >)](stackoverflow.com/questions/14571090/)
  use:  with RedirectOutput(FilePfx = 'my.'):
          print(123)
  %load_ext autoreload
  Mode: default to 'a' = append to existing file, 'w' = write to new file
  """
  def __init__(self, StdOut=None, StdErr=None, Mode='a', FilePfx='',
               NewFilePerEntry=False):
    "wTm.StaticYMDHM is static upon py init, time is dynamic, so filename incr"
    self.FilePfx= FilePfx
    self.NewFilePerEntry = NewFilePerEntry
    self.StdOut = (self.GetLogFilePath() if NewFilePerEntry or StdOut is None
                   else StdOut)
    self.StdErr = StdErr or self.StdOut
    self.Mode   = Mode

  def GetLogFilePath(self):
    import wpy.time as wTm                       # or: + wTm.NowYMDHM()
    return '/fs/log/py/'+ (LogFilePfx or self.FilePfx) + wTm.NowYMDHMS()

  def __enter__(self):
    self.sys_stdout = sys.stdout
    self.sys_stderr = sys.stderr

    #if self.StdOut:
    sys.stdout = open(self.GetLogFilePath() if self.NewFilePerEntry
                                            else self.StdOut       , self.Mode)
    #if self.StdErr:
    if self.StdErr == self.StdOut:
      sys.stderr = sys.stdout
    else:
      sys.stderr = open(self.StdErr, self.Mode)

  #def __exit__(self, exc_type, exc_value, traceback):
  #follow docs.python.org/3/library/contextlib.html#contextlib.ContextDecorator
  def  __exit__(self, *exc):
    sys.stdout = self.sys_stdout
    sys.stderr = self.sys_stderr


class RedirectOutputDctr(RedirectOutput):
  """ @RedirectOutputDctr(FilePfx='web_deploy/wordpy.')
  [Func act as decorator & context manager](stackoverflow.com/questions/9213600)
  """
  def __init__(self, *args, RedirectOn=True, **kwargs):
    '[toggling decorators](stackoverflow.com/questions/14636350/)'
    RedirectOutput.__init__(self, *args, **kwargs)
    self.RedirectOn = RedirectOn
  def __enter__(self):
    RedirectOutput.__enter__(self)
  def __exit__(self, *exc):
    RedirectOutput.__exit__(self, *exc)
  def __call__(self, func):
    '[class method decorator w/ self args](stackoverflow.com/questions/11731136'
    if not self.RedirectOn:
      return func
    def wrapper(*args, **kwargs):
      with self:
        return func(*args, **kwargs)
    return wrapper


#from contextlib import ContextDecorator
#
#class RedirectOutputContextDecorator(RedirectOutput, ContextDecorator):
#  """ @RedirectOutputContextDecorator(FilePfx='web_deploy/wordpy.')
#  docs.python.org/3/library/contextlib.html#contextlib.ContextDecorator
#  github.com/python/cpython/blob/3.6/Lib/contextlib.py
#  """
#  def __init__(self, *args, **kwargs):
#     RedirectOutput.__init__(self, *args, **kwargs)
#  def __enter__(self):
#     RedirectOutput.__enter__(self)
#  def __exit__(self, *exc):
#     RedirectOutput.__exit__(self, *exc)
#



# [Attach decorator to all class methods](stackoverflow.com/questions/3467526#43434925
# metaclasses are the most pythonic way to go when you want to modify the way that python creates objects. It can be done by overriding the __new__ method of your class. Notes (specially for py 3.X):
#     types.FunctionType doesn't protect the special methods from being decorated, as they are function types. As a more general way you can just decorate the objects which their names are not started with double underscore (__). One other benefit of this method is that it also covers those objects that exist in namespace and starts with __ but are not function like __qualname__, __module__ , etc.
#     The namespace argument in __new__'s header doesn't contain class attributes within the __init__. The reason is that the __new__ executes before the __init__ (initializing).
#     It's not necessary to use a classmethod as the decorator, as in most of the times you import your decorator from another module.
#     If your class is contain a global item (out side of the __init__) for refusing of being decorated alongside checking if the name is not started with __ you can check the type with types.FunctionType to be sure that you're not decorating a non-function object.

def MyDecorator(func):
  def wrapper(self, *arg, **kwargs):
    # You can also use *args instead of (self, arg) and pass the *args
    # to the function in following call.
    ClsMethodResult = func(self, *arg, **kwargs)
    return "  value {} gets modified!!".format(ClsMethodResult)
  return wrapper

#[functions type in python3](https://stackoverflow.com/questions/32021996/)
import types

class MyMetaCls(type):
  ''' [Attach decorator to all class methods]
  (stackoverflow.com/questions/3467526#43434925
  special method not decorated: k.startswith('__')
  '''
  def __new__(cls, name, bases, namespace, **kwds):
    ''' MyDecorator = cls.MyDecorator (if the decorator is a classmethod)
    '''
    namespace= { k: v if k.startswith('__')    # or k == '__init__'
                         or  not isinstance(v, collections.Callable) #for >py3.2
                         #or not isinstance(v, types.FunctionType)   #ok too!
                      else MyDecorator(v) for k, v in namespace.items()}
    return type.__new__(cls, name, bases, namespace)

class MyClass(metaclass=MyMetaCls):
  a = 10  #MyInstance.a returns: <bound method MyDecorator.<locals>.wrapper of 
  #                                <MyClass object at 0x...>>
  def __init__(self, *args, **kwargs):
    self.item = args[0]
    self.value = kwargs['value']
  def __getattr__(self, attr):
    return "MyClass hasn't provide attr {}.".format(attr)
  def MyFunc1(self, arg):
    return arg ** 2
  def MyFunc2(self, arg):
    return arg ** 3

MyInstance = MyClass(1, 2, value=100)
# MyInstance.MyFunc1(5) #Out: value 25 gets modified!!
# MyInstance.MyFunc2(2) #Out: value 8 gets modified!!
# MyInstance.item       #Out: 1
# MyInstance.p #Out: MyClass hasn't provide attr p # special method not decorated
# 
# uncomment line 'a = 10' and 'MyInstance.a' returns:
#   Out: <bound method MyDecorator.<locals>.wrapper of <MyClass object at 0x...>>
# change dict comprehension in __new__ as follows then see the result again:
#     namespace = { k: v if k.startswith('__') and
#                           not isinstance(v, types.FunctionType)
#                        else MyDecorator(v) for k, v in namespace.items()}
# Out: --> 128 MyInstance = MyClass(1, 2, value=100)
# Out: TypeError: __init__() should return None, not 'str'




# [How to decorate all methods of a class](stackoverflow.com/questions/6307761/)
#
#Decorate class with a function that walks through the class's attributes and decorates callables. This may be the wrong thing to do if you have class variables that may happen to be callable, and will also decorate nested classes (credits to Sven Marnach for pointing this out) but generally it's a rather clean and simple solution. Example implementation (note that this will not exclude special methods (__init__ etc.), which may or may not be desired):
#
#Q: why not use inspect.getmembers(cls, inspect.ismethod) instead of __dict__ and callable() ? of course static method will be out of the question in this case.
#A: In Python 3 inspect.getmembers(cls, inspect.ismethod) won't work because inspect.ismethod returns False for unbound methods. In Python 2 inspect.ismethod returns True for unbound methods but inspect.isfunction returns False. Maybe it's best to write inspect.getmembers(cls, inspect.isroutine) instead as that works for both. 

def DecorateAllClassMethods(decorator, UseDecorator=True):
  def Decorate(cls):
    if not UseDecorator:
      return cls
    for attr in cls.__dict__: # there's propably a better way to do this
      # if callable(getattr(cls, attr)): #callable does not exist in py 3.0 & 3.1
      if ( isinstance(getattr(cls, attr), collections.Callable)  #for py 3.2+
           and not attr.startswith('__') ):
        setattr(cls, attr, decorator(getattr(cls, attr)))
    return cls
  return Decorate

#Use like this:
#@DecorateAllClassMethods(mydecorator)
#class C(object):
#  def m1(self): pass
#  def m2(self, x): pass

@DecorateAllClassMethods(MyDecorator)
class MyClassA:
  a = 10  #MyInstance.a returns: <bound method MyDecorator.<locals>.wrapper of 
  #                               <MyClassA object at 0x...>>
  def __init__(self, *args, **kwargs):
    self.item = args[0]
    self.value = kwargs['value']
  def __getattr__(self, attr):
    return "MyClassA hasn't provide attr {}.".format(attr)
  def MyFunc1(self, arg):
    return arg ** 2
  def MyFunc2(self, arg):
    return arg ** 3

MyInstanceA = MyClassA(1, 2, value=100)

string_types = (str,)

# ~/.pyenv/versions/py3/lib/python3.6/site-packages/flask/config.py
class Config(dict):
  """Works exactly like a dict but provides ways to fill it from files
  or special dictionaries.
  you can define the configuration options in the
  module that calls :meth:`from_object` or provide an import path to
  a module that should be loaded.  It is also possible to tell it to
  use the same module and with that provide the configuration values
  just before the call::

      DEBUG = True
      SECRET_KEY = 'development key'
      app.config.from_object(__name__)

  In both cases (loading from any Python file or loading from modules),
  only uppercase keys are added to the config.  This makes it possible to use
  lowercase values in the config file for temporary values that are not added
  to the config or to define the config keys in the same file that implements
  the application.

  :param defaults: an optional dictionary of default values
  """

  #def __init__(self, root_path, defaults=None):
  def  __init__(self, obj= None, defaults=None):  #, **kwargs):
    dict.__init__(self, defaults or {})
    #self.root_path = root_path
    if obj:
      self.from_object(obj)
    #Instead of below, use: Config(defaults={'DB_DIALECT':'mysql',})
    #for k,v in kwargs.items():#VT Added to allow kwargs ini values
    #    if k.isupper():
    #        self[k] = v

  def from_object(self, obj):
    """Updates the values from the given object.  An object can be of one
    of the following two types:

    -   a string: in this case the object with that name will be imported
    -   an actual object reference: that object is used directly

    Objects are usually either modules or classes. :meth:`from_object`
    loads only the uppercase attributes of the module/class. A ``dict``
    object will not work with :meth:`from_object` because the keys of a
    ``dict`` are not attributes of the ``dict`` class.

    Example of module-based configuration::

        app.config.from_object('yourapplication.default_config')
        from yourapplication import default_config
        app.config.from_object(default_config)

    You should not use this function to load the actual configuration but
    rather configuration defaults.  The actual config should be loaded
    with :meth:`from_pyfile` and ideally from a location not within the
    package because the package might be installed system wide.

    See :ref:`config-dev-prod` for an example of class-based configuration
    using :meth:`from_object`.

    :param obj: an import name or object
    """
    if isinstance(obj, string_types):
      from   werkzeug.utils import import_string
      obj = import_string(obj)
    for key in dir(obj):
      if key.isupper():
        self[key] = getattr(obj, key)

  def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
    """Returns a dictionary containing a subset of configuration options
    that match the specified namespace/prefix. Example usage::

        app.config['IMAGE_STORE_TYPE'] = 'fs'
        app.config['IMAGE_STORE_PATH'] = '/var/app/images'
        app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
        image_store_config = app.config.get_namespace('IMAGE_STORE_')

    The resulting dictionary `image_store_config` would look like::

        {
            'type': 'fs',
            'path': '/var/app/images',
            'base_url': 'http://img.website.com'
        }

    This is often useful when configuration options map directly to
    keyword arguments in functions or class constructors.

    :param namespace: a configuration namespace
    :param lowercase: a flag indicating if the keys of the resulting
                      dictionary should be lowercase
    :param trim_namespace: a flag indicating if the keys of the resulting
                      dictionary should not include the namespace

    .. versionadded:: 0.11
    """
    rv = {}
    #~/.pyenv/versions/py3/lib/python3.6/site-packages/flask/_compat.py
    #py3: iteritems = lambda d: iter(d.items())
    #py2: iteritems = lambda d: d.iteritems()
    #for k, v in iteritems(self):
    for  k, v in self.items():
      if not k.startswith(namespace):
        continue
      if trim_namespace:
        key = k[len(namespace):]
      else:
        key = k
      if lowercase:
        key = key.lower()
      rv[key] = v
    return rv

  def __repr__(self):
    return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))





class BaseConfC:
  DEBUG   = False   # Default: True if ENV is 'development', or False otherwise.
  TESTING = False   # Default: False
  # Enable testing mode. Exceptions are propagated rather than handled by the the app’s error handlers. Extensions may also change their behavior to facilitate easier testing. You should enable this in your own tests.

  SQL_ISOLATION_LEVEL = 'SERIALIZABLE'
  SQL_ECHO_POOL = False
  SQL_CONVERT_UNICODE = True
  SQL_AUTOCOMMIT = False
  SQL_AUTOFLUSH = True
  # expire_on_commit – Defaults to True. When True, all instances will be fully expired after each commit(), so that all attribute/object access subsequent to a completed transaction will load from the most recent database state.
  #SQL_EXPIRE_ON_COMMIT = True
  SQL_EXPIRE_ON_COMMIT = False


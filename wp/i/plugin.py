# Need to implement pointer!!!
#from  wp.conf import WB  # can't use WB here, since WpC.WB was init to None
#                         #   before end of wpy.web: WpC.WB = WB = WpBlogCls()
import wp.conf     as WpC
import pyx.php     as Php
import wp.i.func   as WiFc
array = Php.array


# The following is from /fs/web/wp.4.6.1 , not latest wp.4.7.1, so to avoid:
#   $wp_filter = WP_Hook::build_preinitialized_hooks( $wp_filter );

#The plugin API is located in this file, which allows for creating actions
#and filters and hooking functions, and methods. The functions or methods will
#then be run when the action or filter is called.
#The API callback examples reference functions, but can be methods of classes.
#To hook methods, you'll need to pass an array one of two ways.
#Any of the syntaxes explained in the PHP documentation for the
#{@link https://secure.php.net/manual/en/language.pseudo-types.php#language.types.callback 'callback'}
#type are valid.
#Also see the {@link https://codex.wordpress.org/Plugin_API Plugin API} for
#more information and examples on how to use a lot of these functions.
#This file should have no external dependencies.
#@package WordPress
#@subpackage Plugin

#def InitFilterGlobals(self):
#  ''' Initialize the filter globals. Call from wp.settings. self = WB.Wj
#  global var==>self.var, except: var=self.var=same Obj,mutable array
#  global var in the rest of this module is assigned to the same mutable obj
#  '''
#  #global wp_filter, wp_actions, merged_filters, wp_current_filter
#  
#  if not isinstance(getattr(self, 'wp_filter',        None), array):
#    self.wp_filter  = array()  # array()
#  if not isinstance(getattr(self, 'wp_actions',       None), array):
#    self.wp_actions = array()  # array()
#  if not isinstance(getattr(self, 'merged_filters',   None), array):
#    self.merged_filters = array()  # array()
#  if not isinstance(getattr(self, 'wp_current_filter',None), list ):
#    self.wp_current_filter = array()
#  #wp_filter         = self.wp_filter      #assign to the same mutable array()
#  #wp_actions        = self.wp_actions     #assign to the same mutable array()
#  #merged_filters    = self.merged_filters #assign to the same mutable array()
#  #wp_current_filter = self.wp_current_filter #assign to the same mutable list


# Add Wj, since in wp.i.default_filters, WB.Wj was not initialized yet
#def add_filter(tag, function_to_add, priority =10, accepted_args =1 ):
def add_filter( tag, function_to_add, priority =10, accepted_args =1, Wj=None ):
  ''' Hook a function or method to a specific filter action.
  WordPress offers filter hooks to allow plugins to modify
  various types of internal data at runtime.
  A plugin can modify data by binding a callback to a filter hook. When the filter
  is later applied, each bound callback is run in order of priority, and given
  the opportunity to modify a value by returning a new value.
  The following example shows how a callback function is bound to a filter hook.
  Note that `example` is passed to the callback, (maybe) modified, then returned:
      function example_callback( example ) {
          # Maybe modify example in some way.
          return example
      }
      add_filter( 'example_filter', 'example_callback' )

  Bound callbacks can accept from none to the total number of arguments passed as parameters
  in the corresponding apply_filters() call.
  In other words, if an apply_filters() call passes four total arguments, callbacks bound to
  it can accept none (the same as 1) of the arguments or up to four. The important part is that
  the `accepted_args` value must reflect the number of arguments the bound callback *actually*
  opted to accept. If no arguments were accepted by the callback that is considered to be the
  same as accepting 1 argument. For example:
      # Filter call.
      value = apply_filters( 'hook', value, arg2, arg3 )
      # Accepting zero/one arguments.
      function example_callback() {
          ...
          return 'some value'
      }
      add_filter( 'hook', 'example_callback' ); # Where priority is default 10, accepted_args is default 1.
      # Accepting two arguments (three possible).
      function example_callback( value, arg2 ) {
          ...
          return maybe_modified_value
      }
      add_filter( 'hook', 'example_callback', 10, 2 ); # Where priority is 10, accepted_args is 2.

  *Note:* The function will return True whether or not the callback is valid.
  It is up to you to take care. This is done for optimization purposes, so
  everything is as quick as possible.
  @global array wp_filter      A multidimensional array of all hooks and the callbacks hooked to them.
  @global array merged_filters Tracks the tags that need to be merged for later. If the hook is added,
                                it doesn't need to run through that process.
  @param string   tag             The name of the filter to hook the function_to_add callback to.
  @param callable function_to_add The callback to be run when the filter is applied.
  @param int      priority        Optional. Used to specify the order in which the functions
                                   associated with a particular action are executed. Default 10.
                                   Lower numbers correspond with earlier execution,
                                   and functions with the same priority are executed
                                   in the order in which they were added to the action.
  @param int      accepted_args   Optional. The number of arguments the function accepts. Default 1.
  @return True
  '''
  #global var==>WB.Wj.var, except: var=WB.Wj.var=same Obj,mutable array
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_filter = Wj.wp_filter  # global wp_filter
  merged_filters = Wj.merged_filters  # global merged_filters

  #idx= _wp_filter_build_unique_id(tag, function_to_add, priority)
  idx = _wp_filter_build_unique_id(tag, function_to_add, priority, Wj=Wj)
  if tag not in wp_filter:
    wp_filter[tag]           = array()     # need to init array for py
  if priority not in wp_filter[tag]:
    wp_filter[tag][priority] = array()     # need to init array for py
    
  wp_filter[tag][priority][idx] = array(('function'     , function_to_add),
                                        ('accepted_args', accepted_args  ),)
  Php.unset( merged_filters, tag )
  return True


def has_filter(tag, function_to_check = False):
  ''' Check if any filter has been registered for a hook.
  @global array wp_filter Stores all of the filters.
  @param string        tag               The name of the filter hook.
  @param callable|bool function_to_check Optional. The callback to check for.
                       Default False.
  @return False|int If function_to_check is omitted, returns boolean for
     whether the hook has anything registered. When checking a specific
     function, the priority of that hook is returned, or False if the function
     is not attached. When using the function_to_check argument, this function
     may return a non-boolean value that evaluates to False (e.g.) 0, so use
     the === operator for testing the return value.
  '''
  # Don't reset the internal array pointer  #VT Need to implement pointer!!!
  wp_filter = WpC.WB.Wj.wp_filter  # = GLOBALS['wp_filter'] = globals()['wp_filter']
  #VT# Since wp_filter shares the same mutable array, need to shallow copy it
  #VT# But there is no array pointer in py, and wp_filter is not modifed below
  #VT# So comment out:  import copy #shallow copy only if array can be changed
  #VT# wp_filter = copy.copy(wp_filter)

  has = not Php.empty(wp_filter, tag)

  # Make sure at least one priority has a filter callback
  if has:
    exists = False
    for callbacks in wp_filter[ tag ]:
      if callbacks:    # not Php.empty(locals(), 'callbacks'):
        exists = True
        break

    if not exists:
      has = False

  if function_to_check is False or has is False:
    return has

  idx = _wp_filter_build_unique_id(tag, function_to_check, False)
  if not idx:
    return False

  for priority in Php.Array( array_keys(wp_filter[tag])):
    if Php.isset(wp_filter[tag][priority], idx):
      return priority

  return False


# Add Wj, since in wp.i.default_filters, WB.Wj was not initialized yet
#def apply_filters(tag, value, *OtherArgs ):   #Orig: ( tag, value ):
def apply_filters( tag, value, *OtherArgs, Wj=None ):
  ''' Call the functions added to a filter hook.
  The callback functions attached to filter hook tag are invoked by calling
  this function. This function can be used to create a new filter hook by
  simply calling this function with the name of the new hook specified using
  the tag parameter.
  The function allows for additional arguments to be added and passed to hooks.
      # Our filter callback function
      function example_callback( string, arg1, arg2 ) {
          # (maybe) modify string
          return string
      }
      add_filter( 'example_filter', 'example_callback', 10, 3 )
      /*
       * Apply the filters by calling the 'example_callback' function we
       * "hooked" to 'example_filter' using the add_filter() function above.
       * - 'example_filter' is the filter hook tag
       * - 'filter me' is the value being filtered
       * - arg1 and arg2 are the additional arguments passed to the callback.
      value = apply_filters( 'example_filter', 'filter me', arg1, arg2 )

  @global array wp_filter         Stores all of the filters.
  @global array merged_filters    Merges the filter hooks using this function.
  @global array wp_current_filter Stores the list of current filters with the current one last.
  @param string tag     The name of the filter hook.
  @param mixed  value   The value on which the filters hooked to `tag` are applied on.
  @param mixed  var,... Additional variables passed to the functions hooked to `tag`.
  @return mixed The filtered value after all hooked functions are applied to it.
  '''
  #global var==>WB.Wj.var, except: var=WB.Wj.var=same Obj,mutable array
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_filter = Wj.wp_filter  # global wp_filter
  merged_filters = Wj.merged_filters  # global merged_filters
  wp_current_filter = Wj.wp_current_filter  # global wp_current_filter

  AllArgs = tag, value, *OtherArgs
  #print("WiPg.apply_filters:", tag, value, OtherArgs)

  args = array()

  # Do 'all' actions first.
  if Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)
    args = Php.func_get_args( AllArgs )
    _wp_call_all_hook(args)

  if not Php.isset(wp_filter, tag):
    if Php.isset(wp_filter, 'all'):
      wp_current_filter.popitem()
    return value

  if not Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)

  # Sort.
  if not Php.isset(merged_filters, tag):
    wp_filter[tag] = Php.ksort(wp_filter[tag])
    merged_filters[ tag ] = True

  # No need to reset in py since for loop alawys starts at elem#1 in list
  Php.reset( wp_filter[ tag ] )

  if not args:  # Php.empty(locals(), 'args'):
    args = Php.func_get_args( AllArgs )

  #do {
  #Php: the first iteration of a do-while loop is guaranteed to run
  #    (the truth expression is only checked at the end of the iteration)
  #for Tag in [True, *wp_filter[tag] ]:
  #  if Tag is False:
  #    break
  for Tag in wp_filter[tag]:
    if Tag is False:
      break
    #for the_ in Php.Array( Php.current(wp_filter[tag])):
    for  the_ in Php.Array( Tag ):
      if not Php.is_null(the_['function']):
        args[1] = value
        value = Php.call_user_func_array(the_['function'],
                         Php.array_slice(args, 1, int( the_['accepted_args'])))

  #} while ( next(wp_filter[tag]) is not False )

  wp_current_filter.popitem()

  return value


def apply_filters_ref_array(tag, args, *OtherArgs):   #Orig: ( tag, args ):
  ''' Execute functions hooked on a specific filter hook, specifying arguments in an array.
  @see apply_filters() This function is identical, but the arguments passed to the
  functions hooked to `tag` are supplied using an array.
  @global array wp_filter         Stores all of the filters
  @global array merged_filters    Merges the filter hooks using this function.
  @global array wp_current_filter Stores the list of current filters with the current one last
  @param string tag  The name of the filter hook.
  @param array  args The arguments supplied to the functions hooked to tag.
  @return mixed The filtered value after all hooked functions are applied to it.
  '''
  #global var==>WB.Wj.var, except: var=WB.Wj.var=same Obj,mutable array
  wp_filter = WpC.WB.Wj.wp_filter  # global wp_filter
  merged_filters = WpC.WB.Wj.merged_filters  # global merged_filters
  wp_current_filter = WpC.WB.Wj.wp_current_filter  # global wp_current_filter

  AllArgs = tag, args, *OtherArgs

  # Do 'all' actions first
  if Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)
    # php2python.com/wiki/function.func-get-args/
    all_args = Php.func_get_args(AllArgs)
    _wp_call_all_hook(all_args)

  if not Php.isset(wp_filter, tag):
    if Php.isset(wp_filter, 'all'):
      wp_current_filter.popitem()
    return args[0]

  if not Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)

  # Sort
  if not Php.isset(merged_filters, tag):
    wp_filter[tag] = Php.ksort(wp_filter[tag])
    merged_filters[ tag ] = True

  # No need to reset in py since for loop alawys starts at elem#1 in list
  #reset( wp_filter[ tag ] )

  #do {
  #Php: the first iteration of a do-while loop is guaranteed to run
  #    (the truth expression is only checked at the end of the iteration)
  for Tag in [True, *wp_filter[tag] ]:
    if Tag is False:
      break
    for the_ in Php.Array( Php.current(wp_filter[tag])):
      if not Php.is_null(the_['function']):
        args[0] = Php.call_user_func_array(the_['function'], Php.array_slice(args, 0, int( the_['accepted_args'])))
  #} while ( next(wp_filter[tag]) is not False )

  wp_current_filter.popitem()

  return args[0]


def remove_filter( tag, function_to_remove, priority = 10 ):
  ''' Removes a function from a specified filter hook.
  This function removes a function attached to a specified filter hook. This
  method can be used to remove default functions attached to a specific filter
  hook and possibly replace them with a substitute.
  To remove a hook, the function_to_remove and priority arguments must match
  when the hook was added. This goes for both filters and actions. No warning
  will be given on removal failure.
  @global array wp_filter         Stores all of the filters
  @global array merged_filters    Merges the filter hooks using this function.
  @param string   tag                The filter hook to which the function to be removed is hooked.
  @param callable function_to_remove The name of the function which should be removed.
  @param int      priority           Optional. The priority of the function. Default 10.
  @return bool    Whether the function existed before it was removed.
  '''
  function_to_remove = _wp_filter_build_unique_id( tag, function_to_remove, priority )

  #r= Php.isset( GLOBALS['wp_filter'][ tag ][ priority ], function_to_remove )
  r = Php.isset(WpC.WB.Wj.wp_filter[tag ][ priority ], function_to_remove )

  if r is True:
    del  WpC.WB.Wj.wp_filter[ tag ][ priority ][ function_to_remove ]
    if Php.empty(WpC.WB.Wj.wp_filter[ tag ], 'priority'):
      del WpC.WB.Wj.wp_filter[ tag ][ priority ]
    if Php.empty(WpC.WB.Wj.wp_filter, 'tag'):
      WpC.WB.Wj.wp_filter[ tag ] = array()
    del WpC.WB.Wj.merged_filters[ tag ]

  return r


def remove_all_filters( tag, priority = False ):
  ''' Remove all of the hooks from a filter.
  @global array wp_filter         Stores all of the filters
  @global array merged_filters    Merges the filter hooks using this function.
  @param string   tag      The filter to remove hooks from.
  @param int|bool priority Optional. The priority number to remove. Default False.
  @return True True when finished.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wp_filter = WpC.WB.Wj.wp_filter  # global wp_filter
  merged_filters = WpC.WB.Wj.merged_filters  # global merged_filters

  if Php.isset(wp_filter, tag):
    if priority is False:
      wp_filter[ tag ] = array()
    elif Php.isset(wp_filter[ tag ], priority):
      wp_filter[ tag ][ priority ] = array()

  del merged_filters[ tag ]

  return True


def current_filter():
  ''' Retrieve the name of the current filter or action.
  @global array wp_current_filter Stores the list of current filters with the current one last
  @return string Hook name of the current filter or action.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wp_current_filter = WpC.WB.Wj.wp_current_filter  # global wp_current_filter
  return end( wp_current_filter )


def current_action():
  ''' Retrieve the name of the current action.
  @return string Hook name of the current action.
  '''
  return current_filter()


def doing_filter( Filter = None ):
  ''' Retrieve the name of a filter currently being processed.
  The function current_filter() only returns the most recent filter or action
  being executed. did_action() returns True once the action is initially
  processed.
  This function allows detection for any filter currently being
  executed (despite not being the most recent filter to fire, in the case of
  hooks called from hook callbacks) to be verified.
  @see current_filter()
  @see did_action()
  @global array wp_current_filter Current filter.
  @param None|string Filter Optional. Filter to check. Defaults to None, which
                             checks if any filter is currently being run.
  @return bool Whether the filter is currently in the stack.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wp_current_filter = WpC.WB.Wj.wp_current_filter  # global wp_current_filter

  if Filter is None:
    return not Php.empty(WpC.WB.Wj.__dict__, 'wp_current_filter')

  return Php.in_array( Filter, wp_current_filter )


def doing_action( action = None ):
  ''' Retrieve the name of an action currently being processed.
  @param string|None action Optional. Action to check. Defaults to None, which checks
                             if any action is currently being run.
  @return bool Whether the action is currently in the stack.
  '''
  return doing_filter( action )


def add_action(tag, function_to_add, priority = 10, accepted_args = 1):
  ''' Hooks a function on to a specific action.
  Actions are the hooks that the WordPress core launches at specific points
  during execution, or when specific events occur. Plugins can specify that
  one or more of its PHP functions are executed at these points, using the
  Action API.
  @param string   tag             The name of the action to which the function_to_add is hooked.
  @param callable function_to_add The name of the function you wish to be called.
  @param int      priority        Optional. Used to specify the order in which the functions
                                   associated with a particular action are executed. Default 10.
                                   Lower numbers correspond with earlier execution,
                                   and functions with the same priority are executed
                                   in the order in which they were added to the action.
  @param int      accepted_args   Optional. The number of arguments the function accepts. Default 1.
  @return True Will always return True.
  '''
  return add_filter(tag, function_to_add, priority, accepted_args)


# Add Wj, since in wp.i.default_filters, WB.Wj was not initialized yet
#def do_action(tag, arg = '', *OtherArgs):   #Orig: ( tag, arg ):
def do_action( tag, arg = '', *OtherArgs, Wj=None):
  ''' Execute functions hooked on a specific action hook.
  This function invokes all functions attached to action hook `tag`. It is
  possible to create new action hooks by simply calling this function,
  specifying the name of the new hook using the `tag` parameter.
  You can pass extra arguments to the hooks, much like you can with apply_filters().
  @global array wp_filter         Stores all of the filters
  @global array wp_actions        Increments the amount of times action was triggered.
  @global array merged_filters    Merges the filter hooks using this function.
  @global array wp_current_filter Stores the list of current filters with the current one last
  @param string tag     The name of the action to be executed.
  @param mixed  arg,... Optional. Additional arguments which are passed on to the
                         functions hooked to the action. Default empty.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_filter = Wj.wp_filter  # global wp_filter
  wp_actions = Wj.wp_actions  # global wp_actions
  merged_filters = Wj.merged_filters  # global merged_filters
  wp_current_filter = Wj.wp_current_filter  # global wp_current_filter

  AllArgs = tag, arg, *OtherArgs

  if not Php.isset(wp_actions, tag):
    wp_actions[tag] = 1
  else:
    wp_actions[tag] += 1

  # Do 'all' actions first
  if Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)
    # php2python.com/wiki/function.func-get-args/
    all_args = Php.func_get_args(AllArgs)
    _wp_call_all_hook(all_args)

  if not Php.isset(wp_filter, tag):
    if Php.isset(wp_filter, 'all'):
      wp_current_filter.popitem()
    return

  if not Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)

  args = array()
  # 1 == len(arg) #implies: isset(arg[0])
  if Php.is_array(arg) and 1 == len(arg) and Php.is_object(arg[0]): # array(&this)
    #args.append(& arg[0])    # & <<== Check!!  # & not needed for object?
    args.append(arg[0])
  else:
    args.append(arg)
  #for ( a = 2, num = func_num_args(); a < num; a++ )
  for a in range(2, Php.func_num_args(AllArgs)):
    args[None] = Php.func_get_arg(AllArgs, a)    # differ from func_get_args

  # Sort
  if not Php.isset(merged_filters, tag):
    wp_filter[tag] = Php.ksort(wp_filter[tag])
    merged_filters[ tag ] = True

  # No need to reset in py since for loop alawys starts at elem#1 in list
  #reset( wp_filter[ tag ] )

  #do {
  #Php: the first iteration of a do-while loop is guaranteed to run
  #    (the truth expression is only checked at the end of the iteration)
  for Tag in [True, *wp_filter[tag] ]:
    if Tag is False:
      break
    for the_ in Php.Array( Php.current(wp_filter[tag])):
      if not Php.is_null(the_['function']):
        Php.call_user_func_array(the_['function'], Php.array_slice(args, 0, int( the_['accepted_args'])))

  #} while ( next(wp_filter[tag]) is not False )

  wp_current_filter.popitem()


# Add Wj, since in wp.i.default_filters, WB.Wj was not initialized yet
#def did_action(tag):
def did_action(tag, Wj=None):
  ''' Retrieve the number of times an action is fired.
  @global array wp_actions Increments the amount of times action was triggered.
  @param string tag The name of the action hook.
  @return int The number of times action hook tag is fired.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_actions = Wj.wp_actions  # global wp_actions

  if not Php.isset(wp_actions, tag):
    return 0

  return wp_actions[tag]


def do_action_ref_array( tag, args, *OtherArgs):   #Orig: ( tag, args ):
  ''' Execute functions hooked on a specific action hook, specifying arguments in an array.
  @see do_action() This function is identical, but the arguments passed to the
                   functions hooked to tag< are supplied using an array.
  @global array wp_filter         Stores all of the filters
  @global array wp_actions        Increments the amount of times action was triggered.
  @global array merged_filters    Merges the filter hooks using this function.
  @global array wp_current_filter Stores the list of current filters with the current one last
  @param string tag  The name of the action to be executed.
  @param array  args The arguments supplied to the functions hooked to `tag`.
  '''
  #global var==>WB.Wj.var, except: var=WB.Wj.var=same Obj,mutable array
  wp_filter = WpC.WB.Wj.wp_filter  # global wp_filter
  wp_actions = WpC.WB.Wj.wp_actions  # global wp_actions
  merged_filters = WpC.WB.Wj.merged_filters  # global merged_filters
  wp_current_filter = WpC.WB.Wj.wp_current_filter  # global wp_current_filter

  AllArgs = tag, args, *OtherArgs

  if not Php.isset(wp_actions, tag):
    wp_actions[tag] = 1
  else:
    wp_actions[tag] += 1

  # Do 'all' actions first
  if Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)
    # php2python.com/wiki/function.func-get-args/
    all_args = Php.func_get_args(AllArgs)
    _wp_call_all_hook(all_args)

  if not Php.isset(wp_filter, tag):
    if Php.isset(wp_filter, 'all'):
      wp_current_filter.popitem()
    return

  if not Php.isset(wp_filter, 'all'):
    wp_current_filter.append(tag)

  # Sort
  if not Php.isset(merged_filters, tag):
    wp_filter[tag] = Php.ksort(wp_filter[tag])
    merged_filters[ tag ] = True

  # No need to reset in py since for loop alawys starts at elem#1 in list
  #reset( wp_filter[ tag ] )

  #do {
  #Php: the first iteration of a do-while loop is guaranteed to run
  #    (the truth expression is only checked at the end of the iteration)
  for Tag in [True, *wp_filter[tag] ]:
    if Tag is False:
      break
    for the_ in Php.Array( current(wp_filter[tag])):
      if not Php.is_null(the_['function']):
        Php.call_user_func_array(the_['function'], Php.array_slice(args, 0, int( the_['accepted_args'])))

  #} while ( next(wp_filter[tag]) is not False )

  wp_current_filter.popitem()


def has_action(tag, function_to_check = False):
  ''' Check if any action has been registered for a hook.
  @see has_filter() has_action() is an alias of has_filter().
  @param string        tag               The name of the action hook.
  @param callable|bool function_to_check Optional. The callback to check for. Default False.
  @return bool|int If function_to_check is omitted, returns boolean for whether the hook has
                   anything registered. When checking a specific function, the priority of that
                   hook is returned, or False if the function is not attached. When using the
                   function_to_check argument, this function may return a non-boolean value
                   that evaluates to False (e.g.) 0, so use the === operator for testing the
                   return value.
  '''
  return has_filter(tag, function_to_check)


def remove_action( tag, function_to_remove, priority = 10 ):
  ''' Removes a function from a specified action hook.
  This function removes a function attached to a specified action hook. This
  method can be used to remove default functions attached to a specific filter
  hook and possibly replace them with a substitute.
  @param string   tag                The action hook to which the function to be removed is hooked.
  @param callable function_to_remove The name of the function which should be removed.
  @param int      priority           Optional. The priority of the function. Default 10.
  @return bool Whether the function is removed.
  '''
  return remove_filter( tag, function_to_remove, priority )


def remove_all_actions(tag, priority = False):
  ''' Remove all of the hooks from an action.
  @param string   tag      The action to remove hooks from.
  @param int|bool priority The priority number to remove them from. Default False.
  @return True True when finished.
  '''
  return remove_all_filters(tag, priority)


def apply_filters_deprecated( tag, args, version, replacement = False, message = None ):
  ''' Fires functions attached to a deprecated filter hook.
  When a filter hook is deprecated, the apply_filters() call is replaced with
  apply_filters_deprecated(), which triggers a deprecation notice and then fires
  the original filter hook.
  @see _deprecated_hook()
  @param string tag         The name of the filter hook.
  @param array  args        Array of additional function arguments to be passed to apply_filters().
  @param string version     The version of WordPress that deprecated the hook.
  @param string replacement Optional. The hook that should have been used. Default False.
  @param string message     Optional. A message regarding the change. Default None.
  '''
  if not has_filter( tag ):
    return args[0]

  _deprecated_hook( tag, version, replacement, message )

  return apply_filters_ref_array( tag, args )


def do_action_deprecated( tag, args, version, replacement = False, message = None ):
  ''' Fires functions attached to a deprecated action hook.
  When an action hook is deprecated, the do_action() call is replaced with
  do_action_deprecated(), which triggers a deprecation notice and then fires
  the original hook.
  @see _deprecated_hook()
  @param string tag         The name of the action hook.
  @param array  args        Array of additional function arguments to be passed to do_action().
  @param string version     The version of WordPress that deprecated the hook.
  @param string replacement Optional. The hook that should have been used.
  @param string message     Optional. A message regarding the change.
  '''
  if not has_action( tag ):
    return

  _deprecated_hook( tag, version, replacement, message )

  do_action_ref_array( tag, args )


#
# Functions for handling plugins.
#

def plugin_basename( File ):
  ''' Gets the basename of a plugin.
  This method extracts the name of a plugin from its filename.
  @global array wp_plugin_paths
  @param string File The filename of plugin.
  @return string The name of a plugin.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wp_plugin_paths = WpC.WB.Wj.wp_plugin_paths  # global wp_plugin_paths

  # wp_plugin_paths contains normalized paths.
  File = WiFc.wp_normalize_path( File )

  Php.arsort( wp_plugin_paths )
  for Dir, realdir in wp_plugin_paths.items():
    if Php.strpos( File, realdir ) == 0:  # ===
      File = Dir + Php.substr( File, Php.strlen( realdir ) )

  plugin_dir = WiFc.wp_normalize_path( WpC.WB.Wj.WP_PLUGIN_DIR )
  mu_plugin_dir = WiFc.wp_normalize_path( WpC.WB.Wj.WPMU_PLUGIN_DIR )

  File = Php.preg_replace('#^' + Php.preg_quote(plugin_dir, '#') + '/|^' + Php.preg_quote(mu_plugin_dir, '#') + '/#','',File); # get relative path from plugins dir
  File = Php.trim(File, '/')
  return File


@Php.static_vars(wp_plugin_path = None, wpmu_plugin_path = None)
def wp_register_plugin_realpath( File ):
  ''' Register a plugin's real path.
  This is used in plugin_basename() to resolve symlinked paths.
  @see WiFc.wp_normalize_path()
  @global array wp_plugin_paths
  @staticvar string wp_plugin_path
  @staticvar string wpmu_plugin_path
  @param string File Known path to the file.
  @return bool Whether the path was able to be registered.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  #global wp_plugin_paths  #ini in wp.settings to array()
  wp_plugin_paths = WpC.WB.Wj.wp_plugin_paths

  # Normalize, but store as static to avoid recalculation of a constant value
  #static wp_plugin_path = None, wpmu_plugin_path = None
  if not Php.isset(wp_register_plugin_realpath, 'wp_plugin_path'):
    wp_register_plugin_realpath.wp_plugin_path   = WiFc.wp_normalize_path( WpC.WB.Wj.WP_PLUGIN_DIR   )
    wp_register_plugin_realpath.wpmu_plugin_path = WiFc.wp_normalize_path( WpC.WB.Wj.WPMU_PLUGIN_DIR )

  plugin_path = WiFc.wp_normalize_path( dirname( File ) )
  plugin_realpath = WiFc.wp_normalize_path( dirname( realpath( File ) ) )

  #if plugin_path === wp_plugin_path or plugin_path === wpmu_plugin_path:
  if (plugin_path == wp_register_plugin_realpath.wp_plugin_path  or
      plugin_path == wp_register_plugin_realpath.wpmu_plugin_path  ):
    return False

  #if plugin_path !== plugin_realpath:
  if plugin_path != plugin_realpath:
    wp_plugin_paths[ plugin_path ] = plugin_realpath

  return True


def plugin_dir_path( File ):
  ''' Get the filesystem directory path (with trailing slash) for the plugin __FILE__ passed in.
  @param string File The filename of the plugin (__FILE__).
  @return string the filesystem path of the directory that contains the plugin.
  '''
  return trailingslashit( dirname( File ) )


def plugin_dir_url( File ):
  ''' Get the URL directory path (with trailing slash) for the plugin __FILE__ passed in.
  @param string File The filename of the plugin (__FILE__).
  @return string the URL path of the directory that contains the plugin.
  '''
  return trailingslashit( plugins_url( '', File ) )


def register_activation_hook(File, function):
  ''' Set the activation hook for a plugin.
  When a plugin is activated, the action 'activate_PLUGINNAME' hook is
  called. In the name of this hook, PLUGINNAME is replaced with the name
  of the plugin, including the optional subdirectory. For example, when the
  plugin is located in wp-content/plugins/sampleplugin/sample.php, then
  the name of this hook will become 'activate_sampleplugin/sample.php'.
  When the plugin consists of only one file and is (as by default) located at
  wp-content/plugins/sample.php the name of this hook will be
  'activate_sample.php'.
  @param string   File     The filename of the plugin including the path.
  @param callable function The function hooked to the 'activate_PLUGIN' action.
  '''
  File = plugin_basename(File)
  add_action('activate_' + File, function)


def register_deactivation_hook(File, function):
  ''' Set the deactivation hook for a plugin.
  When a plugin is deactivated, the action 'deactivate_PLUGINNAME' hook is
  called. In the name of this hook, PLUGINNAME is replaced with the name
  of the plugin, including the optional subdirectory. For example, when the
  plugin is located in wp-content/plugins/sampleplugin/sample.php, then
  the name of this hook will become 'deactivate_sampleplugin/sample.php'.
  When the plugin consists of only one file and is (as by default) located at
  wp-content/plugins/sample.php the name of this hook will be
  'deactivate_sample.php'.
  @param string   File     The filename of the plugin including the path.
  @param callable function The function hooked to the 'deactivate_PLUGIN' action.
  '''
  File = plugin_basename(File)
  add_action('deactivate_' + File, function)


def register_uninstall_hook( File, callback ):
  ''' Set the uninstallation hook for a plugin.
  Registers the uninstall hook that will be called when the user clicks on the
  uninstall link that calls for the plugin to uninstall itself. The link won't
  be active unless the plugin hooks into the action.
  The plugin should not run arbitrary code outside of functions, when
  registering the uninstall hook. In order to run using the hook, the plugin
  will have to be included, which means that any code laying outside of a
  function will be run during the uninstall process. The plugin should not
  hinder the uninstall process.
  If the plugin can not be written without running code within the plugin, then
  the plugin should create a file named 'uninstall.php' in the base plugin
  folder. This file will be called, if it exists, during the uninstall process
  bypassing the uninstall hook. The plugin, when using the 'uninstall.php'
  should always check for the 'WP_UNINSTALL_PLUGIN' constant, before
  executing.
  @param string   File     Plugin file.
  @param callable callback The callback to run when the hook is called. Must be
                            a static method or function.
  '''
  import wp.i.option as WiO
  if Php.is_array( callback ) and Php.is_object( callback[0] ):
    _doing_it_wrong( register_uninstall_hook.__name__,    # __FUNCTION__,
        __( 'Only a static class method or function can be used in an uninstall hook.' ), '3.1.0' )
    return

  # The option should not be autoloaded, because it is not needed in most
  # cases. Emphasis should be put on using the 'uninstall.php' way of
  # uninstalling the plugin.
  uninstallable_plugins = Php.Array( WiO.get_option('uninstall_plugins'))
  uninstallable_plugins[plugin_basename(File)] = callback

  WiO.update_option('uninstall_plugins', uninstallable_plugins)


def _wp_call_all_hook(args):
  ''' Call the 'all' hook, which will process the functions hooked into it.
  The 'all' hook passes all of the arguments or parameters that were used for
  the hook, which this function was called for.
  This function is used internally for apply_filters(), do_action(), and
  do_action_ref_array() and is not meant to be used from outside those
  functions. This function does not check for the existence of the all hook, so
  it will fail unless the all hook exists prior to this function call.
  @global array wp_filter  Stores all of the filters
  @param array args The collected parameters from the hook that was called.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  wp_filter = WpC.WB.Wj.wp_filter  # global wp_filter

  # No need to reset in py since for loop alawys starts at elem#1 in list
  #reset( wp_filter['all'] )

  #do {
  #Php: the first iteration of a do-while loop is guaranteed to run
  #    (the truth expression is only checked at the end of the iteration)
  for Tag in [True, *wp_filter['all'] ]:
    if Tag is False:
      break
    for the_ in Php.Array( Php.current(wp_filter['all'])):
      if not Php.is_null(the_['function']):
        Php.call_user_func_array(the_['function'], args)

  #} while ( next(wp_filter['all']) is not False )


@Php.static_vars(filter_id_count = 0)
#def _wp_filter_build_unique_id(tag, function, priority):
def _wp_filter_build_unique_id( tag, function, priority, Wj=None):
  ''' Build Unique ID for storage and retrieval.
  The old way to serialize the callback caused issues and this function is the
  solution. It works by checking for objects and creating a new property in
  the class to keep track of the object and new objects of the same class that
  need to be added.
  It also allows for the removal of actions and filters for objects after they
  change class properties. It is possible to include the property wp_filter_id
  in your class and set it to "None" or a number to bypass the workaround.
  However this will prevent you from adding new classes and any new classes
  will overwrite the previous hook by the same class.
  Functions and static method callbacks are just returned as strings and
  shouldn't have any speed penalty.
  @link https://core.trac.wordpress.org/ticket/3875
  @global array wp_filter Storage for all of the filters and actions.
  @staticvar int filter_id_count
  @param string   tag      Used in counting how many hooks were applied
  @param callable function Used for creating unique id
  @param int|bool priority Used in counting how many hooks were applied. If === False
                            and function is an object reference, we return the unique
                            id only if it already has one, False otherwise.
  @return string|False Unique ID for usage as array key or False if priority === False
                       and function is an object reference, and it does not already have
                       a unique id.
  '''
  #global var==>WpC.WB.Wj.var, except: var=WpC.WB.Wj.var=same Obj,mutable array
  if Wj is None:
    Wj = WpC.WB.Wj
  wp_filter = Wj.wp_filter  # global wp_filter
  #static filter_id_count = 0

  if Php.is_string(function):
    return function

  if Php.is_object(function):
    # Closures are currently implemented as objects
    function = array( function, '' )
  else:
    function = Php.Array( function)

  if Php.is_object(function[0]):
    # Object Class Calling
    if Php.function_exists('spl_object_hash'):
      return spl_object_hash(function[0]) + function[1]
    else:
      obj_idx = get_class(function[0]).function[1]
      if not Php.isset(function[0], 'wp_filter_id'):
        if priority is False:
          return False
        obj_idx += (len(Php.Array(wp_filter[tag][priority]))
                    if Php.isset(wp_filter[tag], priority)
                    else _wp_filter_build_unique_id.filter_id_count )
        function[0].wp_filter_id = _wp_filter_build_unique_id.filter_id_count
        _wp_filter_build_unique_id.filter_id_count += 1
      else:
        obj_idx += function[0].wp_filter_id

      return obj_idx

  elif Php.is_string( function[0] ):
    # Static Calling
    return function[0] + '::' + function[1]

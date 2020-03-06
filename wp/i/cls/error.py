#!/usr/bin/python3
import pyx.php as Php
array = Php.array

class WP_Error(Php.stdClass):
  '''WordPress Error class.   # wp-includes/class-wp-error.php
     Container for checking for WordPress errors and error messages. Return
     WP_Error & use {@link is_wp_error()} to check if this class is returned.
     Many core WP functions pass this class in the event of an error and
     if not handled properly will result in code errors.
  '''
  #errors  = error_data = {}  #BAD# both are same mutable {}, not instance var

  def __init__(self, code = '', message = '', data = '' ):
    '''If `$code` is empty, the other parameters will be ignored.
    When `$code` is not empty, `$message` will be used even if
    it is empty. The `$data` parameter will be used only if it
    is not empty.
    Though the class is constructed with a single error code and
    message, multiple codes can be added using the `add()` method.
    @param string|int $code Error code
    @param string $message Error message
    @param mixed $data Optional. Error data.
    Inherited classes no long need to define 'self._obj=array()' in __init__()
    '''
    if not code:  #if empty
      return

    ##if code not in self.errors:
    ##  self.errors[code] = []
    ##if not isinstance(self.errors[code], list):
    ##  print("\nDon't know why but self.errors[{}]={}, not instance of list!"
    ##        .format(code, self.errors[code]), 'Reset it to []!')
    ##  self.errors[code] = []

    ##should be separate instance array, not same class mutable dict!!
    self.errors     = array( (code, array()) )    # php auto init array[code]
    self.error_data = array()
    ##self.errors[code].append( message ) #keyerror since self.errors = array(
    #self.errors[code] = [ message, ]
    self.errors[code][None]  = message
    if data:      #if ! empty
      self.error_data = array( (code, array()) )  # php auto init array[code]
      self.error_data[code] = data

  def get_error_codes(self):
    ''' Retrieve all error codes.
        return array List of error codes, if available.
    '''
    if Php.empty(self, 'errors'):   # if empty
      return array()    # []
    return Php.array_keys(self.errors)

  def get_error_code(self):
    ''' Retrieve first error code available.
        @return string|int Empty string, if no error codes.
    '''
    codes = self.get_error_codes()
    if not codes:   # if empty
      return ''
    return codes[0]

  def get_error_messages(self, code = ''):
    ''' Retrieve all error messages or error messages matching code.
        @param string|int code Optional.
               Retrieve messages matching code, if exists.
        @return array Error strings on success, or empty array on failure
                (if using code parameter).
                Return all messages if no code specified.
    '''
    if not code:   # if empty
      all_messages = array()    # []
      for code, messages in Php.Array(self.errors.items()):
        all_messages = Php.array_merge(all_messages, messages)
      return all_messages
    if Php.isset(self.errors, code):
      return self.errors[code]
    else:
      return array()

  def get_error_message(self, code = ''):
    '''Get single error message.
       This will get the first message available for the code. If no code is
       given then the first code available will be used.
       @param string|int code Optional. Error code to retrieve message.
       @return string
    '''
    if not code:   # if empty
      code = self.get_error_code()
    messages = self.get_error_messages(code)
    if not messages:   # if empty
      return ''
    return messages[0]

  def get_error_data(self, code = ''):
    '''Retrieve error data for error code.
       @param string|int code Optional. Error code.
       @return mixed Error data, if it exists.
    '''
    if not code:   # if empty
      code = self.get_error_code()
    if Php.isset(self.error_data, code):
      return self.error_data[code]

  def add(self, code, message, data = ''):
    '''Add an error or append additional message to an existing error.
       @param string|int code Error code.
       @param string message Error message.
       @param mixed data Optional. Error data.
    '''
    self.errors[code][None] = message
    if data:      #if ! empty
      self.error_data[code] = data

  def add_data(self, data, code = ''):
    '''Add data for error code.
       The error code can only contain one error data.
       @param mixed data Error data.
       @param string|int code Error code.
    '''
    if not code:   # if empty
      code = self.get_error_code()
    self.error_data[code] = data

  def remove(self, code ):
    '''Removes the specified error.
       This function removes all error messages associated with the specified
       error code, along with any error data for that code.
       @param string|int code Error code.
    '''
    del self.errors[ code ]
    del self.error_data[ code ]


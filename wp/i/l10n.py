import pyx.php    as Php
array = Php.array

''' Core Translation API
@package WordPress  @subpackage i18n
'''

def _x( text, context, domain = 'default' ):
  return text
def __( text, domain = 'default' ):
  return text

def _n_noop( singular, plural, domain = None ):
  ''' Registers plural strings in POT file, but does not translate them.
  Used when you want to keep structures with translatable plural
  strings and use them later when the number is known.
  Example:
      messages = array(
       	'post' => _n_noop( '%s post', '%s posts', 'text-domain' ),
       	'page' => _n_noop( '%s pages', '%s pages', 'text-domain' ),
      )
      ...
      message = messages[ type ]
      usable_text = sprintf( translate_nooped_plural( message, count,
                             'text-domain' ), number_format_i18n( count ) )
  @param string singular Singular form to be localized.
  @param string plural   Plural form to be localized.
  @param string domain   Optional. Text domain. Unique identifier for retrieving translated strings.
                          Default None.
  @return array {
      Array of translation information for the strings.
  
      @type string 0        Singular form to be localized. No longer used.
      @type string 1        Plural form to be localized. No longer used.
      @type string singular Singular form to be localized.
      @type string plural   Plural form to be localized.
      @type None   context  Context information for the translators.
      @type string domain   Text domain.
  }'''
  return array((0         , singular), (1       , plural),
               ('singular', singular), ('plural', plural),
               ('context' , None    ), ('domain', domain),)


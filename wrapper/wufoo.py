'''A library that provides a Python interface to the Wufoo API

Challenges and design decisions:

Some of the code is generated, but the final version is made by hand.
Certain classes have custom logic that had to be added which prevented
it all from being generated from an IDL. Here's a list:

* embed_code method of Widget class (which needs subdomain)
* filtering in Entry class
* count method for Entry
* count method for Comment
* compressing Fields in Entry class into a map (comes as a list,
  can't make them properties on the fly)

Lingering Concerns:

* Post using a form url? This works, but should maybe rename the parameter 'form_hash'
* Consistent error and success messages
  * posting entry is different than the others...
* PUT web hook has a 500 reponse?
* Login not going to be implemeted b/c can't be tested w/o integrationKey
  * Also, 'integraitonKey'? Is that mispelled?
* Forms IncludeTodayCount

'''

__author__ = 'mpare@gatech.edu'
__version__ = '0.1-devel'

import base64
import os
import simplejson
import sys
import urllib
import urllib2
from urllib2 import HTTPError
import urlparse
import dateutil
import dateutil.parser
import datetime

# ----------------------------------------
#
# Class Definitions
#
# ----------------------------------------

class WufooError(Exception):
  '''Base class for Wufoo errors'''
  
  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class Field(object):
  def __init__(self, type=None, id=None, title=None, is_required=None, subfields=None, label=None, score=None, choices=None):
    self._type=type
    self._id=id
    self._title=title
    self._is_required=is_required
    self._subfields=subfields
    self._label=label
    self._score=score
    self._choices=choices

  @property
  def type(self):
    return self._type

  @property
  def id(self):
    return self._id

  @property
  def title(self):
    return self._title

  @property
  def is_required(self):
    return self._is_required

  @property
  def subfields(self):
    return self._subfields

  @property
  def label(self):
    return self._label

  @property
  def score(self):
    return self._score

  @property
  def choices(self):
    return self._choices


  def __str__(self):
    '''A string representation of this wufoo.Field instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this wufoo.Field instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this wufoo.Field instance.

    Returns:
      A JSON string representation of this wufoo.Field instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this wufoo.Field instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this wufoo.Field instance
    '''
    data = {}

    if self._type:
      data['type'] = self._type
    if self._id:
      data['id'] = self._id
    if self._title:
      data['title'] = self._title
    if self._is_required:
      data['is_required'] = self._is_required
    if self._subfields:
      data['subfields'] = [x.AsDict() for x in self._subfields]
    if self._label:
      data['label'] = self._label
    if self._score:
      data['score'] = self._score
    if self._choices:
      data['choices'] = [x.AsDict() for x in self._choices]

    return data

  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data: A JSON dict, as converted from the JSON in the Wufoo API
    Returns:
      A wufoo.Field instance
    '''
    
    # If there are subfields or choices, create Field instances
    if 'Choices' in data:
      data['Choices'] = [Field.NewFromJsonDict(x) for x in data['Choices']]
    if 'SubFields' in data:
      data['SubFields'] = [Field.NewFromJsonDict(x) for x in data['SubFields']]

    return Field(type=data.get('Type', None),
                  id=data.get('ID', None),
                  title=data.get('Title', None),
                  is_required=data.get('IsRequired', None),
                  subfields=data.get('SubFields', None),
                  label=data.get('Label', None),
                  score=data.get('Score', None),
                  choices=data.get('Choices', None))

class Comment(object):
  '''Class for representing the structure of the Comment class in the Wufoo API'''
  
  def __init__(self, commented_by=None, comment_id=None, date_created=None, entry_id=None, text=None):
    self._commented_by=commented_by
    self._comment_id=comment_id
    self._date_created=date_created
    self._entry_id=entry_id
    self._text=text

  @property
  def commented_by(self):
    return self._commented_by

  @property
  def comment_id(self):
    return self._comment_id

  @property
  def date_created(self):
    return dateutil.parser.parse(self._date_created)

  @property
  def entry_id(self):
    return self._entry_id

  @property
  def text(self):
    return self._text

  def __str__(self):
    '''A string representation of this wufoo.Comment instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this wufoo.Comment instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this wufoo.Comment instance.

    Returns:
      A JSON string representation of this wufoo.Comment instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this wufoo.Comment instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this wufoo.Comment instance
    '''
    data = {}

    if self._commented_by:
      data['commented_by'] = self._commented_by
    if self._comment_id:
      data['comment_id'] = self._comment_id
    if self._date_created:
      data['date_created'] = self._date_created
    if self._entry_id:
      data['entry_id'] = self._entry_id
    if self._text:
      data['text'] = self._text

    return data

  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data: A JSON dict, as converted from the JSON in the Wufoo API
    Returns:
      A wufoo.Comment instance
    '''
    # Compress the Field[id] values into maps
    fields = {}
    for k, v in data.items():
      if k.startswith('Field'):
        fields[k] = v

    return Comment(commented_by=data.get('CommentedBy', None),
                    comment_id=data.get('CommentId', None),
                    date_created=data.get('DateCreated', None),
                    entry_id=data.get('EntryId', None),
                    text=data.get('Text', None))

class Widget(object):
  '''Class for representing the structure of the Widget class in Wufoo API'''

  def __init__(self, subdomain=None, type=None, type_desc=None, hash=None, name=None, size=None):
    self._subdomain=subdomain
    self._type=type
    self._type_desc=type_desc
    self._hash=hash
    self._name=name
    self._size=size

  @property
  def embed_code(self):
    return '''
    <script type="text/javascript">
      var host = (("https:" == document.location.protocol) ? "https://" : "http://");
      document.write(unescape("%%3Cscript src='" + host + "%s.wufoo.com/scripts/widget/embed.js?w=%s' type='text/javascript'%%3E%%3C/script%%3E"));
    </script>
    ''' % (self.subdomain, self.hash)
  
  @property
  def subdomain(self):
    return self._subdomain
  
  @property
  def type(self):
    return self._type

  @property
  def type_desc(self):
    return self._type_desc

  @property
  def hash(self):
    return self._hash

  @property
  def name(self):
    return self._name

  @property
  def size(self):
    return self._size

  def __str__(self):
    '''A string representation of this wufoo.Widget instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this wufoo.Widget instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this wufoo.Widget instance.

    Returns:
      A JSON string representation of this wufoo.Widget instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this wufoo.Widget instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this wufoo.Widget instance
    '''
    data = {}

    if self._type:
      data['type'] = self._type
    if self._type_desc:
      data['type_desc'] = self._type_desc
    if self._hash:
      data['hash'] = self._hash
    if self._name:
      data['name'] = self._name
    if self._size:
      data['size'] = self._size
      
    data['embed_code'] = self.embed_code

    return data

  @staticmethod
  def NewFromJsonDict(data, subdomain):
    '''Create a new instance based on a JSON dict.

    Args:
      data: A JSON dict, as converted from the JSON in the Wufoo API
    Returns:
      A wufoo.Widget instance
    '''

    # Compress the Field[id] values into maps
    fields = {}
    for k, v in data.items():
      if k.startswith('Field'):
        fields[k] = v

    return Widget(subdomain=subdomain,
                  type=data.get('Type', None),
                  type_desc=data.get('TypeDesc', None),
                  hash=data.get('Hash', None),
                  name=data.get('Name', None),
                  size=data.get('Size', None))

class User(object):
  '''Class to represent the User structure in the Wufoo API.'''
  def __init__(self, api_key=None, hash=None, is_account_owner=None, image=None, company=None, link_forms=None, create_themes=None, link_reports=None, user=None, create_reports=None, time_zone=None, create_forms=None, admin_access=None, email=None):
    self._api_key=api_key
    self._hash=hash
    self._is_account_owner=is_account_owner
    self._image=image
    self._company=company
    self._link_forms=link_forms
    self._create_themes=create_themes
    self._link_reports=link_reports
    self._user=user
    self._create_reports=create_reports
    self._time_zone=time_zone
    self._create_forms=create_forms
    self._admin_access=admin_access
    self._email=email

  @property
  def api_key(self):
    return self._api_key

  @property
  def hash(self):
    return self._hash

  @property
  def is_account_owner(self):
    return self._is_account_owner

  @property
  def image(self):
    return self._image

  @property
  def company(self):
    return self._company

  @property
  def link_forms(self):
    return self._link_forms

  @property
  def create_themes(self):
    return self._create_themes

  @property
  def link_reports(self):
    return self._link_reports

  @property
  def user(self):
    return self._user

  @property
  def create_reports(self):
    return self._create_reports

  @property
  def time_zone(self):
    return self._time_zone

  @property
  def create_forms(self):
    return self._create_forms

  @property
  def admin_access(self):
    return self._admin_access

  @property
  def email(self):
    return self._email

  def __str__(self):
    '''A string representation of this wufoo.User instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this wufoo.User instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this wufoo.User instance.

    Returns:
      A JSON string representation of this wufoo.User instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this wufoo.User instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this wufoo.User instance
    '''
    data = {}

    if self._api_key:
      data['api_key'] = self._api_key
    if self._hash:
      data['hash'] = self._hash
    if self._is_account_owner:
      data['is_account_owner'] = self._is_account_owner
    if self._image:
      data['image'] = self._image
    if self._company:
      data['company'] = self._company
    if self._link_forms:
      data['link_forms'] = self._link_forms
    if self._create_themes:
      data['create_themes'] = self._create_themes
    if self._link_reports:
      data['link_reports'] = self._link_reports
    if self._user:
      data['user'] = self._user
    if self._create_reports:
      data['create_reports'] = self._create_reports
    if self._time_zone:
      data['time_zone'] = self._time_zone
    if self._create_forms:
      data['create_forms'] = self._create_forms
    if self._admin_access:
      data['admin_access'] = self._admin_access
    if self._email:
      data['email'] = self._email

    return data

  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data: A JSON dict, as converted from the JSON in the Wufoo API
    Returns:
      A wufoo.User instance
    '''

    # Compress the Field[id] values into maps
    fields = {}
    for k, v in data.items():
      if k.startswith('Field'):
        fields[k] = v

    return User(api_key=data.get('ApiKey', None),
                hash=data.get('Hash', None),
                is_account_owner=data.get('IsAccountOwner', None),
                image=data.get('Image', None),
                company=data.get('Company', None),
                link_forms=data.get('LinkForms', None),
                create_themes=data.get('CreateThemes', None),
                link_reports=data.get('LinkReports', None),
                user=data.get('User', None),
                create_reports=data.get('CreateReports', None),
                time_zone=data.get('TimeZone', None),
                create_forms=data.get('CreateForms', None),
                admin_access=data.get('AdminAccess', None),
                email=data.get('Email', None))

class Filter(object):
  ''' A class for constructing Entry query filters
  
  Consists of
  
  {ID} {Operator} {Value}
  
  Can filter on any valid Field ID
  
  Valid operators

      * 'contains';
      * 'does_not_contain';
      * 'begins_with';
      * 'ends_with';
      * 'is_less_than';
      * 'is_greater_than';
      * 'is_on';
      * 'is_before';
      * 'is_after';
      * 'is_not_equal_to';
      * 'is_equal_to';
      * 'is_not_null';
  
  Value is not needed for the is_not_NULL operator
  
  '''
  
  def __init__(self, field_id, operator, value=None):
    self._field_id = field_id
    self._value = value
    
    self._operator_map = {
    'contains':'Contains',
    'does_not_contain':'Does_not_contain',
    'begins_with':'Begins_with',
    'ends_with':'Ends_with',
    'is_less_than':'Is_less_than',
    'is_greater_than':'Is_greater_than',
    'is_on':'Is_on',
    'is_before':'Is_before',
    'is_after':'Is_after',
    'is_not_equal_to':'Is_not_equal_to',
    'is_equal_to':'Is_equal_to',
    'is_not_null':'Is_not_NULL'
    }
    
    if operator not in self._operator_map.keys():
      raise ValueError('Operator must be defined one of the following: ' + ', '.join(self._operator_map.keys()))
    
    self._operator = operator
    
  @property
  def field_id(self):
    return self._field_id
  
  @property
  def operator(self):
    return self._operator
  
  @property
  def value(self):
    return self._value
  
  def __str__(self):
    op = self._operator_map[self.operator]
    
    if self._value is None:
      ret = "%s+%s" % (self.field_id, op)
    else:
      ret = "%s+%s+%s" % (self.field_id, op, self.value)
    return ret
    
class Entry(object):
  ''' A class for representing the Entry object in the Wufoo API
  '''
  
  def __init__(self, fields=None, entry_id=None, date_created=None, created_by=None, date_updated=None, updated_by=None, status=None, purchase_total=None, ip=None, last_page=None, currency=None, transaction_id=None, complete_submission=None, merchant_type=None):
    self._fields = fields
    self._entry_id=entry_id
    self._date_created=date_created
    self._created_by=created_by
    self._date_updated=date_updated
    self._updated_by=updated_by
    self._status=status
    self._purchase_total=purchase_total
    self._ip=ip
    self._last_page=last_page
    self._currency=currency
    self._transaction_id=transaction_id
    self._complete_submission=complete_submission
    self._merchant_type=merchant_type

  @property
  def entry_id(self):
    return self._entry_id

  @property
  def date_created(self):
    return dateutil.parser.parse(self._date_created)

  @property
  def created_by(self):
    return self._created_by

  @property
  def date_updated(self):
    return dateutil.parser.parse(self._date_updated)

  @property
  def updated_by(self):
    return self._updated_by

  @property
  def status(self):
    return self._status

  @property
  def purchase_total(self):
    return self._purchase_total

  @property
  def ip(self):
    return self._ip

  @property
  def last_page(self):
    return self._last_page

  @property
  def currency(self):
    return self._currency

  @property
  def transaction_id(self):
    return self._transaction_id

  @property
  def complete_submission(self):
    return self._complete_submission

  @property
  def merchant_type(self):
    return self._merchant_type

  @property 
  def fields(self):
    return self._fields
    
  def __str__(self):
    '''A string representation of this wufoo.Entry instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this wufoo.Entry instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this wufoo.Entry instance.

    Returns:
      A JSON string representation of this wufoo.Entry instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this wufoo.Entry instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this wufoo.Entry instance
    '''
    data = {}
    
    if self._fields:
      data['fields'] = self._fields
    if self._entry_id:
      data['entry_id'] = self._entry_id
    if self._date_created:
      data['date_created'] = self._date_created
    if self._created_by:
      data['created_by'] = self._created_by
    if self._date_updated:
      data['date_updated'] = self._date_updated
    if self._updated_by:
      data['updated_by'] = self._updated_by
    if self._status:
      data['status'] = self._status
    if self._purchase_total:
      data['purchase_total'] = self._purchase_total
    if self._ip:
      data['ip'] = self._ip
    if self._last_page:
      data['last_page'] = self._last_page
    if self._currency:
      data['currency'] = self._currency
    if self._transaction_id:
      data['transaction_id'] = self._transaction_id
    if self._complete_submission:
      data['complete_submission'] = self._complete_submission
    if self._merchant_type:
      data['merchant_type'] = self._merchant_type
      
    return data
    
  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data: A JSON dict, as converted from the JSON in the Wufoo API
    Returns:
      A wufoo.Entry instance
    '''
    
    # Compress the Field[id] values into maps
    fields = {}
    for k, v in data.items():
      if k.startswith('Field'):
        fields[k] = v
    
    return Entry(fields=fields,
                  entry_id=data.get('EntryId', None),
                  date_created=data.get('DateCreated', None),
                  created_by=data.get('CreatedBy', None),
                  date_updated=data.get('DateUpdated', None),
                  updated_by=data.get('UpdatedBy', None),
                  status=data.get('Status', None),
                  purchase_total=data.get('PurchaseTotal', None),
                  ip=data.get('IP', None),
                  last_page=data.get('LastPage', None),
                  currency=data.get('Currency', None),
                  transaction_id=data.get('TransactionId', None),
                  complete_submission=data.get('CompleteSubmission', None),
                  merchant_type=data.get('MerchantType', None))


class Report(object):
  '''A class representing the Report structure used by the Wufoo API.
  '''
  
  def __init__(self, link_entries=None, hash=None, name=None, url=None, is_public=None, date_created=None, link_fields=None, link_widgets=None, date_updated=None, link_entries_count=None, description=None):
    self._link_entries=link_entries
    self._hash=hash
    self._name=name
    self._url=url
    self._is_public=is_public
    self._date_created=date_created
    self._link_fields=link_fields
    self._link_widgets=link_widgets
    self._date_updated=date_updated
    self._link_entries_count=link_entries_count
    self._description=description
    
  @property
  def link_entries(self):
    return self._link_entries

  @property
  def hash(self):
    return self._hash

  @property
  def name(self):
    return self._name

  @property
  def url(self):
    return self._url

  @property
  def is_public(self):
    return self._is_public

  @property
  def date_created(self):
    return dateutil.parser.parse(self._date_created)

  @property
  def link_fields(self):
    return self._link_fields

  @property
  def link_widgets(self):
    return self._link_widgets

  @property
  def date_updated(self):
    return dateutil.parser.parse(self._date_updated)

  @property
  def link_entries_count(self):
    return self._link_entries_count

  @property
  def description(self):
    return self._description

  def __str__(self):
    '''A string representation of this wufoo.Report instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this wufoo.Report instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this wufoo.Report instance.

    Returns:
      A JSON string representation of this wufoo.Report instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this wufoo.Report instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this wufoo.Report instance
    '''
    data = {}
    if self._link_entries:
      data['link_entries'] = self._link_entries
    if self._hash:
      data['hash'] = self._hash
    if self._name:
      data['name'] = self._name
    if self._url:
      data['url'] = self._url
    if self._is_public:
      data['is_public'] = self._is_public
    if self._date_created:
      data['date_created'] = self._date_created
    if self._link_fields:
      data['link_fields'] = self._link_fields
    if self._link_widgets:
      data['link_widgets'] = self._link_widgets
    if self._date_updated:
      data['date_updated'] = self._date_updated
    if self._link_entries_count:
      data['link_entries_count'] = self._link_entries_count
    if self._description:
      data['description'] = self._description

    return data

  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data: A JSON dict, as converted from the JSON in the Wufoo API
    Returns:
      A wufoo.Report instance
    '''
    return Report(link_entries=data.get('LinkEntries', None),
                  hash=data.get('Hash', None),
                  name=data.get('Name', None),
                  url=data.get('Url', None),
                  is_public=data.get('IsPublic', None),
                  date_created=data.get('DateCreated', None),
                  link_fields=data.get('LinkFields', None),
                  link_widgets=data.get('LinkWidgets', None),
                  date_updated=data.get('DateUpdated', None),
                  link_entries_count=data.get('LinkEntriesCount', None),
                  description=data.get('Description', None))  

class Form(object):
  ''' A class for representing the data in a Wufoo Form
  '''
  def __init__(self,
               start_date=None,
               link_entries=None,
               end_date=None,
               name=None,
               language=None,
               url=None,
               redirect_message=None,
               is_public=None,
               date_created=None,
               link_fields=None,
               entry_limit=None,
               hash=None,
               date_updated=None,
               email=None,
               link_entries_count=None,
               description=None):
    self._start_date=start_date
    self._link_entries=link_entries
    self._end_date=end_date
    self._name=name
    self._language=language
    self._url=url
    self._redirect_message=redirect_message
    self._is_public=is_public
    self._date_created=date_created
    self._link_fields=link_fields
    self._entry_limit=entry_limit
    self._hash=hash
    self._date_updated=date_updated
    self._email=email
    self._link_entries_count=link_entries_count
    self._description=description
    
  @property
  def start_date(self):
    return dateutil.parser.parse(self._start_date)

  @property
  def link_entries(self):
    return self._link_entries

  @property
  def end_date(self):
    return dateutil.parser.parse(self._end_date)

  @property
  def name(self):
    return self._name

  @property
  def language(self):
    return self._language

  @property
  def url(self):
    return self._url

  @property
  def redirect_message(self):
    return self._redirect_message

  @property
  def is_public(self):
    return self._is_public

  @property
  def date_created(self):
    return dateutil.parser.parse(self._date_created)

  @property
  def link_fields(self):
    return self._link_fields

  @property
  def entry_limit(self):
    return self._entry_limit

  @property
  def hash(self):
    return self._hash

  @property
  def date_updated(self):
    return dateutil.parser.parse(self._date_updated)

  @property
  def email(self):
    return self._email

  @property
  def link_entries_count(self):
    return self._link_entries_count

  @property
  def description(self):
    return self._description

  def __str__(self):
    '''A string representation of this wufoo.Form instance.

    The return value is the same as the JSON string representation.

    Returns:
      A string representation of this wufoo.Form instance.
    '''
    return self.AsJsonString()

  def AsJsonString(self):
    '''A JSON string representation of this wufoo.Form instance.

    Returns:
      A JSON string representation of this wufoo.Form instance
   '''
    return simplejson.dumps(self.AsDict(), sort_keys=True)

  def AsDict(self):
    '''A dict representation of this wufoo.Form instance.

    The return value uses the same key names as the JSON representation.

    Return:
      A dict representing this wufoo.Form instance
    '''
    data = {}
    if self._start_date:
      data['start_date'] = self._start_date
    if self._link_entries:
      data['link_entries'] = self._link_entries
    if self._end_date:
      data['end_date'] = self._end_date
    if self._name:
      data['name'] = self._name
    if self._language:
      data['language'] = self._language
    if self._url:
      data['url'] = self._url
    if self._redirect_message:
      data['redirect_message'] = self._redirect_message
    if self._is_public:
      data['is_public'] = self._is_public
    if self._date_created:
      data['date_created'] = self._date_created
    if self._link_fields:
      data['link_fields'] = self._link_fields
    if self._entry_limit:
      data['entry_limit'] = self._entry_limit
    if self._hash:
      data['hash'] = self._hash
    if self._date_updated:
      data['date_updated'] = self._date_updated
    if self._email:
      data['email'] = self._email
    if self._link_entries_count:
      data['link_entries_count'] = self._link_entries_count
    if self._description:
      data['description'] = self._description
      
    return data

  @staticmethod
  def NewFromJsonDict(data):
    '''Create a new instance based on a JSON dict.

    Args:
      data: A JSON dict, as converted from the JSON in the Wufoo API
    Returns:
      A wufoo.Form instance
    '''
    return Form(start_date=data.get('StartDate', None),
                link_entries=data.get('LinkEntries', None),
                end_date=data.get('EndDate', None),
                name=data.get('Name', None),
                language=data.get('Language', None),
                url=data.get('Url', None),
                redirect_message=data.get('RedirectMessage', None),
                is_public=data.get('IsPublic', None),
                date_created=data.get('DateCreated', None),
                link_fields=data.get('LinkFields', None),
                entry_limit=data.get('EntryLimit', None),
                hash=data.get('Hash', None),
                date_updated=data.get('DateUpdated', None),
                email=data.get('Email', None),
                link_entries_count=data.get('LinkEntriesCount', None),
                description=data.get('Description', None))

# ----------------------------------------
#
# API class
#
# ----------------------------------------

class Api(object):

  _API_REALM = 'Wufoo API'

  def __init__(self,
               subdomain,
               apikey,
               input_encoding=None,
               request_headers=None):
    '''Instantiate a new wufoo.Api object.

    Args:
      subdomain: The subdomain of the Wufoo account
      apikey: The API key of the Wufoo account. 
      input_encoding: The encoding used to encode input strings. [optional]
      request_header: A dictionary of additional HTTP request headers. [optional]
    '''
    self._urllib = urllib2
    self._InitializeRequestHeaders(request_headers)
    self._InitializeUserAgent()
    self._InitializeDefaultParameters()
    self._input_encoding = input_encoding
    self.SetCredentials(apikey)
    self.SetSubdomain(subdomain)

  def SetSubdomain(self, subdomain):
    self._subdomain = subdomain
    
  def SetCredentials(self, apikey):
    self._apikey = apikey

  def GetFieldsForForm(self, form_hash, system=None):
    return self._GetFields('forms', form_hash, system)
    
  def GetFieldsForReport(self, report_hash, system=None):
    return self._GetFields('reports', report_hash, system)

  def _GetFields(self, for_what, identifier, system=None):
    '''Fetch all the fields.

    Returns:
      A sequence of wufoo.Field instances, one for each field
    '''
    parameters = {}
    if system:
      parameters['system'] = system
      
    url = "https://%s.wufoo.com/api/v3/%s/%s/fields.json" % (self._subdomain, for_what, identifier)
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)
        
    return [Field.NewFromJsonDict(x) for x in data['Fields']]

  def GetForms(self):
    '''Fetch the sequence of all forms for a user.

    Returns:
      A sequence of wufoo.Form instances, one for each form
    '''
    parameters = {}
    url = "https://%s.wufoo.com/api/v3/forms.json" % self._subdomain
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)
    
    return [Form.NewFromJsonDict(x) for x in data['Forms']]

  def GetForm(self, hash):
    '''Fetch a single form for a user.

    Args:
      hash:
        Returns the Form with the specified hash
    
    Returns:
      The wufoo.Form instance that corresponds to the given hash

    '''
    parameters = {}
    url = "https://%s.wufoo.com/api/v3/forms/%s.json" % (self._subdomain, hash)
    
    try:
      json = self._FetchUrl(url, parameters=parameters)
    except HTTPError, ef:
      if ef.msg == 'Invalid identifier.':
        raise WufooError(ef.msg)
      else:
        # A different type of HTTP error
        raise ef
      
    data = simplejson.loads(json)
  
    return Form.NewFromJsonDict(data['Forms'][0])

  def GetReports(self):
    '''Fetch the sequence of all reports for a user.
    
    Returns:
      A sequence of wufoo.Report instances, one for each report
    '''
    parameters = {}
    url = "https://%s.wufoo.com/api/v3/reports.json" % self._subdomain
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)
    
    return [Report.NewFromJsonDict(x) for x in data['Reports']]   
    
  def GetReport(self, hash):
    '''Fetch a single report for a user.

    Args:
      hash:
        Returns the Report with the specified hash
    
    Returns:
      The wufoo.Report instance that corresponds to the given hash

    '''
    parameters = {}
    url = "https://%s.wufoo.com/api/v3/reports/%s.json" % (self._subdomain, hash)
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)

    if data['Reports'][0] is None:
      raise WufooError('Invalid identifier.')

    return Report.NewFromJsonDict(data['Reports'][0])
  
  def GetFormEntryCount(self, hash):
    '''Fetch the entry count for a Form
    
    Args:
      hash:
        Returns the count of the entries for the Form with the specified hash
    
    Returns:
      An integer count of the number of entries
    '''    
    parameters = {}
    
    url = "https://%s.wufoo.com/api/v3/forms/%s/entries/count.json" % (self._subdomain, hash)
    
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)

    return int(data['EntryCount'])
  
  def GetReportEntryCount(self, hash):
    '''Fetch the entry count for a Report

    Args:
      hash:
        Returns the count of the entries for the Report with the specified hash

    Returns:
      An integer count of the number of entries
    '''
    parameters = {}

    url = "https://%s.wufoo.com/api/v3/reports/%s/entries/count.json" % (self._subdomain, hash)

    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)

    return int(data['EntryCount']) 
    
  def GetEntriesForForm(self, hash, system=False, filters=None, match='AND', sort_id=None, sort_direction='DESC', page_start=None, page_size=None):
    return self._GetEntries(hash, 'forms', system=system, filters=filters, match=match, sort_id=sort_id, sort_direction=sort_direction, page_start=page_start, page_size=page_size)

  def GetEntriesForReport(self, hash, system=False, filters=None, match='AND', sort_id=None, sort_direction='DESC', page_start=None, page_size=None):
    return self._GetEntries(hash, 'reports', system=system, filters=filters, match=match, sort_id=sort_id, sort_direction=sort_direction, page_start=page_start, page_size=page_size)
    
  def _GetEntries(self, hash, for_what, system=False, filters=None, match='AND', sort_id=None, sort_direction='DESC', page_start=None, page_size=None):
    '''Fetch all entries related to a Report or Form

    Args:
      for_what:
        Either "form" or "report"
      hash:
        Returns the Entries from the form with the specified hash
      system:
        Set to True to include system fields
      filter:
        List of filters applied to the results
      match:
        'AND' or 'OR' to chain together filters
      sort_id:
        Field ID to sort on. See the Field API
      sort_direction:
        Sort direction, either ASC or DESC
      page_start:
        Page to start on (0 by default)
      page_end:
        Page to end on

    Returns:
      Set of wufoo.Entry instances that corresponds to the given Report or Form
    '''
    parameters = {}
    if system:
      parameters['system'] = 'true'
    if sort_id:
      parameters['sort'] = sort_id
    if sort_direction:
      parameters['sortDirection'] = sort_direction
    if page_start:
      parameters['pageStart'] = page_start
    if page_size:
      parameters['pageSize'] = page_size
    if match:
      parameters['match'] = match
    if filters:
      try:
        # Is it a list of filter objects?
        for (i, f) in zip(range(len(filters)), filters):
          parameters['Filter'+str(i)] = str(f)
      except (TypeError):
        # It's just one filter?
        parameters['Filter1'] = str(filters)

    url = "https://%s.wufoo.com/api/v3/%s/%s/entries.json" % (self._subdomain, for_what, hash)
    
    # The filter can't have the + signs url encoded.
    def re_plus(s):
      return s.replace('%2B', '+')
    
    json = self._FetchUrl(url, parameters=parameters, url_post_process=re_plus)
    data = simplejson.loads(json)

    return [Entry.NewFromJsonDict(x) for x in data['Entries']]
  
  def GetUsers(self):
    url = "https://%s.wufoo.com/api/v3/users.json" % (self._subdomain)
    json = self._FetchUrl(url, parameters={})
    data = simplejson.loads(json)
    return [User.NewFromJsonDict(x) for x in data['Users']]

  def GetWidgets(self, report_hash):
    url = "https://%s.wufoo.com/api/v3/reports/%s/widgets.json" % (self._subdomain, report_hash)
    json = self._FetchUrl(url, parameters={})
    data = simplejson.loads(json)
    return [Widget.NewFromJsonDict(x, self._subdomain) for x in data['Widgets']]

  def GetComments(self, form_hash, entry_id=None, page_start=None, page_size=None):
    '''Fetch all comments related to a Form

    Args:
      for_what:
        Either "form" or "report"
      form_hash:
        Returns the Entries from the form with the specified hash
      entry_id
        Return only comments from a specific entry
      page_start:
        Page to start on (0 by default)
      page_size:
        Number of comments per page

    Returns:
      Set of wufoo.Comment instances that corresponds to the given Form
    '''
    parameters = {}
    if entry_id:
      parameters['entryId'] = entry_id
    if page_start:
      parameters['pageStart'] = page_start
    if page_size:
      parameters['pageSize'] = page_size

    url = "https://%s.wufoo.com/api/v3/forms/%s/comments.json" % (self._subdomain, form_hash)
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)

    return [Comment.NewFromJsonDict(x) for x in data['Comments']]
    
    
  def GetCommentCount(self, form_hash, entry_id=None):
    '''Fetch the number of comments for a form
    
    Args:
      hash:
        Returns the count of the entries for the Form with the specified hash
    
    Returns:
      An integer count of the number of entries
    '''    
    url = "https://%s.wufoo.com/api/v3/forms/%s/comments/count.json" % (self._subdomain, form_hash)
    
    parameters = {}
    if entry_id:
      parameters['entryId'] = entry_id
    
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)

    return int(data['Count'])
  
  def PostEntry(self, form_hash, entry_data):
    '''Post an entry for a form. Assumes data is well-formed.

    Args:
      form_hash:
        The identifier for the form to be submitted.
      data:
        A dictionary of the data to be submitted. Keys should correspond
        to field names.
    '''

    url = 'https://%s.wufoo.com/api/v3/forms/%s/entries.json' % (self._subdomain, form_hash)

    try:
      #print url
      json = self._FetchUrl(url, post_data=entry_data)
      # Error
      data = simplejson.loads(json)
      raise WufooError(data['ErrorText'])
    except HTTPError, e:
      # Success if 201 response
      json = e.read()
      data = simplejson.loads(json)
      
  def PutWebHook(self, form_hash, url, handshake_key=None, metadata=None):
    ''' Creates/Updates a web hook on a Wufoo form.
    
    Args:
      form_hash:
        The form to add the hook to
      url:
        The URL to receive web hook calls
      handshake_key:
        Optional authentication key to prevent spam
      metadata:
        Optional parameter to send along form/field metadata
    
    Returns:
      The web hook hash used to delete the web hook
    '''
    
    url = "https://%s.wufoo.com/api/v3/forms/%s/webhooks.json" % (self._subdomain, form_hash)
    
    post_data = {}
    post_data['url'] = url
    if handshake_key:
      post_data['handshakeKey'] = handshake_key
    if metadata:
      post_data['metadata'] = metadata
    
    json = self._FetchUrl(url, post_data=post_data)
    data = simplejson.loads(json)

  def ClearCredentials(self):
    '''Clear the username and password for this instance
    '''
    self._username = None
    self._password = None
    
  def SetUrllib(self, urllib):
    '''Override the default urllib implementation.

    Args:
      urllib: an instance that supports the same API as the urllib2 module
    '''
    self._urllib = urllib

  def GetUrllib(self):
    '''The the implementation of urllib used.
    
    Returns:
      The urllib instance used by this API wrapper
    '''
    return self._urllib

  def SetUserAgent(self, user_agent):
    '''Override the default user agent

    Args:
      user_agent: a string that should be send to the server as the User-agent
    '''
    self._request_headers['User-Agent'] = user_agent

  def _BuildUrl(self, url, path_elements=None, extra_params=None):
    # Break url into consituent parts
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

    # Add any additional path elements to the path
    if path_elements:
      # Filter out the path elements that have a value of None
      p = [i for i in path_elements if i]
      if not path.endswith('/'):
        path += '/'
      path += '/'.join(p)

    # Add any additional query parameters to the query string
    if extra_params and len(extra_params) > 0:
      extra_query = self._EncodeParameters(extra_params)
      # Add it to the existing query
      if query:
        query += '&' + extra_query
      else:
        query = extra_query

    # Return the rebuilt URL
    return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

  def _InitializeRequestHeaders(self, request_headers):
    if request_headers:
      self._request_headers = request_headers
    else:
      self._request_headers = {}

  def _InitializeUserAgent(self):
    user_agent = 'Python-urllib/%s (python-twitter/%s)' % \
                 (self._urllib.__version__, __version__)
    self.SetUserAgent(user_agent)

  def _InitializeDefaultParameters(self):
    self._default_params = {}

  def _AddAuthorizationHeader(self, username, password):
    if username and password:
      basic_auth = base64.encodestring('%s:%s' % (username, password))[:-1]
      self._request_headers['Authorization'] = 'Basic %s' % basic_auth

  def _RemoveAuthorizationHeader(self):
    if self._request_headers and 'Authorization' in self._request_headers:
      del self._request_headers['Authorization']

  def _GetOpener(self, url, username=None, password=None):
    if username and password:
      self._AddAuthorizationHeader(username, password)
      handler = self._urllib.HTTPBasicAuthHandler()
      (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
      handler.add_password(Api._API_REALM, netloc, username, password)
      opener = self._urllib.build_opener(handler)
    else:
      opener = self._urllib.build_opener()
    opener.addheaders = self._request_headers.items()
    return opener

  def _Encode(self, s):
    if self._input_encoding:
      return unicode(s, self._input_encoding).encode('utf-8')
    else:
      return unicode(s).encode('utf-8')

  def _EncodeParameters(self, parameters):
    '''Return a string in key=value&key=value form

    Values of None are not included in the output string.

    Args:
      parameters:
        A dict of (key, value) tuples, where value is encoded as
        specified by self._encoding
    Returns:
      A URL-encoded string in "key=value&key=value" form
    '''
    if parameters is None:
      return None
    else:
      return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in parameters.items() if v is not None]))

  def _EncodePostData(self, post_data):
    '''Return a string in key=value&key=value form

    Values are assumed to be encoded in the format specified by self._encoding,
    and are subsequently URL encoded.

    Args:
      post_data:
        A dict of (key, value) tuples, where value is encoded as
        specified by self._encoding
    Returns:
      A URL-encoded string in "key=value&key=value" form
    '''
    if post_data is None:
      return None
    else:
      return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in post_data.items()]))

  def _FetchUrl(self,
                url,
                post_data=None,
                parameters=None,
                url_post_process=None):
    '''Fetch a URL, optionally caching for a specified time.

    Args:
      url: The URL to retrieve
      post_data: 
        A dict of (str, unicode) key/value pairs.  If set, POST will be used.
      parameters:
        A dict whose key/value pairs should encoded and added 
        to the query string. [OPTIONAL]
      url_post_process:
        Function to post process the URL once it has been encoded. [OPTIONAL]

    Returns:
      A string containing the body of the response.
    '''
    # Build the extra parameters dict
    extra_params = {}
    if self._default_params:
      extra_params.update(self._default_params)
    if parameters:
      extra_params.update(parameters)

    # Add key/value parameters to the query string of the url
    url = self._BuildUrl(url, extra_params=extra_params)

    # Get a url opener that can handle basic auth
    opener = self._GetOpener(url, username=self._apikey, password="foo")

    encoded_post_data = self._EncodePostData(post_data)
    
    # HACK: is there a better way to do this?
    # In order for filtering to work, we can't url encode the + signs
    if url_post_process:
      url = url_post_process(url)
    
    # Open and return the URL
    url_data = opener.open(url, encoded_post_data).read()
    opener.close()
    
    return url_data
    
if __name__ == "__main__":
  pass
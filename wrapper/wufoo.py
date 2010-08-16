'''A library that provides a Python interface to the Wufoo API'''

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

class WufooError(Exception):
  '''Base class for Wufoo errors'''
  
  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class Report(object):
  '''A class representing the Report structure used by the Wufoo API.
  
  The Report class exposed the following properties:
  
  {'LinkEntries': 'https://marcpare.wufoo.com/api/v3/reports/z5p8s6/entries.json', 
  'Hash': 'z5p8s6', 
  'Name': 'Untitled Report',
  'Url': 'untitled-report', 
  'IsPublic': '0', 
  'DateCreated': '2010-08-08 17:47:34', 
  'LinkFields': 'https://marcpare.wufoo.com/api/v3/reports/z5p8s6/fields.json', 
  'LinkWidgets': 'https://marcpare.wufoo.com/api/v3/reports/z5p8s6/widgets.json', 
  'DateUpdated': '2010-08-08 17:47:34', 
  'LinkEntriesCount': 'https://marcpare.wufoo.com/api/v3/reports/z5p8s6/entries/count.json', 
  'Description': 'This is my report. View it in all its glory!'}
  
  ['LinkEntries', 'Hash', 'Name', 'Url', 'IsPublic', 'DateCreated', 'LinkFields', 'LinkWidgets', 'DateUpdated', 'LinkEntriesCount', 'Description']
  
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
  '''
  A sample JSON response:
  
  {'Forms': 
    [{'StartDate': '2000-01-01 12:00:00', 
      'LinkEntries': 'https://marcpare.wufoo.com/api/v3/forms/z7x4a9/entries.json', 
      'EndDate': '2030-01-01 12:00:00', 
      'Name': 'How awesome is Marc?', 
      'Language': 'english', 
      'Url': 'how-awesome-is-marc', 
      'RedirectMessage': 'Success! Thanks for filling out my form!', 
      'IsPublic': '1', 
      'DateCreated': '2010-08-04 02:31:53', 
      'LinkFields': 'https://marcpare.wufoo.com/api/v3/forms/z7x4a9/fields.json', 
      'EntryLimit': '0', 'Hash': 'z7x4a9', 'DateUpdated': '2010-08-11 00:26:02', 
      'Email': None, 
      'LinkEntriesCount': 'https://marcpare.wufoo.com/api/v3/forms/z7x4a9/entries/count.json', 
      escription': "This is my form. Please fill it out. It's awesome!"}
    ]}
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

class Api(object):

  _API_REALM = 'Wufoo API'

  def __init__(self,
               subdomain,
               apikey,
               input_encoding=None,
               request_headers=None):
    '''Instantiate a new wufoo.Api object.

    Args:
      subdomain: The subdomain of the WUfoo account
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

  def GetForms(self):
    '''Fetch the sequence of all forms for a user.

    Returns:
      A sequence of wufoo.Form instances, one for each form
    '''
    parameters = {}
    url = "https://%s.wufoo.com/api/v3/forms.json" % self._subdomain
    json = self._FetchUrl(url, parameters=parameters)
    data = simplejson.loads(json)
    
    print data
    
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

  def GetPublicTimeline(self, since_id=None):
    '''Fetch the sequnce of public twitter.Status message for all users.

    Args:
      since_id:
        Returns only public statuses with an ID greater than (that is,
        more recent than) the specified ID. [Optional]

    Returns:
      An sequence of twitter.Status instances, one for each message
    '''
    parameters = {}
    if since_id:
      parameters['since_id'] = since_id
    url = 'http://twitter.com/statuses/public_timeline.json'
    json = self._FetchUrl(url,  parameters=parameters)
    data = simplejson.loads(json)
    self._CheckForTwitterError(data)
    return [Status.NewFromJsonDict(x) for x in data]

  def PostUpdate(self, status, in_reply_to_status_id=None):
    '''Post a twitter status message from the authenticated user.

    The twitter.Api instance must be authenticated.

    Args:
      status:
        The message text to be posted.  Must be less than or equal to
        140 characters.
      in_reply_to_status_id:
        The ID of an existing status that the status to be posted is
        in reply to.  This implicitly sets the in_reply_to_user_id
        attribute of the resulting status to the user ID of the
        message being replied to.  Invalid/missing status IDs will be
        ignored. [Optional]
    Returns:
      A twitter.Status instance representing the message posted.
    '''
    if not self._username:
      raise TwitterError("The twitter.Api instance must be authenticated.")

    url = 'http://twitter.com/statuses/update.json'

    if len(status) > CHARACTER_LIMIT:
      raise TwitterError("Text must be less than or equal to %d characters. "
                         "Consider using PostUpdates." % CHARACTER_LIMIT)

    data = {'status': status}
    if in_reply_to_status_id:
      data['in_reply_to_status_id'] = in_reply_to_status_id
    json = self._FetchUrl(url, post_data=data)
    data = simplejson.loads(json)
    self._CheckForTwitterError(data)
    return Status.NewFromJsonDict(data)

  def DestroyDirectMessage(self, id):
    '''Destroys the direct message specified in the required ID parameter.

    The twitter.Api instance must be authenticated, and the
    authenticating user must be the recipient of the specified direct
    message.

    Args:
      id: The id of the direct message to be destroyed

    Returns:
      A twitter.DirectMessage instance representing the message destroyed
    '''
    url = 'http://twitter.com/direct_messages/destroy/%s.json' % id
    json = self._FetchUrl(url, post_data={})
    data = simplejson.loads(json)
    self._CheckForTwitterError(data)
    return DirectMessage.NewFromJsonDict(data)

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

  def SetXTwitterHeaders(self, client, url, version):
    '''Set the X-Twitter HTTP headers that will be sent to the server.

    Args:
      client:
         The client name as a string.  Will be sent to the server as
         the 'X-Twitter-Client' header.
      url:
         The URL of the meta.xml as a string.  Will be sent to the server
         as the 'X-Twitter-Client-URL' header.
      version:
         The client version as a string.  Will be sent to the server
         as the 'X-Twitter-Client-Version' header.
    '''
    self._request_headers['X-Twitter-Client'] = client
    self._request_headers['X-Twitter-Client-URL'] = url
    self._request_headers['X-Twitter-Client-Version'] = version

  def SetSource(self, source):
    '''Suggest the "from source" value to be displayed on the Twitter web site.

    The value of the 'source' parameter must be first recognized by
    the Twitter server.  New source values are authorized on a case by
    case basis by the Twitter development team.

    Args:
      source:
        The source name as a string.  Will be sent to the server as
        the 'source' parameter.
    '''
    self._default_params['source'] = source

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

  def _CheckForTwitterError(self, data):
    """Raises a TwitterError if twitter returns an error message.

    Args:
      data: A python dict created from the Twitter json response
    Raises:
      TwitterError wrapping the twitter error message if one exists.
    """
    # Twitter errors are relatively unlikely, so it is faster
    # to check first, rather than try and catch the exception
    if 'error' in data:
      raise TwitterError(data['error'])

  def _FetchUrl(self,
                url,
                post_data=None,
                parameters=None):
    '''Fetch a URL, optionally caching for a specified time.

    Args:
      url: The URL to retrieve
      post_data: 
        A dict of (str, unicode) key/value pairs.  If set, POST will be used.
      parameters:
        A dict whose key/value pairs should encoded and added 
        to the query string. [OPTIONAL]

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

    # Open and return the URL
    url_data = opener.open(url, encoded_post_data).read()
    opener.close()
    
    return url_data
    
if __name__ == "__main__":
  
  wufoo = Api("footest", "W9NL-EB7O-LYRQ-SZNT")
  #wufoo.GetForms()
  
  #for x in wufoo.GetForms():
  #  print str(x)
    
  # Nice! The difference between when the form was updated and right now
  #wufoo.GetForms()
  a_form = wufoo.GetForm('m7x3p9adf')
  # updated = a_form.date_updated
  # print datetime.datetime.now() - updated


  
  
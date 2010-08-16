'''Unit tests for API wrapper.

Using [pyfacebook](http://github.com/sciyoshi/pyfacebook/) to learn unit testing
for an API wrapper.

Run the tests in the wrapper directory with nosetests.

Note: mocking depends on using urllib2 as the opener.

What to test?

# Tests:
# GetForm for a valid hash
# GetForm for an invalid hash
# Date accessors in mock

  global response_str
  response = {'stuff':'abcd'}
  response_str = simplejson.dumps(response)
  fb = facebook.Facebook(my_api_key, my_secret_key)
  fb.login = self.login
  fb.auth.createToken()
  self.assertEquals(str(fb.auth_token['stuff']),"abcd")
  fb.login()
  response = {"session_key":"key","uid":"my_uid","secret":"my_secret","expires":"my_expires"}
  response_str = simplejson.dumps(response)
  res = fb.auth.getSession()
  self.assertEquals(str(res["expires"]),response["expires"])
  self.assertEquals(str(res["secret"]),response["secret"])
  self.assertEquals(str(res["session_key"]),response["session_key"])
  self.assertEquals(str(res["uid"]),response["uid"])

  response = {'Forms': 
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
      'EntryLimit': '0', 
      'Hash': 'z7x4a9', 
      'DateUpdated': '2010-08-11 00:26:02', 
      'Email': None, 
      'LinkEntriesCount': 'https://marcpare.wufoo.com/api/v3/forms/z7x4a9/entries/count.json', 
      'Description': "This is my form. Please fill it out. It's awesome!"}, 
      { 'StartDate': '2000-01-01 12:00:00', 
        'LinkEntries': 'https://marcpare.wufoo.com/api/v3/forms/m7x3k1/entries.json', 
        'EndDate': '2030-01-01 12:00:00', 
        'Name': 'This is gonna be awesome', 
        'Language': 'english', 
        'Url': 'this-is-gonna-be-awesome', 
        'RedirectMessage': 'Success! Thanks for filling out my form!', 
        'IsPublic': '1',
        'DateCreated': '2010-08-12 03:34:32', 
        'LinkFields': 'https://marcpare.wufoo.com/api/v3/forms/m7x3k1/fields.json', 
        'EntryLimit': '0', 
        'Hash': 'm7x3k1', 
        'DateUpdated': '2010-08-12 03:34:32', 
        'Email': None, 
        'LinkEntriesCount': 'https://marcpare.wufoo.com/api/v3/forms/m7x3k1/entries/count.json', 
        'Description': "This is my form. Please fill it out. It's awesome!"}]}



'''

import unittest
import sys
import os
import wufoo
from wufoo import WufooError
import urllib2
import simplejson
from minimock import Mock

my_api_key = "W9NL-EB7O-LYRQ-SZNT"
my_subdomain = "footest"

response_str = '{"stuff":"abcd"}'
class MyUrlOpen:
    def __init__(self,*args,**kwargs):
        pass
    
    def read(self):
      global response_str
      return response_str

class wufoo_MockTests(unittest.TestCase):
  def setUp(self):      
      wufoo.urllib2.OpenerDirector.open = Mock('urllib2.OpenerDirector.open')
      wufoo.urllib2.OpenerDirector.open.mock_returns_func = MyUrlOpen      
      
  def tearDown(self):
      pass

  def login(self):
      pass

  def test1(self):
    global response_str
    response = {'Forms' : [ {}, {}, {} ]}
    response_str = simplejson.dumps(response)
    
    w = wufoo.Api(my_subdomain, my_api_key)
    forms = w.GetForms()
    
    self.assertEquals(len(forms), 3)
    
class wufoo_Livetests(unittest.TestCase):

  def test1(self):
    # Test getting forms
    w = wufoo.Api(my_subdomain, my_api_key)
    forms = w.GetForms()
    
    # Correct number of forms
    self.assertEquals(len(forms), 2)
    
    # Grab one of the values from each of the forms
    self.assertEquals(forms[0].url, 'extensive-cheese-survey')
    self.assertEquals(forms[1].url, 'short-cheese-survey')
    
    # Test getting a single form
    a_form = w.GetForm(forms[0].hash)
    self.assertEquals(a_form.hash, forms[0].hash)
    
    a_form = w.GetForm(forms[1].hash)
    self.assertEquals(a_form.hash, forms[1].hash)
    
    # Invalid identifier
    self.assertRaises(WufooError, w.GetForm, 'foo')
    
    
  def test2(self):
    # Test getting a report
    w = wufoo.Api(my_subdomain, my_api_key)
    reports = w.GetReports()
    
    # Correct number of reports
    self.assertEquals(len(reports), 1)
    
    # Value in a report
    self.assertEquals(reports[0].name, 'Cheese Report')
    
    # A single report
    a_report = w.GetReport(reports[0].hash)
    self.assertEquals(a_report.hash, reports[0].hash)
    
    # Invalid identifier
    self.assertRaises(WufooError, w.GetReport, 'foo')
      
if __name__ == "__main__":
  # Build the test suite
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(wufoo_MockTests))
  suite.addTest(unittest.makeSuite(wufoo_LiveTests))

  # Execute the test suite
  print("Testing Proxy class\n")
  result = unittest.TextTestRunner(verbosity=2).run(suite)
  # sys.exit(len(result.errors) + len(result.failures))
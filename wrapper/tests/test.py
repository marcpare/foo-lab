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

'''

import unittest
import sys
import os
import wufoo
from wufoo import WufooError, Filter
import urllib2
import simplejson
from minimock import Mock

my_api_key = "XXXX-XXXX-XXXX-XXXX"
my_subdomain = "test"

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
      
  def test3(self):
    w = wufoo.Api(my_subdomain, my_api_key)
    # Test getting entries for each of the forms and reports
    all_forms = w.GetForms()
    for x in all_forms:
      w.GetEntriesForForm(x.hash)
    
    all_reports = w.GetReports()
    for x in all_reports:
      w.GetEntriesForReport(x.hash)

    sample_entries = w.GetEntriesForForm( 'm7x3p9')

    self.assertEquals(sample_entries[0].fields['Field1'], '10.32')
    
    # Do we get a currency if we add the System field?
    sample_entries = w.GetEntriesForForm('m7x3p9', system=True)
    self.assertEquals(sample_entries[0].complete_submission, '1')
  
  def test4(self):
    w = wufoo.Api(my_subdomain, my_api_key)
    # Sorting
    one_way = w.GetEntriesForForm('m7x3p9', sort_id='Field1', sort_direction='ASC')
    other_way = w.GetEntriesForForm('m7x3p9', sort_id='Field1', sort_direction='DESC')
    
    # one_way[0]['Field1']: '10.32'
    # other_way[0]['Field1]: '11.10'
    self.assertTrue(float(one_way[0].fields['Field1']) <
                    float(other_way[0].fields['Field1']))
  
  def test5(self):
    w = wufoo.Api(my_subdomain, my_api_key)      
    # Paging
    self.assertFalse(w.GetEntriesForForm('m7x3p9', page_size=1, page_start=0)[0].fields['Field1'] ==
                     w.GetEntriesForForm('m7x3p9', page_size=1, page_start=1)[0].fields['Field1'])
    
    self.assertEqual(len(w.GetEntriesForForm('m7x3p9', page_size=1)), 1)

class wufoo_Filtertests(unittest.TestCase):

  def test1(self):
    self.assertEquals(str(Filter('EntryID', 'is_equal_to', 2)), 'EntryID+Is_equal_to+2')
  
  def test2(self):
    w = wufoo.Api(my_subdomain, my_api_key)      
    f1 = Filter('EntryId', 'is_equal_to', 2)
    entries = w.GetEntriesForForm('m7x3p9', filters=f1)
    self.assertEqual(len(entries), 1)
    
    print entries[0]
    self.assertEqual(entries[0].entry_id, '2')
    
    f1 = Filter('EntryId', 'is_equal_to', 2)
    f2 = Filter('EntryId', 'is_equal_to', 1)
    entries = w.GetEntriesForForm('m7x3p9', filters=[f1, f2])    
    self.assertEqual(len(entries), 0)
      
if __name__ == "__main__":
  
  # Run single tests with:
  # nosetests tests/test.py:wufooFilterTests
  
  pass
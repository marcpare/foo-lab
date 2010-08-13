'''Unit tests for API wrapper.

Using [pyfacebook](http://github.com/sciyoshi/pyfacebook/) to learn unit testing
for an API wrapper.

'''

import unittest
import sys
import os
import wufoo
import urllib2
import simplejson
from minimock import Mock

my_api_key = "ADGZ-9NNW-1U81-LVXA"
my_subdomain = "marcpare"

response_str = '{"stuff":"abcd"}'
class MyUrlOpen:
    def __init__(self,*args,**kwargs):
        pass
    
    def read(self):
        global response_str
        return response_str

class wufoo_UnitTests(unittest.TestCase):
  def setUp(self):
      wufoo.urllib2.urlopen = Mock('urllib2.urlopen')
      wufoo.urllib2.urlopen.mock_returns_func = MyUrlOpen
      pass

  def tearDown(self):
      pass

  def login(self):
      pass

  def test1(self):
    w = wufoo.Api(my_subdomain, my_api_key)
    print w.GetForms()
          
      
if __name__ == "__main__":
  # Build the test suite
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(wufoo_UnitTests))

  # Execute the test suite
  print("Testing Proxy class\n")
  result = unittest.TextTestRunner(verbosity=2).run(suite)
  # sys.exit(len(result.errors) + len(result.failures))
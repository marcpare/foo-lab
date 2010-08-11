#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

import os
import os.path

import urllib
import base64

# ----------------------------------------
#
# Utility functions
#
# ----------------------------------------

API-KEY = "ADGZ-9NNW-1U81-LVXA"
SUBDOMAIN = "marcpare"

def renderPageHelper(self, filename, template_values = {}, include_session_data = True):	
	path = os.path.join(os.path.dirname(__file__), filename)
	self.response.out.write(template.render(path, template_values))

# ----------------------------------------
#
# Request Handler classes
#
# ----------------------------------------

class MainPage(webapp.RequestHandler):
	def get(self):
		renderPageHelper(self, 'views/index.html', {})
		
class AddHook(webapp.RequestHandler):
    def get(self):
        # This is where we use an API wrapper that we've written
        # For now: do it w/ curl

        pass

def main():
    handlers = []
    handlers.append(('/', MainPage))
    handlers.append(('/addhook', AddHook))
    
    application = webapp.WSGIApplication(handlers, debug=True)
    util.run_wsgi_app(application)
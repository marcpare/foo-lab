
def gen_init(var_list):

  format_string = '''%s=None'''
  
  final_string = "def __init__(self, "
  for x in var_list:
    final_string += format_string % x + ", "
  
  final_string = final_string[0:-2] + "):\n"
  
  format_string2 = '''  self._%(x)s=%(x)s'''
  
  for x in var_list:
    final_string += format_string2 % {"x": x} + "\n"
  
  print final_string

def gen_AsDict(var_list):
  format_string = '''
if self._%(x)s:
  data['%(x)s'] = self._%(x)s'''
  
  final = ""
  for x in var_list:
    final += format_string % {"x": x}
    
  print final

def gen_NewFromJsonDict(var_list, json_var_list):
  format_string = '''%s=data.get('%s', None)'''

  final = "Form("
  
  for (x, y) in zip(var_list, json_var_list):
    final += format_string % (x, y) + ",\n"
  
  final = final[0:-2] + ")"
  
  print final  

def gen_properties(var_list):
  format_string = '''
@property
def %(x)s(self):
  return self._%(x)s
'''
  date_format_string = '''
@property
def %(x)s(self):
  return dateutil.parser.parse(self._%(x)s)
'''
  
  final = ""
  for x in var_list:
    if "date" in x:
      final += date_format_string % {"x": x}
    else:
      final += format_string % {"x": x}
      
  print final

if __name__ == "__main__":
  
  form_vars = ['start_date', 
               'link_entries', 
               'end_date',
               'name', 
               'language', 
               'url',
               'redirect_message',
               'is_public', 
               'date_created', 
               'link_fields', 
               'entry_limit', 
               'hash', 
               'date_updated',
               'email', 
               'link_entries_count', 
               'description']
  form_json_vars = ['StartDate', 'LinkEntries', 'EndDate', 'Name', 'Language', 'Url', 'RedirectMessage', 'IsPublic', 'DateCreated', 'LinkFields', 'EntryLimit', 'Hash', 'DateUpdated', 'Email', 'LinkEntriesCount', 'Description']
          
  # gen_AsDict(form_vars)
  # gen_NewFromJsonDict(form_vars, form_json_vars)
  # gen_properties(form_vars)
  
  report_vars = ['link_entries', 'hash', 'name', 'url', 'is_public', 'date_created', 'link_fields', 'link_widgets', 'date_updated', 'link_entries_count', 'description']
  report_json_vars = ['LinkEntries', 'Hash', 'Name', 'Url', 'IsPublic', 'DateCreated', 'LinkFields', 'LinkWidgets', 'DateUpdated', 'LinkEntriesCount', 'Description']
  
  gen_init(report_vars)
  gen_AsDict(report_vars)
  gen_NewFromJsonDict(report_vars, report_json_vars)
  gen_properties(report_vars)
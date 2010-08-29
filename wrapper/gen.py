

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

def gen_NewFromJsonDict(class_name, var_list, json_var_list):
  format_string = '''%s=data.get('%s', None)'''

  final = "%s(" % class_name
  
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
    if "date" in x and not x == 'updated_by':
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
  # gen_NewFromJsonDict('Form', form_vars, form_json_vars)
  # gen_properties(form_vars)
  
  report_vars = ['link_entries', 'hash', 'name', 'url', 'is_public', 'date_created', 'link_fields', 'link_widgets', 'date_updated', 'link_entries_count', 'description']
  report_json_vars = ['LinkEntries', 'Hash', 'Name', 'Url', 'IsPublic', 'DateCreated', 'LinkFields', 'LinkWidgets', 'DateUpdated', 'LinkEntriesCount', 'Description']
  
  # gen_init(report_vars)
  # gen_AsDict(report_vars)
  # gen_NewFromJsonDict('Report', report_vars, report_json_vars)
  # gen_properties(report_vars)
  
  entry_vars = ['entry_id', 'date_created', 'created_by', 'date_updated', 'updated_by', 'status', 'purchase_total', 'ip', 'last_page', 'currency', 'transaction_id', 'complete_submission', 'merchant_type']
  entry_json_vars = ['EntryId', 'DateCreated', 'CreatedBy', 'DateUpdated', 'UpdatedBy', 'Status', 'PurchaseTotal', 'IP', 'LastPage', 'Currency', 'TransactionId', 'CompleteSubmission', 'MerchantType']
  
  #gen_init(entry_vars)
  #gen_AsDict(entry_vars)
  #gen_NewFromJsonDict('Entry', entry_vars, entry_json_vars)
  #gen_properties(entry_vars)
  

  user_vars = ['api_key', 'hash', 'is_account_owner', 'image', 'company', 'link_forms', 'create_themes', 'link_reports', 'user', 'create_reports', 'time_zone', 'create_forms', 'admin_access', 'email']
  user_json_vars = ['ApiKey', 'Hash', 'IsAccountOwner', 'Image', 'Company', 'LinkForms', 'CreateThemes', 'LinkReports', 'User', 'CreateReports', 'TimeZone', 'CreateForms', 'AdminAccess', 'Email']
  # gen_init(user_vars)
  # gen_AsDict(user_vars)
  # gen_NewFromJsonDict('User', user_vars, user_json_vars)
  # gen_properties(user_vars)
  
  widget_vars = ['type', 'type_desc', 'hash', 'name', 'size']
  widget_json_vars = ['Type', 'TypeDesc', 'Hash', 'Name', 'Size']
  # gen_init(widget_vars)
  # gen_properties(widget_vars)
  # gen_AsDict(widget_vars)
  # gen_NewFromJsonDict('Widget', widget_vars, widget_json_vars)
  
  comment_vars = ['commented_by', 'comment_id', 'date_created', 'entry_id', 'text']
  comment_json_vars = ['CommentedBy', 'CommentId', 'DateCreated', 'EntryId', 'Text']
  # gen_init(comment_vars)
  # gen_properties(comment_vars)
  # gen_AsDict(comment_vars)
  # gen_NewFromJsonDict('Comment', comment_vars, comment_json_vars)
  
  field_vars = ['type', 'id', 'title', 'is_required', 'subfields', 'label', 'score', 'choices']
  field_json_vars = ['Type', 'ID', 'Title', 'IsRequired', 'SubFields', 'Label', 'Score', 'Choices']
  gen_init(field_vars)
  gen_properties(field_vars)
  gen_AsDict(field_vars)
  gen_NewFromJsonDict('Field', field_vars, field_json_vars)
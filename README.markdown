### Wufoo Python API Wrapper

Wouldn't a be nice to use Python to deal with your Wufoo data? Now you can!

This API wrapper makes working with the Wufoo API easier within Python. The abstraction is simple for now and there is no new functionality to learn. The API is meant to look and feel like Python should.

P.S. this is a labor of love as part of a bigger project, so feel free to send feedback on improvements.

### Basics

First, authenticate with your Wufoo account:

    wf = wufoo.Api("subdomain", "XXXX-XXXX-XXXX-XXXX")

Each specific API has its own functions. It should be unsurprising how to use each one. For instance, here is how we would get data on an account's users:

    users = wf.GetUsers()

Return values are wrapped in classes with properties to expose their fields. For our fictional users:

    for user in users:
        print user.email

Optional parameters are added as keyword arguments:

    forms = wf.GetComments("x7x7x7", page_start=15)

The full API documentation is below.
    
### Full API Documentation

Wufoo API spec available here: http://wufoo.com/docs/api/v3/users/
    
### Users

Information about all users:

    wf.GetUsers()
    
Full documentation: http://wufoo.com/docs/api/v3/users/

### Widgets

Get all the widgets:

    wf.GetWidgets()
    
You can easily generate the embed code for a widget:

    wf.embed_code()

### Forms

Information about all forms:

    wf.GetForms()
    
Information about a specific form:
    
    wf.GetForm("x7x7x7")

Full documentation: http://wufoo.com/docs/api/v3/forms/

### Entries

Entries from a form:

    wf.GetEntriesForForm("m7x3r3")
        
Entries from a report:

    wf.GetEntriesForReport("r9x5r6")
    
Get the number of entries:

    wf.GetFormEntryCount("m7x3r3")
    wf.GetReportEntryCount("r9x5r6")

Entries can be filtered by creating a Filter object:

    f1 = Filter('EntryId', 'is_equal_to', 2)
    f2 = Filter('EntryId', 'is_equal_to', 1)
    wufoo.GetEntriesForForm('m7x3p9', filters=[f1, f2])

Optional:

* match
* system
* match ('AND' or 'OR') 
* sort_id
* sort_direction
* page_start
* page_size

POST an entry by providing a dictionary with the field data:

    wf.PostEntry("m7x3r3", {"Field2": 10.42})

Full documentation: http://wufoo.com/docs/api/v3/entries/

### Fields

Fields of a form:

    wf.GetFieldsForForm("r7x2s9")
    
Fields of a report:

    wf.GetFieldsForReport("r7x2s9")
    
`SubFields` and `Choices` get created as instances of the Field class, as well. So,
you can do something like:

    fields = wf.GetFieldsForReport("r7x2s9")
    for field in fields:
        if field.choices:
            for choice in choices:
                print choice.label + ": " + choice.score

Full documentation: http://wufoo.com/docs/api/v3/fields/

### Comments

Comments are entered in the Wufoo.com Entry Manager. 

Get the number of comments for a form:

    wf.GetCommentCount("w7x1p5")

Optional:

* entry_id
    
Get comments from a form:

    wf.GetComments("w7x1p5")

Optional:

* entry_id
* page_start
* page_size
    
Full documentation: http://wufoo.com/docs/api/v3/comments/
    
### Reports

Information about all reports:
    
    wf.GetReports()

Information about single report:

    wf.GetReport("m5p7k0")

Full documentation: http://wufoo.com/docs/api/v3/reports/

### Web Hooks

Add a web hook to a form

    wf.PutWebHook("m5p7k0", "http://www.example.com")
    
Optional:

* handshake_key
* metadata

### To Do

- More robust testing (especially mock tests)
- Remove web hooks
- Log in API (restricted)
# Wammu - Phone manager
# Copyright (c) 2003-4 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Misc functions like charset conversion, entries parsers,..
'''

import wx
import codecs
import locale
import sys

fallbacklocalecharset = 'iso-8859-1'

# Determine "correct" character set
try:
    # works only in python > 2.3
    localecharset = locale.getpreferredencoding()
except:
    try:
        localecharset = locale.getdefaultlocale()[1]
    except:
        try:
            localecharset = sys.getdefaultencoding()
        except:
            localecharset = fallbacklocalecharset
if localecharset in [None, 'ANSI_X3.4-1968']:
    localecharset = fallbacklocalecharset

charsetencoder = codecs.getencoder(localecharset)

def StrConv(txt):
    """
    This function coverts something (txt) to string form usable by wxPython. There
    is problem that in default configuration in most distros (maybe all) default
    encoding for unicode objects is ascii. This leads to exception when converting
    something different than ascii. And this exception is not catched inside
    wxPython and leads to segfault.

    So if wxPython supports unicode, we give it unicode, otherwise locale
    dependant text.
    """
    try:
        if wx.USE_UNICODE:
            if type(txt) == type(u''):
                return txt
            if type(txt) == type(''):
                return unicode(txt, localecharset)
        else:
            if type(txt) == type(''):
                return txt
            if type(txt) == type(u''):
                return str(charsetencoder(txt)[0])
        return str(txt)
    except UnicodeEncodeError:
        return '???'

def UnicodeConv(txt):
    """
    This function coverts something (txt) to string form usable by wxPython. There
    is problem that in default configuration in most distros (maybe all) default
    encoding for unicode objects is ascii. This leads to exception when converting
    something different than ascii. And this exception is not catched inside
    wxPython and leads to segfault.

    So if wxPython supports unicode, we give it unicode, otherwise locale
    dependant text.
    """
    try:
        if type(txt) == type(u''):
            return txt
        if type(txt) == type(''):
            return unicode(txt, localecharset)
        return unicode(str(txt), localecharset)
    except UnicodeEncodeError:
        return '???'

def Str_(txt):
    return StrConv(_(txt))

def GetItemType(txt):
    if txt == '':
        return None
    elif txt[-8:] == 'DATETIME':
        return 'datetime'
    elif txt[-4:] == 'DATE' or txt == 'Date':
        return 'date'
    elif txt == 'TEXT' or txt == 'LOCATION' or txt[:4] == 'Text':
        return 'text'
    elif txt == 'PHONE' or txt[:6] == 'Number':
        return 'phone'
    elif txt == 'CONTACTID':
        return 'contact'
    elif txt == 'PRIVATE' or txt == 'Private' or txt == 'COMPLETED':
        return 'bool'
    elif txt == 'Category' or txt == 'CATEGORY':
        return 'category'
    elif txt == 'PictureID' or txt == 'RingtoneID' or txt == 'RingtoneFileSystemID':
        return 'id'
    else:
        return 'number'
        
def SearchLocation(list, loc, second = None):
    result = -1
    for i in range(len(list)):
        if second != None:
            if not list[i][second[0]] == second[1]:
                continue
        if type(list[i]['Location']) == type(loc):
            if loc == list[i]['Location']:
                result = i
                break
        else:
            if str(loc) in list[i]['Location'].split(', '):
                result = i
                break
    return result

def SearchItem(list, item):
    for i in range(len(list)):
        if item == list[i]:
            return result
    return -1

def SearchNumber(list, number):
    for i in range(len(list)):
        for x in list[i]['Entries']:
            if GetItemType(x['Type']) == 'phone' and number == x['Value']:
                return i
    return -1

def GetContactLink(list, i, txt):
    return StrConv('<a href="memory://%s/%d">%s</a> (%s)</a>' % (list[i]['MemoryType'], list[i]['Location'], list[i]['Name'], txt))
    
def GetNumberLink(list, number):
    i = SearchNumber(list, number)
    if i == -1:
        return StrConv(number)
    return GetContactLink(list, i, number)

def GetTypeString(type, value, values, linkphone = True):
    t = GetItemType(type)
    if t == 'contact':
        i = SearchLocation(values['contact']['ME'], value)
        if i == -1:
            return '%d' % value
        else:
            return GetContactLink([] + values['contact']['ME'], i, str(value))
    elif linkphone and t == 'phone':
        return StrConv(GetNumberLink([] + values['contact']['ME'] + values['contact']['SM'], value))
    elif t == 'id':
        v = hex(value)
        if v[-1] == 'L':
            v = v[:-1]
        return v
    else:
        return StrConv(value)

def ParseMemoryEntry(entry):
    first = ''
    last = ''
    name = ''
    company = ''
    number = ''
    number_result = ''
    name_result = ''
    for i in entry['Entries']:
        if i['Type'] == 'Text_Name':
            name = i['Value']
        elif i['Type'] == 'Text_FirstName':
            first = i['Value']
        if i['Type'] == 'Text_LastName':
            last = i['Value']
        if i['Type'] == 'Text_Company':
            company = i['Value']
        if i['Type'] == 'Number_General':
            number_result = i['Value']
        elif i['Type'][:7] == 'Number_':
            number =  i['Value']
    if name != '':
        name_result = name
    elif first != '':
        if last != '':
            name_result = last + ', ' + first
        else:
            name_result = first
    elif last != '':
        name_result = last
    elif company != '':
        name_result = company
    else:
        name_result = ''
    if number_result == '':
        number_result = number
    entry['Number'] = number_result
    entry['Name'] = name_result

def ParseTodo(entry):
    _ = Str_
    dt = ''
    text = ''
    completed = ''
    for i in entry['Entries']:
        if i['Type'] == 'END_DATETIME':
            dt = str(i['Value'])
        elif i['Type'] == 'TEXT':
            text = i['Value']
        elif i['Type'] == 'COMPLETED':
            if i['Value']:
                completed = _('Yes')
            else:
                completed = _('No')
    entry['Completed'] = completed 
    entry['Text'] = text
    entry['Date'] = dt

def ParseCalendar(entry):
    start = ''
    end = ''
    text = ''
    completed = ''
    for i in entry['Entries']:
        if i['Type'] == 'END_DATETIME':
            end = str(i['Value'])
        elif i['Type'] == 'START_DATETIME':
            start = str(i['Value'])
        elif i['Type'] == 'TEXT':
            text = i['Value']
    entry['Text'] = text
    entry['Start'] = start
    entry['End'] = end

def ParseMessage(msg, parseinfo = False):
    txt = ''
    loc = ''
    msg['Folder'] = msg['SMS'][0]['Folder']
    msg['State'] = msg['SMS'][0]['State']
    msg['Number'] = msg['SMS'][0]['Number']
    msg['Name'] = StrConv(msg['SMS'][0]['Name'])
    msg['DateTime'] = msg['SMS'][0]['DateTime']
    if parseinfo:
        for i in msg['SMSInfo']['Entries']:
            if i['Buffer'] != None:
                txt = txt + i['Buffer']
    else:
        for i in msg['SMS']:
            txt = txt + i['Text']
    for i in msg['SMS']:
        if loc != '':
            loc = loc + ', '
        loc = loc + str(i['Location'])
    msg['Text'] = txt
    msg['Location'] = loc

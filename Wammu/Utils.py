import wx
import codecs
import locale
import sys

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
            localecharset = 'ascii'

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


def GetItemType(str):
    if str == '':
        return None
    elif str[-8:] == 'DATETIME':
        return 'datetime'
    elif str[-4:] == 'DATE' or str == 'Date':
        return 'date'
    elif str == 'TEXT' or str == 'LOCATION' or str[:4] == 'Text':
        return 'text'
    elif str == 'PHONE' or str[:6] == 'Number':
        return 'phone'
    elif str == 'CONTACTID':
        return 'contact'
    elif str == 'PRIVATE' or str == 'Private' or str == 'COMPLETED':
        return 'bool'
    elif str == 'Category' or str == 'CATEGORY':
        return 'category'
    elif str == 'PictureID' or str == 'RingtoneID':
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
        return number
    return getcontactlink(list, i, number)

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
    else:
        name_result = last
    if number_result == '':
        number_result = number
    entry['Number'] = StrConv(number_result)
    entry['Name'] = StrConv(name_result)

def ParseTodo(entry):
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
    entry['Text'] = StrConv(text)
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
    entry['Text'] = StrConv(text)
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
    msg['Text'] = StrConv(txt)
    msg['Location'] = loc

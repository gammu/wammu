# -*- coding: UTF-8 -*-
'''
Wammu - Phone manager
Misc functions like charset conversion, entries parsers,..
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2006 Michal Čihař

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import wx
import codecs
import locale
import sys
import re
import string

import Wammu
if Wammu.gammu_error == None:
    import gammu

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

# prepare encoder for strings
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
                return str(charsetencoder(txt, 'replace')[0])
        return str(txt)
    except UnicodeEncodeError:
        return '???'

# detect html charset
htmlcharset = localecharset
if localecharset.lower() == 'utf-8' and not wx.USE_UNICODE:
    htmlcharset = 'iso-8859-1'
    if locale.getdefaultlocale()[0][:2] in ['cs', 'pl', 'sk']:
        htmlcharset = 'iso-8859-2'
    print StrConv(_('Warning: you are using utf-8 locales and non unicode enabled wxPython, some text migth be displayed incorrectly!'))
    print StrConv(_('Warning: assuming charset %s for html widget') % htmlcharset)

# prepare html encoder
htmlencoder = codecs.getencoder(htmlcharset)

def HtmlStrConv(txt):
    """
    This function coverts something (txt) to string form usable by wxPython
    html widget. There is problem that in default configuration in most distros
    (maybe all) default encoding for unicode objects is ascii. This leads to
    exception when converting something different than ascii. And this
    exception is not catched inside wxPython and leads to segfault.

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
                return str(htmlencoder(txt, 'replace')[0])
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
        return unicode('???')

def Str_(txt):
    return StrConv(_(txt))

def HtmlStr_(txt):
    return HtmlStrConv(_(txt))

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

def SearchLocation(lst, loc, second = None):
    result = -1
    for i in range(len(lst)):
        if second != None:
            if not lst[i][second[0]] == second[1]:
                continue
        if type(lst[i]['Location']) == type(loc):
            if loc == lst[i]['Location']:
                result = i
                break
        else:
            if str(loc) in lst[i]['Location'].split(', '):
                result = i
                break
    return result

def MatchesText(item, match, num):
    for x in item:
        if type(item) == dict:
            val = item[x]
        else:
            val = x
        if type(val) in (str, unicode):
            if match.search(val) != None:
                return True
        elif num is not None and type(val) == int and num == val:
            return True
        elif type(val) == list:
            for i in range(len(val)):
                val2 = val[i]['Value']
                if type(val2) in (str, unicode):
                    if match.search(val2) != None:
                        return True
                elif dig and type(val2) == int and num == val2:
                    return True
    return False


def SearchItem(lst, item):
    for i in range(len(lst)):
        if item == lst[i]:
            return i
    return -1

def GrabNumberPrefix(number, prefixes):
    if number[0] != '+':
        return None
    i = 2
    l = len(number)
    while not number[:i] in prefixes:
        i += 1
        if i > l:
            return None
    return number[:i]

'''Prefix for making international numbers'''
NumberPrefix = ''

NumberStrip = re.compile('^([#*]\d+[#*])?(\\+?.*)$')

def NormalizeNumber(number):
    # Strip magic prefixes (like no CLIR)
    nbmatch = NumberStrip.match(number)
    resnumber = nbmatch.group(2)
    # Add international prefix
    if resnumber[0] != '+':
        resnumber = NumberPrefix + resnumber
    return resnumber

def SearchNumber(lst, number):
    for i in range(len(lst)):
        for x in lst[i]['Entries']:
            if GetItemType(x['Type']) == 'phone' and NormalizeNumber(number) == NormalizeNumber(x['Value']):
                return i
    return -1

def GetContactLink(lst, i, txt):
    return StrConv('<a href="memory://%s/%d">%s</a> (%s)' % (lst[i]['MemoryType'], lst[i]['Location'], lst[i]['Name'], txt))

def GetNumberLink(lst, number):
    i = SearchNumber(lst, number)
    if i == -1:
        return StrConv(number)
    return GetContactLink(lst, i, number)

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
    entry['Synced'] = False
    return entry

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
    entry['Synced'] = False
    return entry

def ParseCalendar(entry):
    start = ''
    end = ''
    text = ''
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
    entry['Synced'] = False
    return entry

def ParseMessage(msg, parseinfo = False):
    txt = ''
    loc = ''
    msg['Folder'] = msg['SMS'][0]['Folder']
    msg['State'] = msg['SMS'][0]['State']
    msg['Number'] = msg['SMS'][0]['Number']
    msg['Name'] = msg['SMS'][0]['Name']
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
    try:
        tmp = StrConv(txt)
        msg['Text'] = txt
    except:
        s2 = ''
        for x in txt:
            if x in string.printable:
                s2 += x
        msg['Text'] = s2
    msg['Location'] = loc
    msg['Synced'] = False
    return msg

def ProcessMessages(list, synced):
    read = []
    unread = []
    sent = []
    unsent = []
    data = gammu.LinkSMS(list)

    for x in data:
        i = {}
        v = gammu.DecodeSMS(x)
        i['SMS'] = x
        if v != None:
            i['SMSInfo'] = v
        ParseMessage(i, (v != None))
        i['Synced'] = synced
        if i['State'] == 'Read':
            read.append(i)
        elif i['State'] == 'UnRead':
            unread.append(i)
        elif i['State'] == 'Sent':
            sent.append(i)
        elif i['State'] == 'UnSent':
            unsent.append(i)

    return {'read':read, 'unread':unread, 'sent':sent, 'unsent':unsent}

def FormatError(txt, info):
    _ = Str_
    if info['Code'] == gammu.Errors['ERR_NOTSUPPORTED']:
        message = _('Your phone doesn\'t support this function.')
    elif info['Code'] == gammu.Errors['ERR_NOTIMPLEMENTED']:
        message = _('This function is not implemented for your phone. If you want help with implementation please contact authors.')
    elif info['Code'] == gammu.Errors['ERR_SECURITYERROR']:
        message = _('Your phone asks for PIN.')
    elif info['Code'] == gammu.Errors['ERR_FULL']:
        message = _('Memory is full, try deleting some entries.')
    elif info['Code'] == gammu.Errors['ERR_CANCELED']:
        message = _('Communication canceled by phone, did you press cancel on phone?')
    elif info['Code'] == gammu.Errors['ERR_EMPTY']:
        message = _('Empty entry received. This usually should not happen and most likely is caused by bug in phone firmware or in Gammu/Wammu.\n\nIf you miss some entry, please contact Gammu/Wammu authors.')
    elif info['Code'] == gammu.Errors['ERR_INSIDEPHONEMENU']:
        message = _('Please close opened menu in phone and retry, data can not be accessed while you have opened them.')
    elif info['Code'] == gammu.Errors['ERR_TIMEOUT']:
        message = _('Timeout while trying to communicate with phone. Maybe phone is not connected (for cable) or out of range (for bluetooth or IrDA).')
    else:
        message = '%s %s\n%s %s\n%s %d' % (_('Description:'), StrConv(info['Text']), _('Function:'), info['Where'], _('Error code:'), info['Code'])
    return StrConv(txt + '\n\n' + message)

def FixupMaskedEdit(edit):
        # XXX: this is not clean way of reseting to system colour, but I don't know better.
        bgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
        fgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        setattr(edit, '_validBackgroundColour', bgc)
        setattr(edit, '_foregroundColour', fgc)

# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Misc functions like charset conversion, entries parsers,..
'''

import locale
import sys
import re
import wx
import string
import os
import base64
try:
    import grp
    HAVE_GRP = True
except ImportError:
    HAVE_GRP = False
import Wammu.Locales
from Wammu.Locales import StrConv
from Wammu.Locales import ugettext as _

import Wammu
if Wammu.gammu_error is None:
    import gammu


def GetItemType(txt):
    if txt == '':
        return None
    elif txt[-8:] == 'DATETIME' or txt == 'Date' or txt == 'LastModified' or txt == 'LAST_MODIFIED':
        return 'datetime'
    elif txt[-4:] == 'DATE':
        return 'date'
    elif txt in ['TEXT', 'DESCRIPTION', 'LOCATION', 'LUID'] or txt[:4] == 'Text':
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
    elif txt == 'Photo':
        return 'photo'
    else:
        return 'number'


def SearchLocation(lst, loc, second=None):
    result = -1
    for i in range(len(lst)):
        if second is not None:
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
    testkeys = ['Value', 'Text', 'Number']
    for x in item:
        if type(item) == dict:
            val = item[x]
        else:
            val = x
        if type(val) in (str, unicode):
            if match.search(val) is not None:
                return True
        elif num is not None and type(val) == int and num == val:
            return True
        elif type(val) == list:
            for i in range(len(val)):
                for key in testkeys:
                    try:
                        val2 = val[i][key]
                        if type(val2) in (str, unicode):
                            if match.search(val2) is not None:
                                return True
                        elif num is not None and type(val2) == int and num == val2:
                            return True
                    except KeyError:
                        # Ignore not found keys
                        pass
    return False


def SearchItem(lst, item):
    for i in range(len(lst)):
        if item == lst[i]:
            return i
    return -1


def GrabNumberPrefix(number, prefixes):
    l = len(number)
    if l == 0 or number[0] != '+':
        return None
    i = 2
    while number[:i] not in prefixes:
        i += 1
        if i > l:
            return None
    return number[:i]

'''Prefix for making international numbers'''
NumberPrefix = ''

NumberStrip = re.compile('^([#*]\d+[#*])?(\\+?.*)$')


def NormalizeNumber(number):
    '''
    Attempts to create international number from anything it receives.
    It does strip any network prefixes and attempts to properly add
    international prefix. However this is a bit tricky, as there are
    many ways which can break this.
    '''
    # Strip magic prefixes (like no CLIR)
    nbmatch = NumberStrip.match(number)
    resnumber = nbmatch.group(2)
    # If we stripped whole number, return original
    if len(resnumber) == 0:
        return number
    # Handle 00 prefix same as +
    if resnumber[0:2] == '00':
        resnumber = '+' + resnumber[2:]
    # Detect numbers with international prefix and without +
    # This can be national number in some countries (eg. US)
    if len(NumberPrefix) > 0 and NumberPrefix[0] == '+' and resnumber[:len(NumberPrefix) - 1] == NumberPrefix[1:]:
        resnumber = '+' + resnumber
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


def GetTypeString(type, value, values, linkphone=True):
    '''
    Returns string for entry in data dictionary. Formats it according to
    knowledge of format types.
    '''
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
    elif t == 'photo':
        return '<wxp module="Wammu.Image" class="EncodedBitmap">' + \
                    '<param name="image" value="' + \
                    base64.b64encode(value) + \
                    '">' + \
                    '</wxp>'
    else:
        return StrConv(value)


def ParseMemoryEntry(entry, config=None):
    first = ''
    last = ''
    name = ''
    nickname = ''
    formalname = ''
    company = ''
    number = ''
    number_result = ''
    name_result = ''
    date = None
    for i in entry['Entries']:
        if i['Type'] == 'Text_Name':
            name = i['Value']
        elif i['Type'] == 'Text_FirstName':
            first = i['Value']
        if i['Type'] == 'Text_LastName':
            last = i['Value']
        if i['Type'] == 'Text_NickName':
            nickname = i['Value']
        if i['Type'] == 'Text_FormalName':
            formalname = i['Value']
        if i['Type'] == 'Date':
            # Store date olny if it is more recent
            # This can happen in multiple call records
            if date is None:
                date = i['Value']
            else:
                if i['Value'] > date:
                    date = i['Value']
        if i['Type'] == 'Text_Company':
            company = i['Value']
        if i['Type'] == 'Number_General':
            number_result = i['Value']
        elif i['Type'][:7] == 'Number_':
            number = i['Value']

    if config is None:
        format = 'auto'
    else:
        format = config.Read('/Wammu/NameFormat')

    if format == 'custom':
        name_result = config.Read('/Wammu/NameFormatString') % {
            'Name': name,
            'FirstName': first,
            'LastName': last,
            'NickName': nickname,
            'FormalName': formalname,
            'Company': company,
        }
    else:
        if name != '':
            name_result = name
        elif first != '':
            if last != '':
                if format == 'auto-first-last':
                    name_result = '%s %s' % (first, last)
                else:
                    name_result = '%s, %s' % (last, first)
            else:
                name_result = first
        elif last != '':
            name_result = last
        elif nickname != '':
            name_result = nickname
        elif formalname != '':
            name_result = formalname
        else:
            name_result = ''

        if name_result == '':
            if company != '':
                name_result = company
        else:
            if company != '':
                name_result = '%s (%s)' % (name_result, company)

    if number_result == '':
        number_result = number

    entry['Number'] = number_result
    entry['Name'] = name_result
    entry['Synced'] = False
    entry['Date'] = date

    return entry


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
    entry['Text'] = text
    entry['Date'] = dt
    entry['Synced'] = False
    return entry


def ParseCalendar(entry):
    start = ''
    end = ''
    text = ''
    description = ''
    tone_alarm = None
    silent_alarm = None
    recurrence = None
    for i in entry['Entries']:
        if i['Type'] == 'END_DATETIME':
            end = str(i['Value'])
        elif i['Type'] == 'START_DATETIME':
            start = str(i['Value'])
        elif i['Type'] == 'TONE_ALARM_DATETIME':
            tone_alarm = _('enabled (tone)')
        elif i['Type'] == 'SILENT_ALARM_DATETIME':
            silent_alarm = _('enabled (silent)')
        elif i['Type'] == 'TEXT':
            text = i['Value']
        elif i['Type'] == 'DESCRIPTION':
            description = i['Value']
        elif i['Type'] == 'REPEAT_MONTH':
            recurrence = _('yearly')
        elif i['Type'] == 'REPEAT_DAY':
            recurrence = _('monthly')
        elif i['Type'] == 'REPEAT_FREQUENCY':
            if i['Value'] == 1:
                recurrence = _('daily')
            elif i['Value'] == 2:
                recurrence = _('biweekly')
        elif (i['Type'] == 'REPEAT_DAYOFWEEK'):
            if i['Value'] == 1:
                recurrence = _('weekly on monday')
            elif i['Value'] == 2:
                recurrence = _('weekly on tuesday')
            elif i['Value'] == 3:
                recurrence = _('weekly on wednesday')
            elif i['Value'] == 4:
                recurrence = _('weekly on thursday')
            elif i['Value'] == 5:
                recurrence = _('weekly on friday')
            elif i['Value'] == 6:
                recurrence = _('weekly on saturday')
            elif i['Value'] == 7:
                recurrence = _('weekly on sunday')

    if tone_alarm is not None:
        entry['Alarm'] = tone_alarm
    elif silent_alarm is not None:
        entry['Alarm'] = silent_alarm
    else:
        entry['Alarm'] = _('disabled')

    if recurrence is None:
        entry['Recurrence'] = _('nonrecurring')
    else:
        entry['Recurrence'] = recurrence

    if text == '':
        entry['Text'] = description
    elif description == '':
        entry['Text'] = text
    else:
        entry['Text'] = '%s (%s)' % (text, description)

    entry['Start'] = start
    entry['End'] = end
    entry['Synced'] = False
    return entry


def ParseMessage(msg, parseinfo=False):
    txt = ''
    loc = ''
    msg['Folder'] = msg['SMS'][0]['Folder']
    msg['State'] = msg['SMS'][0]['State']
    msg['Number'] = msg['SMS'][0]['Number']
    msg['Name'] = msg['SMS'][0]['Name']
    msg['DateTime'] = msg['SMS'][0]['DateTime']
    if parseinfo:
        for i in msg['SMSInfo']['Entries']:
            if i['Buffer'] is not None:
                txt = txt + i['Buffer']
    else:
        for i in msg['SMS']:
            txt = txt + i['Text']
    for i in msg['SMS']:
        if loc != '':
            loc = loc + ', '
        loc = loc + str(i['Location'])
    try:
        StrConv(txt)
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
        if v is not None:
            i['SMSInfo'] = v
        ParseMessage(i, (v is not None))
        i['Synced'] = synced
        if i['State'] == 'Read':
            read.append(i)
        elif i['State'] == 'UnRead':
            unread.append(i)
        elif i['State'] == 'Sent':
            sent.append(i)
        elif i['State'] == 'UnSent':
            unsent.append(i)

    return {
        'read': read,
        'unread': unread,
        'sent': sent,
        'unsent': unsent
    }


def FormatError(txt, info, gammu_config=None):
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
        message = _('Timeout while trying to communicate with phone. Maybe phone is not connected (for cable) or out of range (for Bluetooth or IrDA).')
    elif info['Code'] == gammu.Errors['ERR_DEVICENOTEXIST']:
        if gammu_config is None:
            message = _('Device for communication with phone does not exist. Maybe you don\'t have phone plugged or your configuration is wrong.')
        else:
            message = _('Device "%s" for communication with phone does not exist. Maybe you don\'t have phone plugged or your configuration is wrong.') % gammu_config['Device']
    elif info['Code'] == gammu.Errors['ERR_DEVICENOPERMISSION']:
        if sys.platform[:5] == 'linux':
            message_group = ' ' + _('Maybe you need to be member of some group to have acces to device.')
        else:
            message_group = ''
        if gammu_config is None:
            message = _('Can not access device for communication with phone.')
        else:
            check = CheckDeviceNode(gammu_config['Device'])
            if check[0] == -2:
                message = check[3]
                message_group = ''
            else:
                message = _('Can not access device "%s" for communication with phone.') % gammu_config['Device']
        if message_group != '':
            message += ' ' + message_group
    elif info['Code'] == gammu.Errors['ERR_NOSIM']:
        message = _('Can not access SIM card. Please check whether it is properly inserted in phone and/or try to reboot the phone by removing battery.')
    else:
        message = '%s %s\n%s %s\n%s %d' % (_('Description:'), StrConv(info['Text']), _('Function:'), info['Where'], _('Error code:'), info['Code'])
    return StrConv(txt + '\n\n' + message)


def FixupMaskedEdit(edit):
    # XXX: this is not clean way of reseting to system colour, but I don't know better.
    bgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
    fgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
    setattr(edit, '_validBackgroundColour', bgc)
    setattr(edit, '_foregroundColour', fgc)


def GetWebsiteLang():
    loc, charset = locale.getdefaultlocale()
    try:
        lang = loc[:2].lower()
        if lang in ('cs', 'de', 'es', 'fr', 'sk'):
            return '%s.' % lang
        return ''
    except TypeError:
        return ''


def DBUSServiceAvailable(bus, interface, try_start_service=False):
    try:
        import dbus
    except ImportError:
        return False
    obj = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
    dbus_iface = dbus.Interface(obj, 'org.freedesktop.DBus')
    avail = dbus_iface.ListNames()
    if interface not in avail and try_start_service:
        try:
            bus.start_service_by_name(interface)
            avail = dbus_iface.ListNames()
        except dbus.exceptions.DBusException:
            print 'Failed to start DBus service %s' % interface
    return interface in avail


def CheckDeviceNode(curdev):
    '''
    Checks whether it makes sense to perform searching on this device and
    possibly warns user about misconfigurations.

    Returns tuple of 4 members:
    - error code (0 = ok, -1 = device does not exits, -2 = no permissions)
    - log text
    - error dialog title
    - error dialog text
    '''
    if sys.platform == 'win32':
        try:
            import win32file
            if curdev[:3] == 'COM':
                try:
                    win32file.QueryDosDevice(curdev)
                    return (0, '', '', '')
                except:
                    return (-1,
                            _('Device %s does not exist!') % curdev,
                            _('Error opening device'),
                            _('Device %s does not exist!') % curdev
                            )
        except ImportError:
            return (0, '', '', '')
    if not os.path.exists(curdev):
        return (-1,
                _('Device %s does not exist!') % curdev,
                _('Error opening device'),
                _('Device %s does not exist!') % curdev
                )
    if not os.access(curdev, os.R_OK) or not os.access(curdev, os.W_OK):
        gid = os.stat(curdev).st_gid
        try:
            group = grp.getgrgid(gid)[0]
        except:
            group = str(gid)
        return (-2,
                _('You don\'t have permissions for %s device!') % curdev,
                _('Error opening device'),
                (_('You don\'t have permissions for %s device!') % curdev) +
                ' ' +
                (_('Maybe you need to be member of %s group.') % group)
                )
    return (0, '', '', '')


def CompatConfig(cfg):
    '''
    Adjust configuration for possible changes in Gammu history.
    '''

    # 1.27.0 changed handling of boolean options
    # Pre 1.27.0 used strings
    if tuple(map(int, gammu.Version()[1].split('.'))) < (1, 27, 0):
        if cfg['SyncTime']:
            cfg['SyncTime'] = 'yes'
        else:
            cfg['SyncTime'] = 'no'
        if cfg['LockDevice']:
            cfg['LockDevice'] = 'yes'
        else:
            cfg['LockDevice'] = 'no'
        if cfg['StartInfo']:
            cfg['StartInfo'] = 'yes'
        else:
            cfg['StartInfo'] = 'no'
    # 1.27.0 accepted only numbers
    if tuple(map(int, gammu.Version()[1].split('.'))) == (1, 27, 0):
        if cfg['SyncTime']:
            cfg['SyncTime'] = 1
        else:
            cfg['SyncTime'] = 0
        if cfg['LockDevice']:
            cfg['LockDevice'] = 1
        else:
            cfg['LockDevice'] = 0
        if cfg['StartInfo']:
            cfg['StartInfo'] = 1
        else:
            cfg['StartInfo'] = 0

    # Older versions did not use model auto
    if cfg['Model'] == 'auto':
        cfg['Model'] = ''

    return cfg

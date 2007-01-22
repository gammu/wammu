# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Module for writing SMS to Email.
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2007 Michal Čihař

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

from Wammu.Utils import SearchNumber
from Wammu.MessageDisplay import SmsTextFormat
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import email.Utils
import md5
import time
import tempfile
import os
import wx
import Wammu.Data
if Wammu.gammu_error == None:
    import gammu

header_format = 'X-Wammu-%s'
cid_format = '%d*sms@wammu.sms'

def XPMToPNG(image):
    # FIXME: I'd like to avoid creating temporary file, but even PIL doesn't seem to provide such functionality
    handle, name = tempfile.mkstemp()
    os.close(handle)
    bitmap = wx.BitmapFromXPMData(image)
    bitmap.SaveFile(name, wx.BITMAP_TYPE_PNG)
    f = file(name)
    data = f.read()
    f.close()
    os.unlink(name)
    return data

def RingtoneToMIDI(data):
    # FIXME: I'd like to avoid creating temporary file, but Gammmu doesn't provide such functionality
    handle, name = tempfile.mkstemp()
    f = os.fdopen(handle, 'w+')
    gammu.SaveRingtone(f, data, 'mid')
    f.seek(0)
    data = f.read()
    f.close()
    os.unlink(name)
    return data

def DateToString(dt):
    return email.Utils.formatdate(time.mktime(dt.timetuple()), True)

def SMSToMail(cfg, sms, lookuplist = None, mailbox = False):
    msg = MIMEMultipart('related', None, None, type='text/html')
    prepend = ''
    name = ''
    if lookuplist != None:
        i = SearchNumber(lookuplist, sms['Number'])
        if i != -1:
            msg.add_header(header_format % 'ContactID', str(i))
            name = '%s ' % lookuplist[i]['Name']

    for header in ['Folder', 'Memory', 'Location', 'Name', 'Type', 'State', 'Class', 'MessageReference']:
        msg.add_header(header_format % header, unicode(sms['SMS'][0][header]))
    msg.add_header(header_format % 'SMSC', sms['SMS'][0]['SMSC']['Number'])
    if sms['SMS'][0]['SMSCDateTime'] is not None:
        msg.add_header(header_format % 'SMSCDate', DateToString(sms['SMS'][0]['SMSCDateTime']))

    remote = '%s<%s@wammu.sms>' % (name, sms['Number'])
    local = 'Wammu <wammu@wammu.sms>' # FIXME: make this configurable?
    if sms['SMS'][0]['Type'] == 'Submit':
        msg['To'] = remote
        msg['From'] = local
    else:
        msg['To'] = local
        msg['From'] = remote
        prepend = ('Received: from %s via GSM\n' % unicode(sms['SMS'][0]['SMSC']['Number'])) + prepend

    if len(sms['Name']) > 0 :
        msg['Subject'] = SmsTextFormat(cfg, sms['Name'], False)
    else:
        msg['Subject'] = SmsTextFormat(cfg, sms['Text'], False)[:50] + '...'

    if sms['DateTime'] is not None:
        msg['Date'] = DateToString(sms['DateTime'])

    if sms.has_key('SMSInfo'):
        text = ''
        cid = 0
        for i in sms['SMSInfo']['Entries']:
            if i['ID'] in Wammu.Data.SMSIDs['PredefinedAnimation']:
                if i['Number'] > len(Wammu.Data.PredefinedAnimations):
                    sub = MIMEImage(XPMToPNG(Wammu.Data.UnknownPredefined))
                else:
                    sub = MIMEImage(XPMToPNG(Wammu.Data.PredefinedAnimations[i['Number']][1]))
                sub.add_header('Content-ID', '<%s>' % cid_format % cid)
                sub.add_header('Content-Disposition', 'inline')
                msg.attach(sub)
                text = text + '<img src="cid:%s">' % (cid_format % cid)
                cid = cid + 1

            if 0 and i['ID'] in Wammu.Data.SMSIDs['PredefinedSound']: # FIXME: need sounds
                if i['Number'] >= len(Wammu.Data.PredefinedSounds):
                    sub = ''
                else:
                    sub = ''
                sub.add_header('Content-Disposition', 'attachment')
                msg.attach(sub)

            if i['ID'] in Wammu.Data.SMSIDs['Sound']:
                sub = MIMEAudio(RingtoneToMIDI(i['Ringtone']), 'midi')
                sub.add_header('Content-Disposition', 'attachment')
                msg.attach(sub)

            if i['ID'] in Wammu.Data.SMSIDs['Text']:
                fmt = '%s'
                for x in Wammu.Data.TextFormats:
                    for name, txt, style in x[1:]:
                        if i.has_key(name) and i[name]:
                            fmt = style % fmt
                text = text + (fmt % SmsTextFormat(cfg, i['Buffer']))

            if i['ID'] in Wammu.Data.SMSIDs['Bitmap']:
                for x in i['Bitmap']:
                    sub = MIMEImage(XPMToPNG(x['XPM']))
                    sub.add_header('Content-ID', '<%s>' % cid_format % cid)
                    sub.add_header('Content-Disposition', 'inline')
                    msg.attach(sub)
                    text = text + '<img src="cid:%s">' % (cid_format % cid)
                    cid = cid + 1

            if i['ID'] in Wammu.Data.SMSIDs['Animation']:
                for x in i['Bitmap']:
                    sub = MIMEImage(XPMToPNG(x['XPM']))
                    sub.add_header('Content-ID', '<%s>' % cid_format % cid)
                    sub.add_header('Content-Disposition', 'inline')
                    msg.attach(sub)
                    text = text + '<img src="cid:%s">' % (cid_format % cid)
                    cid = cid + 1

    else:
        text = SmsTextFormat(cfg, sms['Text'])

    sub = MIMEText('<html><head></head><body>%s</body></html>' % text.encode('utf-8'), 'html', 'utf-8')
    msg.attach(sub)

    if sms['DateTime'] is not None:
        filename = '%s-%s-%s.eml' % (sms['SMS'][0]['Type'], sms['DateTime'].strftime("%Y%m%d%H%M%S"), md5.new(sms['Text'].encode('utf-8')).hexdigest())
    else:
        filename = '%s-%s.eml' % (sms['SMS'][0]['Type'], md5.new(sms['Text'].encode('utf-8')).hexdigest())

    # Add message ID
    msg.add_header('Message-ID', '<%s@%s>' % (filename[:-4], sms['Number']))

    if mailbox:
        if sms['DateTime'] is None:
            ts = email.Utils.formatdate(None, True)
        else:
            ts = DateToString(sms['DateTime'])
        prepend = ('From wammu@wammu.sms %s\n' % ts) + prepend

    return filename, prepend + msg.as_string()


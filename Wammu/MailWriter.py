# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2006 Michal Čihař
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
Module for writing SMS to Email.
'''

from Wammu.Utils import SearchNumber
from Wammu.MessageDisplay import SmsTextFormat
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import md5
import time
import tempfile
import os
import wx
import gammu
import Wammu.Data

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

def SMSToMail(cfg, sms, lookuplist = None, mailbox = False):
    msg = MIMEMultipart('related', None, None, type='text/html')
    name = ''
    if lookuplist != None:
        i = SearchNumber(lookuplist, sms['Number'])
        if i != -1:
            msg.add_header(header_format % 'ContactID', str(i))
            name = '%s ' % lookuplist[i]['Name']

    for header in ['Folder', 'Memory', 'Location', 'Name', 'Type', 'State', 'Class', 'MessageReference']:
        msg.add_header(header_format % header, str(sms['SMS'][0][header]))
    msg.add_header(header_format % 'SMSC', sms['SMS'][0]['SMSC']['Number'])
    if sms['SMS'][0]['SMSCDateTime'] is not None:
        msg.add_header(header_format % 'SMSCDate', sms['SMS'][0]['SMSCDateTime'].strftime('%a, %d %b %Y %H:%M:%S %z'))

    remote = '%s<%s@wammu.sms>' % (name, sms['Number'])
    local = 'Wammu <wammu@wammu.sms>' # FIXME: make this configurable?
    if sms['SMS'][0]['Type'] == 'Submit':
        msg['To'] = remote
        msg['From'] = local
    else:
        msg['To'] = local
        msg['From'] = remote

    msg['Subject'] = SmsTextFormat(cfg, sms['Text'], False)[:50] + '...'

    if sms['DateTime'] is not None:
        msg['Date'] = sms['DateTime'].strftime('%a, %d %b %Y %H:%M:%S %z')

    if sms.has_key('SMSInfo'):
        text = ''
        cid = 0
        for i in sms['SMSInfo']['Entries']:
            if i['ID'] in Wammu.Data.SMSIDs['PredefinedAnimation']:
                if i['Number'] > len(Wammu.Data.PredefinedAnimations):
                    sub = MIMEImage(XPMToPNG(Wammu.Data.UnknownPredefined))
                else:
                    sub = MIMEImage(XPMToPNG(Wammu.Data.PredefinedAnimations[i['Number']][1]))
                sub.add_header('Content-ID', '<%s>' % cid_format % cid);
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
                    sub.add_header('Content-ID', '<%s>' % cid_format % cid);
                    msg.attach(sub)
                    text = text + '<img src="cid:%s">' % (cid_format % cid)
                    cid = cid + 1

            if i['ID'] in Wammu.Data.SMSIDs['Animation']:
                for x in i['Bitmap']:
                    sub = MIMEImage(XPMToPNG(x['XPM']))
                    sub.add_header('Content-ID', '<%s>' % cid_format % cid);
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

    if mailbox:
        if sms['DateTime'] is not None:
            ts = sms['DateTime'].strftime('%a %b %d %H:%M:%S %Y')
        else:
            ts = time.asctime()
        prepend = 'From wammu@wammu.sms %s\n' % ts
    else:
        prepend = ''

    return filename, prepend + msg.as_string()


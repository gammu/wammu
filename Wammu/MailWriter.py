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
Module for writing SMS to Email.
'''

from Wammu.Utils import SearchNumber
from Wammu.MessageDisplay import SmsTextFormat
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import email.Utils
from hashlib import md5
import time
import tempfile
import os
import wx
import Wammu.Data
if Wammu.gammu_error is None:
    import gammu

HEADER_FORMAT = 'X-Wammu-%s'
CID_FORMAT = '%d*sms@wammu.sms'
PARTS_TO_HEADER = [
        'Folder',
        'Memory',
        'Location',
        'Name',
        'Type',
        'State',
        'Class',
        'MessageReference',
        ]


def XPMToPNG(image):
    '''
    Convert XPM data to PNG image.

    @todo: I'd like to avoid creating temporary file, but even PIL doesn't
    seem to provide such functionality.
    '''
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
    '''
    Converts ringtone to MIDI data.

    @todo: I'd like to avoid creating temporary file, but Gammmu doesn't
    provide such functionality.
    '''
    handle, name = tempfile.mkstemp()
    f = os.fdopen(handle, 'w+')
    gammu.SaveRingtone(f, data, 'mid')
    f.seek(0)
    data = f.read()
    f.close()
    os.unlink(name)
    return data

def DateToString(date):
    '''
    Convert date to RFC 2822 format.
    '''
    return email.Utils.formatdate(time.mktime(date.timetuple()), True)

def SMSToMail(cfg, sms, lookuplist=None, mailbox=False):
    '''
    Converts SMS to formated mail. It will contain all images and sounds from
    message and predefined animations. Also text formatting is preserved in
    HTML.
    '''
    msg = MIMEMultipart('related', None, None, type='text/html')
    prepend = ''
    name = ''
    if lookuplist is not None:
        i = SearchNumber(lookuplist, sms['Number'])
        if i != -1:
            msg.add_header(HEADER_FORMAT % 'ContactID', str(i))
            name = '%s ' % lookuplist[i]['Name']

    for header in PARTS_TO_HEADER:
        msg.add_header(HEADER_FORMAT % header, unicode(sms['SMS'][0][header]))
    msg.add_header(HEADER_FORMAT % 'SMSC', sms['SMS'][0]['SMSC']['Number'])
    if sms['SMS'][0]['SMSCDateTime'] is not None:
        msg.add_header(
            HEADER_FORMAT % 'SMSCDate', DateToString(sms['SMS'][0]['SMSCDateTime'])
        )

    remote = '%s<%s@wammu.sms>' % (name, sms['Number'].replace(' ', '_'))
    local = cfg.Read('/MessageExport/From')

    if sms['SMS'][0]['Type'] == 'Submit':
        msg['To'] = remote
        msg['From'] = local
    else:
        msg['To'] = local
        msg['From'] = remote
        prepend = (
            'Received: from %s via GSM\n' % unicode(sms['SMS'][0]['SMSC']['Number'])
        ) + prepend

    if len(sms['Name']) > 0:
        msg['Subject'] = SmsTextFormat(cfg, sms['Name'], False)
    else:
        msg['Subject'] = SmsTextFormat(cfg, sms['Text'], False)[:50] + '...'

    if sms['DateTime'] is not None:
        msg['Date'] = DateToString(sms['DateTime'])

    if 'SMSInfo' in sms:
        text = ''
        cid = 0
        for i in sms['SMSInfo']['Entries']:
            if i['ID'] in Wammu.Data.SMSIDs['PredefinedAnimation']:
                if i['Number'] > len(Wammu.Data.PredefinedAnimations):
                    sub = MIMEImage(XPMToPNG(Wammu.Data.UnknownPredefined))
                else:
                    img = Wammu.Data.PredefinedAnimations[i['Number']][1]
                    xpm = XPMToPNG(img)
                    sub = MIMEImage(xpm)
                sub.add_header('Content-ID', '<%s>' % CID_FORMAT % cid)
                sub.add_header('Content-Disposition', 'inline')
                msg.attach(sub)
                text = text + '<img src="cid:%s">' % (CID_FORMAT % cid)
                cid = cid + 1

            # FIXME: need sounds
            if 0 and i['ID'] in Wammu.Data.SMSIDs['PredefinedSound']:
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
                for format_data in Wammu.Data.TextFormats:
                    for name, dummy, style in format_data[1:]:
                        if name in i and i[name]:
                            fmt = style % fmt
                text = text + (fmt % SmsTextFormat(cfg, i['Buffer']))

            if i['ID'] in Wammu.Data.SMSIDs['Bitmap']:
                for bitmap in i['Bitmap']:
                    sub = MIMEImage(XPMToPNG(bitmap['XPM']))
                    sub.add_header('Content-ID', '<%s>' % CID_FORMAT % cid)
                    sub.add_header('Content-Disposition', 'inline')
                    msg.attach(sub)
                    text = text + '<img src="cid:%s">' % (CID_FORMAT % cid)
                    cid = cid + 1

            if i['ID'] in Wammu.Data.SMSIDs['Animation']:
                for bitmap in i['Bitmap']:
                    sub = MIMEImage(XPMToPNG(bitmap['XPM']))
                    sub.add_header('Content-ID', '<%s>' % CID_FORMAT % cid)
                    sub.add_header('Content-Disposition', 'inline')
                    msg.attach(sub)
                    text = text + '<img src="cid:%s">' % (CID_FORMAT % cid)
                    cid = cid + 1

    else:
        text = SmsTextFormat(cfg, sms['Text'])

    html = '<html><head></head><body>%s</body></html>'
    sub = MIMEText(html % text.encode('utf-8'), 'html', 'utf-8')
    msg.attach(sub)

    if sms['DateTime'] is not None:
        filename = '%s-%s-%s.eml' % (
                sms['SMS'][0]['Type'],
                sms['DateTime'].strftime("%Y%m%d%H%M%S"),
                md5(sms['Text'].encode('utf-8')).hexdigest())
    else:
        filename = '%s-%s.eml' % (
                sms['SMS'][0]['Type'],
                md5(sms['Text'].encode('utf-8')).hexdigest())

    # Add message ID
    msgid = '<%s@%s>' % (filename[:-4], sms['Number'].replace(' ', '_'))
    msgid = msgid.encode('ascii', 'xmlcharrefreplace')
    msg.add_header('Message-ID', msgid)

    if mailbox:
        if sms['DateTime'] is None:
            timestamp = time.asctime(time.localtime(None))
        else:
            timestamp = time.asctime(sms['DateTime'].timetuple())
        prepend = ('From wammu@wammu.sms %s\n' % timestamp) + prepend

    return filename, prepend + msg.as_string(), msgid

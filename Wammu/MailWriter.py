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
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import md5
import Wammu.Data

header_format = 'X-Wammu-%s'

def SMSToMail(cfg, sms, lookuplist = None):
    msg = MIMEMultipart()
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

    msg['Subject'] = SmsTextFormat(cfg, sms['Text'])[:50] + '...'

    if sms['DateTime'] is not None:
        msg['Date'] = sms['DateTime'].strftime('%a, %d %b %Y %H:%M:%S %z')

    if sms.has_key('SMSInfo'):
        for i in sms['SMSInfo']['Entries']:
            if 0 and i['ID'] in Wammu.Data.SMSIDs['PredefinedAnimation']: # FIXME: make real image
                if i['Number'] > len(Wammu.Data.PredefinedAnimations):
                    sub = MIMEImage(Wammu.Data.UnknownPredefined)
                else:
                    sub = MIMEImage(Wammu.Data.PredefinedAnimations[i['Number']][1])
                sub.add_header('Content-Disposition', 'attachment')
                msg.attach(sub)

            if 0 and i['ID'] in Wammu.Data.SMSIDs['PredefinedSound']: # FIXME: need sounds
                if i['Number'] >= len(Wammu.Data.PredefinedSounds):
                    sub = ''
                else:
                    sub = ''
                sub.add_header('Content-Disposition', 'attachment')
                msg.attach(sub)

            if 0 and i['ID'] in Wammu.Data.SMSIDs['Sound']: # FIXME: convert to midi and attach
                sub = i['Ringtone']
                sub.add_header('Content-Disposition', 'attachment')
                msg.attach(sub)

            if i['ID'] in Wammu.Data.SMSIDs['Text']:
                # FIXME: handle text formatting
                sub = MIMEText(SmsTextFormat(cfg, i['Buffer']).encode('utf-8'), 'plain', 'utf-8')
                sub.add_header('Content-Disposition', 'attachment')
                msg.attach(sub)

            if 0 and i['ID'] in Wammu.Data.SMSIDs['Bitmap']: # FIXME: make real image
                for x in i['Bitmap']:
                    sub = MIMEImage(x['XPM'])
                    sub.add_header('Content-Disposition', 'attachment')
                    msg.attach(sub)

            if 0 and i['ID'] in Wammu.Data.SMSIDs['Animation']: # FIXME: make real animation
                for x in i['Bitmap']:
                    sub = MIMEImage(x['XPM'])
                    sub.add_header('Content-Disposition', 'attachment')
                    msg.attach(sub)

    else:
        sub = MIMEText(SmsTextFormat(cfg, sms['Text']).encode('utf-8'), 'plain', 'utf-8')
        msg.attach(sub)

    if sms['DateTime'] is not None:
        filename = '%s-%s-%s.eml' % (sms['SMS'][0]['Type'], sms['DateTime'].strftime("%Y%m%d%H%M%S"), md5.new(sms['Text'].encode('utf-8')).hexdigest())
    else:
        filename = '%s-%s.eml' % (sms['SMS'][0]['Type'], md5.new(sms['Text'].encode('utf-8')).hexdigest())

    return filename, msg.as_string()


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
Message to HTML conversion
'''

import Wammu
import Wammu.Data
import Wammu.Ringtone
import string
import re
import xml.sax.saxutils
from Wammu.Locales import UnicodeConv, HtmlStrConv, ugettext as _

def SmsTextFormat(cfg, txt, dohtml=True, doxml=False):
    if txt is None:
        return ''
    if cfg.Read('/Message/Format') == 'yes':
        parts = []
        arr = txt.split(' ')
        for a in arr:
            if re.match('^([a-z]+[^ ]*)?[A-Z].*[a-z]{2,}[A-Z]{2,}.*$', a) is not None:
                prevtype = 'p'
                if UnicodeConv(string.lowercase).find(a[0]) != -1:
                    curtype = 'l'
                elif UnicodeConv(string.uppercase).find(a[0]) != -1:
                    curtype = 'u'
                elif UnicodeConv(string.digits).find(a[0]) != -1:
                    curtype = 'd'
                else:
                    curtype = 'p'

                s = a[0]

                for x in a[1:]:
                    if UnicodeConv(string.lowercase).find(x) != -1:
                        nexttype = 'l'
                    elif UnicodeConv(string.uppercase).find(x) != -1:
                        nexttype = 'u'
                    elif UnicodeConv(string.digits).find(x) != -1:
                        nexttype = 'd'
                    else:
                        nexttype = 'p'

                    if curtype == nexttype:
                        s += x
                    else:
                        if curtype == 'u' and nexttype == 'l' and prevtype == 'p' and len(s) == 1:
                            curtype = 'l'
                            prevtype = 'u'
                            s += x
                            continue
                        if curtype == 'p':
                            parts[-1] += s
                        elif curtype == 'u':
                            parts.append(s.lower())
                        else:
                            parts.append(s)
                        s = x
                        prevtype = curtype
                        curtype = nexttype

                if curtype == 'p':
                    parts[-1] += s
                elif curtype == 'u':
                    parts.append(s.lower())
                else:
                    parts.append(s)
                s = x
            else:
                parts.append(a)
        ret = ' '.join(parts)
    else:
        ret = txt
    if dohtml or doxml:
        xmlsafe = xml.sax.saxutils.escape(ret)
        if doxml:
            return xmlsafe.replace('\n', '<br />')
        else:
            return xmlsafe.replace('\n', '<br>')
    else:
        return ret.replace('\n', ' ')

def SmsToHtml(cfg, v):
    if 'SMSInfo' in v:
        text = ''
        ringno = 0
        Wammu.Ringtone.ringtones = {}
        for i in v['SMSInfo']['Entries']:
            if i['ID'] in Wammu.Data.SMSIDs['PredefinedAnimation']:
                if i['Number'] > len(Wammu.Data.PredefinedAnimations):
                    text = text + \
                        '<wxp module="Wammu.Image" class="Bitmap">' + \
                        '<param name="tooltip" value="' + (_('Predefined animation number %d') % i['Number']) + '">' + \
                        '<param name="image" value="' + "['" + string.join(Wammu.Data.UnknownPredefined, "', '") + "']" + '">' + \
                        '</wxp>'
                else:
                    text = text + \
                        '<wxp module="Wammu.Image" class="Bitmap">' + \
                        '<param name="tooltip" value="' + Wammu.Data.PredefinedAnimations[i['Number']][0] + '">' + \
                        '<param name="image" value="' + "['" + string.join(Wammu.Data.PredefinedAnimations[i['Number']][1], "', '") + "']" + '">' + \
                        '</wxp>'

            if i['ID'] in Wammu.Data.SMSIDs['PredefinedSound']:
                if i['Number'] >= len(Wammu.Data.PredefinedSounds):
                    desc = _('Unknown predefined sound #%d') % i['Number']
                else:
                    desc = Wammu.Data.PredefinedSounds[i['Number']][0]
                text = text + \
                    '[<wxp module="Wammu.Image" class="Bitmap">' + \
                    '<param name="image" value="' + "['" + string.join(Wammu.Data.Note, "', '") + "']" + '">' + \
                    '</wxp>' + desc + ']'

            if i['ID'] in Wammu.Data.SMSIDs['Sound']:
                Wammu.Ringtone.ringtones[ringno] = i['Ringtone']
                text = text + \
                    '<wxp module="Wammu.Ringtone" class="Ringtone">' + \
                    '<param name="tooltip" value="' + i['Ringtone']['Name'] + '">' + \
                    '<param name="ringno" value="' + str(ringno) + '">' + \
                    '</wxp>'
                ringno += 1

            if i['ID'] in Wammu.Data.SMSIDs['Text']:
                fmt = '%s'
                for x in Wammu.Data.TextFormats:
                    for name, txt, style in x[1:]:
                        if name in i and i[name]:
                            fmt = style % fmt
                text = text + (fmt % SmsTextFormat(cfg, i['Buffer']))

            if i['ID'] in Wammu.Data.SMSIDs['Bitmap']:
                x = i['Bitmap'][0]
                text = text + \
                    '<wxp module="Wammu.Image" class="Bitmap">' + \
                    '<param name="scale" value="(' + str(cfg.ReadInt('/Message/ScaleImage')) + ')">' + \
                    '<param name="image" value="' + "['" + string.join(x['XPM'], "', '") + "']" + '">' + \
                    '</wxp>'

            if i['ID'] in Wammu.Data.SMSIDs['Animation']:
                data = []
                for x in i['Bitmap']:
                    data.append("['" + string.join(x['XPM'], "', '") + "']")
                text = text + \
                    '<wxp module="Wammu.Image" class="Throbber">' + \
                    '<param name="scale" value="(' + str(cfg.ReadInt('/Message/ScaleImage')) + ')">' + \
                    '<param name="images" value="' + "[" + string.join(data, ", ") + "]" + '">' + \
                    '</wxp>'
        if 'Unknown' in v['SMSInfo'] and v['SMSInfo']['Unknown']:
            text = ('<table border="1" bgcolor="#dd7777" color="#000000"><tr><td>%s</td></tr></table>' % _('Some parts of this message were not decoded correctly, probably due to missing support for it in Gammu.')) + text
    else:
        text = SmsTextFormat(cfg, v['Text'])

    return HtmlStrConv(text)

# Wammu - Phone manager
# Copyright (c) 2003-4 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MER- CHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Message to HTML conversion
'''

import Wammu
import Wammu.Data
import Wammu.Ringtone
import string
import re
from Wammu.Utils import UnicodeConv, StrConv, Str_ as _

def SmsTextFormat(cfg, txt):
    if cfg.ReadInt('/Wammu/FormatSMS', 1):
        ret = ''
        arr = txt.split(' ')
        for a in arr:
            if re.match('^([a-z]+[^ ]*)?[A-Z].*[a-z]{2,}[A-Z]{2,}.*$', a) != None:
                prevtype = 'p'
                if UnicodeConv(string.lowercase).find(a[0]) != -1:
                    type = 'l'
                elif UnicodeConv(string.uppercase).find(a[0]) != -1:
                    type = 'u'
                elif UnicodeConv(string.digits).find(a[0]) != -1:
                    type = 'd'
                else:
                    type = 'p'
                   
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

                    if type == nexttype:
                        s += x
                    else:
                        if type == 'u' and nexttype == 'l' and prevtype == 'p' and len(s) == 1:
                            type = 'l'
                            prevtype = 'u'
                            s += x
                            continue
                        if type == 'p':
                            ret = ret.rstrip() + s + ' '
                        elif type == 'u':
                            ret += s.lower() + ' '
                        else:
                            ret += s + ' ' 
                        s = x
                        prevtype = type
                        type = nexttype
                
                if type == 'p':
                    ret = ret.rstrip() + s + ' '
                elif type == 'u':
                    ret += s.lower() + ' '
                else:
                    ret += s + ' ' 
                s = x
            else:
                ret += a + ' '
        return StrConv(ret)
    else:
        return StrConv(txt)

def SmsToHtml(cfg, v):
    if v.has_key('SMSInfo'):
        text = ''
        ringno = 0
        Wammu.Ringtone.ringtones = {}
        for i in v['SMSInfo']['Entries']:
            if i['ID'] in Wammu.SMSIDs['PredefinedAnimation']:
                if i['Number'] > len(Wammu.Data.PredefinedAnimations):
                    text = text + \
                        '<wxp module="Wammu.Image" class="Bitmap">' + \
                        '<param name="tooltip" value="' + (_('Predefined animation number %d') % i['Number']) + '">' + \
                        '<param name="image" value="' + "['" + string.join(Wammu.Data.UnknownPredefined, "', '") + "']" + '">' + \
                        '</wxp>'
                else:
                    text = text + \
                        '<wxp module="Wammu.Image" class="Bitmap">' + \
                        '<param name="tooltip" value="' + Wammu.Data.PredefinedAnimations[i['Number']][0]+ '">' + \
                        '<param name="image" value="' + "['" + string.join(Wammu.Data.PredefinedAnimations[i['Number']][1], "', '") + "']" + '">' + \
                        '</wxp>'

            if i['ID'] in Wammu.SMSIDs['PredefinedSound']:
                if i['Number'] >= len(Wammu.Data.PredefinedSounds):
                    desc = _('Unknown predefined sound #%d') % i['Number']
                else:
                    desc = Wammu.Data.PredefinedSounds[i['Number']][0]
                text = text + \
                    '[<wxp module="Wammu.Image" class="Bitmap">' + \
                    '<param name="image" value="' + "['" + string.join(Wammu.Data.Note, "', '") + "']" + '">' + \
                    '</wxp>' + desc + ']'

            if i['ID'] in Wammu.SMSIDs['Sound']:
                Wammu.Ringtone.ringtones[ringno] = i['Ringtone']
                text = text + \
                    '<wxp module="Wammu.Ringtone" class="Ringtone">' + \
                    '<param name="tooltip" value="' + i['Ringtone']['Name'] + '">' + \
                    '<param name="ringno" value="' + str(ringno) + '">' + \
                    '</wxp>'
                ringno += 1

            if i['ID'] in Wammu.SMSIDs['Text']:
                fmt = '%s'
                for x in Wammu.TextFormats:
                    for name, txt, style in x[1:]:
                        if i.has_key(name) and i[name]:
                            fmt = style % fmt
                #FIXME: handle special chars
                text = text + (fmt % SmsTextFormat(cfg, i['Buffer']))

            if i['ID'] in Wammu.SMSIDs['Bitmap']:
                x = i['Bitmap'][0]
                text = text + \
                    '<wxp module="Wammu.Image" class="Bitmap">' + \
                    '<param name="scale" value="(' + str(cfg.ReadInt('/Wammu/ScaleImage', 1)) + ')">' + \
                    '<param name="image" value="' + "['" + string.join(x['XPM'], "', '") + "']" + '">' + \
                    '</wxp>'

            if i['ID'] in Wammu.SMSIDs['Animation']:
                data = []
                for x in i['Bitmap']:
                    data.append("['" + string.join(x['XPM'], "', '") + "']")
                    text = text + \
                        '<wxp module="Wammu.Image" class="Throbber">' + \
                        '<param name="scale" value="(' + str(cfg.ReadInt('/Wammu/ScaleImage', 1)) + ')">' + \
                        '<param name="images" value="' + "['" + string.join(data, "', '") + "']" + '">' + \
                        '</wxp>'
        if v['SMSInfo'].has_key('Unknown') and v['SMSInfo']['Unknown']:
            text = ('<i>%s</i><hr>' % _('Some parts of this message were not decoded correctly, probably due to missing support for it')) + text
    else:
        text = SmsTextFormat(cfg, v['Text'])

    return StrConv(text)

import Wammu
import Wammu.Data
import string

def SmsToHtml(cfg, v):
    if v.has_key('SMSInfo'):
        text = ''
        for i in v['SMSInfo']['Entries']:
            if i['ID'] in Wammu.SMSIDs['PredefinedAnimation']:
                if i['Number'] > len(Wammu.Data.PredefinedAnimations):
                    text = text + \
                        '[<wxp module="Wammu.Image" class="Bitmap">' + \
                        '<param name="image" value="' + "['" + string.join(Wammu.Data.UnknownPredefined, "', '") + "']" + '">' + \
                        '</wxp>' + str(i['Number']) + ']'
                else:
                    text = text + \
                        '<wxp module="Wammu.Image" class="Bitmap">' + \
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
                text = text + \
                    '<wxp module="Wammu.Image" class="Bitmap">' + \
                    '<param name="image" value="' + "['" + string.join(Wammu.Data.Note, "', '") + "']" + '">' + \
                    '</wxp>'
            if i['ID'] in Wammu.SMSIDs['Text']:
                fmt = '%s'
                for x in Wammu.TextFormats:
                    for name, txt, style in x[1:]:
                        if i.has_key(name) and i[name]:
                            fmt = style % fmt
                #FIXME: handle special chars
                text = text + (fmt % i['Buffer'])
                
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
    else:
        text = v['Text']

    return text

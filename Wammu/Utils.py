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
    else:
        return 'number'

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
    entry['Number'] = number_result
    entry['Name'] = name_result

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
    entry['Text'] = text
    entry['Start'] = start
    entry['End'] = end

def ParseMessage(msg, parseinfo = False):
    txt = ''
    loc = ''
    msg['Folder'] = msg['SMS'][0]['Folder']
    msg['State'] = msg['SMS'][0]['State']
    msg['Number'] = msg['SMS'][0]['Number']
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
    msg['Text'] = txt
    msg['Location'] = loc

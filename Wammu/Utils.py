def GetMemoryEntryName(entry):
    first = ''
    last = ''
    name = ''
    for i in entry['Values']:
        if i['Type'] == 'Text_Name':
            name = i['Value']
        elif i['Type'] == 'Text_FirstName':
            first = i['Value']
        if i['Type'] == 'Text_LastName':
            last = i['Value']
    if name != '':
        result = name
    elif first != '':
        if last != '':
            result = last + ', ' + first
        else:
            result = first
    else:
        result = last
    entry['Name'] = result

def GetMemoryEntryNumber(entry):
    number = ''
    result = ''
    for i in entry['Values']:
        if i['Type'] == 'Number_General':
            result = i['Value']
        elif i['Type'][:7] == 'Number_':
            number =  i['Value']
    if result == '':
        result = number
    entry['Number'] = result

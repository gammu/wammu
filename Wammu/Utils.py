def ParseMemoryEntry(entry):
    first = ''
    last = ''
    name = ''
    number = ''
    number_result = ''
    name_result = ''
    for i in entry['Values']:
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
    for i in entry['Values']:
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

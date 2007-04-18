def GetMemoryEntryName(entry):
    first = ''
    last = ''
    name = ''
    for i in entry["Values"]:
        if i["Type"] == 'Text_Name':
            name = i["Value"]
        elif i["Type"] == 'Text_FirstName':
            first = i["Value"]
        if i["Type"] == 'Text_LastName':
            last = i["Value"]
    if name != '':
        return name
    if first != '':
        if last != '':
            return last + ', ' + first
        else:
            return first
    else:
        return last

def GetMemoryEntryNumber(entry):
    number = ''
    for i in entry["Values"]:
        if i["Type"] == 'Number_General':
            return i["Value"]
        elif i["Type"][:7] == 'Number_':
            number =  i["Value"]
    return number

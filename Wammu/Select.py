import wx
import Wammu.Utils

def SortName(i1, i2):
    return cmp(i1['Name'], i2['Name'])

def SelectContact(parent, list, index = False):
    list.sort(SortName)
    choices = []
    for e in list:
        choices.append(e['Name'])
        
    dlg = wx.SingleChoiceDialog(parent, 'Select contact from bellow list', 'Select contact',
                                choices, wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
    if dlg.ShowModal() == wx.ID_OK and len(choices) > 0:
        rs = dlg.GetSelection()
        if not index:
            rs =  list[rs]['Location']
    else:
        rs = -1
    dlg.Destroy()
    return rs

def SelectNumber(parent, list):
    i = SelectContact(parent, list, True)
    if i == -1:
        return None

    numbers = []
    texts = []
    for x in range(len(list[i]['Entries'])):
        if Wammu.Utils.GetItemType(list[i]['Entries'][x]['Type']) == 'phone':
            numbers.append(list[i]['Entries'][x]['Value'])
            texts.append(list[i]['Entries'][x]['Type'] + ' : ' + list[i]['Entries'][x]['Value'])

    if len(numbers) == 0:
        return None
    elif len(numbers) == 1:
        return numbers[0]
    dlg = wx.SingleChoiceDialog(parent, 'Select number for selected contact', 'Select number',
                                texts, wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
    if dlg.ShowModal() == wx.ID_OK:
        rs = numbers[dlg.GetSelection()]
    else:
        rs = None
    dlg.Destroy()
    return rs

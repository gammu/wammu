import wx

def SortName(i1, i2):
    return cmp(i1['Name'], i2['Name'])

def SelectContact(parent, list):
    list.sort(SortName)
    choices = []
    for e in list:
        choices.append(e['Name'])
        
    dlg = wx.SingleChoiceDialog(parent, 'Select contact', 'Select contact from bellow list',
                                choices, wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
    if dlg.ShowModal() == wx.ID_OK and len(choices) > 0:
        rs =  list[dlg.GetSelection()]['Location']
    else:
        rs = -1
    dlg.Destroy()
    return rs


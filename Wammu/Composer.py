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
SMS composer
'''

import wx
import wx.lib.editor.editor
import wx.lib.mixins.listctrl
import Wammu
import Wammu.Data
import Wammu.MessageDisplay
import Wammu.Utils
import Wammu.PhoneValidator
import Wammu.Select
import Wammu.EditContactList
if Wammu.gammu_error is None:
    import gammu
import Wammu.Locales
from Wammu.Locales import ugettext as _

class MessagePreview(wx.Dialog):
    text = '''
<html>
<body>
%s
<center>
<p><wxp module="wx" class="Button">
    <param name="id"    value="ID_OK">
</wxp></p>
</center>
</body>
</html>
'''

    def __init__(self, parent, content):
        wx.Dialog.__init__(self, parent, -1, _('Message preview'))
        html = wx.html.HtmlWindow(self, -1, size=(420, -1))
        html.SetPage(self.text % content)
        btn = html.FindWindowById(wx.ID_OK)
        btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize((ir.GetWidth() + 25, ir.GetHeight() + 25))
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

class StyleEdit(wx.Dialog):
    def __init__(self, parent, entry):
        wx.Dialog.__init__(self, parent, -1, _('Text style'))

        self.sizer = wx.GridBagSizer()

        self.entry = entry

        self.fmt = {}

        row = 1

        col = 1
        maxcol = 1

        for x in Wammu.Data.TextFormats:
            if len(x) == 2:
                name = x[1][0]
                text = x[1][1]
                self.fmt[name] = wx.CheckBox(self, -1, text)
                if name in self.entry:
                    self.fmt[name].SetValue(self.entry[name])
                self.sizer.Add(self.fmt[name], pos=(row, col))
                col = col + 2
            else:
                if col > 1:
                    row = row + 2
                    maxcol = max(col, maxcol)
                    col = 1

                self.sizer.Add(wx.StaticText(self, -1, x[0][0] + ':'), pos=(row, col))
                col = col + 2

                rb = wx.RadioButton(self, -1, x[0][1], style=wx.RB_GROUP)
                rb.SetValue(True)
                self.sizer.Add(rb, pos=(row, col))
                col = col + 2
                for name, text, fmt in x[1:]:
                    self.fmt[name] = wx.RadioButton(self, -1, text)
                    if name in self.entry:
                        self.fmt[name].SetValue(self.entry[name])
                    self.sizer.Add(self.fmt[name], pos=(row, col))
                    col = col + 2
                row = row + 2
                maxcol = max(col, maxcol)
                col = 1

        if col > 1:
            row = row + 2
            maxcol = max(col, maxcol)
            col = 1

        self.ok = wx.Button(self, wx.ID_OK)
        self.sizer.Add(self.ok, pos=(row, 1), span=wx.GBSpan(colspan=maxcol), flag=wx.ALIGN_CENTER)
        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)

        self.sizer.AddSpacer((5, 5), pos=(row + 1, maxcol + 1))

        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

        self.CentreOnParent(wx.BOTH)

    def Okay(self, evt):
        for x in Wammu.Data.TextFormats:
            for name, text, fmt in x[1:]:
                self.entry[name] = self.fmt[name].GetValue()
        self.EndModal(wx.ID_OK)

class AutoSizeList(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, firstcol):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER, size=(-1, 100))
        self.InsertColumn(0, firstcol)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

class GenericEditor(wx.Panel):
    """
    Generic class for static text with some edit control.
    """
    def __init__(self, parent, part, cfg, use_unicode):
        wx.Panel.__init__(self, parent, -1, style=wx.RAISED_BORDER)
        self.part = part
        self.cfg = cfg
        self.use_unicode = use_unicode

class TextEditor(GenericEditor):
    def __init__(self, parent, cfg, part, use_unicode):
        GenericEditor.__init__(self, parent, cfg, part, use_unicode)

        self.backuptext = ''

        self.sizer = wx.GridBagSizer()

        self.edit = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)

        self.sizer.Add(self.edit, pos=(0, 0), flag=wx.EXPAND, span=wx.GBSpan(colspan=4))
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableRow(0)

        self.concat = wx.CheckBox(self, -1, _('Concatenated'))
        self.concat.SetToolTipString(_('Create concatenated message, what allows to send longer messages.'))
        self.concat.SetValue(self.part['ID'] != 'Text')
        wx.EVT_CHECKBOX(self.concat, self.concat.GetId(), self.OnConcatChange)
        self.sizer.Add(self.concat, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)

        self.leninfo = wx.StaticText(self, -1, '')
        self.sizer.Add(self.leninfo, pos=(1, 3), flag=wx.ALIGN_RIGHT)

        self.stylebut = wx.Button(self, -1, _('Style'))
        wx.EVT_BUTTON(self, self.stylebut.GetId(), self.StylePressed)
        self.sizer.Add(self.stylebut, pos=(1, 1), flag=wx.ALIGN_CENTER)

        self.OnConcatChange()

        wx.EVT_TEXT(self.edit, self.edit.GetId(), self.TextChanged)
        if 'Buffer' in self.part:
            self.edit.SetValue(self.part['Buffer'])

        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.TextChanged()

    def OnUnicode(self, newu):
        self.use_unicode = newu
        self.CheckTextLen()

    def OnConcatChange(self, evt=None):
        self.stylebut.Enable(self.concat.GetValue())
        self.CheckTextLen()

    def CheckTextLen(self, evt=None):
        if not self.concat.GetValue():
            if self.use_unicode:
                self.edit.SetValue(self.edit.GetValue()[:70])
            else:
                self.edit.SetValue(self.edit.GetValue()[:160])

    def StylePressed(self, evt):
        dlg = StyleEdit(self, self.part)
        dlg.ShowModal()
        del dlg

    def TextChanged(self, evt=None):
        txt = self.edit.GetValue()
        length = len(txt)
        if not self.concat.GetValue() and ((self.use_unicode and length > 70) or (not self.use_unicode and length > 160)):
            self.edit.SetValue(self.backuptext)
            return
        length = len(self.edit.GetValue())
        self.leninfo.SetLabel(Wammu.Locales.ngettext('%d char', '%d chars', length) % length)
        self.sizer.Layout()
        self.backuptext = txt

    def GetValue(self):
        if self.concat.GetValue():
            if self.cfg.Read('/Message/16bitId') == 'yes':
                self.part['ID'] = 'ConcatenatedTextLong16bit'
            else:
                self.part['ID'] = 'ConcatenatedTextLong'
        else:
            self.part['ID'] = 'Text'
        self.part['Buffer'] = Wammu.Locales.UnicodeConv(self.edit.GetValue())
        return self.part

class PredefinedAnimEditor(GenericEditor):
    def __init__(self, parent, part, cfg, use_unicode):
        GenericEditor.__init__(self, parent, part, cfg, use_unicode)
        self.sizer = wx.GridBagSizer()

        values = []
        for x in Wammu.Data.PredefinedAnimations:
            values.append(x[0])

        self.sizer.AddGrowableRow(0)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)

        self.edit = wx.Choice(self, -1, choices=values)

        bitmap = wx.BitmapFromXPMData(Wammu.Data.UnknownPredefined)
        self.bitmap = wx.StaticBitmap(self, -1, bitmap, (0, 0))

        wx.EVT_CHOICE(self.edit, self.edit.GetId(), self.OnChange)

        if 'Number' not in self.part:
            self.part['Number'] = 0

        self.edit.SetSelection(self.part['Number'])
        self.OnChange()

        self.sizer.Add(wx.StaticText(self, -1, _('Select predefined animation:')), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self.edit, pos=(0, 1), flag=wx.ALIGN_CENTER)
        self.sizer.Add(self.bitmap, pos=(0, 2), flag=wx.ALIGN_CENTER)

        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def OnChange(self, evt=None):
        bitmap = wx.BitmapFromXPMData(Wammu.Data.PredefinedAnimations[self.edit.GetSelection()][1])
        self.bitmap.SetBitmap(bitmap)

    def GetValue(self):
        self.part['ID'] = 'EMSPredefinedAnimation'
        self.part['Number'] = self.edit.GetSelection()
        return self.part

class PredefinedSoundEditor(GenericEditor):
    def __init__(self, parent, part, cfg, use_unicode):
        GenericEditor.__init__(self, parent, part, cfg, use_unicode)
        self.sizer = wx.GridBagSizer()

        values = []
        for x in Wammu.Data.PredefinedSounds:
            values.append(x[0])

        self.sizer.AddGrowableRow(0)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableCol(1)

        self.edit = wx.Choice(self, -1, choices=values)

        if 'Number' not in self.part:
            self.part['Number'] = 0

        self.edit.SetSelection(self.part['Number'])

        self.sizer.Add(wx.StaticText(self, -1, _('Select predefined sound:')), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self.edit, pos=(0, 1), flag=wx.ALIGN_CENTER)

        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def GetValue(self):
        self.part['ID'] = 'EMSPredefinedSound'
        self.part['Number'] = self.edit.GetSelection()
        return self.part

# We should support more types...
#   ID, display text, match types, editor, init type
SMSParts = [
    (0, _('Text'), Wammu.Data.SMSIDs['Text'], TextEditor, 'ConcatenatedTextLong16bit'),
    (1, _('Predefined animation'), Wammu.Data.SMSIDs['PredefinedAnimation'], PredefinedAnimEditor, 'EMSPredefinedAnimation'),
    (2, _('Predefined sound'), Wammu.Data.SMSIDs['PredefinedSound'], PredefinedSoundEditor, 'EMSPredefinedSound'),
]

class SMSComposer(wx.Dialog):
    def __init__(self, parent, cfg, entry, values, action='save', addtext=True):
        wx.Dialog.__init__(self, parent, -1, _('Composing SMS'), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.entry = entry
        self.cfg = cfg
        self.values = values
        if 'SMSInfo' not in entry:
            entry['SMSInfo'] = {}
            entry['SMSInfo']['Entries'] = []
            if self.cfg.Read('/Message/Concatenated') == 'yes':
                if self.cfg.Read('/Message/16bitId') == 'yes':
                    typ = 'ConcatenatedTextLong16bit'
                else:
                    typ = 'ConcatenatedTextLong'
            else:
                typ = 'Text'
            if 'Text' in entry:
                entry['SMSInfo']['Entries'].append({'ID': typ, 'Buffer': entry['Text']})
            elif addtext:
                entry['SMSInfo']['Entries'].append({'ID': typ, 'Buffer': ''})
        if 'Number' not in entry:
            entry['Number'] = ''

        self.sizer = wx.GridBagSizer()


        row = 1

        if action not in ['send', 'save']:
            action = 'save'

        self.send = wx.CheckBox(self, -1, _('Send message'))
        self.send.SetToolTipString(_('When checked, message is sent to recipient.'))
        self.send.SetValue(action == 'send')

        self.save = wx.CheckBox(self, -1, _('Save into folder'))
        self.save.SetToolTipString(_('When checked, message is saved to phone.'))
        self.save.SetValue(action == 'save')

        self.Bind(wx.EVT_CHECKBOX, self.OnSave, self.save)
        self.Bind(wx.EVT_CHECKBOX, self.OnSend, self.send)

        self.folder = wx.SpinCtrl(self, -1, '2', style=wx.SP_WRAP | wx.SP_ARROW_KEYS, min=0, max=100, initial=2)

        self.sizer.Add(self.send, pos=(row, 1), flag=wx.ALIGN_LEFT)
        self.sizer.Add(self.save, pos=(row, 6), flag=wx.ALIGN_LEFT)
        self.sizer.Add(self.folder, pos=(row, 7), flag=wx.ALIGN_LEFT)

        row = row + 2

        self.number = wx.TextCtrl(self, -1, entry['Number'], validator=Wammu.PhoneValidator.PhoneValidator(multi=True), size=(150, -1))
        self.contbut = wx.Button(self, -1, _('Add'))
        self.contbut.SetToolTipString(_('Add number of recipient from contacts.'))
        self.editlistbut = wx.Button(self, wx.ID_EDIT, _('Edit'))
        self.editlistbut.SetToolTipString(_('Edit recipients list.'))

        self.sizer.Add(wx.StaticText(self, -1, _('Recipient\'s numbers:')), pos=(row, 1), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self.number, pos=(row, 2), flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, span=wx.GBSpan(colspan=4))
        self.sizer.Add(self.editlistbut, pos=(row, 6), flag=wx.ALIGN_CENTER)
        self.sizer.Add(self.contbut, pos=(row, 7), flag=wx.ALIGN_CENTER)

        self.Bind(wx.EVT_BUTTON, self.ContactPressed, self.contbut)
        self.Bind(wx.EVT_BUTTON, self.EditContactPressed, self.editlistbut)

        row = row + 2

        self.unicode = wx.CheckBox(self, -1, _('Unicode'))
        self.unicode.SetToolTipString(_('Unicode messages can contain national and other special characters, check this if you use non latin-1 characters. Your messages will require more space, so you can write less characters into single message.'))
        if 'Unicode' in self.entry:
            self.unicode.SetValue(self.entry['Unicode'])
        else:
            self.unicode.SetValue(self.cfg.Read('/Message/Unicode') == 'yes')

        self.sizer.Add(self.unicode, pos=(row, 1), flag=wx.ALIGN_LEFT)

        self.Bind(wx.EVT_CHECKBOX, self.OnUnicode, self.unicode)

        self.report = wx.CheckBox(self, -1, _('Delivery report'))
        self.report.SetToolTipString(_('Check to request delivery report for message.'))
        self.report.SetValue(self.cfg.Read('/Message/DeliveryReport') == 'yes')
        self.sizer.Add(self.report, pos=(row, 2), flag=wx.ALIGN_LEFT)

        self.sent = wx.CheckBox(self, -1, _('Sent'))
        self.sent.SetToolTipString(_('Check to save message as sent (has only effect when only saving message).'))
        self.sizer.Add(self.sent, pos=(row, 4), flag=wx.ALIGN_LEFT)

        self.flash = wx.CheckBox(self, -1, _('Flash'))
        self.flash.SetToolTipString(_('Send flash message - it will be just displayed on display, but not saved in phone.'))
        self.sizer.Add(self.flash, pos=(row, 6), flag=wx.ALIGN_LEFT)


        row = row + 2
        self.sizer.SetRows(row + 1)
        self.sizer.AddGrowableRow(row)

        self.current = AutoSizeList(self, _('Parts of current message'))
        self.available = AutoSizeList(self, _('Available message parts'))
        # FIXME: add icons?

        self.addbut = wx.Button(self, wx.ID_ADD)
        self.delbut = wx.Button(self, wx.ID_REMOVE)

        self.Bind(wx.EVT_BUTTON, self.AddPressed, self.addbut)
        self.Bind(wx.EVT_BUTTON, self.DeletePressed, self.delbut)

        self.sizer.Add(self.current, pos=(row, 1), flag=wx.EXPAND, span=wx.GBSpan(colspan=2, rowspan=2))
        self.sizer.Add(self.addbut, pos=(row, 4), flag=wx.ALIGN_CENTER)
        self.sizer.Add(self.delbut, pos=(row + 1, 4), flag=wx.ALIGN_CENTER)
        self.sizer.Add(self.available, pos=(row, 6), flag=wx.EXPAND, span=wx.GBSpan(colspan=2, rowspan=2))

        row = row + 3

        self.upbut = wx.Button(self, wx.ID_UP)
        self.dnbut = wx.Button(self, wx.ID_DOWN)

        self.sizer.Add(self.upbut, pos=(row, 1), flag=wx.ALIGN_CENTER)
        self.sizer.Add(self.dnbut, pos=(row, 2), flag=wx.ALIGN_CENTER)

        self.Bind(wx.EVT_BUTTON, self.UpPressed, self.upbut)
        self.Bind(wx.EVT_BUTTON, self.DnPressed, self.dnbut)

        row = row + 2
        self.sizer.SetRows(row + 1)
        self.sizer.AddGrowableRow(row)
        self.editorrow = row

        self.editor = wx.StaticText(self, -1, _('Create new message by adding part to left list...'), size=(-1, 150))
        self.sizer.Add(self.editor, pos=(row, 1), flag=wx.EXPAND, span=wx.GBSpan(colspan=7))

        row = row + 2

        self.preview = wx.Button(self, -1, _('Preview'))
        self.button_sizer = wx.StdDialogButtonSizer()
        self.button_sizer.AddButton(wx.Button(self, wx.ID_OK))
        self.button_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        self.button_sizer.SetNegativeButton(self.preview)
        self.button_sizer.Realize()
        self.sizer.Add(self.button_sizer, pos=(row, 1), span=wx.GBSpan(colspan=7), flag=wx.ALIGN_RIGHT)

        self.Bind(wx.EVT_BUTTON, self.Okay, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.Preview, self.preview)

        self.sizer.AddSpacer((5, 5), pos=(row + 1, 8))
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableCol(6)
        self.sizer.AddGrowableCol(7)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

        self.prevedit = -1
        self.availsel = -1

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.CurrentSelected, self.current)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.AvailableSelected, self.available)

        if action == 'send':
            self.OnSave()
        else:
            self.OnSend()

        for x in SMSParts:
            self.available.InsertImageStringItem(x[0], x[1], x[0])
        self.available.SetItemState(0, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)

        self.GenerateCurrent()

    def ContactPressed(self, evt):
        v = Wammu.Select.SelectNumber(self, [] + self.values['contact']['ME'] + self.values['contact']['SM'])
        if v is not None:
            self.number.SetValue(self.number.GetValue() + ' ' + v)

    def EditContactPressed(self, evt):
        '''
        Opens dialog for editing contact list.
        '''
        contacts = [] + self.values['contact']['ME'] + self.values['contact']['SM']
        current = self.number.GetValue()
        dlg = Wammu.EditContactList.EditContactList(self, contacts, current)
        if dlg.ShowModal() == wx.ID_OK:
            self.number.SetValue(dlg.GetNumbers())

    def OnSend(self, evt=None):
        self.save.Enable(self.send.GetValue())
        self.number.GetValidator().empty = not self.send.GetValue()

    def OnSave(self, evt=None):
        self.send.Enable(self.save.GetValue())

    def GenerateCurrent(self, select=0):
        self.current.DeleteAllItems()
        for i in range(len(self.entry['SMSInfo']['Entries'])):
            found = False
            x = self.entry['SMSInfo']['Entries'][i]
            for p in SMSParts:
                if x['ID'] in p[2]:
                    self.current.InsertImageStringItem(i, p[1], p[0])
                    found = True
                    break
            if not found:
                self.current.InsertImageStringItem(i, _('Not supported id: %s') % x['ID'], -1)
                print 'Not supported id: %s' % x['ID']

        count = self.current.GetItemCount()

        if count > 0:
            while select > count:
                select = select - 1
            self.current.SetItemState(select, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)
        else:
            if hasattr(self, 'editor'):
                self.sizer.Detach(self.editor)
                self.editor.Destroy()
                del self.editor
            self.editor = wx.StaticText(self, -1, _('Create new message by adding part to left list...'), size=(-1, 150))
            self.sizer.Add(self.editor, pos=(self.editorrow, 1), flag=wx.EXPAND, span=wx.GBSpan(colspan=7))
            self.sizer.Layout()

    def AvailableSelected(self, event):
        self.availsel = event.m_itemIndex

    def OnUnicode(self, event):
        self.entry['SMSInfo']['Unicode'] = self.unicode.GetValue()
        if hasattr(self.editor, 'OnUnicode'):
            self.editor.OnUnicode(self.unicode.GetValue())

    def CurrentSelected(self, event):
        self.StoreEdited()
        if hasattr(self, 'editor'):
            self.sizer.Detach(self.editor)
            self.editor.Destroy()
            del self.editor

        found = False
        for p in SMSParts:
            if self.entry['SMSInfo']['Entries'][event.m_itemIndex]['ID'] in p[2]:
                self.editor = p[3](self, self.entry['SMSInfo']['Entries'][event.m_itemIndex], self.cfg, self.unicode.GetValue())
                self.sizer.Add(self.editor, pos=(self.editorrow, 1), flag=wx.EXPAND, span=wx.GBSpan(colspan=7))
                found = True
                break
        if not found:
            self.editor = wx.StaticText(self, -1, _('No editor available for type %s') % self.entry['SMSInfo']['Entries'][event.m_itemIndex]['ID'])
            self.sizer.Add(self.editor, pos=(self.editorrow, 1), flag=wx.EXPAND, span=wx.GBSpan(colspan=7))
            self.prevedit = -1
        else:
            self.prevedit = event.m_itemIndex
        self.sizer.Layout()

    def UpPressed(self, evt):
        if self.prevedit == -1:
            return
        next = self.prevedit - 1
        if next < 0:
            return
        self.StoreEdited()
        v = self.entry['SMSInfo']['Entries'][self.prevedit]
        self.entry['SMSInfo']['Entries'][self.prevedit] = self.entry['SMSInfo']['Entries'][next]
        self.entry['SMSInfo']['Entries'][next] = v
        self.prevedit = -1
        self.GenerateCurrent(next)

    def DnPressed(self, evt):
        if self.prevedit == -1:
            return
        next = self.prevedit + 1
        if next >= self.current.GetItemCount():
            return
        self.StoreEdited()
        v = self.entry['SMSInfo']['Entries'][self.prevedit]
        self.entry['SMSInfo']['Entries'][self.prevedit] = self.entry['SMSInfo']['Entries'][next]
        self.entry['SMSInfo']['Entries'][next] = v
        self.prevedit = -1
        self.GenerateCurrent(next)

    def DeletePressed(self, evt):
        if self.prevedit == -1:
            return
        self.StoreEdited()
        del self.entry['SMSInfo']['Entries'][self.prevedit]
        next = self.prevedit - 1
        self.prevedit = -1
        self.GenerateCurrent(max(next, 0))

    def AddPressed(self, evt):
        if self.availsel == -1:
            return
        v = {'ID': SMSParts[self.availsel][4]}
        if v['ID'][-5:] == '16bit' and self.cfg.Read('/Message/16bitId') != 'yes':
            v['ID'] = v['ID'][:-5]
        self.StoreEdited()
        self.entry['SMSInfo']['Entries'].insert(self.prevedit + 1, v)
        next = self.prevedit + 1
        self.prevedit = -1
        self.GenerateCurrent(next)

    def StoreEdited(self):
        if self.prevedit != -1:
            self.entry['SMSInfo']['Entries'][self.prevedit] = self.editor.GetValue()

        if self.report.GetValue():
            self.entry['Type'] = 'Status_Report'
        else:
            self.entry['Type'] = 'Submit'

        if self.sent.GetValue():
            self.entry['State'] = 'Sent'
        else:
            self.entry['State'] = 'UnSent'

        if self.flash.GetValue():
            self.entry['SMSInfo']['Class'] = 0
        else:
            self.entry['SMSInfo']['Class'] = 1

        self.entry['Numbers'] = Wammu.PhoneValidator.SplitNumbers(self.number.GetValue())
        self.entry['SMSInfo']['Unicode'] = self.unicode.GetValue()
        self.entry['Save'] = self.save.GetValue()
        self.entry['Send'] = self.send.GetValue()
        self.entry['Folder'] = self.folder.GetValue()

    def Preview(self, evt):
        if len(self.entry['SMSInfo']['Entries']) == 0:
            dlg = wx.MessageDialog(
                self,
                _('Nothing to preview, message is empty.'),
                _('Message empty!'),
                wx.OK | wx.ICON_WARNING
            )
        else:
            self.StoreEdited()
            msg = gammu.EncodeSMS(self.entry['SMSInfo'])
            info = gammu.DecodeSMS(msg)
            result = {}
            result['SMS'] = msg
            if info is not None:
                result['SMSInfo'] = info
            Wammu.Utils.ParseMessage(result, (info is not None))
            dlg = MessagePreview(self, ('<i>%s</i><hr>' % (_('Message will fit into %d SMSes') % len(msg))) + Wammu.MessageDisplay.SmsToHtml(self.cfg, result))

        dlg.ShowModal()
        del dlg

    def Okay(self, evt):
        if not self.number.GetValidator().Validate(self):
            return

        self.StoreEdited()

        self.EndModal(wx.ID_OK)

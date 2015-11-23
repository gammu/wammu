; Inno Setup Script for Wammu installation
; Copyright (c) 2006 Michal Èihaø
; Language selection code based on GTK+ 2 installation script
; made by Jernej Simoncic, <jernej.simoncic@guest.arnes.si>

#define MyAppDosName "wammu"
#define MyAppName "Wammu"
#define MyAppVersion "0.41"
#define MyAppPublisher "Micha Èihaø"
#define MyAppURL "http://wammu.eu/"
#define MyAppPublisherURL "http://cihar.com/"
#define MyAppBugsURL "http://bugs.wammu.eu/"
#define MyAppDescription "Wammu Mobile Phone Manager"
#define MyAppExeName "wammu.exe"
#define MyAppUrlName "wammu.url"
#define MyAppBugsUrlName "wammu-bugs.url"

[Setup]
AppName={#MyAppName}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppPublisherURL}
AppSupportURL={#MyAppBugsURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=true
LicenseFile=COPYING
OutputBaseFilename={#MyAppDosName}-{#MyAppVersion}-setup
Compression=lzma/ultra
SolidCompression=true
InternalCompressLevel=ultra
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
ShowLanguageDialog=yes
AppVersion={#MyAppVersion}
UninstallDisplayIcon={app}\share\pixmaps\wammu.ico
AppModifyPath="{uninstallexe}" /langsetup
ChangesEnvironment=true
;SetupIconFile={app}\icon\wammu.ico

[Languages]
Name: en; MessagesFile: compiler:Default.isl
;Name: af; MessagesFile: compiler:Languages\Afrikaans.isl
Name: ca; MessagesFile: compiler:Languages\Catalan.isl
Name: cs; MessagesFile: compiler:Languages\Czech.isl
Name: de; MessagesFile: compiler:Languages\German.isl
;Name: el; MessagesFile: compiler:Languages\Greek.isl
Name: es; MessagesFile: compiler:Languages\Spanish.isl
;Name: et; MessagesFile: compiler:Languages\Estonian.isl
Name: fi; MessagesFile: compiler:Languages\Finnish.isl
Name: fr; MessagesFile: compiler:Languages\French.isl
;Name: gl; MessagesFile: compiler:Languages\Galician.isl
Name: he; MessagesFile: compiler:Languages\Hebrew.isl
Name: hu; MessagesFile: compiler:Languages\Hungarian.isl
;Name: id; MessagesFile: compiler:Languages\Indonesian.isl
Name: it; MessagesFile: compiler:Languages\Italian.isl
;Name: ko; MessagesFile: compiler:Languages\Korean.isl
Name: nl; MessagesFile: compiler:Languages\Dutch.isl
Name: pl; MessagesFile: compiler:Languages\Polish.isl
Name: pt_BR; MessagesFile: compiler:Languages\BrazilianPortuguese.isl
Name: ru; MessagesFile: compiler:Languages\Russian.isl
Name: sk; MessagesFile: compiler:Languages\Slovak.isl
;Name: sv; MessagesFile: compiler:Languages\Swedish.isl
;Name: zh_tw; MessagesFile: compiler:Languages\SimpChinese.isl
;Name: zh_cz; MessagesFile: compiler:Languages\TradChinese.isl

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked

[Files]
Source: dist\*; DestDir: {app}; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: locale
Source: uninst.isl; DestDir: {app}
Source: dist\share\locale\*; DestDir: {app}\share\locale; Flags: ignoreversion recursesubdirs createallsubdirs; Components: " Translations"; Tasks: ; Languages: 

[INI]
Filename: {app}\{#MyAppUrlName}; Section: InternetShortcut; Key: URL; String: {#MyAppURL}
Filename: {app}\{#MyAppBugsUrlName}; Section: InternetShortcut; Key: URL; String: {#MyAppBugsURL}

[Icons]
Name: {group}\{#MyAppName}; Filename: {app}\{#MyAppExeName}; IconFilename: {app}\share\pixmaps\wammu.ico; IconIndex: 0
Name: {group}\{cm:ProgramOnTheWeb,{#MyAppName}}; Filename: {app}\{#MyAppUrlName}
Name: {group}\{cm:ReportBug,{#MyAppName}}; Filename: {app}\{#MyAppBugsUrlName}
Name: {group}\{cm:UninstallProgram,{#MyAppName}}; Filename: {uninstallexe}
Name: {userdesktop}\{#MyAppName}; Filename: {app}\{#MyAppExeName}; Tasks: desktopicon
Name: {group}\{cm:SelectLanguage}; Filename: {uninstallexe}; Parameters: /langsetup; IconFilename: {app}\share\pixmaps\wammu.ico; IconIndex: 0

[Run]
Filename: {app}\{#MyAppExeName}; Description: {cm:LaunchProgram,{#MyAppName}}; Flags: nowait postinstall skipifsilent unchecked
Filename: {uninstallexe}; Parameters: /langsetup; Description: {cm:SelectLanguage}; Flags: postinstall nowait

[Components]
Name: Translations; Description: {cm:TranslationsDesc}; Types: custom full; Languages: 

[UninstallDelete]
Type: files; Name: {app}\{#MyAppUrlName}
Type: files; Name: {app}\{#MyAppBugsUrlName}

[CustomMessages]
en.ReportBug=Report bug in application %1
cs.ReportBug=Nahlásit chybu v aplikaci %1
en.SelectLanguage=Select application language
cs.SelectLanguage=Zvolit jazyk aplikace
en.Translations=Translations
en.TranslationsDesc=Translations of user interface
cs.Translations=Pøeklady
cs.TranslationsDesc=Pøeklady uživatelského rozhraní

[Registry]
Root: HKCU; Subkey: Environment; ValueType: string; ValueName: LANG; ValueData: {language}; Check: UsingWinNT

; Following part is heavily based on GTK+ 2 setup
[Code]
program Setup;

function SendMessageTimeout(hWnd: HWND; Msg: Cardinal; wParam: DWORD; lParam: String; fuFlags, uTimeout: Cardinal; lpdwResult: DWORD): {Int64}Cardinal; external 'SendMessageTimeoutA@user32 stdcall';

var
	frmLangChooser: TForm;
	cbUser, cbSystem: TComboBox;

const
	WM_SETTINGCHANGE = 26;
	//HWND_BROADCAST = $FFFF;
	SMTO_ABORTIFHUNG = 2;

function RevPos(const SearchStr, Str: string): Integer;
var i: Integer;
begin

	if (Length(SearchStr) < Length(Str)) and (Pos(SearchStr, Str) > 0) then
		for i := (Length(Str) - Length(SearchStr) + 1) downto 1 do
		begin

			if Copy(Str, i, Length(SearchStr)) = SearchStr then
			begin
				Result := i;
				exit;
			end;

		end;

	Result := 0;
end;


function ExtractLang(const Txt: String): String;
var S: String;
	i: Integer;
begin
	S := LowerCase(Txt);
	if (S[Length(S)] = ')') then
	begin
		i := RevPos('(',S);
		if (i > 0) then
			S := Copy(Txt,i+1,Length(Txt)-i-1)
		else
			S := Txt;
	end else
		S := Txt;

	Result := S;
end;


function GetLangIndex(Items: TStrings; Lang: String): Integer;
var i: Integer;
	s: String;
begin
	Lang := LowerCase(Lang);
	for i := 0 to Items.Count - 1 do
	begin
		S := LowerCase(ExtractLang(Items.Strings[i]));
		if (S = Lang) then
			break;
	end;

	if (i >= Items.Count) then
		Result := -1
	else
		Result := i;
end;


function GetTransStr(const Str: String): String; //ExpandConstant('{cm:...}') doesn't work on uninstall
begin
	Result := GetIniString('CustomMessages',Str,'',ExpandConstant('{app}\uninst.isl'));

	if (Result = '') then
		RaiseException(Str + ' not found in translation file.');
end;


procedure LanguageForm;
var	lblInfo, lblUser, lblSystem: TLabel;
	btnOK,btnCancel: TButton;
	frMsgs: TFindRec;
	i,j: Integer;
	lang1,lang2,regSys,regUser: String;
	AutoExec: TArrayOfString;
	MsgResult: DWORD;
begin

	frmLangChooser := CreateCustomForm();

	with frmLangChooser do
	begin
		ClientWidth := ScaleX(321);
		ClientHeight := ScaleY(119);
		Caption := GetTransStr('LangTitle');
		Position := poScreenCenter;
	end;

	{ lblInfo }
	lblInfo := TLabel.Create(frmLangChooser);
	with lblInfo do
	begin
		Parent := frmLangChooser;
		Left := ScaleX(8);
		Top := ScaleY(8);
		Width := ScaleX(283);
		Height := ScaleY(13);
		Caption := GetTransStr('LangText');
	end;

	{ lblUser }
	lblUser := TLabel.Create(frmLangChooser);
	with lblUser do
	begin
		Parent := frmLangChooser;
		Left := ScaleX(8);
		Top := ScaleY(34);
		Width := ScaleX(119);
		Height := ScaleY(13);
		Caption := GetTransStr('LangUser');
		FocusControl := cbUser;
	end;

	{ lblSystem }
	lblSystem := TLabel.Create(frmLangChooser);
	with lblSystem do
	begin
		Parent := frmLangChooser;
		Left := ScaleX(8);
		Top := ScaleY(58);
		Width := ScaleX(93);
		Height := ScaleY(13);
		Caption := GetTransStr('LangSystem');
		FocusControl := cbSystem;
	end;

	{ cbUser }
	cbUser := TComboBox.Create(frmLangChooser);
	with cbUser do
	begin
		Parent := frmLangChooser;
		Style := csDropDownList;
		Left := ScaleX(144);
		Top := ScaleY(32);
		Width := ScaleX(169);
		Height := ScaleY(16);
		Hint := GetTransStr('LangUserHint');
		ShowHint := True;
		TabOrder := 0;
		Sorted := True;
	end;

	{ cbSystem }
	cbSystem := TComboBox.Create(frmLangChooser);
	with cbSystem do
	begin
		Parent := frmLangChooser;
		Style := csDropDownList;
		Left := ScaleX(144);
		Top := ScaleY(56);
		Width := ScaleX(169);
		Height := ScaleY(16);
		Hint := GetTransStr('LangSystemHint');
		ShowHint := True;
		TabOrder := 1;
		Sorted := True;
	end;

	{ btnOK }
	btnOK := TButton.Create(frmLangChooser);
	with btnOK do
	begin
		Parent := frmLangChooser;
		Left := ScaleX(82);
		Top := ScaleY(88);
		Width := ScaleX(75);
		Height := ScaleY(23);
		Caption := SetupMessage(msgButtonOK);
		Default := True;
		TabOrder := 2;
		ModalResult := 1;
	end;

	{ btnCancel }
	btnCancel := TButton.Create(frmLangChooser);
	with btnCancel do
	begin
		Parent := frmLangChooser;
		Left := ScaleX(164);
		Top := ScaleY(88);
		Width := ScaleX(75);
		Height := ScaleY(23);
		Caption := SetupMessage(msgButtonCancel);
		Cancel := True;
		TabOrder := 3;
		ModalResult := 2;
	end;

	cbUser.Items.Add(GetTransStr('LangDefault'));
	cbUser.Items.Add('English (C)');
	//cbSystem.Items.Add(GetTransStr('LangDefault'));

	if FindFirst(ExpandConstant('{app}\share\locale\*'),frMsgs) then
	begin

		try
			repeat
				if ((frMsgs.Attributes and FILE_ATTRIBUTE_DIRECTORY) = FILE_ATTRIBUTE_DIRECTORY) and ((frMsgs.Name <> '.') and (frMsgs.Name <> '..')) then
				begin

					try
						lang1 := frMsgs.Name;
						StringChange(lang1,'@','_'); //custom messages only support letters,numbers and _
						lang1 := GetTransStr('Lang_'+lang1+'');
					except
						lang1 := '';
					end;

					i := pos('@',frMsgs.Name);
					if (lang1 = '') and (i > 0) then
						try
							lang1 := GetTransStr('Lang_'+Copy(frMsgs.Name,1,i-1)+'');
							lang2 := Copy(frMsgs.Name,i+1,length(frMsgs.Name))
						except
							lang1 := '';
						end;

					if (lang1 = '') and (Length(frMsgs.Name) > 2) then
						try
							lang1 := GetTransStr('Lang_'+Copy(frMsgs.Name,1,2)+'');
						except
							lang1 := '';
						end;

					case lowercase(lang2) of
						'latn': lang2 := 'Latin';
					end;

					if (lang1 <> '') then
					begin
						if (lang2 <> '') then
						begin
							cbUser.Items.Add(lang1+' '+lang2+' ('+frMsgs.Name+')');
						end else
						begin
							cbUser.Items.Add(lang1+' ('+frMsgs.Name+')');
						end
					end else
					begin
						cbUser.Items.Add(frMsgs.Name);
					end;

				end;
			until not FindNext(frMsgs);

			cbSystem.Items := cbUser.Items;

		finally
			FindClose(frMsgs);
		end;
	end;

	if UsingWinNT then
	begin
		if not IsAdminLoggedOn then //only admins can change system-wide environment variables
		begin
			cbSystem.Enabled := False;
			lblSystem.Enabled := False;
		end;

		if RegQueryStringValue(HKEY_LOCAL_MACHINE,'SYSTEM\CurrentControlSet\Control\Session Manager\Environment','LANG',regSys) then
			cbSystem.ItemIndex := GetLangIndex(cbSystem.Items,regSys)
		else
			cbSystem.ItemIndex := 0;

		if cbSystem.ItemIndex = -1 then
			cbSystem.ItemIndex := cbSystem.Items.Add(regSys);


		if RegQueryStringValue(HKEY_CURRENT_USER,'Environment','LANG',regUser) then
			cbUser.ItemIndex := GetLangIndex(cbSystem.Items,regUser)
		else
			cbUser.ItemIndex := 0;

		if cbUser.ItemIndex = -1 then
			cbUser.ItemIndex := cbUser.Items.Add(regUser);
	end;


	if frmLangChooser.ShowModal = 1 then
	begin
		regSys := ExtractLang(cbSystem.Items.Strings[cbSystem.ItemIndex]);

		if UsingWinNT then
		begin
			regUser := ExtractLang(cbUser.Items.Strings[cbUser.ItemIndex]);

			if cbUser.ItemIndex <> 0 then
			begin
				if not RegWriteStringValue(HKEY_CURRENT_USER,'Environment','LANG',regUser) then
					MsgBox(GetTransStr('LangRegUserFailed'),mbCriticalError,mb_ok);
			end else
				if RegValueExists(HKEY_CURRENT_USER,'Environment','LANG') and
				  (not RegDeleteValue(HKEY_CURRENT_USER,'Environment','LANG')) then
					MsgBox(GetTransStr('LangRegUserFailed'),mbCriticalError,mb_ok);

			if IsAdminLoggedOn then
			begin
				if cbSystem.ItemIndex <> 0 then
				begin
					if not RegWriteStringValue(HKEY_LOCAL_MACHINE,'SYSTEM\CurrentControlSet\Control\Session Manager\Environment','LANG',regSys) then
						MsgBox(GetTransStr('LangRegSysFailed'),mbCriticalError,mb_ok);
				end else
					if RegValueExists(HKEY_LOCAL_MACHINE,'SYSTEM\CurrentControlSet\Control\Session Manager\Environment','LANG') and
					  (not RegDeleteValue(HKEY_LOCAL_MACHINE,'SYSTEM\CurrentControlSet\Control\Session Manager\Environment','LANG')) then
						MsgBox(GetTransStr('LangRegSysFailed'),mbCriticalError,mb_ok);
			end;

			//straight from the Inno source
			SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, MsgResult);

		end else
		begin
			if not FileCopy(ExpandConstant('{sd}\AutoExec.bat'),ExpandConstant('{sd}\AutoExec.WAM'),False) then
				if MsgBox(GetTransStr('LangAutoExecBackupFailed'),mbConfirmation,mb_yesno) = idno then
					exit;

			if LoadStringsFromFile(ExpandConstant('{sd}\Autoexec.bat'), AutoExec) then
			begin
				for i := GetArrayLength(AutoExec) - 1 downto 0 do
					if pos('set lang=',LowerCase(AutoExec[i])) > 0 then
						if (i>0) and (i<(GetArrayLength(AutoExec)-1))
						  and (LowerCase(AutoExec[i-1]) = 'REM /=== by Wammu Language Setup ===\')
						  and (LowerCase(AutoExec[i+1]) = 'REM \=== by Wammu Language Setup ===/') then
						begin
							for j := i to GetArrayLength(AutoExec) - 2 do //remove previous setting
								AutoExec[j-1] := AutoExec[j+1];
							SetArrayLength(AutoExec,GetArrayLength(AutoExec) - 3);
						end;

				i := GetArrayLength(AutoExec);
				SetArrayLength(AutoExec,i + 3);
				AutoExec[i] := 'REM /=== by Wammu Language Setup ===\';
				AutoExec[i+1] := 'SET LANG='+regSys;
				AutoExec[i+2] := 'REM \=== by Wammu Language Setup ===/';

				if SaveStringsToFile(ExpandConstant('{sd}\AutoExec.bat'),AutoExec,False) then
					MsgBox(GetTransStr('LangRestartRequired'),mbInformation,mb_ok)
				else
					MsgBox(GetTransStr('LangErrorSavingAutoExec'),mbCriticalError,mb_ok);

			end else
				MsgBox(GetTransStr('LangErrorLoadingAutoExec'), mbCriticalError, MB_OK);
		end;
	end;

end;


function InitializeUninstall(): Boolean;
var i: Integer;
begin

	Result := True;

	for i := 1 to ParamCount do
	begin
		if LowerCase(ParamStr(i)) = '/langsetup' then
		begin
			LanguageForm;
			Result := False;
			break;
		end;
	end;


end;

begin
end.

; vim: fileencoding=windows-1250 fencs=windows-1250:

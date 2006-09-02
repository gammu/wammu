; Inno Setup Script for Wammu installation
; Copyright (c) 2006 Michal Èihaø

#define MyAppDosName "wammu"
#define MyAppName "Wammu"
#define MyAppVersion "0.15"
#define MyAppPublisher "Micha Èihaø"
#define MyAppURL "http://cihar.com/gammu/wammu"
#define MyAppPublisherURL "http://cihar.com"
#define MyAppBugsURL "http://bugs.cihar.com"
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

[Languages]
Name: en; MessagesFile: compiler:Default.isl
Name: ca; MessagesFile: compiler:Languages\Catalan.isl
Name: cz; MessagesFile: compiler:Languages\Czech.isl
Name: nl; MessagesFile: compiler:Languages\Dutch.isl
Name: fr; MessagesFile: compiler:Languages\French.isl
Name: de; MessagesFile: compiler:Languages\German.isl
Name: hu; MessagesFile: compiler:Languages\Hungarian.isl
Name: it; MessagesFile: compiler:Languages\Italian.isl
Name: pl; MessagesFile: compiler:Languages\Polish.isl
Name: pt; MessagesFile: compiler:Languages\Portuguese.isl
Name: sk; MessagesFile: compiler:Languages\Slovak.isl

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked

[Files]
Source: dist\*; DestDir: {app}; Flags: ignoreversion recursesubdirs createallsubdirs

[INI]
Filename: {app}\{#MyAppUrlName}; Section: InternetShortcut; Key: URL; String: {#MyAppURL}
Filename: {app}\{#MyAppBugsUrlName}; Section: InternetShortcut; Key: URL; String: {#MyAppBugsURL}

[Icons]
Name: {group}\{#MyAppName}; Filename: {app}\{#MyAppExeName}; IconFilename: {app}\share\pixmaps\wammu.ico; IconIndex: 0
Name: {group}\{cm:ProgramOnTheWeb,{#MyAppName}}; Filename: {app}\{#MyAppUrlName}
Name: {group}\{cm:ReportBug,{#MyAppName}}; Filename: {app}\{#MyAppBugsUrlName}
Name: {group}\{cm:UninstallProgram,{#MyAppName}}; Filename: {uninstallexe}
Name: {userdesktop}\{#MyAppName}; Filename: {app}\{#MyAppExeName}; Tasks: desktopicon

[Run]
Filename: {app}\{#MyAppExeName}; Description: {cm:LaunchProgram,{#MyAppName}}; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: files; Name: {app}\{#MyAppUrlName}
Type: files; Name: {app}\{#MyAppBugsUrlName}

[CustomMessages]
en.ReportBug=Report bug in application %1
cz.ReportBug=Nahlásit chybu v aplikaci %1

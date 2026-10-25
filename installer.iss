; Inno Setup Script for Twitch OCR Chatbot
; Produces a single self-contained Windows Installer (.exe) with Start Menu and Desktop shortcuts.

#define MyAppName "Twitch OCR Chatbot"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Twitch OCR Chatbot"
#define MyAppURL "https://github.com/matt1/Twitch-OCR-Chatbot"
#define MyAppExeName "TwitchOCRBot.exe"

[Setup]
AppId={{9F82B761-464A-4BC7-95AC-E44CE08D8E5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\TwitchOCRChatbot
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
SetupIconFile=static\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=dist
OutputBaseFilename=TwitchOCRBot-Setup-v1.0.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy all compiled binaries and assets from the PyInstaller dist directory
Source: "dist\TwitchOCRBot\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Launch Twitch OCR Chatbot Background Service & OBS Dock"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}} (Opens OBS Dock Control Center)"; Flags: nowait postinstall skipifsilent

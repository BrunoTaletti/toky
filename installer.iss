#define MyAppVersion "1.0"

[Setup]
AppName=Toky
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Toky
DefaultGroupName=Toky 2FA
OutputDir=setup
OutputBaseFilename=TokySetup_{#MyAppVersion}
Compression=lzma
SolidCompression=yes
SetupIconFile=app-icon.ico
DisableProgramGroupPage=no

[Files]
Source: "dist\toky.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}\resources"; Flags: recursesubdirs createallsubdirs
Source: "styles\*"; DestDir: "{app}\styles"; Flags: recursesubdirs createallsubdirs
Source: "translations\*"; DestDir: "{app}\translations"; Flags: recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Criar ícone na área de trabalho"; GroupDescription: "Opções adicionais:"; Flags: unchecked

[Icons]
Name: "{group}\Toky 2FA"; Filename: "{app}\toky.exe"
Name: "{commondesktop}\Toky 2FA"; Filename: "{app}\toky.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\toky.exe"; Description: "Executar Toky"; Flags: nowait postinstall skipifsilent
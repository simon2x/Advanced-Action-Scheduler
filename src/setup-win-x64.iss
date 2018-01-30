[Setup]
AppName=Advanced Action Scheduler
AppVersion=0.1.0
DefaultDirName={pf64}\Advanced Action Scheduler
DefaultGroupName=Advanced Action Scheduler
UninstallDisplayIcon={app}\icon.ico
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "advancedactionscheduler-win-x64.exe"; DestDir: "{app}"; DestName: "advancedactionscheduler.exe";
Source: "splash.png"; DestDir: "{app}"
Source: "images\*.png"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icons\*.png"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE"; DestDir: "{app}";
Source: "icon.ico"; DestDir: "{app}";

[Icons]
Name: "{group}\Advanced Action Scheduler"; Filename: "{app}\advancedactionscheduler.exe"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\Advanced Action Scheduler.exe"; Filename: "{app}\advancedactionscheduler.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks] 
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Run]
;Filename: "{app}\INIT.EXE"; Parameters: "/x"
;Filename: "{app}\README.TXT"; Description: "View the README file"; Flags: postinstall shellexec skipifsilent
Filename: "{app}\advancedactionscheduler.exe"; Description: "Launch Advanced Action Scheduler"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
;Type: files; Name: "{app}\config.json"
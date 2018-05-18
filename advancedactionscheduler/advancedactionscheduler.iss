[Setup]
AppName=Advanced Action Scheduler
AppVersion=0.1.0
DefaultDirName={pf64}\Advanced Action Scheduler
DefaultGroupName=Advanced Action Scheduler
UninstallDisplayIcon={app}\advancedactionscheduler.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "advancedactionscheduler.exe"; DestDir: "{app}"; Check: IsWin64;
Source: "splash.png"; DestDir: "{app}"
Source: "images\*.png"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icons\*.png"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "MyProg.chm"; DestDir: "{app}"
;Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\AdvancedActionScheduler"; Filename: "{app}\advancedactionscheduler.exe"; IconFilename: "{app}\icon.ico"

[Tasks] 
;Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked 

[Run]
;Filename: "{app}\INIT.EXE"; Parameters: "/x"
;Filename: "{app}\README.TXT"; Description: "View the README file"; Flags: postinstall shellexec skipifsilent
Filename: "{app}\advancedactionscheduler.EXE"; Description: "Launch Advanced Action Scheduler"; Flags: postinstall nowait skipifsilent unchecked

[UninstallDelete]
Type: files; Name: "{app}\config.json"
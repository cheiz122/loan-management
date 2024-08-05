; Inno Setup Script

[Setup]
AppName=Loan Management System
AppVersion=1.0
DefaultDirName={pf}\Loan Management System
DefaultGroupName=Loan Management System
OutputDir=C:\Users\peter\Desktop\loan\customer_management\installer
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes

; Define the path to your .exe and other files
[Files]
Source: "C:\Users\peter\Desktop\loan\customer_management\dist\manage.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\peter\Desktop\loan\customer_management\customer_management_app\static\*"; DestDir: "{app}\customer_management_app\static"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\peter\Desktop\loan\customer_management\customer_management_app\templates\*"; DestDir: "{app}\customer_management_app\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\peter\Desktop\loan\customer_management\logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Loan Management System"; Filename: "{app}\manage.exe"
Name: "{userdesktop}\Loan Management System"; Filename: "{app}\manage.exe"

[Run]
Filename: "{app}\manage.exe"; Description: "Launch Loan Management System"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Add any additional setup tasks here if needed
  end;
end;



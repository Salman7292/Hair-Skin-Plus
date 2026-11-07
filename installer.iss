; ══════════════════════════════════════════════════════════════
;  Hair Skin Plus — Inno Setup Installer Script
;  Builds: HairSkinPlus-Setup.exe  (~self-contained Windows installer)
;
;  PREREQUISITES:
;    1. Run PyInstaller first:
;         pyinstaller HairSkinPlus.spec
;       This creates dist\HairSkinPlus\ folder.
;    2. Install Inno Setup 6 from: https://jrsoftware.org/isdl.php
;    3. Open this file in Inno Setup IDE → Compile
;       OR run: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
;
;  Output: Output\HairSkinPlus-Setup.exe
; ══════════════════════════════════════════════════════════════

#define AppName    "Hair Skin Plus"
#define AppVersion "1.0.0"
#define AppPublish "Dr. Seyab Ur Rahman — Dermatology Clinic"
#define AppURL     "https://github.com/Salman7292/Hair-Skin-Plus"
#define AppExe     "HairSkinPlus.exe"
#define DistDir    "dist\HairSkinPlus"

[Setup]
AppId={{A3F7B2C1-D904-4E8A-B6F0-1234567890AB}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublish}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\HairSkinPlus
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Installer icon and banner
SetupIconFile=static\app_icon.ico
WizardImageFile=static\stamp.png
WizardSmallImageFile=static\stamp.png
WizardStyle=modern
; Output
OutputDir=Output
OutputBaseFilename=HairSkinPlus-Setup
Compression=lzma2/max
SolidCompression=yes
; Minimum Windows 10
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; Require admin so it installs for all users
PrivilegesRequired=admin
; Uninstall support
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";  Description: "Create a &Desktop shortcut";      GroupDescription: "Additional icons:"; Flags: checked
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut";  GroupDescription: "Additional icons:"; Flags: checked
Name: "launchatstart"; Description: "&Launch Hair Skin Plus after install"; GroupDescription: ""; Flags: checked

[Files]
; ── Main application bundle (from PyInstaller) ──────────────────────────────
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ── Preserve existing medicines.db in AppData (don't overwrite user data) ───
; The initial database is bundled inside the dist folder already.
; On update installs, we skip overwriting the live database.
Source: "{#DistDir}\medicines.db"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
; Desktop shortcut
Name: "{autodesktop}\{#AppName}";     Filename: "{app}\{#AppExe}"; IconFilename: "{app}\{#AppExe}"; Tasks: desktopicon
; Start Menu shortcuts
Name: "{group}\{#AppName}";           Filename: "{app}\{#AppExe}"; IconFilename: "{app}\{#AppExe}"; Tasks: startmenuicon
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

[Run]
; Launch after install
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent; Tasks: launchatstart

[UninstallDelete]
; Remove the generated __pycache__ and .pyc files on uninstall
Type: filesandordirs; Name: "{app}\__pycache__"


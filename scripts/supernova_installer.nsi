# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
!define APPNAME "SuperNova 2177"
!define APPEXE "supernova-cli.exe"
!define OUTPUT "superNova_2177_Installer.exe"

OutFile "${OUTPUT}"
InstallDir "$PROGRAMFILES\SuperNova2177"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\\${APPEXE}"
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\${APPEXE}"
SectionEnd

; NSIS installer script for superNova_2177
OutFile "supernova-setup.exe"
InstallDir "$PROGRAMFILES\superNova_2177"
Page directory
Page instfiles
Section "Install"
  SetOutPath $INSTDIR
  File "dist\supernova-cli.exe"
  CreateShortcut "$DESKTOP\superNova.lnk" "$INSTDIR\supernova-cli.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\superNova.lnk"
  Delete "$INSTDIR\supernova-cli.exe"
  RMDir $INSTDIR
SectionEnd

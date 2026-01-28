; Instalador NSIS para Furious App (Electron)
; Requer NSIS 3.08 ou superior
; Instalador profissional, seguro e facil de usar

!include "MUI2.nsh"
!include "x64.nsh"
!include "LogicLib.nsh"

; Configuracoes gerais
Name "Furious App"
OutFile "FuriousAppInstaller.exe"
InstallDir "$PROGRAMFILES\FuriousApp"
Icon "images\icon.ico"

; Imagens para o instalador
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "launcher\\images\\banner.bmp"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_WELCOMEFINISHPAGE_BITMAP "launcher\\images\\header.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "launcher\\images\\header.bmp"
!define MUI_ICON "launcher\images\icone.ico"
!define MUI_UNICON "launcher\images\icone.ico"

; Verificar privilegios de administrador
RequestExecutionLevel admin

; Variaveis
Var StartMenuFolder

; ====================================
; Paginas do instalador
; ====================================
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU "FuriousApp" $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; ====================================
; Idiomas
; ====================================
!insertmacro MUI_LANGUAGE "Portuguese"
!insertmacro MUI_LANGUAGE "English"

; ====================================
; Secao de Instalacao
; ====================================
Section "Instalar Furious App"
    SetOutPath "$INSTDIR\backend"
    File /r "backend\*.*"
    
    SetOutPath "$INSTDIR\engine"
    File /r "engine\*.*"
    
    SetOutPath "$INSTDIR\frontend\dist"
    File /r "frontend\dist\*.*"
    
    ; Copia arquivo principal do Electron
    SetOutPath "$INSTDIR"
    File "electron-main.js"
    File "electron-preload.js"
    File "package.json"
    
    SetOutPath "$INSTDIR\portables\aria2-1.37.0"
    File /r "portables\aria2-1.37.0\*.*"
    
    SetOutPath "$INSTDIR\portables\node-v18.16.1-win-x64"
    File /r "portables\node-v18.16.1-win-x64\*.*"
    
    ; Copia Python portatil
    SetOutPath "$INSTDIR\portables\python-64bits"
    File /r "portables\python-64bits\*.*"
    
    SetOutPath "$INSTDIR\images"
    File /r "images\*.*"
    
    SetOutPath "$INSTDIR"
    File "README.md"
    
    ; Cria atalho no Desktop
    CreateDirectory "$DESKTOP"
    CreateShortCut "$DESKTOP\Furious App.lnk" "$INSTDIR\Furious App.exe" "" "$INSTDIR\Furious App.exe" 0
    
    ; Cria atalhos no Menu Iniciar
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Furious App.lnk" "$INSTDIR\Furious App.exe" "" "$INSTDIR\Furious App.exe" 0
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Desinstalar.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Pasta de Instalacao.lnk" "$INSTDIR"
    
    ; Cria desinstalador
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Adiciona entrada no Painel de Controle (Adicionar/Remover Programas)
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "DisplayName" "Furious App"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "DisplayVersion" "3.3.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "Publisher" "Diego's Apps"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "NoRepair" 1
    
    ; Cria arquivo de informacoes de instalacao
    FileOpen $0 "$INSTDIR\INSTALACAO.txt" w
    FileWrite $0 "====================================$\r$\n"
    FileWrite $0 "Furious App - Informacoes de Instalacao$\r$\n"
    FileWrite $0 "====================================$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "Versao: 3.3.0$\r$\n"
    FileWrite $0 "Local: $INSTDIR$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "Componentes Instalados:$\r$\n"
    FileWrite $0 "- Backend FastAPI$\r$\n"
    FileWrite $0 "- Engine Download$\r$\n"
    FileWrite $0 "- Frontend Vue.js$\r$\n"
    FileWrite $0 "- aria2 1.37.0$\r$\n"
    FileWrite $0 "- Node.js 18.16.1$\r$\n"
    FileWrite $0 "- Launcher Scripts$\r$\n"
    FileWrite $0 "$\r$\n"
    FileWrite $0 "Uso: Execute 'Furious App' no Menu Iniciar ou Desktop$\r$\n"
    FileClose $0
    
    MessageBox MB_OK "Furious App foi instalado com sucesso!$\n$\nUse o atalho no Desktop ou Menu Iniciar para iniciar."
    
SectionEnd

; ====================================
; Secao de Desinstalacao
; ====================================
Section "Uninstall"
    SetShellVarContext all
    
    Delete "$DESKTOP\Furious App.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Furious App.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Desinstalar.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Pasta de Instalacao.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"
    
    ; Remove arquivos e pasta de instalacao
    RMDir /r "$INSTDIR"

    ; --- LIMPEZA DE DADOS DO USUARIO (ROAMING) ---
    SetShellVarContext current
    RMDir /r "$APPDATA\furiousapp"
    RMDir /r "$LOCALAPPDATA\furiousapp"
    ; Limpeza legado
    RMDir /r "$APPDATA\furious-app"
    RMDir /r "$LOCALAPPDATA\furious-app"
    SetShellVarContext all
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp"
    
    MessageBox MB_OK "Furious App foi desinstalado com sucesso!"
    
SectionEnd


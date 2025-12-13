; Instalador NSIS para Furious App (Electron)
; Requer NSIS 3.08 ou superior
; Instalador profissional, seguro e facil de usar

!include "MUI2.nsh"
!include "x64.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; Configuracoes gerais
Name "Furious App"
OutFile "launcher\Furious App Setup 2.1.0.exe"
InstallDir "$PROGRAMFILES\FuriousApp"
Icon "launcher\images\icone.ico"

; Imagens para o instalador
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
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
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU "FuriousApp" $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\Furious App.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Executar Furious App"
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
Section "Instalar Furious App" SecMain
    SectionIn RO  ; Read-only, sempre instalado
    
    ; Copia todos os arquivos do Electron (win-unpacked)
    ; Exclui ferramentas antigas do PyQt5/WebView/PyInstaller que não são mais usadas
    SetOutPath "$INSTDIR"
    File /r /x "PyScripter" /x "tcl" /x "Doc" /x "PyQt5" /x "PyQt5-Qt5" /x "PyQt5_Qt5" /x "PyQtWebEngine" /x "PyQtWebEngine_Qt5" /x "PyInstaller" /x "_pyinstaller_hooks_contrib" /x "altgraph" /x "pyarmor" /x "pyarmor_runtime" "launcher\win-unpacked\*.*"
    
    ; Cria atalho no Desktop
    CreateDirectory "$DESKTOP"
    CreateShortCut "$DESKTOP\Furious App.lnk" "$INSTDIR\Furious App.exe" "" "$INSTDIR\Furious App.exe" 0
    
    ; Cria atalhos no Menu Iniciar
    !insertmacro MUI_STARTMENU_WRITE_BEGIN "FuriousApp"
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Furious App.lnk" "$INSTDIR\Furious App.exe" "" "$INSTDIR\Furious App.exe" 0
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Desinstalar.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Pasta de Instalacao.lnk" "$INSTDIR"
    !insertmacro MUI_STARTMENU_WRITE_END
    
    ; Cria desinstalador
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Adiciona entrada no Painel de Controle (Adicionar/Remover Programas)
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "DisplayName" "Furious App"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "DisplayVersion" "2.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "Publisher" "Furious Apps"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "DisplayIcon" "$INSTDIR\Furious App.exe"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "NoRepair" 1
    
    ; Calcula tamanho da instalacao
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp" "EstimatedSize" "$0"
    
SectionEnd

; ====================================
; Descricoes das Secoes
; ====================================
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Arquivos principais do Furious App"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ====================================
; Secao de Desinstalacao
; ====================================
Section "Uninstall"
    SetShellVarContext all

    SetShellVarContext current
    RMDir /r "$APPDATA\Furious App"
    RMDir /r "$LOCALAPPDATA\Furious App"
    SetShellVarContext all
    
    ; Remove atalhos
    Delete "$DESKTOP\Furious App.lnk"
    
    ; Remove pasta do Menu Iniciar
    !insertmacro MUI_STARTMENU_GETFOLDER "FuriousApp" $StartMenuFolder
    Delete "$SMPROGRAMS\$StartMenuFolder\Furious App.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Desinstalar.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Pasta de Instalacao.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"
    
    ; Remove arquivos e pasta de instalacao
    RMDir /r "$INSTDIR"
    
    ; Remove entrada do registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FuriousApp"
    
    MessageBox MB_OK "Furious App foi desinstalado com sucesso!"
    
SectionEnd

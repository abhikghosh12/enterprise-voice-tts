; Enterprise Voice Browser with Ollama - Unified Installer
; NSIS Script for Windows Installer
; Version 2.0.0

!define PRODUCT_NAME "Enterprise Voice Browser"
!define PRODUCT_VERSION "2.0.0"
!define PRODUCT_PUBLISHER "Enterprise Voice Team"
!define PRODUCT_WEB_SITE "https://github.com/yourusername/enterprise-voice-tts"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\EnterpriseVoiceBrowser.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI Settings
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

; MUI Settings / Icons
!define MUI_ICON "icon.png"
!define MUI_UNICON "icon.png"

; MUI Settings / Header
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "icon.png"
!define MUI_ABORTWARNING

; MUI Settings / Welcome page
!define MUI_WELCOMEPAGE_TITLE "Welcome to ${PRODUCT_NAME} Setup"
!define MUI_WELCOMEPAGE_TEXT "This installer will install ${PRODUCT_NAME} and Ollama AI Engine on your computer.$\r$\n$\r$\nOllama is required for AI features and will be downloaded and installed automatically.$\r$\n$\r$\nClick Next to continue."

; MUI Settings / Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\EnterpriseVoiceBrowser.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Enterprise-Voice-Browser-Setup-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES64\Enterprise Voice Browser"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel admin

; Variables
Var OllamaInstalled
Var OllamaPath
Var DownloadOllama
Var TempOllamaInstaller

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try

  ; Display installation message
  DetailPrint "Installing ${PRODUCT_NAME}..."

  ; Check if Ollama is already installed
  DetailPrint "Checking for existing Ollama installation..."
  Call CheckOllamaInstalled

  ${If} $OllamaInstalled == "0"
    DetailPrint "Ollama not found. Will download and install..."
    MessageBox MB_YESNO "Ollama AI Engine is required but not installed.$\r$\n$\r$\nWould you like to download and install Ollama now? (Recommended)$\r$\n$\r$\nSize: ~500MB" IDYES download_ollama IDNO skip_ollama

    download_ollama:
      DetailPrint "Downloading Ollama installer..."
      StrCpy $TempOllamaInstaller "$TEMP\OllamaSetup.exe"

      ; Download Ollama
      NSISdl::download "https://ollama.com/download/OllamaSetup.exe" "$TempOllamaInstaller"
      Pop $0

      ${If} $0 == "success"
        DetailPrint "Download complete. Installing Ollama..."
        MessageBox MB_OK "Ollama will now be installed. Please follow the Ollama installation wizard.$\r$\n$\r$\nAfter Ollama installs, this installer will continue."

        ; Run Ollama installer
        ExecWait '"$TempOllamaInstaller"' $0

        ${If} $0 == 0
          DetailPrint "Ollama installed successfully!"
          MessageBox MB_OK "Ollama has been installed successfully!"
        ${Else}
          DetailPrint "Ollama installation may have failed or was cancelled."
          MessageBox MB_OK "Ollama installation completed with code: $0$\r$\n$\r$\nYou may need to install Ollama manually from ollama.com"
        ${EndIf}

        ; Clean up
        Delete "$TempOllamaInstaller"
      ${Else}
        DetailPrint "Failed to download Ollama: $0"
        MessageBox MB_OK "Failed to download Ollama automatically.$\r$\n$\r$\nPlease download Ollama manually from: https://ollama.com/download$\r$\n$\r$\nThe browser installation will continue, but you'll need Ollama to use AI features."
      ${EndIf}
      Goto ollama_done

    skip_ollama:
      DetailPrint "Ollama installation skipped by user."
      MessageBox MB_OK "You chose to skip Ollama installation.$\r$\n$\r$\nYou can install Ollama later from: https://ollama.com/download$\r$\n$\r$\nThe browser will not have AI features until Ollama is installed."
      Goto ollama_done
  ${Else}
    DetailPrint "Ollama is already installed at: $OllamaPath"
    MessageBox MB_OK "Ollama is already installed on your system.$\r$\n$\r$\nSkipping Ollama installation."
  ${EndIf}

  ollama_done:

  ; Install browser files
  DetailPrint "Installing Enterprise Voice Browser..."

  ; Copy browser files (these will come from the electron build)
  File /r "dist\win-unpacked\*.*"

  ; Create README
  FileOpen $0 "$INSTDIR\README.txt" w
  FileWrite $0 "Enterprise Voice Browser v${PRODUCT_VERSION}$\r$\n"
  FileWrite $0 "======================================$\r$\n$\r$\n"
  FileWrite $0 "Thank you for installing Enterprise Voice Browser!$\r$\n$\r$\n"
  FileWrite $0 "IMPORTANT - Before First Use:$\r$\n"
  FileWrite $0 "1. Make sure Ollama is running$\r$\n"
  FileWrite $0 "2. Download an AI model:$\r$\n"
  FileWrite $0 "   - Open PowerShell or Command Prompt$\r$\n"
  FileWrite $0 "   - Run: ollama pull llama3.2:1b$\r$\n"
  FileWrite $0 "   - Wait for download to complete (~1.3GB)$\r$\n$\r$\n"
  FileWrite $0 "3. Launch Enterprise Voice Browser$\r$\n$\r$\n"
  FileWrite $0 "For help and documentation:$\r$\n"
  FileWrite $0 "${PRODUCT_WEB_SITE}$\r$\n"
  FileClose $0

  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Enterprise Voice Browser"
  CreateShortCut "$SMPROGRAMS\Enterprise Voice Browser\Enterprise Voice Browser.lnk" "$INSTDIR\EnterpriseVoiceBrowser.exe"
  CreateShortCut "$SMPROGRAMS\Enterprise Voice Browser\Uninstall.lnk" "$INSTDIR\uninst.exe"
  CreateShortCut "$DESKTOP\Enterprise Voice Browser.lnk" "$INSTDIR\EnterpriseVoiceBrowser.exe"

SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\Enterprise Voice Browser\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\EnterpriseVoiceBrowser.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\EnterpriseVoiceBrowser.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Check if Ollama is installed
Function CheckOllamaInstalled
  ; Check if ollama.exe exists in common locations
  StrCpy $OllamaInstalled "0"

  ; Check PATH
  nsExec::ExecToStack 'where ollama.exe'
  Pop $0 ; return value
  Pop $1 ; output

  ${If} $0 == 0
    StrCpy $OllamaInstalled "1"
    StrCpy $OllamaPath $1
  ${Else}
    ; Check common install locations
    IfFileExists "$PROGRAMFILES\Ollama\ollama.exe" 0 check_local
      StrCpy $OllamaInstalled "1"
      StrCpy $OllamaPath "$PROGRAMFILES\Ollama\ollama.exe"
      Goto end_check

    check_local:
    IfFileExists "$LOCALAPPDATA\Programs\Ollama\ollama.exe" 0 end_check
      StrCpy $OllamaInstalled "1"
      StrCpy $OllamaPath "$LOCALAPPDATA\Programs\Ollama\ollama.exe"
  ${EndIf}

  end_check:
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer.$\r$\n$\r$\nNote: Ollama was NOT uninstalled. If you want to remove Ollama, please uninstall it separately from Windows Settings."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\README.txt"

  ; Remove browser files
  RMDir /r "$INSTDIR"

  ; Remove shortcuts
  Delete "$SMPROGRAMS\Enterprise Voice Browser\Uninstall.lnk"
  Delete "$SMPROGRAMS\Enterprise Voice Browser\Website.lnk"
  Delete "$SMPROGRAMS\Enterprise Voice Browser\Enterprise Voice Browser.lnk"
  Delete "$DESKTOP\Enterprise Voice Browser.lnk"

  RMDir "$SMPROGRAMS\Enterprise Voice Browser"

  ; Remove registry keys
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  SetAutoClose true
SectionEnd

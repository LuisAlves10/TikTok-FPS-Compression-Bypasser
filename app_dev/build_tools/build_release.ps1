$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")

$vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $vswhere)) {
    throw "Could not locate vswhere.exe."
}

$installationPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $installationPath) {
    throw "Could not locate Microsoft C++ Build Tools."
}

$vsDevCmd = Join-Path $installationPath "Common7\Tools\VsDevCmd.bat"
cmd /c "`"$vsDevCmd`" -arch=x64 -host_arch=x64 && python app_dev\build_tools\build_release.py"

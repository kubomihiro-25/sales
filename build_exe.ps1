param(
  [switch]$InstallPyInstaller,
  [switch]$Clean,
  [string]$OutputDirectory = ""
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if ($InstallPyInstaller) { py -m pip install pyinstaller }
$output = if ($OutputDirectory) { $OutputDirectory } else { Join-Path $PSScriptRoot "NewtonXSalesCopilot" }
if ($Clean -and (Test-Path (Join-Path $output "NewtonXSalesCopilot.exe"))) { Get-Process NewtonXSalesCopilot -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id | ForEach-Object { Stop-Process -Id $_ -Force }; Remove-Item (Join-Path $output "NewtonXSalesCopilot.exe") -Force }
py -m PyInstaller --noconfirm --clean --onefile --windowed --name NewtonXSalesCopilot --distpath $output --workpath (Join-Path $PSScriptRoot "build\desktop") --specpath (Join-Path $PSScriptRoot "build\desktop") --hidden-import newtonx_adk --hidden-import requests --hidden-import msal --hidden-import jwt --hidden-import cryptography desktop_app.py
Write-Host "Built native desktop app: $(Join-Path $output 'NewtonXSalesCopilot.exe')"

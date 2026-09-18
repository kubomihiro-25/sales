param(
  [switch]$InstallPyInstaller,
  [switch]$Clean
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if ($InstallPyInstaller) { py -m pip install pyinstaller }
if ($Clean -and (Test-Path .\dist\NewtonXSalesCopilot.exe)) { Get-Process NewtonXSalesCopilot -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id | ForEach-Object { Stop-Process -Id $_ -Force }; Remove-Item .\dist\NewtonXSalesCopilot.exe -Force }
py -m PyInstaller --noconfirm --clean --onefile --name NewtonXSalesCopilot --add-data "index.html;." --add-data "styles.css;." --add-data "app.js;." --hidden-import newtonx_adk --hidden-import requests --hidden-import msal --hidden-import jwt --hidden-import cryptography app.py
Write-Host "Built: $PSScriptRoot\dist\NewtonXSalesCopilot.exe"

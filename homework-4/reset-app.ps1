$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Copy-Item -Recurse -Force .\seed\src\* .\src\
Copy-Item -Recurse -Force .\seed\tests\* .\tests\
if (Test-Path .\src\receipts) { Remove-Item -Recurse -Force .\src\receipts }

Write-Host "App reset to buggy seed."
Write-Host "calculator.py now contains:"
Get-Content .\src\calculator.py | Select-String "per_person ="


# Script PowerShell para baixar fbclient.dll
$url = "https://github.com/FirebirdSQL/firebird/releases/download/v3.0.10/Firebird-3.0.10.33601-0_x64.zip"
$zipFile = "$env:TEMP\firebird_client.zip"
$extractPath = "$env:TEMP\firebird_extract"

Write-Host "Baixando Firebird Client..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $url -OutFile $zipFile

Write-Host "Extraindo arquivo..." -ForegroundColor Yellow
Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

Write-Host "Copiando fbclient.dll..." -ForegroundColor Yellow
Copy-Item "$extractPath\fbclient.dll" -Destination "C:\Firebird\bin\fbclient.dll" -Force

Write-Host "Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item $zipFile -Force
Remove-Item $extractPath -Recurse -Force

Write-Host "✓ Firebird Client instalado em: C:\Firebird\bin" -ForegroundColor Green
Write-Host "✓ Adicione ao PATH ou copie para C:\Windows\System32" -ForegroundColor Green

# generate-logs.ps1
New-Item -ItemType Directory -Force -Path logs | Out-Null
while ($true) {
  $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  $levels = @("INFO", "WARN", "ERROR")
  $level = Get-Random -InputObject $levels
  "$ts $level demo log line id=$([int](Get-Random -Maximum 9999))" | Out-File -Append -FilePath .\logs\app.log
  Start-Sleep 2
}

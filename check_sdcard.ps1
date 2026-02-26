$shell = New-Object -ComObject Shell.Application
$computer = $shell.Namespace(17)

$tablet = $computer.Items() | Where-Object { $_.Name -match "SwoopG'sTab A7" }
if (-not $tablet) { Write-Host "Tablet not found"; exit }

$sdcard = $tablet.GetFolder.Items() | Where-Object { $_.Name -match "SD card" }
if (-not $sdcard) { Write-Host "SD card not found"; exit }

Write-Host "Files on SD card:"
$sdcard.GetFolder.Items() | ForEach-Object {
    if (-not $_.IsFolder) {
        Write-Host " - $($_.Name): $($_.Size) bytes"
    }
}

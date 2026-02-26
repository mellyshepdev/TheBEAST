$shell = New-Object -ComObject Shell.Application
$computer = $shell.Namespace(17)

$tablet = $computer.Items() | Where-Object { $_.Name -match "SwoopG'sTab A7" }
if ($tablet) {
    Write-Host "Found Tablet: '$($tablet.Name)'"
    $tablet.GetFolder.Items() | ForEach-Object { Write-Host " - '$($_.Name)'" }
}
else {
    Write-Host "Tablet not found"
}

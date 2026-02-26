$shell = New-Object -ComObject Shell.Application
$computer = $shell.Namespace(17)

$tablet = $computer.Items() | Where-Object { $_.Name -match "SwoopG'sTab A7" }
if (-not $tablet) {
    Write-Host "Tablet not found"
    exit
}

$sdcard = $tablet.GetFolder.Items() | Where-Object { $_.Name -match "SD card" }
if (-not $sdcard) {
    Write-Host "SD card not found"
    exit
}

$offloadFolder = $sdcard

$files = @(
    "C:\Users\Georg\OneDrive\Pictures\SD Card 1\20250128_143721.mp4",
    "C:\Users\Georg\OneDrive\Pictures\SD Card 1\20240412_105340.mp4",
    "C:\Users\Georg\OneDrive\Pictures\SD Card\videos\Downloading\Photos.zip",
    "C:\Users\Georg\OneDrive\Pictures\SD Card\videos\Downloading\Photos\Photos.zip",
    "C:\Users\Georg\OneDrive\Pictures\SD Card\videos\20241215_120945.mp4",
    "C:\Users\Georg\OneDrive\Pictures\Camera Roll\VID_20250902_174701.mp4",
    "C:\Users\Georg\OneDrive\Pictures\SD Card\videos\20250913_071345.mp4",
    "C:\Users\Georg\OneDrive\Pictures\SD Card 1\20210722_135103.mp4"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Moving $file to SD card..."
        $offloadFolder.GetFolder.CopyHere($file, 256 + 16)
        
        $fileName = Split-Path $file -Leaf
        $copiedFile = $null
        $sourceSize = (Get-Item $file).Length
        
        $timeout = 300
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        While ($stopwatch.Elapsed.TotalSeconds -lt $timeout) {
            $offloadFolder.GetFolder.Items() | ForEach-Object {
                if ($_.Name -eq $fileName) {
                    $copiedFile = $_
                }
            }
            if ($copiedFile -and $copiedFile.Size -ge $sourceSize) {
                Write-Host "Copy complete for $fileName. Deleting source."
                Remove-Item $file -Force
                break
            }
            Start-Sleep -Seconds 5
        }
        if (-not $copiedFile -or $copiedFile.Size -lt $sourceSize) {
            Write-Host "Timeout or error waiting for copy of $fileName"
        }
    }
    else {
        Write-Host "Source file not found: $file"
    }
}
Write-Host "Done."

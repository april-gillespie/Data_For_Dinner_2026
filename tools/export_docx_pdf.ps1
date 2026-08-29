param(
    [Parameter(Mandatory = $true)][string]$InputDocx,
    [Parameter(Mandatory = $true)][string]$OutputPdf
)

$inputPath = [System.IO.Path]::GetFullPath($InputDocx)
$outputPath = [System.IO.Path]::GetFullPath($OutputPdf)
$outputDirectory = [System.IO.Path]::GetDirectoryName($outputPath)
if (-not (Test-Path -LiteralPath $inputPath -PathType Leaf)) {
    throw "Input document not found: $inputPath"
}
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null

$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($inputPath, $false, $true)
    $document.Fields.Update() | Out-Null
    foreach ($storyRange in $document.StoryRanges) {
        $storyRange.Fields.Update() | Out-Null
    }
    $document.ExportAsFixedFormat($outputPath, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
    }
    if ($null -ne $word) {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Get-Item -LiteralPath $outputPath | Select-Object FullName, Length, LastWriteTime

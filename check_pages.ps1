$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open('e:\ROUTE_IQ_version1\RouteIQ_Mini_Project_Report.docx', $false, $true)
    $pages = $doc.ComputeStatistics(2)
    Write-Host "Exact Word Pages: $pages"
    $doc.Close($false)
} catch {
    Write-Host "Error: $_"
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    Get-Process -Name WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force
}

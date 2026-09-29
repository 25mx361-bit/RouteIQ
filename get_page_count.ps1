$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $word.Documents.Open('e:\ROUTE_IQ_version1\RouteIQ_Mini_Project_Report.docx', $false, $true)
$pages = $doc.ComputeStatistics(2)
Write-Host "EXACT_WORD_PAGES:$pages"
$doc.Close($false)
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null

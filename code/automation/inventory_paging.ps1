# Runbook: inventario VM da Azure Resource Graph, paginato per sottoscrizione.
# Lezioni incorporate:
#  - Search-AzGraph -Skip accetta solo valori >= 1: con 0 genera un warning e il job risulta comunque "Completed"
#  - un inventario VUOTO non deve sovrascrivere l'ultimo file buono né attivare la sincronizzazione a valle
$all = @()
foreach ($sub in Get-AzSubscription) {      # vede solo le sottoscrizioni su cui la Managed Identity ha Reader
    $skip = 1
    while ($true) {
        $page = Search-AzGraph -Query $query -Subscription $sub.Id -First $pageSize -Skip $skip
        if (-not $page -or $page.Count -eq 0) { break }
        $all += $page | ForEach-Object {
            [pscustomobject]@{ id = $_.id; name = $_.name; vmSize = $_.vmSize; ResourceId = $_.id }
        }
        if ($page.Count -lt $pageSize) { break }
        $skip += $pageSize
    }
}
if ($all.Count -eq 0) { throw "Inventario vuoto: abort, non sovrascrivo l'ultimo report valido." }   # guard-rail
$all | ConvertTo-Json -Depth 5 | Set-Content vm_report.json
# ... upload su ADLS e chiamata del trigger HTTP della Logic App solo dopo il guard-rail

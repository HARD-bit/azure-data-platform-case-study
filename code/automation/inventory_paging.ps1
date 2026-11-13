# Runbook: VM inventory from Azure Resource Graph, paged per subscription.
# Lessons built in:
#  - Search-AzGraph -Skip only accepts values >= 1: with 0 it raises a warning and the job still shows "Completed"
#  - an EMPTY inventory must never overwrite the last good file nor trigger the downstream sync
$all = @()
foreach ($sub in Get-AzSubscription) {      # only sees subscriptions where the Managed Identity has Reader
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
if ($all.Count -eq 0) { throw "Empty inventory: aborting, the last valid report is not overwritten." }   # guard-rail
$all | ConvertTo-Json -Depth 5 | Set-Content vm_report.json
# ... upload to ADLS, then call the Logic App HTTP trigger only after the guard-rail

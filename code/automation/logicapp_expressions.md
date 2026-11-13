# Logic App expressions that closed the registry sync bugs

```text
# Robust comparison: null-safe, case-insensitive, whitespace-tolerant
@equals(toLower(trim(coalesce(item()?['ResourceId'], ''))),
        toLower(trim(coalesce(items('For_each_3')?['Creation'], ''))))

# Concurrency: Foreach loops that write to the same array variable must run sequentially
"runtimeConfiguration": { "concurrency": { "repetitions": 1 } }

# State idempotency: when a VM is restored, the deletion date must be cleared as well
{ "Deleted": "NO", "DeletionDate": null }

# Skip rows whose ID is not a full VM path (blank or resource-group level) instead of marking them deleted
@contains(toLower(coalesce(items('For_each_3')?['Creation'], '')), '/providers/microsoft.compute/virtualmachines/')
```

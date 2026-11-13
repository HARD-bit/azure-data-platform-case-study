# IaC roadmap (experimental, not yet applied): the data lake as a reusable module.
# Planned flow: terraform import -> terraform plan until "No changes".
variable "resource_group_name"  { type = string }
variable "location"             { type = string }
variable "storage_account_name" { type = string }
variable "container_names"      { type = list(string) } # ["msexports", "ingestion", "config"]

resource "azurerm_storage_account" "lake" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true # hierarchical namespace = ADLS Gen2
}

resource "azurerm_storage_container" "this" {
  for_each              = toset(var.container_names)
  name                  = each.value
  storage_account_name  = azurerm_storage_account.lake.name
  container_access_type = "private"
}

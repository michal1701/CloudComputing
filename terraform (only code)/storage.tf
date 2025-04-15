resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "model_container" {
  name                  = "model"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}

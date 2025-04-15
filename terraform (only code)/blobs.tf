
resource "azurerm_storage_blob" "model_blob" {
  name                   = "model.pkl"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = azurerm_storage_container.model_container.name
  type                   = "Block"
  source                 = "C:/Users/aleks/OneDrive/Pulpit/CloudComputing/src/model/model.pkl" 
}


resource "azurerm_storage_blob" "city_mapping_blob" {
  name                   = "city_mapping.pkl"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = azurerm_storage_container.model_container.name
  type                   = "Block"
  source                 = "C:/Users/aleks/OneDrive/Pulpit/CloudComputing/src/model/city_mapping.pkl" 
}

data "azurerm_storage_account_sas" "blob_sas" {
  connection_string = azurerm_storage_account.storage.primary_connection_string

  https_only = true
  start      = "2025-04-15T10:43:00Z"
  expiry     = "2025-08-12T00:00:00Z"

  resource_types {
    service   = false
    container = false
    object    = true
  }

  services {
    blob  = true
    queue = false
    table = false
    file  = false
  }

  permissions {
    read    = true
    write   = false
    delete  = false
    list    = false
    add     = false
    create  = false
    update  = false
    process = false
    filter  = false
    tag     = false
  }
}


output "blob_model_url" {
  description = "URL for model.pkl with SAS token"
  value       = "https://${azurerm_storage_account.storage.name}.blob.core.windows.net/${azurerm_storage_container.model_container.name}/model.pkl?${data.azurerm_storage_account_sas.blob_sas.sas}"
  sensitive   = true
}

output "blob_city_mapping_url" {
  description = "URL for city_mapping.pkl with SAS token"
  value       = "https://${azurerm_storage_account.storage.name}.blob.core.windows.net/${azurerm_storage_container.model_container.name}/city_mapping.pkl?${data.azurerm_storage_account_sas.blob_sas.sas}"
  sensitive   = true
}

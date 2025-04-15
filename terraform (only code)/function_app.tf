resource "azurerm_service_plan" "function_plan" {
  name                = var.function_app_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_function_app" "function_app" {
  name                       = var.function_app_name
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  service_plan_id            = azurerm_service_plan.function_plan.id
  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

  site_config {
    
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME = "python"
    "FUNCTIONS_EXTENSION_VERSION" = "~4"
    "BLOB_MODEL_URL"          = "https://realvaluatorstorage.blob.core.windows.net/model/model.pkl?sp=r&st=2025-04-15T10:09:58Z&se=2025-07-15T18:09:58Z&sv=2024-11-04&sr=b&sig=JZvFZQdOpp5KM0VoZM3rE4MF%2B4M%2FB1JvDvydgYj%2FQKc%3D"
    "BLOB_CITY_MAPPING_URL"   = "https://realvaluatorstorage.blob.core.windows.net/model/city_mapping.pkl?sp=r&st=2025-04-15T10:08:56Z&se=2025-07-15T18:08:56Z&sv=2024-11-04&sr=b&sig=jHCLfmke3XuvkykNEiY%2FgpIv6ENk%2B7V9bsmzv6%2Bo4pc%3D"
    "DB_CONNECTION"           = "DRIVER={ODBC Driver 18 for SQL Server};Server=realvaluator-sql.database.windows.net,1433;Database=predictionsdb;Uid=adminuser;Pwd=eigh8Ahk;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.app_insights.instrumentation_key
  }
}

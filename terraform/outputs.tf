output "sql_server_fqdn" {
  value       = azurerm_mssql_server.sql_server.fully_qualified_domain_name
}

output "storage_account_conn_string" {
  value       = azurerm_storage_account.storage.primary_connection_string
  sensitive   = true
}

output "blob_model_url" {
  value       = "https://${azurerm_storage_account.storage.name}.blob.core.windows.net/${azurerm_storage_container.model_container.name}/model.pkl?${data.azurerm_storage_account_sas.blob_sas.sas}"
  sensitive   = true
}

output "blob_city_mapping_url" {
  value       = "https://${azurerm_storage_account.storage.name}.blob.core.windows.net/${azurerm_storage_container.model_container.name}/city_mapping.pkl?${data.azurerm_storage_account_sas.blob_sas.sas}"
  sensitive   = true
}

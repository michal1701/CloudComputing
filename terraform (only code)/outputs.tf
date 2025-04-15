output "resource_group_name" {
  description = "The name of the resource group."
  value       = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  description = "The name of the storage account."
  value       = azurerm_storage_account.storage.name
}

output "sql_server_name" {
  description = "The name of the SQL Server."
  value       = azurerm_mssql_server.sql_server.name
}

output "sql_database_name" {
  description = "The name of the SQL Database."
  value       = azurerm_mssql_database.db.name
}

output "function_app_default_hostname" {
  description = "The default hostname of the Function App."
  value       = azurerm_linux_function_app.function_app.default_hostname
}

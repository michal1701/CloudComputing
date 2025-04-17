terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "azurerm" {
  features {}
}

##### Resource Group ###################################################
resource "azurerm_resource_group" "rg" {
  name = var.resource_group_name
  location = var.location
}

##### Azure Container ###################################################
resource "azurerm_container_group" "realval_app" {
  name = var.container_group_name
  location = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type = "Linux"

  image_registry_credential {
    server = var.registry_server
    username = var.registry_username
    password = var.registry_password
  }

  container {
    name = "realval"
    image = var.container_image
    cpu = var.cpu
    memory = var.memory

    ports {
      port = 8501
      protocol = "TCP"
    }
  }

  ip_address_type = "Public"
  dns_name_label  = var.dns_name_label
}

##### Azure SQL Server and database ###################################################
resource "azurerm_mssql_server" "sql_server" {
  name = var.sql_server_name
  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  version = "12.0"
  administrator_login = var.sql_admin_user
  administrator_login_password = var.sql_admin_password
}

resource "azurerm_mssql_database" "db" {
  name = var.sql_database_name
  server_id = azurerm_mssql_server.sql_server.id
  sku_name  = "Basic"
}

##### Azure Storage Account and container ###################################################
resource "azurerm_storage_account" "storage" {
  name = var.storage_account_name
  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  account_tier = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "model_container" {
  name = var.storage_container_name
  storage_account_id = azurerm_storage_account.storage.id
  container_access_type = "private"
}

##### Model blobs ###################################################
resource "azurerm_storage_blob" "model_blob" {
  name = "model.pkl"
  storage_account_name = azurerm_storage_account.storage.name
  storage_container_name = azurerm_storage_container.model_container.name
  type = "Block"
  source = var.model_source_path
}

resource "azurerm_storage_blob" "city_mapping_blob" {
  name = "city_mapping.pkl"
  storage_account_name = azurerm_storage_account.storage.name
  storage_container_name = azurerm_storage_container.model_container.name
  type = "Block"
  source = var.city_mapping_source_path
}

##### SAS token for blobs ###################################################
data "azurerm_storage_account_sas" "blob_sas" {
  connection_string = azurerm_storage_account.storage.primary_connection_string

  https_only = true
  start = var.sas_start
  expiry = var.sas_expiry

  resource_types {
    service  = false
    container = false
    object = true
  }
  services {
    blob = true
  }
  permissions {
    read = true
    list = true
  }
}

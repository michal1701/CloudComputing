variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
  default     = "RealValuator"
}

variable "location" {
  description = "Azure region location."
  type        = string
  default     = "northeurope"
}

variable "storage_account_name" {
  description = "Name of the storage account."
  type        = string
  default     = "realvaluatorstorage"
}

variable "sql_server_name" {
  description = "Name of the SQL server."
  type        = string
  default     = "realvaluator-sql"
}

variable "sql_admin_user" {
  description = "SQL server admin username."
  type        = string
  default     = "adminuser"
}

variable "sql_admin_password" {
  description = "SQL server admin password."
  type        = string
  default     = "eigh8Ahk"
}

variable "sql_database_name" {
  description = "Name of the SQL database."
  type        = string
  default     = "predictionsdb"
}

variable "function_app_name" {
  description = "Name of the Azure Function App."
  type        = string
  default     = "realvaluator-function"
}

variable "function_app_plan_name" {
  description = "Name of the Azure Function App Service Plan."
  type        = string
  default     = "realvaluator-functionplan"
}

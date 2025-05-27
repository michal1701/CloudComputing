#### Core infrastructure ##############################################
variable "resource_group_name" {
  type = string
  default = "Real_Valuator"
}
variable "location" {
  type = string
  default = "northeurope"
}

##### Container ###################################################
variable "container_group_name" {
  type = string
  default = "realvalcontainer"
}
variable "container_image" {
  type = string
  default = "realvalacr.azurecr.io/realval:latest"
}
variable "registry_server" {
  type = string
  default = "realvalacr.azurecr.io"
}
variable "registry_username" {
  type = string
  default = "realvalacr"
}
variable "registry_password" {
  type = string
  default = "W7lEhuDMixqO4RjrdwnO+q9Yds1JNNrb4iYw1UdCAc+ACRCOC5cg"
}
variable "cpu" {
  type = number
  default = 1
}
variable "memory" {
  type = number
  default = 1.5
}
variable "dns_name_label" {
  type = string
  default = "realvaluatorapp"
}

##### SQL Server and database ###################################################
variable "sql_server_name" {
  type = string
  default = "realvaluator-sql"
}
variable "sql_admin_user" {
  type = string
  default = "sqladmin"
}
variable "sql_admin_password" {
  type = string
  default = "eigh8Ahk"   
}
variable "sql_database_name" {
  type = string
  default = "realvaluatordb"
}

##### Storage Account and model blobs ###################################################
variable "storage_account_name" {
  type = string
  default = "realvalstorage"   
}
variable "storage_container_name" {
  type = string
  default = "model"
}

variable "model_source_path" {
  type = string
  default = "../src/model/model.pkl"
}
variable "city_mapping_source_path" {
  type = string
  default = "../src/model/city_mapping.pkl"
}

variable "sas_start" {
  type = string
  default = "2025-05-26T00:00:00Z"
}
variable "sas_expiry" {
  type = string
  default = "2025-08-12T00:00:00Z"
}

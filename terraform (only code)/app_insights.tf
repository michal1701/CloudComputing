resource "azurerm_application_insights" "app_insights" {
  name                = "realvaluator-insights"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  application_type    = "web"
}

resource "azurerm_linux_web_app" "realvaluator_streamlit" {
  name                = "realvaluator-streamlit"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id = azurerm_service_plan.function_plan.id



  site_config { 
  }

  app_settings = {
    "WEBSITE_RUN_FROM_PACKAGE" = "1"
  }
}
